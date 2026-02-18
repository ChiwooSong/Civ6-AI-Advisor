import os
import sys
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
    advice_updated = pyqtSignal(str) # AI 조언 업데이트 시그널
    status_updated = pyqtSignal(str) # 상태 메시지 업데이트
    data_ready = pyqtSignal(bool)    # 분석 버튼 활성화 여부

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.advisor = None
        self.current_data = None # 현재 턴 데이터 저장

    @pyqtSlot(dict)
    def process_data(self, data):
        """새로운 데이터를 받으면 저장하고 UI에 알림 (자동 분석 X)"""
        self.current_data = data
        turn = data.get("header", {}).get("turn", "?")
        
        # 상태 업데이트
        msg = f"Turn {turn} 데이터 준비 완료.\n분석 버튼을 눌러 전략을 확인하세요."
        self.advice_updated.emit(msg)
        self.data_ready.emit(True) # 버튼 활성화

    @pyqtSlot()
    def perform_analysis(self):
        """버튼 클릭 시 실행: 저장된 데이터로 AI 분석 시작"""
        if not self.current_data:
            self.advice_updated.emit("분석할 데이터가 없습니다.")
            return

        if not self.advisor:
            self.advisor = GeminiAdvisor(self.api_key)
        
        self.advice_updated.emit("🔍 전략 분석 중... (잠시만 기다려주세요)")
        self.data_ready.emit(False) # 분석 중 버튼 비활성화
        
        try:
            advice = self.advisor.get_advice(self.current_data)
            self.advice_updated.emit(advice)
        except Exception as e:
            self.advice_updated.emit(f"❌ 분석 중 오류 발생: {e}")
        finally:
            self.data_ready.emit(True) # 다시 활성화

# 시그널 전달용 헬퍼 클래스
class SignalEmitter(QObject):
    data_received = pyqtSignal(dict)

class AdvisorApp:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.log_path = os.getenv("CIV6_LOG_PATH")
        self.overlay = None
        self.worker = None
        self.worker_thread = None
        self.observer = None
        self.data_signal = None

    def run(self):
        print("=== Civ6 Gemini Strategist Advisor ===")
        
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("Error: API 키가 설정되지 않았습니다.")
            return

        app = QApplication(sys.argv)
        
        self.overlay = AdvisorOverlay()
        self.overlay.show()

        # --- 워커 스레드 설정 ---
        self.worker_thread = QThread()
        self.worker = AdvisorWorker(self.api_key)
        self.worker.moveToThread(self.worker_thread)
        
        # 1. 로그 데이터 수신 -> 워커 데이터 처리 (저장)
        self.data_signal = SignalEmitter()
        self.data_signal.data_received.connect(self.worker.process_data)
        
        # 2. UI 버튼 클릭 -> 워커 분석 시작
        self.overlay.analysis_requested.connect(self.worker.perform_analysis)

        # 3. 워커 결과 -> UI 업데이트
        self.worker.advice_updated.connect(self.overlay.update_advice)
        self.worker.data_ready.connect(self.overlay.set_button_enabled) # 버튼 활성화 제어

        self.worker_thread.start()
        # ------------------------

        # 로그 감시 시작
        print(f"로그 모니터링 시작: {self.log_path}")
        self.observer = start_watching(self.log_path, lambda d: self.data_signal.data_received.emit(d))

        print("Advisor 실행 중... (창을 닫으면 종료됩니다)")
        
        try:
            sys.exit(app.exec())
        except SystemExit:
            self.cleanup()

    def cleanup(self):
        if self.observer:
            self.observer.stop()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        print("종료합니다.")

if __name__ == "__main__":
    app = AdvisorApp()
    app.run()
