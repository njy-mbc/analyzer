# analyzer.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- Gemini API 설정 ---
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
except Exception as e:
    print(f"Gemini 모델 초기화 중 오류 발생: {e}")
    model = None
# --- 설정 끝 ---


def create_daily_report(analysis_data):
    """
    분석 데이터를 기반으로 Gemini API를 호출하여 일일 비즈니스 레포트를 생성합니다.
    """
    if not model:
        return "Gemini 모델이 초기화되지 않아 레포트를 생성할 수 없습니다."

    try:
        # Gemini API에 보낼 프롬프트를 작성합니다.
        prompt = f"""
        당신은 전문 데이터 분석가입니다. 다음은 온라인 마켓의 하루 동안의 데이터입니다.
        이 데이터를 기반으로 경영진이 볼 '일일 비즈니스 레포트'를 마크다운 형식으로 작성해주세요.

        데이터:
        ```json
        {json.dumps(analysis_data, indent=2, ensure_ascii=False)}
        ```

        마크다운 레포트 작성 가이드라인:
        - "네, 전문 데이터 분석가로서 제공해주신"과 같은 평문은 필요 없습니다. 데이터 분석후 다음과 같이 레포트만 제공해주세요.
        - # 일일 비즈니스 레포트 (오늘 날짜) 로 시작하세요.
        - ## 주요 지표 요약 섹션을 만드세요. KPI 데이터를 어제와 비교하여 성장률(%)과 함께 명확한 표로 제시해주세요.
        - ## 매출 상세 분석 섹션을 만드세요. 리소스 카테고리별 매출, 시간대별 매출 데이터를 기반으로 어떤 상품이, 언제 많이 팔렸는지 분석하고 인사이트를 도출해주세요.
        - ## 사용자 동향 분석 섹션을 만드세요. 전체 사용자 중 활성/휴면 사용자 비율을 분석하고 고객 유지 관점에서 의견을 제시해주세요.
        - ## 상품 랭킹 분석 섹션을 만드세요. 이달의 인기 상품 TOP5를 언급하고, 왜 이 상품들이 인기가 있는지 추측해보세요.
        - ## 결론 및 제안 섹션을 만드세요. 분석 내용을 종합하여 긍정적인 부분과 개선이 필요한 부분을 요약하고, 내일 시도해볼 만한 액션 아이템을 1~2가지 제안해주세요.
        - 전체적으로 전문가적이고, 객관적인 데이터를 근거로 논리적인 분석을 제공해야 합니다.
        """

        # Gemini API 호출
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Gemini 레포트 생성 중 오류 발생: {e}")
        return f"Gemini 레포트 생성 중 오류가 발생했습니다: {e}"