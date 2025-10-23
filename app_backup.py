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
from pages.related_keywords import show_related_keywords
from pages.shopping_ranking import show_shopping_ranking
from pages.keyword_analysis import show_keyword_analysis
from utils.styles import apply_custom_css, show_footer


def show_sidebar():
    """사이드바 메뉴 표시"""
    with st.sidebar:
        st.title("🔍 chaechaeLab")
        st.markdown("---")
        
        # 메뉴 선택
        menu_options = {
            "🔗 연관키워드 조회": "related_keywords", 
            "📊 쇼핑 순위 리스트": "shopping_ranking",
            "🎯 키워드 분석": "keyword_analysis"
        }
        
        selected_menu = st.selectbox(
            "메뉴 선택",
            options=list(menu_options.keys()),
            index=0,
            key="menu_selection"
        )
        
        st.session_state.current_page = menu_options[selected_menu]
        
        st.markdown("---")
        
        # 선택된 메뉴에 따른 기능 설명
        if st.session_state.current_page == "related_keywords":
            st.subheader("�🔗 연관키워드 조회")
            st.markdown("""
            **📋 주요 기능**
            - 파워링크 캠페인 기반 연관키워드 추출
            - 월간 검색량, 경쟁정도, 평균 입찰가 분석
            - 관련성 점수를 통한 키워드 우선순위 제공
            - 마케팅 전략 수립에 활용
            
            **� 사용법**
            1. 기준 키워드 입력
            2. 연관키워드 조회 버튼 클릭
            3. 결과를 통해 광고 전략 수립
            """)
            
        elif st.session_state.current_page == "shopping_ranking":
            st.subheader("📊 쇼핑 순위 리스트")
            st.markdown("""
            **📋 주요 기능**
            - 네이버 쇼핑 인기 상품 순위 조회
            - 가격대별 분석 및 쇼핑몰 분포
            - 상품별 상세 정보 제공
            - 시장 트렌드 파악 가능
            
            **💡 사용법**
            1. 조회할 키워드 입력
            2. 쇼핑 순위 조회 버튼 클릭
            3. 상위 랭킹 상품 분석
            """)
            
        elif st.session_state.current_page == "keyword_analysis":
            st.subheader("🎯 키워드 분석")
            st.markdown("""
            **📋 주요 기능**
            - 네이버 키워드 도구 API 활용
            - 상세 검색량, 클릭률, 경쟁정도 분석
            - PC/모바일별 광고 노출 데이터
            - 키워드별 성과 예측 정보
            
            **💡 사용법**
            1. 분석할 키워드 입력
            2. 키워드 분석 버튼 클릭
            3. 상세 분석 결과 검토
            """)
        
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
        st.session_state.current_page = 'related_keywords'
    
    # 커스텀 CSS 적용
    apply_custom_css()
    
    # 로그인 확인
    if not is_logged_in():
        show_login_page()
        return
    
    # 사이드바 메뉴 표시
    show_sidebar()
    
    # 로그인된 사용자 정보 표시 (상단)
    show_user_info()
    
    # 선택된 페이지에 따라 컨텐츠 표시
    if st.session_state.current_page == 'related_keywords':
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
    
    # 푸터
    show_footer()


if __name__ == "__main__":
    main()