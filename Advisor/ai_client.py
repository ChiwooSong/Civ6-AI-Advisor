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
        
        당신은 다음 정보를 심도 있게 분석해야 합니다:
        1. 국가 지표: 과학, 문화, 신앙, 금 생산량 및 누적치.
        2. 연구 및 사회 제도: 현재 진행 중인 항목이 승리 목표와 일치하는지, 유레카/영감을 고려한 효율적 연구인지 판단.
        3. 정책 카드: 현재 장착된 카드가 국가 상황(전쟁, 확장, 경제 등)에 최적화되어 있는지 평가.
        4. 도시 생산: 각 도시에서 생산 중인 유닛/건물/특수지구가 현재 상황에 적절한지 분석 (예: 전쟁 위협 시 군사 유닛 생산 권장).
        
        응답은 다음 구조를 따르세요:
        1. 📊 현재 상황 요약: 턴수, 문명/지도자 특징, 주요 산출량 요약.
        2. 💡 전략적 평가: 연구/제도/정책 설정에 대한 비판적 평가 및 개선점.
        3. ⚠️ 즉각적 조언 (10턴 내): 도시 생산 항목 변경 추천 및 긴급한 행동 지침.
        4. 🏆 장기 승리 전략: 현재 상황에서 가장 유망한 승리 유형과 그를 위한 로드맵.
        
        한국어로 친절하고 전문적인 어조로 답변하십시오.
        """

    def get_advice(self, game_data, version="몰려드는 폭풍 (Gathering Storm)"):
        prompt = f"""현재 게임 데이터: {game_data}
        
플레이 중인 문명 6 버전(DLC): {version}

위 데이터와 게임 버전을 고려하여 전략적 조언을 부탁드립니다.
특히 해당 확장팩의 특수 규칙(충성도, 암흑기, 환경 효과 등)이 적용된다면 이를 고려해 주세요."""
        
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