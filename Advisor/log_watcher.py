import time
import json
import os
import threading

class Civ6LogPoller:
    def __init__(self, log_path, callback, check_interval=1.0):
        self.log_path = log_path
        self.callback = callback
        self.check_interval = check_interval
        self.running = False
        self.last_position = 0
        self.thread = None

    def start(self):
        if self.running:
            return
        
        # 파일 존재 확인 및 생성
        log_dir = os.path.dirname(self.log_path)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError:
                print(f"Error: Log directory could not be created: {log_dir}")
                return

        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                pass
        
        # 초기 파일 위치 설정 (파일 끝)
        self.last_position = os.path.getsize(self.log_path)

        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        return self

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

    def join(self):
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def _poll_loop(self):
        while self.running:
            try:
                # 파일 크기 확인
                current_size = os.path.getsize(self.log_path)
                
                # 파일이 작아졌으면 (로그 초기화 등) 처음부터 다시 읽기
                if current_size < self.last_position:
                    self.last_position = 0
                
                # 새로운 내용이 있으면 읽기
                if current_size > self.last_position:
                    with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(self.last_position)
                        lines = f.readlines()
                        self.last_position = f.tell()
                        
                        for line in lines:
                            if "[CIV6_AI_DATA]" in line:
                                try:
                                    # 접두어 제거 후 JSON 파싱
                                    parts = line.split("[CIV6_AI_DATA]")
                                    if len(parts) > 1:
                                        json_str = parts[1].strip()
                                        if json_str:
                                            data = json.loads(json_str)
                                            self.callback(data)
                                except (IndexError, json.JSONDecodeError) as e:
                                    print(f"Error parsing JSON: {e}")
                                except Exception as e:
                                    print(f"Unexpected error processing line: {e}")
            
            except FileNotFoundError:
                # 파일이 삭제된 경우 대기 후 재시도
                self.last_position = 0
            except PermissionError:
                # 다른 프로세스가 파일 사용 중인 경우 잠시 대기
                pass
            except Exception as e:
                print(f"Polling error: {e}")
            
            time.sleep(self.check_interval)

def start_watching(log_path, callback):
    poller = Civ6LogPoller(log_path, callback)
    poller.start()
    return poller
