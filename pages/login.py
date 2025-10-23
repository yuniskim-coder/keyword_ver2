"""
로그인 페이지
"""
import streamlit as st
from modules.auth import authenticate_user


def show_login_page():
    """로그인 페이지 표시"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.markdown("# 🔐 chaechaeLab")
    st.markdown("### 마케팅 도구 로그인")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 로그인 폼
    with st.form("login_form"):
        username = st.text_input("사용자 ID", placeholder="아이디를 입력하세요")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        submit_button = st.form_submit_button("로그인", width="stretch")
        
        if submit_button:
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 도움말 정보
    st.markdown("---")
    st.markdown("**📱 chaechaeLab 마케팅 도구**")
    st.markdown("- 네이버 쇼핑 순위 체크")
    st.markdown("- 연관 키워드 분석")
    st.markdown("- 쇼핑 랭킹 조회")
    st.markdown("- 월간 검색량 분석")


def show_user_info():
    """로그인된 사용자 정보 표시"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<div class="login-welcome">👋 환영합니다, {st.session_state.username}님!</div>', 
                   unsafe_allow_html=True)
    
    with col2:
        if st.button("로그아웃", key="logout_btn"):
            from modules.auth import logout
            logout()