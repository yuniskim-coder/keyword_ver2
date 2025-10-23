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