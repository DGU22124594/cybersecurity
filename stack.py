import pandas as pd
import urllib.parse
import re
import math
from collections import Counter
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 도메인 엔트로피 계산
def calculate_entropy(domain: str) -> float:
    if not domain:
        return 0.0
    counts = Counter(domain)
    probs = [cnt / len(domain) for cnt in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

# IPv4 주소 포함 여부
def has_ip(url: str) -> int:
    ip_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
    return int(bool(ip_pattern.search(url)))

# 특징 추출 함수
def extract_features(url: str) -> dict:
    url = url.replace("[.]", ".")
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.replace("www.", "") if parsed.netloc else ""
        path = parsed.path
        query = parsed.query
        return {
            'url_length': len(url),
            'num_digits': sum(c.isdigit() for c in url),
            'num_special_chars': len(re.findall(r'[^a-zA-Z0-9]', url)),
            'has_https': 1 if parsed.scheme == 'https' else 0,
            'domain_entropy': calculate_entropy(domain),
            'num_subdomains': max(0, domain.count('.') - 1),
            'path_depth': len([p for p in path.split('/') if p]),
            'num_query_params': len(query.split('&')) if query else 0,
            'has_ip': has_ip(url)
        }
    except Exception:
        # 오류 시 0으로 채움
        return dict.fromkeys([
            'url_length', 'num_digits', 'num_special_chars',
            'has_https', 'domain_entropy', 'num_subdomains',
            'path_depth', 'num_query_params', 'has_ip'
        ], 0)

if __name__ == '__main__':
    # 1) CSV 읽기: 인코딩 자동 재시도
    encodings = ['utf-8', 'cp949', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv('urldata.csv', encoding=enc)
            print(f"Loaded CSV with encoding: {enc}")
            break
        except Exception as e:
            print(f"Failed to read with {enc}: {e}")
    else:
        raise RuntimeError('Could not read urldata.csv with any tested encoding.')

    # 2) 라벨 이진화 및 NaN 제거
    df = df[df['url'].notnull() & df['label'].notnull()]
    # 정상:0, 악성:1, 나머지 라벨은 제거
    binary_map = {'benign': 0, 'malicious': 1}
    df['binary_label'] = df['label'].map(binary_map)
    df = df[df['binary_label'].notnull()]
    df['binary_label'] = df['binary_label'].astype(int)

    # 3) 피처 생성
    X = pd.DataFrame([extract_features(u) for u in df['url']])
    y = df['binary_label']

    # 4) 학습/테스트 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    print(f"Train samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")

    # 5) 모델 정의 및 학습
    rf = RandomForestClassifier(n_estimators=100, random_state=1)
    xgb = XGBClassifier(n_estimators=100, use_label_encoder=False,
                        eval_metric='logloss', random_state=1)
    meta = LogisticRegression(max_iter=1000)
    stacking = StackingClassifier(
        estimators=[('rf', rf), ('xgb', xgb)],
        final_estimator=meta, cv=5, passthrough=False
    )
    stacking.fit(X_train, y_train)

    # 6) 평가
    y_pred = stacking.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=['benign','malicious']))

    # 7) 모델 저장
    joblib.dump(stacking, 'stacking_model.pkl')
    print('Model saved to stacking_model.pkl')
