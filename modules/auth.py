"""
인증 관련 모듈
"""
import streamlit as st
from config import VALID_CREDENTIALS


def init_session_state():
    """세션 상태 초기화"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # 세션 강제 초기화 (개발용)
    if 'force_reset' not in st.session_state:
        st.session_state.force_reset = True
        st.session_state.logged_in = False
        st.session_state.username = None


def authenticate_user(username, password):
    """사용자 인증"""
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password


def login():
    """로그인 처리"""
    st.session_state.logged_in = True


def logout():
    """로그아웃 처리"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()


def is_logged_in():
    """로그인 상태 확인"""
    return st.session_state.get('logged_in', False)


def get_current_user():
    """현재 사용자 정보 반환"""
    return st.session_state.get('username', None)