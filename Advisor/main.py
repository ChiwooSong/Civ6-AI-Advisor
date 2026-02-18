import os
import sys
import time
import threading
from dotenv import load_dotenv
from log_watcher import start_watching
from ai_client import GeminiAdvisor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from ui_overlay import AdvisorOverlay

# 환경 변수 로드
load_dotenv()

class AdvisorWorker(QObject):
    # 데이터를 전달하기 위한 시그널 정의
    advice_updated = pyqtSignal(str)
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.advisor = None
        self.current_data = None

    @pyqtSlot(dict)
    def process_data(self, data):
        # 이 함수는 worker_thread에서 실행됨
        if not self.advisor:
            self.advisor = GeminiAdvisor(self.api_key)
        
        # 분석 시작 알림
        self.advice_updated.emit("🔍 새로운 상황 판단 중...")
        
        try:
            # 실제 AI 분석 (네트워크 통신)
            advice = self.advisor.get_advice(data)
            # 분석 결과 전달
            self.advice_updated.emit(advice)
        except Exception as e:
            self.advice_updated.emit(f"❌ 분석 중 오류 발생: {e}")

class AdvisorApp:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.log_path = os.getenv("CIV6_LOG_PATH")
        self.overlay = None
        self.worker = None
        self.worker_thread = None
        self.observer = None

    def on_log_update(self, data):
        # log_watcher 스레드에서 호출됨 -> 메인 스레드의 worker에게 데이터 전달
        if self.worker:
            # 스레드 간 안전한 신호 전달 (QueuedConnection 자동 적용)
            self.data_signal.emit(data)

    # 데이터 전달용 내부 시그널
    data_signal = pyqtSignal(dict)

    def run(self):
        print("=== Civ6 Gemini Strategist Advisor ===")
        
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("Error: API 키가 설정되지 않았습니다.")
            return

        app = QApplication(sys.argv)
        
        # UI 오버레이
        self.overlay = AdvisorOverlay()
        self.overlay.show()

        # --- 백그라운드 워커 스레드 설정 ---
        self.worker_thread = QThread()
        self.worker = AdvisorWorker(self.api_key)
        self.worker.moveToThread(self.worker_thread)
        
        # 시그널 연결
        # 1. 앱 클래스의 시그널 -> 워커의 슬롯
        self.data_signal = SignalEmitter()
        self.data_signal.data_received.connect(self.worker.process_data)
        
        # 2. 워커의 결과 시그널 -> UI 업데이트
        self.worker.advice_updated.connect(self.overlay.update_advice)
        
        self.worker_thread.start()
        # --------------------------------

        # 로그 감시 시작
        print(f"로그 모니터링 시작: {self.log_path}")
        self.observer = start_watching(self.log_path, lambda d: self.data_signal.data_received.emit(d))

        print("Advisor 실행 중...")
        
        try:
            exit_code = app.exec()
            self.cleanup()
            sys.exit(exit_code)
        except SystemExit:
            self.cleanup()

    def cleanup(self):
        if self.observer:
            self.observer.stop()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        print("종료합니다.")

# 시그널을 보내기 위한 간단한 클래스
class SignalEmitter(QObject):
    data_received = pyqtSignal(dict)

if __name__ == "__main__":
    # AdvisorApp에서 시그널을 정의하려면 QObject 상속이 필요하므로 
    # 대신 SignalEmitter를 사용하거나 구조를 약간 변경합니다.
    app = AdvisorApp()
    app.run()