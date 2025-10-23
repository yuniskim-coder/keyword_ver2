"""
본 프로그램 'RankChecker by L&C'는 chaechaeLab에 의해 개발된 소프트웨어입니다.
해당 소스코드 및 실행 파일의 무단 복제, 배포, 역컴파일, 수정은
저작권법 및 컴퓨터프로그램 보호법에 따라 엄격히 금지됩니다.

무단 유포 및 상업적 이용 시 민형사상 법적 책임을 물을 수 있습니다.
※ 본 프로그램은 사용자 추적 및 차단 기능이 포함되어 있습니다.

Copyright ⓒ 2025 chaechaeLab. All rights reserved.
Unauthorized reproduction or redistribution is strictly prohibited. 
"""

import streamlit as st
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta
import time
import pandas as pd
import hashlib
import base64
import hmac

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# 로그인 자격 증명
VALID_CREDENTIALS = {
    "master": "56tyghbn"
}

# 네이버 API 키 설정
client_id = "tp2ypJeFL98lJyTSWLy5"
client_secret = "QeYFNiR0k7"

# 네이버 광고센터 API 설정
NAVER_AD_API_URL = "https://api.naver.com"
CUSTOMER_ID = "3811341"
ACCESS_LICENSE = "01000000004d7e825880699447a01faa9d45783000d6eb445ac3b843474d7f01df7078c502"
SECRET_KEY = "AQAAAABNfoJYgGmUR6Afqp1FeDAApswumrPrvkZhst9UN6hVNg=="

# CSS 스타일 설정
st.markdown("""
<style>
.stButton > button {
    background-color: #03C75A !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background-color: #02B051 !important;
    box-shadow: 0 2px 8px rgba(3, 199, 90, 0.3) !important;
    transform: translateY(-1px) !important;
}

.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-welcome {
    background: linear-gradient(135deg, #03C75A, #02B051);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

def generate_signature(timestamp, method, uri, secret_key):
    """네이버 광고센터 API 서명 생성"""
    message = f"{timestamp}.{method}.{uri}"
    return base64.b64encode(
        hmac.new(
            base64.b64decode(secret_key),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

def get_naver_ad_related_keywords(keyword, max_results=20):
    """네이버 광고센터 API를 사용한 연관키워드 조회"""
    try:
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        uri = "/keywordstool"
        
        # API 서명 생성
        signature = generate_signature(timestamp, method, uri, SECRET_KEY)
        
        # 요청 URL 및 파라미터
        params = {
            'hintKeywords': keyword,
            'showDetail': '1'
        }
        
        query_string = urllib.parse.urlencode(params)
        full_uri = f"{uri}?{query_string}"
        url = f"{NAVER_AD_API_URL}{full_uri}"
        
        # 헤더 설정
        headers = {
            'X-Timestamp': timestamp,
            'X-API-KEY': ACCESS_LICENSE,
            'X-Customer': CUSTOMER_ID,
            'X-Signature': signature,
            'Content-Type': 'application/json'
        }
        
        # API 요청
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        # 결과 처리
        related_keywords = []
        if 'keywordList' in data:
            for item in data['keywordList'][:max_results]:
                keyword_info = {
                    'keyword': item.get('relKeyword', ''),
                    'monthlyPcQcCnt': item.get('monthlyPcQcCnt', 0),
                    'monthlyMobileQcCnt': item.get('monthlyMobileQcCnt', 0),
                    'monthlyAvePcClkCnt': item.get('monthlyAvePcClkCnt', 0),
                    'monthlyAveMobileClkCnt': item.get('monthlyAveMobileClkCnt', 0),
                    'plAvgDepth': item.get('plAvgDepth', 0),
                    'compIdx': item.get('compIdx', '')
                }
                related_keywords.append(keyword_info)
                
        return related_keywords
        
    except Exception as e:
        st.error(f"네이버 광고센터 API 오류: {str(e)}")
        return []

def format_ad_center_keywords(ad_keywords):
    """네이버 광고센터 API 결과를 사용자 친화적 형태로 변환"""
    formatted_keywords = []
    
    for item in ad_keywords:
        keyword = item.get('keyword', '')
        if not keyword:
            continue
            
        # 월간 검색량 (PC + Mobile)
        pc_search = int(item.get('monthlyPcQcCnt', 0))
        mobile_search = int(item.get('monthlyMobileQcCnt', 0))
        total_search = pc_search + mobile_search
        
        # 경쟁 강도
        comp_idx = item.get('compIdx', '낮음')
        if comp_idx == '높음':
            comp_icon = "🔴"
        elif comp_idx == '중간':
            comp_icon = "🟡"
        else:
            comp_icon = "🟢"
        
        # 검색량에 따른 추천도
        if total_search >= 10000:
            recommend_icon = "⭐⭐⭐"
            recommend_text = "강력추천"
        elif total_search >= 1000:
            recommend_icon = "⭐⭐"
            recommend_text = "추천"
        elif total_search >= 100:
            recommend_icon = "⭐"
            recommend_text = "고려"
        else:
            recommend_icon = "💡"
            recommend_text = "롱테일"
        
        formatted_keywords.append({
            'keyword': keyword,
            'monthly_search_volume': f"{total_search:,}",
            'pc_search': f"{pc_search:,}",
            'mobile_search': f"{mobile_search:,}",
            'competition': f"{comp_icon} {comp_idx}",
            'recommendation': f"{recommend_icon} {recommend_text}",
            'score': total_search
        })
    
    # 검색량 기준으로 정렬
    formatted_keywords.sort(key=lambda x: x['score'], reverse=True)
    return formatted_keywords

def get_related_keywords(keyword):
    """네이버 광고센터 API 기반 연관키워드 조회"""
    try:
        # 네이버 광고센터 API 시도
        ad_keywords = get_naver_ad_related_keywords(keyword)
        if ad_keywords:
            st.success("✅ 네이버 광고센터 API로 정확한 키워드 데이터를 조회했습니다!")
            return format_ad_center_keywords(ad_keywords)
        else:
            st.warning("⚠️ 광고센터 API에서 데이터를 찾을 수 없습니다.")
            return []
        
    except Exception as e:
        st.error(f"⚠️ API 오류: {str(e)}")
        return []

def login_page():
    """로그인 페이지"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown("# 🔐 chaechaeLab")
    st.markdown("### 마케팅 도구 로그인")
    
    with st.form("login_form"):
        username = st.text_input("사용자 ID", placeholder="아이디를 입력하세요")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        submit_button = st.form_submit_button("로그인", use_container_width=True)
        
        if submit_button:
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def authenticate_user(username, password):
    """사용자 인증"""
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password

def logout():
    """로그아웃"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

def show_user_info():
    """사용자 정보 표시 및 로그아웃 버튼"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<div class="login-welcome">👋 환영합니다, {st.session_state.username}님!</div>', 
                   unsafe_allow_html=True)
    
    with col2:
        if st.button("로그아웃", key="logout_btn"):
            logout()

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="chaechaeLab 마케팅 도구",
        page_icon="🔍",
        layout="wide"
    )
    
    # 로그인 확인
    if not st.session_state.logged_in:
        login_page()
        return
    
    # 로그인된 사용자 정보 표시
    show_user_info()
    
    # 타이틀
    st.title("🔍 chaechaeLab 마케팅 도구")
    st.write("네이버 광고센터 API 기반 정확한 연관키워드 분석 도구입니다.")
    
    # 키워드 입력
    keywords_text = st.text_input(
        "🔍 검색할 키워드를 입력하세요 (쉼표로 구분, 최대 10개)",
        placeholder="예: 키보드, 마우스, 헤드셋",
        help="키워드를 쉼표(,)로 구분하여 입력하면 각각의 연관키워드를 조회합니다."
    )
    
    # 연관키워드 조회 버튼
    if st.button("🔗 연관키워드 조회", type="primary"):
        keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
        
        if not keywords:
            st.error("❌ 검색어를 입력해주세요.")
        elif len(keywords) > 10:
            st.error("❌ 최대 10개까지만 입력 가능합니다.")
        else:
            st.header("🔗 연관키워드 조회 결과")
            
            for keyword in keywords:
                with st.expander(f"🔍 {keyword}의 연관키워드 분석", expanded=True):
                    with st.spinner(f"{keyword} 연관키워드 조회 중..."):
                        related_keywords = get_related_keywords(keyword)
                    
                    if related_keywords:
                        st.success(f"✅ {len(related_keywords)}개의 연관키워드를 찾았습니다.")
                        
                        # 탭으로 구분
                        tab1, tab2 = st.tabs(["📊 상세 분석", "📋 키워드 목록"])
                        
                        with tab1:
                            st.subheader("🎯 네이버 광고센터 키워드 분석")
                            
                            # 데이터프레임으로 표시
                            df_data = []
                            for idx, kw_data in enumerate(related_keywords, 1):
                                df_data.append({
                                    '순위': idx,
                                    '키워드': kw_data['keyword'],
                                    '월간검색량': kw_data['monthly_search_volume'],
                                    'PC검색량': kw_data['pc_search'],
                                    '모바일검색량': kw_data['mobile_search'],
                                    '경쟁강도': kw_data['competition'],
                                    '추천도': kw_data['recommendation']
                                })
                            
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                            
                            # 통계 요약
                            col1, col2, col3 = st.columns(3)
                            
                            total_keywords = len(related_keywords)
                            high_volume_keywords = len([k for k in related_keywords if k['score'] >= 10000])
                            recommended_keywords = len([k for k in related_keywords if '⭐⭐⭐' in k['recommendation']])
                            
                            with col1:
                                st.metric("전체 키워드", total_keywords)
                            with col2:
                                st.metric("고검색량 키워드", high_volume_keywords, 
                                         f"{(high_volume_keywords/total_keywords*100):.1f}%")
                            with col3:
                                st.metric("강력추천 키워드", recommended_keywords, 
                                         f"{(recommended_keywords/total_keywords*100):.1f}%")
                        
                        with tab2:
                            st.subheader("📝 키워드 목록")
                            
                            # 추천도별로 그룹화
                            strong_recommend = [k for k in related_keywords if '⭐⭐⭐' in k['recommendation']]
                            recommend = [k for k in related_keywords if '⭐⭐' in k['recommendation'] and '⭐⭐⭐' not in k['recommendation']]
                            consider = [k for k in related_keywords if '⭐' in k['recommendation'] and '⭐⭐' not in k['recommendation']]
                            longtail = [k for k in related_keywords if '💡' in k['recommendation']]
                            
                            if strong_recommend:
                                st.markdown("### ⭐⭐⭐ 강력추천 키워드")
                                cols = st.columns(3)
                                for i, kw in enumerate(strong_recommend):
                                    with cols[i % 3]:
                                        st.markdown(f"**{kw['keyword']}**  \n검색량: {kw['monthly_search_volume']}")
                            
                            if recommend:
                                st.markdown("### ⭐⭐ 추천 키워드")
                                cols = st.columns(4)
                                for i, kw in enumerate(recommend):
                                    with cols[i % 4]:
                                        st.write(f"• {kw['keyword']} ({kw['monthly_search_volume']})")
                            
                            if consider:
                                st.markdown("### ⭐ 고려 키워드")
                                cols = st.columns(4)
                                for i, kw in enumerate(consider):
                                    with cols[i % 4]:
                                        st.write(f"• {kw['keyword']} ({kw['monthly_search_volume']})")
                            
                            if longtail:
                                st.markdown("### 💡 롱테일 키워드")
                                cols = st.columns(5)
                                for i, kw in enumerate(longtail):
                                    with cols[i % 5]:
                                        st.write(f"• {kw['keyword']}")
                            
                            # 다운로드 기능
                            st.markdown("---")
                            st.subheader("💾 데이터 다운로드")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                csv = df.to_csv(index=False, encoding='utf-8-sig')
                                st.download_button(
                                    label="📊 CSV 파일 다운로드",
                                    data=csv,
                                    file_name=f"{keyword}_연관키워드_광고센터_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                    mime="text/csv"
                                )
                            
                            with col2:
                                keywords_text = "\n".join([kw['keyword'] for kw in related_keywords])
                                st.download_button(
                                    label="📝 키워드 목록 다운로드",
                                    data=keywords_text,
                                    file_name=f"{keyword}_키워드목록_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                                    mime="text/plain"
                                )
                    else:
                        st.warning("연관키워드를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()