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
from pages.monthly_search import show_monthly_search
from utils.styles import apply_custom_css, show_footer


def show_sidebar():
    """사이드바 표시"""
    with st.sidebar:
        st.header("📖 사용법 안내")
        st.markdown("""
        ### 🔍 chaechaeLab 마케팅 도구
        
        **🎯 순위 확인기**
        - 네이버 쇼핑에서 특정 판매처의 상품 순위 확인
        - 최대 10개 키워드 동시 검색
        - 1000위까지 정확한 순위 분석
        
        **🔗 연관 키워드**
        - 입력한 키워드와 관련된 검색어 추천
        - 키워드 인사이트 분석
        - 마케팅 전략 수립에 활용
        
        **🛍️ 쇼핑 랭킹**
        - 네이버 쇼핑 인기 상품 순위 조회
        - 가격대별 분석 및 쇼핑몰 분포
        - 시장 트렌드 파악
        
        **📈 월간 검색량**
        - 키워드별 월간 검색 트렌드 분석
        - PC vs 모바일 검색량 비교
        - 데이터 기반 마케팅 계획 수립
        """)


def show_shopping_ranking():
    """쇼핑 랭킹 페이지"""
    from pages.shopping_ranking import show_shopping_ranking as show_shopping
    show_shopping()


def show_monthly_search():
    """월간 검색량 페이지"""
    from pages.monthly_search import show_monthly_search as show_monthly
    show_monthly()


def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(**PAGE_CONFIG)
    
    # 세션 상태 초기화
    init_session_state()
    
    # 커스텀 CSS 적용
    apply_custom_css()
    
    # 로그인 확인
    if not is_logged_in():
        show_login_page()
        return
    
    # 로그인된 사용자 정보 표시
    show_user_info()
    
    # API 상태 확인
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔌 API 연결 상태")
        
        from utils.naver_api import validate_api_keys
        if validate_api_keys():
            st.success("✅ 네이버 API 연결됨")
        else:
            st.error("❌ 네이버 API 연결 실패")
            st.info("관리자에게 문의하세요.")
    
    # 타이틀
    st.title("🔍 chaechaeLab 마케팅 도구")
    st.write("네이버 기반 종합 마케팅 분석 도구입니다.")
    
    # 사이드바
    show_sidebar()
    
    # 메인 영역 - 키워드 입력
    st.header("🔍 검색 설정")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keywords_text = st.text_input(
            "검색어 입력", 
            placeholder="검색어를 쉼표(,)로 구분하여 입력하세요 (최대 10개)",
            help="예: 키보드, 마우스, 헤드셋"
        )
    
    with col2:
        seller_name = st.text_input(
            "판매처명", 
            placeholder="판매처명을 입력하세요",
            help="순위 확인 시 필요"
        )
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 순위 확인", 
        "🔗 연관키워드 조회", 
        "📊 쇼핑 순위 리스트", 
        "📈 월간 검색수"
    ])
    
    with tab1:
        show_rank_checker()
    
    with tab2:
        show_related_keywords()
    
    with tab3:
        show_shopping_ranking()
    
    with tab4:
        show_monthly_search()
    
    # 푸터
    show_footer()


if __name__ == "__main__":
    main()