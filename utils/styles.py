"""
UI 스타일 관련 모듈
"""
import streamlit as st
from config import NAVER_GREEN, NAVER_GREEN_HOVER, NAVER_GREEN_ACTIVE


def apply_custom_css():
    """커스텀 CSS 스타일 적용"""
    st.markdown(f"""
    <style>
    /* 네이버 초록색 버튼 스타일 */
    .stButton > button {{
        background-color: {NAVER_GREEN} !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }}

    .stButton > button:hover {{
        background-color: {NAVER_GREEN_HOVER} !important;
        box-shadow: 0 2px 8px rgba(3, 199, 90, 0.3) !important;
        transform: translateY(-1px) !important;
    }}

    .stButton > button:active {{
        background-color: {NAVER_GREEN_ACTIVE} !important;
        transform: translateY(0px) !important;
    }}

    /* 주요 검색 버튼에 특별한 스타일 적용 */
    div[data-testid="stButton"] button[kind="primary"] {{
        background: linear-gradient(135deg, {NAVER_GREEN} 0%, {NAVER_GREEN_HOVER} 100%) !important;
        box-shadow: 0 4px 15px rgba(3, 199, 90, 0.25) !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem !important;
    }}

    div[data-testid="stButton"] button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {NAVER_GREEN_HOVER} 0%, {NAVER_GREEN_ACTIVE} 100%) !important;
        box-shadow: 0 6px 20px rgba(3, 199, 90, 0.4) !important;
    }}

    /* 스피너 색상도 네이버 초록색으로 */
    .stSpinner > div {{
        border-top-color: {NAVER_GREEN} !important;
    }}

    /* 로그인 페이지 스타일 */
    .login-container {{
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
    }}

    .login-header {{
        text-align: center;
        margin-bottom: 2rem;
        color: #333;
    }}

    .login-welcome {{
        background: linear-gradient(135deg, {NAVER_GREEN}, {NAVER_GREEN_HOVER});
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }}

    /* 사이드바 레이아웃 순서 변경 - 더 구체적인 선택자 */
    section[data-testid="stSidebar"] .st-emotion-cache-8atqhb.e4man115 {{
        display: flex !important;
        flex-direction: column-reverse !important;
    }}

    /* 전체 사이드바 컨테이너 flex 설정 */
    section[data-testid="stSidebar"] > div {{
        display: flex !important;
        flex-direction: column !important;
    }}

    /* 사이드바 내 모든 직접 자식 요소들 순서 재배치 */
    section[data-testid="stSidebar"] > div > div {{
        display: flex !important;
        flex-direction: column !important;
    }}

    /* stSidebarNav 요소를 하단으로 */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
        order: 999 !important;
        margin-top: auto !important;
    }}

    /* 메뉴 버튼들이 포함된 메인 콘텐츠를 상단으로 */
    section[data-testid="stSidebar"] .st-emotion-cache-8atqhb {{
        order: 1 !important;
        flex: 1 !important;
    }}

    /* 특정 클래스를 가진 요소의 순서 강제 변경 */
    .st-emotion-cache-8atqhb.e4man115 {{
        order: 1 !important;
    }}

    [data-testid="stSidebarNav"] {{
        order: 2 !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def show_footer():
    """푸터 표시"""
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 12px;'>"
        "ⓒ 2025 chaechaeLab. 무단 복제 및 배포 금지. All rights reserved."
        "</div>", 
        unsafe_allow_html=True
    )