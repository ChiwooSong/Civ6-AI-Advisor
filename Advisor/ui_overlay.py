import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QPalette

class AdvisorOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.oldPos = self.pos()

    def initUI(self):
        # 창 속성 설정: 테두리 없음, 항상 위, 작업표시줄에 표시 안함
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        # 배경을 반투명하게 설정
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        
        # 제목 표시줄 역할
        self.title_label = QLabel("Civ 6 Gemini Advisor")
        self.title_label.setStyleSheet("color: gold; font-weight: bold; background-color: rgba(0, 0, 0, 180); padding: 5px;")
        layout.addWidget(self.title_label)

        # 텍스트 출력 영역
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setPlainText("AI 분석을 기다리는 중...")
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                border: 1px solid gold;
                font-size: 14px;
                border-bottom-right-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        layout.addWidget(self.text_area)
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def update_advice(self, text):
        self.text_area.setPlainText(text)

    # 창 드래그 이동 기능 구현
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = AdvisorOverlay()
    overlay.show()
    sys.exit(app.exec())
