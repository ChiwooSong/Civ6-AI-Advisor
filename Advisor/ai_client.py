from google import genai
from google.genai import types

class GeminiAdvisor:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        # 최신 모델 사용 (gemini-2.0-flash가 빠르고 성능 좋음)
        self.model_name = "gemini-2.0-flash"
        
        self.system_instruction = """
        당신은 문명 6 (Civilization VI)의 세계적인 전략 참모입니다. 
        플레이어가 제공하는 게임 데이터(JSON 형식)를 분석하여 최적의 승리 전략을 제시하십시오.
        
        응답은 다음 구조를 따르세요:
        1. 현재 상황 요약 (턴, 국가 상태)
        2. 즉각적인 위협 및 기회
        3. 향후 10턴 내 권장 행동
        4. 장기적인 승리 전략 조언
        
        한국어로 친절하고 전문적인 어조로 답변하십시오.
        """

    def get_advice(self, game_data):
        prompt = f"""현재 게임 데이터: {game_data}

이 상황에 대한 전략적 조언을 부탁드립니다."""
        
        try:
            # 새로운 SDK 호출 방식
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )
            )
            return response.text
        except Exception as e:
            return f"AI 조언 생성 중 오류 발생: {e}"