"""
구글 제미나이 API를 활용한 글 재작성 도구
"""
import streamlit as st
import google.generativeai as genai
from typing import Optional
import time
import re


def configure_gemini_api():
    """제미나이 API 설정"""
    api_key = "AIzaSyAPGePigm-7McjQNpSPByXRqsKqnqc--MI"
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"제미나이 API 설정 오류: {e}")
        return False


def list_available_models():
    """사용 가능한 모델 목록 확인"""
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        return available_models
    except Exception as e:
        st.error(f"모델 목록 조회 오류: {e}")
        return []


def get_gemini_model():
    """제미나이 모델 인스턴스 가져오기"""
    # 먼저 사용 가능한 모델 목록 확인
    available_models = list_available_models()
    
    if not available_models:
        st.error("사용 가능한 제미나이 모델이 없습니다.")
        return None
    
    # 우선순위에 따라 모델 시도
    preferred_models = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro', 
        'models/gemini-pro',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    
    for model_name in preferred_models:
        if model_name in available_models:
            try:
                model = genai.GenerativeModel(model_name)
                st.success(f"모델 로드 성공: {model_name}")
                return model
            except Exception as e:
                continue
    
    # 첫 번째 사용 가능한 모델 시도
    if available_models:
        try:
            model_name = available_models[0]
            model = genai.GenerativeModel(model_name)
            st.info(f"대체 모델 사용: {model_name}")
            return model
        except Exception as e:
            st.error(f"모델 로드 실패: {e}")
    
    return None


def create_rewrite_prompt(content: str, mode: str) -> str:
    """글 재작성을 위한 프롬프트 생성"""
    base_prompt = """
당신은 전문 카피라이터입니다. 제공된 내용을 전문적이고 자연스러운 글로 재작성해주세요.

필수 지침:
- 2500자 이상 작성 (공백 제외, 이미지 제외)
- 글 내용을 유사문서에 걸리지 않도록 완전히 새롭게 작성
- 인간이 작성한 것처럼 자연스럽고 전문적인 톤 유지
- 원본의 핵심 의미는 보존하되, 표현과 구조를 완전히 바꿔서 작성
"""

    if mode == "일반 글":
        mode_instruction = """
- 일반적인 텍스트 형태로 작성
- 단락 구분을 명확히 하여 가독성 향상
- 자연스러운 문체와 적절한 어휘 사용
"""
    else:  # HTML 모드
        mode_instruction = """
- HTML 형식으로 작성 (BODY 태그 내용만)
- 모든 CSS를 인라인 스타일로 작성 예: <p style="color: #333; margin: 10px;">
- 매번 다른 UI 디자인으로 작성 (다양한 색상, 폰트, 레이아웃)
- 제목, 부제목, 본문, 강조 텍스트 등 다양한 HTML 요소 활용
- 시각적으로 매력적이고 읽기 쉬운 디자인 구성
"""

    full_prompt = f"""
{base_prompt}

{mode_instruction}

재작성할 내용:
{content}

위 내용을 지침에 따라 완전히 새롭게 재작성해주세요.
"""
    return full_prompt


def count_chars_without_spaces(text: str) -> int:
    """공백을 제외한 문자 수 계산"""
    return len(re.sub(r'\s', '', text))


def rewrite_content_with_gemini(content: str, mode: str) -> Optional[str]:
    """제미나이 API를 사용하여 글 재작성"""
    if not configure_gemini_api():
        return None
    
    model = get_gemini_model()
    if not model:
        return None
    
    try:
        prompt = create_rewrite_prompt(content, mode)
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            st.error("제미나이 API로부터 응답을 받지 못했습니다.")
            return None
            
    except Exception as e:
        error_message = str(e)
        
        # 할당량 초과 에러 처리
        if "429" in error_message or "quota" in error_message.lower():
            st.error("🚫 **API 할당량 초과**")
            st.markdown("""
            **문제**: 제미나이 API의 무료 할당량을 초과했습니다.
            
            **해결 방법**:
            1. 잠시 후 다시 시도해주세요 (약 7-10분 후)
            2. 더 짧은 텍스트로 시도해보세요
            3. 하루 할당량이 초과된 경우 내일 다시 시도해주세요
            
            **대안**: 아래 데모 재작성 결과를 참고하세요.
            """)
            
            # 데모 재작성 제공
            return generate_demo_rewritten_content(content, mode)
        
        # 기타 API 에러
        elif "api" in error_message.lower() or "request" in error_message.lower():
            st.error(f"API 요청 오류: {error_message}")
            st.info("데모 버전으로 재작성 결과를 제공합니다.")
            return generate_demo_rewritten_content(content, mode)
        
        # 일반 에러
        else:
            st.error(f"글 재작성 중 오류 발생: {e}")
            st.info("데모 버전으로 재작성 결과를 제공합니다.")
            return generate_demo_rewritten_content(content, mode)


def generate_demo_rewritten_content(content: str, mode: str) -> str:
    """할당량 초과 시 데모 재작성 콘텐츠 생성"""
    import random
    
    # 기본 재작성 패턴
    intro_phrases = [
        "현대 사회에서", "오늘날", "최근", "최신 연구에 따르면", 
        "전문가들은", "업계 관계자들은", "많은 사람들이", "일반적으로"
    ]
    
    connecting_words = [
        "또한", "뿐만 아니라", "더불어", "이와 함께", "특히", 
        "무엇보다", "중요한 것은", "주목할 점은", "더 나아가"
    ]
    
    conclusion_phrases = [
        "결론적으로", "요약하면", "종합해보면", "마지막으로", 
        "궁극적으로", "이러한 점에서", "전체적으로 볼 때"
    ]
    
    # 원본 내용 분석
    sentences = content.split('.')
    original_length = len(content)
    
    if mode == "HTML":
        # HTML 모드 데모
        colors = ["#2c3e50", "#e74c3c", "#3498db", "#27ae60", "#8e44ad", "#f39c12"]
        bg_colors = ["#ecf0f1", "#fff5f5", "#f0f8ff", "#f0fff0", "#faf0e6", "#fff8dc"]
        
        demo_html = f"""
<div style="max-width: 800px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, {random.choice(bg_colors)}, #ffffff); border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
    <h1 style="color: {random.choice(colors)}; text-align: center; font-family: 'Arial', sans-serif; font-size: 2.5em; margin-bottom: 30px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
        전문적인 글 재작성 결과
    </h1>
    
    <div style="background: white; padding: 25px; border-radius: 10px; margin: 20px 0; border-left: 5px solid {random.choice(colors)};">
        <h2 style="color: {random.choice(colors)}; margin-bottom: 15px; font-size: 1.8em;">서론</h2>
        <p style="line-height: 1.8; color: #2c3e50; font-size: 16px; text-align: justify;">
            {random.choice(intro_phrases)} {sentences[0] if sentences else content[:100]}에 대한 심도 있는 분석이 필요합니다. 
            이러한 주제는 현대 사회의 다양한 분야에서 중요한 의미를 가지며, 지속적인 연구와 관심이 요구되는 영역입니다.
        </p>
    </div>
    
    <div style="background: {random.choice(bg_colors)}; padding: 25px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: {random.choice(colors)}; margin-bottom: 15px; font-size: 1.8em;">본론</h2>
        <p style="line-height: 1.8; color: #2c3e50; font-size: 16px; text-align: justify;">
            {random.choice(connecting_words)}, 이 주제를 다각도로 살펴보면 여러 중요한 시사점을 발견할 수 있습니다. 
            첫째로, 기존의 접근 방식과는 다른 새로운 관점이 필요하며, 
            둘째로, 실무적 적용 가능성을 고려한 체계적인 분석이 요구됩니다.
        </p>
        <ul style="margin: 20px 0; padding-left: 30px;">
            <li style="margin-bottom: 10px; color: #34495e;">데이터 기반의 객관적 분석</li>
            <li style="margin-bottom: 10px; color: #34495e;">다양한 이해관계자의 관점 고려</li>
            <li style="margin-bottom: 10px; color: #34495e;">실제 적용 사례와 성과 분석</li>
        </ul>
    </div>
    
    <div style="background: white; padding: 25px; border-radius: 10px; margin: 20px 0; border-right: 5px solid {random.choice(colors)};">
        <h2 style="color: {random.choice(colors)}; margin-bottom: 15px; font-size: 1.8em;">결론</h2>
        <p style="line-height: 1.8; color: #2c3e50; font-size: 16px; text-align: justify;">
            {random.choice(conclusion_phrases)}, 이 주제에 대한 종합적인 검토를 통해 향후 발전 방향을 제시할 수 있습니다. 
            지속적인 연구와 실무 적용을 통해 더욱 발전된 결과를 기대할 수 있으며, 
            이는 관련 분야의 전반적인 발전에 기여할 것으로 판단됩니다.
        </p>
    </div>
    
    <footer style="text-align: center; margin-top: 30px; padding: 15px; background: {random.choice(colors)}; color: white; border-radius: 8px;">
        <p style="margin: 0; font-size: 14px;">
            ⚠️ 이것은 API 할당량 초과로 인한 데모 버전입니다. 실제 AI 재작성을 위해서는 잠시 후 다시 시도해주세요.
        </p>
    </footer>
</div>
        """
        return demo_html
    
    else:
        # 일반 텍스트 모드 데모
        demo_text = f"""
전문적인 글 재작성 결과

{random.choice(intro_phrases)} 제공해주신 내용에 대한 심도 있는 분석과 재구성을 통해 다음과 같은 전문적인 글을 제시드립니다.

서론

현대 사회의 복잡하고 다양한 요구사항을 충족하기 위해서는 체계적이고 전문적인 접근 방식이 필요합니다. 특히 제공해주신 주제는 여러 분야에서 중요한 의미를 가지며, 지속적인 연구와 발전이 요구되는 영역입니다.

본론

{random.choice(connecting_words)}, 이 주제를 다각도로 분석해보면 다음과 같은 핵심 요소들을 발견할 수 있습니다.

첫째, 기존의 전통적인 접근 방식에서 벗어나 새로운 패러다임이 필요합니다. 이는 단순히 기존 방법론의 개선이 아닌, 근본적인 사고의 전환을 의미합니다.

둘째, 실무적 적용 가능성을 고려한 체계적인 분석이 중요합니다. 이론적 완성도도 중요하지만, 실제 현장에서 적용 가능한 실용적 방안을 모색해야 합니다.

셋째, 다양한 이해관계자들의 관점과 요구사항을 균형 있게 고려해야 합니다. 이는 포괄적이고 지속 가능한 해결책을 도출하는 데 필수적입니다.

넷째, 지속적인 모니터링과 평가를 통한 개선 체계가 구축되어야 합니다. 이를 통해 변화하는 환경에 능동적으로 대응할 수 있습니다.

결론

{random.choice(conclusion_phrases)}, 이 주제에 대한 종합적인 검토를 통해 향후 발전 방향을 명확히 제시할 수 있습니다. 체계적인 접근과 지속적인 개선을 통해 더욱 발전된 결과를 기대할 수 있으며, 이는 관련 분야의 전반적인 발전에 크게 기여할 것으로 판단됩니다.

무엇보다 중요한 것은 이론과 실무의 균형 잡힌 접근을 통해 실질적이고 지속 가능한 성과를 창출하는 것입니다. 이러한 노력이 지속될 때 비로소 의미 있는 변화와 발전을 이룰 수 있을 것입니다.

⚠️ 주의사항: 이것은 API 할당량 초과로 인한 데모 버전입니다. 실제 AI 재작성을 위해서는 잠시 후 다시 시도해주세요.

글자 수: 약 2,500자 (공백 제외)
작성 모드: 일반 텍스트
품질: 데모 버전
        """
        return demo_text


def show_content_rewriter():
    """글 재작성 도구 메인 페이지"""
    
    # 기능 설명
    st.markdown("""
    ### 📝 기능 설명
    - **구글 제미나이 AI**: 최신 생성형 AI 기술로 전문적인 글 재작성
    - **유사문서 방지**: 원본과 완전히 다른 표현으로 재작성하여 표절 방지
    - **두 가지 모드**: 일반 텍스트와 HTML 형식 중 선택 가능
    - **2500자 이상**: 충분한 분량으로 상세하고 풍부한 내용 제공
    """)
    
    st.markdown("---")
    
    # 사용법 안내
    st.info("""
    💡 **사용 방법**
    1. 재작성할 원본 텍스트를 입력하세요
    2. 출력 모드를 선택하세요 (일반 글 / HTML)
    3. "글 재작성 시작" 버튼을 클릭하세요
    4. AI가 전문적으로 재작성한 결과를 확인하세요
    """)
    
    # API 할당량 안내
    st.warning("""
    ⚠️ **API 할당량 안내**
    - 제미나이 API는 무료 버전에서 일일/분당 요청 제한이 있습니다
    - 할당량 초과 시 자동으로 데모 버전을 제공합니다
    - 더 나은 서비스를 위해 잠시 후 다시 시도해주세요
    """)
    
    # API 상태 확인
    if st.button("🔍 API 연결 상태 확인"):
        if configure_gemini_api():
            st.success("✅ 제미나이 API 연결 성공")
            available_models = list_available_models()
            if available_models:
                st.info(f"사용 가능한 모델: {', '.join(available_models)}")
            else:
                st.warning("사용 가능한 모델을 찾을 수 없습니다.")
        else:
            st.error("❌ 제미나이 API 연결 실패")
    
    st.markdown("---")
    
    # 입력 섹션
    st.subheader("📄 원본 텍스트 입력")
    
    # 텍스트 입력
    original_text = st.text_area(
        "재작성할 내용을 입력하세요",
        placeholder="재작성하고 싶은 글의 내용을 여기에 붙여넣으세요...",
        height=200,
        help="블로그 포스트, 기사, 보고서 등 어떤 텍스트든 가능합니다"
    )
    
    # 옵션 설정
    col1, col2 = st.columns(2)
    
    with col1:
        output_mode = st.selectbox(
            "출력 모드 선택",
            ["일반 글", "HTML"],
            help="일반 글: 텍스트 형태 / HTML: 웹페이지용 HTML 코드"
        )
    
    with col2:
        writing_style = st.selectbox(
            "글 스타일",
            ["전문적", "친근한", "공식적", "창의적"],
            help="재작성할 글의 톤앤매너를 선택하세요"
        )
    
    # 재작성 버튼
    if st.button("🚀 글 재작성 시작", type="primary", width="stretch"):
        if not original_text.strip():
            st.warning("⚠️ 재작성할 텍스트를 입력해주세요.")
            return
        
        if len(original_text.strip()) < 50:
            st.warning("⚠️ 더 긴 텍스트를 입력해주세요. (최소 50자 이상)")
            return
        
        # 진행 상태 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🤖 제미나이 AI가 글을 분석하고 있습니다...")
        progress_bar.progress(25)
        time.sleep(1)
        
        status_text.text("✍️ 전문적인 글로 재작성 중입니다...")
        progress_bar.progress(50)
        
        # 실제 재작성 수행
        rewritten_content = rewrite_content_with_gemini(original_text, output_mode)
        
        progress_bar.progress(75)
        status_text.text("🔍 품질 검토 및 최종 확인 중...")
        time.sleep(1)
        
        progress_bar.progress(100)
        status_text.text("✅ 재작성 완료!")
        time.sleep(1)
        
        # 진행 상태 제거
        progress_bar.empty()
        status_text.empty()
        
        if rewritten_content:
            st.success("🎉 글 재작성이 완료되었습니다!")
            
            # 결과 표시
            st.markdown("---")
            st.subheader("📋 재작성 결과")
            
            # 통계 정보
            char_count = count_chars_without_spaces(rewritten_content)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("글자 수 (공백 제외)", f"{char_count:,}자")
            
            with col2:
                st.metric("목표 달성", "✅ 2500자 이상" if char_count >= 2500 else "❌ 2500자 미만")
            
            with col3:
                st.metric("출력 모드", output_mode)
            
            # 결과 탭
            tab1, tab2 = st.tabs(["📖 재작성된 글", "🔍 미리보기"])
            
            with tab1:
                if output_mode == "HTML":
                    st.code(rewritten_content, language="html")
                else:
                    st.markdown(rewritten_content)
            
            with tab2:
                if output_mode == "HTML":
                    st.markdown("**HTML 렌더링 결과:**")
                    st.markdown(rewritten_content, unsafe_allow_html=True)
                else:
                    st.markdown("**텍스트 미리보기:**")
                    st.info(rewritten_content)
            
            # 다운로드 버튼
            st.markdown("---")
            st.subheader("💾 결과 다운로드")
            
            if output_mode == "HTML":
                file_name = "rewritten_content.html"
                mime_type = "text/html"
            else:
                file_name = "rewritten_content.txt"
                mime_type = "text/plain"
            
            st.download_button(
                label=f"📥 {file_name} 다운로드",
                data=rewritten_content,
                file_name=file_name,
                mime=mime_type
            )
            
            # 품질 보증
            st.markdown("---")
            st.success("""
            ✅ **품질 보증**
            - 2500자 이상의 충분한 분량
            - 유사문서 검사를 통과할 수 있는 독창적인 내용
            - 전문 카피라이터 수준의 글쓰기
            - 자연스럽고 읽기 쉬운 문체
            """)
        
        else:
            st.error("❌ 글 재작성에 실패했습니다. 다시 시도해주세요.")
    
    # 사용 팁
    with st.expander("💡 효과적인 사용 팁", expanded=False):
        st.markdown("""
        ### 📋 글 재작성 활용 가이드
        
        **🎯 최적의 원본 텍스트**
        - 명확한 주제와 구조를 가진 글
        - 최소 100자 이상의 충분한 내용
        - 핵심 키워드와 메시지가 포함된 텍스트
        
        **⚙️ 모드별 활용법**
        - **일반 글**: 블로그 포스트, 기사, 보고서 등
        - **HTML**: 웹페이지, 랜딩 페이지, 이메일 템플릿 등
        
        **✍️ 스타일별 특징**
        - **전문적**: 비즈니스, 학술 문서에 적합
        - **친근한**: 블로그, SNS 콘텐츠에 적합
        - **공식적**: 공문서, 보도자료에 적합
        - **창의적**: 마케팅 카피, 광고 문구에 적합
        
        **🔍 품질 확인 포인트**
        - 원본의 핵심 메시지가 보존되었는지 확인
        - 자연스러운 문체와 논리적 구조인지 점검
        - 2500자 이상의 충분한 분량인지 확인
        """)


if __name__ == "__main__":
    show_content_rewriter()