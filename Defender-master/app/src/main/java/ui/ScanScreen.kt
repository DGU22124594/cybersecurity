package ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalInspectionMode
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.alfa.ui.theme.ALFATheme

@Composable
fun ScanScreen(modifier: Modifier = Modifier) {
    var lastScanned by remember { mutableStateOf<String?>(null) }
    var resultColor by remember { mutableStateOf(Color.Transparent) }
    var resultText by remember { mutableStateOf("") }

    val isPreview = LocalInspectionMode.current

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        if (!isPreview) {
            CameraPreview(
                modifier = Modifier.fillMaxSize(),
                onQrScanned = { qrContent ->
                    if (qrContent != lastScanned) {
                        lastScanned = qrContent

                        if (qrContent.startsWith("http://") || qrContent.startsWith("https://")) {
                            resultColor = if (
                                qrContent.contains("phishing") ||
                                qrContent.contains("virus") ||
                                qrContent.contains("t.me")
                            ) {
                                Color.Red.also { resultText = "⚠️ ВОЗМОЖНО ОПАСНАЯ ССЫЛКА" }
                            } else {
                                Color(0xFF4CAF50).also { resultText = "✅ ССЫЛКА БЕЗОПАСНА" }
                            }
                        } else {
                            resultColor = Color.Gray
                            resultText = "Найдено: $qrContent"
                        }
                    }
                }
            )

            CameraOverlay()
        } else {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.DarkGray),
                contentAlignment = Alignment.Center
            ) {
                Text("Камера отключена в Preview", color = Color.White)
            }
        }

        if (resultText.isNotEmpty()) {
            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .background(resultColor)
                    .padding(16.dp)
            ) {
                Text(text = resultText, color = Color.White)
            }
        }
    }
}
@Composable
fun CameraOverlay() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = Modifier
                .size(260.dp)
                .border(
                    width = 3.dp,
                    color = MaterialTheme.colorScheme.primary,
                    shape = RoundedCornerShape(8.dp)
                )
        )

        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 64.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Наведите камеру на QR-код",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onBackground
            )
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun PreviewScanScreenSafe() {
    ALFATheme {
        ScanScreen()
    }
}
