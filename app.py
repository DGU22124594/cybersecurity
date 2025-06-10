# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse
import re
import math
from collections import Counter
import joblib

app = Flask(__name__)
CORS(app)  # Android 에서 Cross-Origin 요청 허용

# ———————— 특징 추출 함수 재정의 ————————
def calculate_entropy(domain: str) -> float:
    if not domain:
        return 0.0
    counts = Counter(domain)
    probs = [cnt / len(domain) for cnt in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def has_ip(url: str) -> int:
    ip_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
    return int(bool(ip_pattern.search(url)))

def extract_features(url: str) -> dict:
    url = url.replace("[.]", ".")
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.", "") if parsed.netloc else ""
    path = parsed.path
    query = parsed.query

    return {
        'url_length'         : len(url),
        'num_digits'         : sum(c.isdigit() for c in url),
        'num_special_chars'  : len(re.findall(r'[^a-zA-Z0-9]', url)),
        'has_https'          : 1 if parsed.scheme == 'https' else 0,
        'domain_entropy'     : calculate_entropy(domain),
        'num_subdomains'     : max(0, domain.count('.') - 1),
        'path_depth'         : len([p for p in path.split('/') if p]),
        'num_query_params'   : len(query.split('&')) if query else 0,
        'has_ip'             : has_ip(url)
    }

# ———————— 모델 로드 ————————
model = joblib.load('stacking_model.pkl')

# ———————— 예측 엔드포인트 ————————
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    url = data.get('url', '')
    feats = extract_features(url)
    X = [list(feats.values())]

    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0].tolist()  # [prob_benign, prob_malicious]

    return jsonify({
        'url': url,
        'prediction': int(pred),            # 0=benign, 1=malicious
        'probabilities': {
            'benign': proba[0],
            'malicious': proba[1]
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
