"""
chaechaeLab 마케팅 도구 메인 애플리케이션

본 프로그램은 chaechaeLab에 의해 개발된 소프트웨어입니다.
무단 복제, 배포, 역컴파일, 수정은 저작권법에 따라 엄격히 금지됩니다.

Copyright ⓒ 2025 chaechaeLab. All rights reserved.
"""

import streamlit as st
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import PAGE_CONFIG
from modules.auth import init_session_state, is_logged_in
from pages.login import show_login_page, show_user_info
from pages.rank_checker import show_rank_checker
from pages.related_keywords import show_related_keywords
from pages.shopping_ranking import show_shopping_ranking
from pages.keyword_analysis import show_keyword_analysis
from pages.content_rewriter import show_content_rewriter
from utils.styles import apply_custom_css, show_footer


def show_main_header():
    """메인 프로그램 헤더 표시"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; font-weight: 700; color: #333; margin-bottom: 0.5rem;">
            🛍️ 네이버 쇼핑 순위 확인 도구
        </h1>
        <p style="font-size: 1.1rem; color: #666; margin: 0; font-weight: 400;">
            by chaechaeLab
        </p>
    </div>
    """, unsafe_allow_html=True)


def show_sidebar():
    """사이드바 메뉴 표시"""
    with st.sidebar:
        st.title("🔍 chaechaeLab")
        
        # 로그인된 사용자 정보 표시 (사이드바 상단)
        st.markdown(f'<div class="login-welcome">👋 환영합니다, {st.session_state.username}님!</div>', 
                   unsafe_allow_html=True)
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", width="stretch", key="sidebar_logout"):
            from modules.auth import logout
            logout()
        
        st.markdown("---")
        
        # 페이지 버튼들 (각각 독립적)
        st.subheader("📋 메뉴")
        
        if st.button("🎯 순위 확인", width="stretch"):
            st.session_state.current_page = 'rank_checker'
        
        if st.button("🔗 연관키워드 조회", width="stretch"):
            st.session_state.current_page = 'related_keywords'
            
        if st.button("📊 쇼핑 순위 리스트", width="stretch"):
            st.session_state.current_page = 'shopping_ranking'
            
        if st.button("🎯 키워드 분석", width="stretch"):
            st.session_state.current_page = 'keyword_analysis'
            
        if st.button("🤖 AI 카피라이터", width="stretch"):
            st.session_state.current_page = 'content_rewriter'
        
        st.markdown("---")
        
        # 현재 선택된 페이지 표시
        current_page_names = {
            'rank_checker': '🎯 순위 확인',
            'related_keywords': '🔗 연관키워드 조회',
            'shopping_ranking': '📊 쇼핑 순위 리스트',
            'keyword_analysis': '🎯 키워드 분석',
            'content_rewriter': '🤖 AI 카피라이터'
        }
        
        current_page = st.session_state.get('current_page', 'rank_checker')
        st.info(f"**현재 페이지**: {current_page_names.get(current_page, '알 수 없음')}")
        
        st.markdown("---")
        
        # API 상태 확인
        st.subheader("🔌 API 연결 상태")
        from utils.naver_api import validate_api_keys
        if validate_api_keys():
            st.success("✅ 네이버 API 연결됨")
        else:
            st.error("❌ 네이버 API 연결 실패")
            st.info("관리자에게 문의하세요.")


def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(**PAGE_CONFIG)
    
    # 세션 상태 초기화
    init_session_state()
    
    # 현재 페이지 세션 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'rank_checker'
    
    # 커스텀 CSS 적용
    apply_custom_css()
    
    # 로그인 확인
    if not is_logged_in():
        show_login_page()
        return
    
    # 사이드바 메뉴 표시
    show_sidebar()
    
    # 메인 프로그램 헤더 표시
    show_main_header()
    
    # 선택된 페이지에 따라 컨텐츠 표시
    if st.session_state.current_page == 'rank_checker':
        st.title("🎯 순위 확인")
        st.markdown("네이버 쇼핑에서 특정 판매처의 상품 순위를 확인합니다.")
        show_rank_checker()
        
    elif st.session_state.current_page == 'related_keywords':
        st.title("🔗 연관키워드 조회")
        st.markdown("파워링크 캠페인 기반으로 연관키워드를 분석합니다.")
        show_related_keywords()
        
    elif st.session_state.current_page == 'shopping_ranking':
        st.title("📊 쇼핑 순위 리스트")
        st.markdown("네이버 쇼핑의 인기 상품 순위를 조회합니다.")
        show_shopping_ranking()
        
    elif st.session_state.current_page == 'keyword_analysis':
        st.title("🎯 키워드 분석")
        st.markdown("네이버 키워드 도구를 통해 상세한 키워드 분석을 제공합니다.")
        show_keyword_analysis()
        
    elif st.session_state.current_page == 'content_rewriter':
        st.title("🤖 AI 카피라이터")
        st.markdown("구글 제미나이 AI를 활용하여 전문적인 글 재작성을 제공합니다.")
        show_content_rewriter()
    
    # 푸터
    show_footer()


if __name__ == "__main__":
    main()