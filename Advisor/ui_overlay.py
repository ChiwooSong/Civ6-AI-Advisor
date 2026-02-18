import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, QPoint, pyqtSignal

class AdvisorOverlay(QWidget):
    analysis_requested = pyqtSignal(str) # 분석 요청 시그널 (버전 정보 포함)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.oldPos = self.pos()

    def initUI(self):
        # 창 속성 설정: 테두리 없음, 항상 위, 작업표시줄에 표시 안함
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        # 배경을 반투명하게 설정
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 400, 400) # 높이 증가 (콤보박스 공간 확보)

        layout = QVBoxLayout()
        
        # 제목 및 종료 버튼 레이아웃
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Civ 6 Gemini Advisor")
        self.title_label.setStyleSheet("color: gold; font-weight: bold; background-color: rgba(0, 0, 0, 180); padding: 5px;")
        header_layout.addWidget(self.title_label)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 25)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(180, 0, 0, 200);
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 230);
            }
        """)
        self.close_btn.clicked.connect(QApplication.instance().quit)
        header_layout.addWidget(self.close_btn)
        header_layout.setSpacing(0)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addLayout(header_layout)

        # 게임 버전 선택 콤보박스
        self.version_combo = QComboBox()
        self.version_combo.addItems(["오리지널 (Base Game)", "흥망성쇠 (Rise & Fall)", "몰려드는 폭풍 (Gathering Storm)"])
        self.version_combo.setCurrentIndex(2) # 기본값: 몰려드는 폭풍
        self.version_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                border: 1px solid gold;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: white;
                selection-background-color: gold;
                selection-color: black;
            }
        """)
        layout.addWidget(self.version_combo)

        # 텍스트 출력 영역
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setPlainText("데이터 대기 중...")
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                border: 1px solid gold;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.text_area)

        # 분석 요청 버튼
        self.analyze_btn = QPushButton("전략 분석 요청 (Click)")
        self.analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(20, 100, 200, 200);
                color: white;
                font-weight: bold;
                border: 1px solid white;
                padding: 8px;
                border-bottom-right-radius: 10px;
                border-bottom-left-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(40, 120, 220, 230);
            }
            QPushButton:pressed {
                background-color: rgba(10, 80, 180, 230);
            }
            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 150);
                color: #aaa;
            }
        """)
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        self.analyze_btn.setEnabled(False) # 데이터가 오기 전엔 비활성화
        layout.addWidget(self.analyze_btn)
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def on_analyze_clicked(self):
        """버튼 클릭 시 즉시 UI 반응 (UX 개선)"""
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("요청 중...")
        self.text_area.setPlainText("⏳ AI에게 분석을 요청하고 있습니다...")
        
        # 선택된 게임 버전 가져오기
        selected_version = self.version_combo.currentText()
        self.analysis_requested.emit(selected_version)

    def update_advice(self, text):
        self.text_area.setMarkdown(text)
    
    def set_button_enabled(self, enabled):
        self.analyze_btn.setEnabled(enabled)
        if enabled:
            self.analyze_btn.setText("전략 분석 요청 (Click)")
        else:
            self.analyze_btn.setText("데이터 대기 중...")

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
