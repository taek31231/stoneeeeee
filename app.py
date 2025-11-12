import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import json

# 실제 운영 시에는 secrets.toml 또는 환경 변수를 사용해야 합니다.
GEMINI_API_KEY = "AIzaSyCUVhECqNMDsoBZSyDXWrhAJN21PerZl_E"

# API 설정
# BASE_URL: Gemini API 기본 주소
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# --- 헬퍼 함수 ---

def image_to_base64(img):
    """PIL Image 객체를 base64 문자열로 변환합니다."""
    buff = BytesIO()
    # JPEG 포맷으로 저장 (일반적으로 안정적)
    img.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

# --- 암석 분류 함수 (Gemini API 호출) ---

def classify_rock(base64_image_data):
    """
    Gemini API를 호출하여 이미지를 분석하고 암석을 분류합니다.
    """
    # 1. API 키 로드 (하드코딩된 전역 변수 사용)
    api_key = GEMINI_API_KEY
    if not api_key:
        st.error("🚨 오류: API 키가 설정되지 않았습니다.")
        return None

    # 2. URL 구성 (403 Forbidden 오류 해결: 키를 URL 쿼리 파라미터에 직접 삽입)
    full_api_url = f"{BASE_URL}?key={api_key}"

    # 텍스트와 이미지 입력 모두를 처리하는 멀티모달 프롬프트
    prompt = """
    당신은 세계적인 지질학자입니다. 제공된 이미지의 암석을 분석하고, 
    다음 네 가지 정보(암석 이름, 유형, 설명, 정확도 추정)를 한국어로만 제공해야 합니다.
    응답은 아래의 Markdown 형식 틀을 엄격하게 지켜야 합니다.

    **암석 이름:** [분류된 암석의 이름]
    **암석 유형:** [화성암, 퇴적암, 또는 변성암]
    **설명:** [암석의 주요 특징 2-3가지에 대한 간략한 설명]
    **정확도 추정:** [당신의 전문 지식에 기반한 분류 정확도(%)]
    """
    
    # API 요청 페이로드 구성
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_image_data
                        }
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": "You are a professional geologist. Analyze the provided rock image and provide a classification in the specified Korean markdown format."}]
        }
    }

    # API 호출 
    with st.spinner("🌌 Gemini AI가 암석을 분석 중입니다..."):
        try:
            response = requests.post(
                full_api_url,  # 키가 포함된 최종 URL 사용
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 응답 구조 확인 및 텍스트 추출
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            return generated_text

        except requests.exceptions.RequestException as e:
            st.error(f"Gemini API 요청 오류 발생: {e}")
            try:
                st.error(f"서버 응답 본문: {response.text}")
            except Exception:
                pass
            return None
        except KeyError:
            st.error("Gemini API 응답 형식 오류가 발생했습니다. (응답 데이터 구조를 확인해 주세요)")
            return None


# --- Streamlit UI 설정 ---

st.set_page_config(page_title="⛏️ AI 암석 분류기", layout="centered")
st.title("⛏️ AI 암석 및 광물 분류기")
st.markdown("사진을 업로드하면 Gemini AI가 암석의 종류를 식별해 드립니다.")
st.markdown("---")


uploaded_file = st.file_uploader("📸 암석 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. 이미지 표시 및 base64 변환
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 암석 사진", use_column_width=True)
        base64_data = image_to_base64(image)
        
    except Exception as e:
        st.error(f"이미지 파일을 처리하는 중 오류가 발생했습니다: {e}")
        st.stop()
    
    # 2. 분류 버튼
    if st.button("✨ 암석 식별 시작", use_container_width=True):
        
        # 3. API 호출 및 결과 표시
        classification_result = classify_rock(base64_data)
        
        if classification_result:
            st.success("✅ 분석 완료!")
            st.subheader("🔬 분석 결과")
            # Markdown 형식으로 받은 결과를 그대로 출력
            st.markdown(classification_result)
            st.info("💡 **참고:** 이 결과는 AI가 이미지를 분석한 추정치이며, 실제 지질학적 분석을 대체할 수 없습니다.")
```eof
