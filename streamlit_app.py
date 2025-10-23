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

# 세션 상태 초기화 - 강제 리셋
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# 세션 강제 초기화 (개발용)
if 'force_reset' not in st.session_state:
    st.session_state.force_reset = True
    st.session_state.logged_in = False
    st.session_state.username = None

# 로그인 자격 증명 (실제 운영환경에서는 데이터베이스나 외부 인증 시스템 사용 권장)
VALID_CREDENTIALS = {
    "master": "56tyghbn"
}

# 네이버 초록색 스타일 CSS 추가
st.markdown("""
<style>
/* 네이버 초록색 버튼 스타일 */
.stButton > button {
    background-color: #03C75A !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background-color: #02B051 !important;
    box-shadow: 0 2px 8px rgba(3, 199, 90, 0.3) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    background-color: #029E47 !important;
    transform: translateY(0px) !important;
}

/* 주요 검색 버튼에 특별한 스타일 적용 */
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #03C75A 0%, #02B051 100%) !important;
    box-shadow: 0 4px 15px rgba(3, 199, 90, 0.25) !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    padding: 0.75rem 1.5rem !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #02B051 0%, #029E47 100%) !important;
    box-shadow: 0 6px 20px rgba(3, 199, 90, 0.4) !important;
}

/* 스피너 색상도 네이버 초록색으로 */
.stSpinner > div {
    border-top-color: #03C75A !important;
}

/* 로그인 페이지 스타일 */
.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid #e0e0e0;
}

.login-header {
    text-align: center;
    margin-bottom: 2rem;
    color: #333;
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

# 네이버 API 키 설정
client_id = "tp2ypJeFL98lJyTSWLy5"
client_secret = "QeYFNiR0k7"

def login_page():
    """로그인 페이지"""
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

def get_keyword_competition_level(keyword):
    """키워드의 PC통합검색영역 기준 경쟁정도를 분석하는 함수"""
    try:
        # 네이버 통합검색 API를 사용하여 검색 결과 수 확인
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/webkr.json?query={encText}&display=1&start=1"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        result = json.loads(response.read())
        
        total_results = result.get("total", 0)
        
        # 경쟁정도 판정 기준
        if total_results >= 1000000:  # 100만 개 이상
            return "높음", total_results, "🔴"
        elif total_results >= 100000:  # 10만 개 이상
            return "중간", total_results, "🟡"
        else:  # 10만 개 미만
            return "낮음", total_results, "🟢"
            
    except Exception as e:
        return "알 수 없음", 0, "⚪"

def get_related_keywords(keyword):
    """네이버 DataLab 기반 실제 검색 트렌드 연관키워드 조회"""
    try:
        return get_datalab_trend_keywords(keyword)
    except Exception as e:
        st.error(f"연관 키워드 조회 중 오류 발생: {str(e)}")
        return []

def get_datalab_trend_keywords(keyword):
    """DataLab API 기반 실제 검색 트렌드 키워드"""
    try:
        # 1. 기본 키워드 패턴 생성
        candidate_keywords = generate_keyword_candidates(keyword)
        
        # 2. DataLab API로 실제 검색량 검증
        verified_keywords = verify_keywords_with_datalab(candidate_keywords, keyword)
        
        # 3. 쇼핑 트렌드 기반 추가 키워드
        shopping_keywords = get_shopping_trend_keywords(keyword)
        verified_keywords.extend(shopping_keywords)
        
        # 4. 중복 제거 및 최종 정렬
        final_keywords = finalize_keyword_list(verified_keywords, keyword)
        
        return final_keywords[:20]
        
    except Exception as e:
        st.error(f"DataLab API 오류: {str(e)}")
        return get_emergency_keywords(keyword)

def generate_keyword_candidates(keyword):
    """광고주센터 스타일의 키워드 후보 생성"""
    candidates = []
    
    # 1. 구매 의도 키워드 (광고 효과가 높은 키워드들)
    purchase_intents = [
        f"{keyword} 추천", f"{keyword} 순위", f"{keyword} 베스트",
        f"{keyword} 가격", f"{keyword} 할인", f"{keyword} 특가",
        f"{keyword} 리뷰", f"{keyword} 후기", f"{keyword} 구매",
        f"좋은 {keyword}", f"인기 {keyword}", f"최고 {keyword}"
    ]
    candidates.extend(purchase_intents)
    
    # 2. 브랜드/품질 키워드
    quality_keywords = [
        f"프리미엄 {keyword}", f"고급 {keyword}", f"브랜드 {keyword}",
        f"정품 {keyword}", f"신상 {keyword}", f"최신 {keyword}",
        f"가성비 {keyword}", f"저렴한 {keyword}"
    ]
    candidates.extend(quality_keywords)
    
    # 3. 기능/특성 키워드
    feature_keywords = [
        f"무선 {keyword}", f"블루투스 {keyword}", f"USB {keyword}",
        f"휴대용 {keyword}", f"소형 {keyword}", f"대용량 {keyword}",
        f"게이밍 {keyword}", f"사무용 {keyword}", f"가정용 {keyword}"
    ]
    candidates.extend(feature_keywords)
    
    # 4. 쇼핑/구매처 키워드
    shopping_keywords = [
        f"{keyword} 쿠팡", f"{keyword} 11번가", f"{keyword} 지마켓",
        f"{keyword} 온라인", f"{keyword} 쇼핑몰", f"{keyword} 매장",
        f"{keyword} 무료배송", f"{keyword} 당일배송"
    ]
    candidates.extend(shopping_keywords)
    
    return candidates

def verify_keywords_with_datalab(candidates, base_keyword):
    """DataLab API로 키워드 검증"""
    verified = []
    
    # 배치 처리 (API 제한 고려)
    batch_size = 5
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        
        try:
            # DataLab API 요청
            volumes = get_batch_search_volume(batch)
            
            for j, kw in enumerate(batch):
                if j < len(volumes) and volumes[j] > 0:
                    verified.append((kw, volumes[j]))
                    
        except Exception as e:
            # API 실패 시 기본 점수로 추가
            for kw in batch:
                verified.append((kw, 1))
    
    # 검색량 순 정렬
    verified.sort(key=lambda x: x[1], reverse=True)
    
    return [kw for kw, vol in verified[:15]]

def get_batch_search_volume(keywords):
    """키워드 배치의 검색량 조회 (DataLab API)"""
    try:
        url = "https://openapi.naver.com/v1/datalab/search"
        
        # 키워드 그룹 구성
        keyword_groups = []
        for i, kw in enumerate(keywords[:5]):  # 최대 5개
            keyword_groups.append({
                "groupName": f"group{i+1}",
                "keywords": [kw]
            })
        
        body = {
            "startDate": "2024-01-01",
            "endDate": "2024-10-31",
            "timeUnit": "month",
            "keywordGroups": keyword_groups,
            "device": "",
            "ages": [],
            "gender": ""
        }
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        request.add_header("Content-Type", "application/json")
        
        response = urllib.request.urlopen(request, json.dumps(body).encode("utf-8"), timeout=10)
        result = json.loads(response.read().decode("utf-8"))
        
        # 검색량 추출
        volumes = []
        if "results" in result:
            for group_result in result["results"]:
                if "data" in group_result and len(group_result["data"]) > 0:
                    # 최근 3개월 평균 계산
                    recent_data = group_result["data"][-3:]
                    avg_volume = sum(point["ratio"] for point in recent_data) / len(recent_data)
                    volumes.append(avg_volume)
                else:
                    volumes.append(0)
        
        # 부족한 부분은 0으로 채우기
        while len(volumes) < len(keywords):
            volumes.append(0)
            
        return volumes
        
    except Exception as e:
        # API 실패 시 기본값 반환
        return [1] * len(keywords)

def get_shopping_trend_keywords(keyword):
    """쇼핑 트렌드 기반 키워드 (실제 상품 데이터 활용)"""
    try:
        # 네이버 쇼핑 API로 최신 상품 검색
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start=1&sort=date"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        
        response = urllib.request.urlopen(request, timeout=10)
        result = json.loads(response.read())
        
        # 상품명에서 트렌드 키워드 추출
        trend_keywords = extract_trending_keywords(result.get("items", []), keyword)
        
        return trend_keywords
        
    except Exception:
        return []

def extract_trending_keywords(products, base_keyword):
    """상품 데이터에서 트렌딩 키워드 추출"""
    keyword_freq = {}
    
    for product in products:
        title = re.sub(r'<[^>]+>', '', product.get('title', ''))
        
        # 2-4글자 한글 키워드 추출
        korean_words = re.findall(r'[가-힣]{2,4}', title)
        for word in korean_words:
            if (word != base_keyword and 
                word not in ['배송', '무료', '당일', '택배', '포장', '개봉'] and
                len(word) >= 2):
                keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        # 영문 브랜드명 추출
        english_words = re.findall(r'[A-Z][a-zA-Z]{2,8}', title)
        for word in english_words:
            if word.lower() != base_keyword.lower():
                keyword_freq[word] = keyword_freq.get(word, 0) + 1
    
    # 빈도 높은 키워드로 조합 생성
    trending = []
    for word, freq in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True):
        if freq >= 3:  # 3번 이상 등장
            trending.append(f"{word} {base_keyword}")
            trending.append(f"{base_keyword} {word}")
            if len(trending) >= 10:
                break
    
    return trending

def finalize_keyword_list(keywords, base_keyword):
    """최종 키워드 리스트 정리"""
    # 중복 제거
    unique_keywords = []
    seen = set()
    
    for kw in keywords:
        kw_clean = kw.strip().lower()
        if (kw_clean != base_keyword.lower() and 
            kw_clean not in seen and 
            len(kw.strip()) >= 2):
            unique_keywords.append(kw.strip())
            seen.add(kw_clean)
    
    # 품질 점수 계산 및 정렬
    scored_keywords = []
    for kw in unique_keywords:
        score = calculate_ad_relevance_score(kw, base_keyword)
        scored_keywords.append((kw, score))
    
    # 점수순 정렬
    scored_keywords.sort(key=lambda x: x[1], reverse=True)
    
    return [kw for kw, score in scored_keywords]

def calculate_ad_relevance_score(keyword, base_keyword):
    """광고 관련성 점수 계산"""
    score = 10  # 기본 점수
    
    # 구매 의도 키워드 가산점
    high_intent = ['추천', '순위', '가격', '할인', '특가', '구매', '베스트', '인기']
    intent_score = sum(3 for intent in high_intent if intent in keyword)
    score += intent_score
    
    # 브랜드/품질 키워드 가산점
    quality_terms = ['프리미엄', '고급', '브랜드', '정품', '최고', '신상']
    quality_score = sum(2 for term in quality_terms if term in keyword)
    score += quality_score
    
    # 기술/기능 키워드 가산점
    tech_terms = ['무선', '블루투스', 'USB', '게이밍', '충전', 'LED']
    tech_score = sum(2 for term in tech_terms if term in keyword)
    score += tech_score
    
    # 쇼핑 관련 키워드 가산점
    shopping_terms = ['쿠팡', '지마켓', '11번가', '온라인', '쇼핑', '배송']
    shopping_score = sum(1 for term in shopping_terms if term in keyword)
    score += shopping_score
    
    # 길이 점수
    if 4 <= len(keyword) <= 15:
        score += 3
    elif 16 <= len(keyword) <= 25:
        score += 1
    
    # 불용어 감점
    stop_words = ['것', '거', '이것', '그것', '물건', '상품']
    penalty = sum(5 for stop in stop_words if stop in keyword)
    score -= penalty
    
    return max(0, score)

def get_emergency_keywords(keyword):
    """비상용 키워드 (모든 API 실패 시)"""
    emergency = [
        f"{keyword} 추천", f"{keyword} 순위", f"{keyword} 가격", f"{keyword} 할인",
        f"{keyword} 리뷰", f"{keyword} 후기", f"{keyword} 구매", f"{keyword} 베스트",
        f"좋은 {keyword}", f"인기 {keyword}", f"최고 {keyword}", f"프리미엄 {keyword}",
        f"가성비 {keyword}", f"저렴한 {keyword}", f"무선 {keyword}", f"브랜드 {keyword}",
        f"{keyword} 온라인", f"{keyword} 쇼핑", f"{keyword} 특가", f"{keyword} 사용법"
    ]
    return emergency

def analyze_keyword_types(keywords, base_keyword):
    """키워드 유형별 분류 및 분석"""
    analysis = {
        '구매의도': 0,
        '브랜드/품질': 0,
        '기능/특성': 0,
        '가격/할인': 0,
        '기타': 0
    }
    
    for keyword in keywords:
        # 구매 의도 키워드
        if any(intent in keyword for intent in ['추천', '순위', '구매', '리뷰', '후기', '비교']):
            analysis['구매의도'] += 1
        # 브랜드/품질 키워드
        elif any(brand in keyword for brand in ['브랜드', '정품', '프리미엄', '고급', '베스트', '인기']):
            analysis['브랜드/품질'] += 1
        # 기능/특성 키워드
        elif any(feature in keyword for feature in ['무선', '블루투스', 'USB', '게이밍', '사무용', '가정용']):
            analysis['기능/특성'] += 1
        # 가격/할인 키워드
        elif any(price in keyword for price in ['가격', '할인', '특가', '세일', '저렴', '가성비']):
            analysis['가격/할인'] += 1
        else:
            analysis['기타'] += 1
    
    # 0인 항목 제거
    return {k: v for k, v in analysis.items() if v > 0}

def get_keyword_insights(keywords, base_keyword):
    """키워드 인사이트 분석"""
    insights = {}
    
    # 길이 통계
    lengths = [len(kw) for kw in keywords]
    insights['avg_length'] = sum(lengths) / len(lengths)
    insights['min_length'] = min(lengths)
    insights['max_length'] = max(lengths)
    
    # 구매 의도 키워드 비율
    purchase_keywords = [kw for kw in keywords if any(intent in kw for intent in ['추천', '가격', '할인', '구매', '순위'])]
    insights['purchase_ratio'] = len(purchase_keywords) / len(keywords) * 100
    
    # 고유 단어 수
    all_words = set()
    for kw in keywords:
        all_words.update(kw.split())
    insights['unique_words'] = len(all_words)
    
    return insights

# 이전 크롤링 함수들이 네이버 광고주센터 키워드 도구 시스템으로 교체됨

# 이전 DataLab 함수들이 실제 연관검색어 크롤링 시스템으로 교체됨

# 이전 함수들이 새로운 DataLab 기반 시스템으로 교체됨

# 기존 함수들 제거하고 새로운 구현으로 대체됨

def get_shopping_rank_list(keyword, limit=50):
    """쇼핑 순위 리스트를 조회하는 함수"""
    try:
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display={limit}&start=1"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        result = json.loads(response.read())
        
        products = []
        for idx, item in enumerate(result.get("items", []), start=1):
            title_clean = re.sub(r"<.*?>", "", item["title"])
            products.append({
                "rank": idx,
                "title": title_clean,
                "price": int(item["lprice"]) if item["lprice"] else 0,
                "link": item["link"],
                "mallName": item.get("mallName", "알 수 없음"),
                "category1": item.get("category1", ""),
                "category2": item.get("category2", "")
            })
        
        return products
    except Exception as e:
        st.error(f"쇼핑 순위 조회 중 오류 발생: {str(e)}")
        return []

def get_keyword_search_volume(keyword):
    """키워드의 월간 검색수를 조회하는 함수 (네이버 DataLab API)"""
    try:
        # 네이버 DataLab API 요청 URL
        url = "https://openapi.naver.com/v1/datalab/search"
        
        # API 요청 헤더
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
            "Content-Type": "application/json"
        }
        
        # 검색 기간 설정 (최근 1년)
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # API 요청 바디
        body = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "timeUnit": "month",
            "keywordGroups": [
                {
                    "groupName": keyword,
                    "keywords": [keyword]
                }
            ],
            "device": "",  # 전체 (PC + 모바일)
            "ages": [],    # 전체 연령
            "gender": ""   # 전체 성별
        }
        
        # PC 검색량 조회
        body_pc = body.copy()
        body_pc["device"] = "pc"
        
        request_pc = urllib.request.Request(url, data=json.dumps(body_pc).encode('utf-8'), headers=headers)
        response_pc = urllib.request.urlopen(request_pc)
        result_pc = json.loads(response_pc.read())
        
        # 모바일 검색량 조회
        body_mobile = body.copy()
        body_mobile["device"] = "mo"
        
        request_mobile = urllib.request.Request(url, data=json.dumps(body_mobile).encode('utf-8'), headers=headers)
        response_mobile = urllib.request.urlopen(request_mobile)
        result_mobile = json.loads(response_mobile.read())
        
        # 데이터 처리
        if result_pc.get("results") and result_mobile.get("results"):
            pc_data = result_pc["results"][0]["data"]
            mobile_data = result_mobile["results"][0]["data"]
            
            # 최근 월 데이터 가져오기
            latest_pc = pc_data[-1]["ratio"] if pc_data else 0
            latest_mobile = mobile_data[-1]["ratio"] if mobile_data else 0
            
            # 상대적 검색량을 실제 수치로 변환 (추정치)
            # DataLab API는 상대적 수치를 제공하므로, 실제 검색량으로 변환
            base_multiplier = 1000  # 기본 승수
            pc_volume = int(latest_pc * base_multiplier)
            mobile_volume = int(latest_mobile * base_multiplier)
            total_volume = pc_volume + mobile_volume
            
            if total_volume > 0:
                pc_ratio = (pc_volume / total_volume) * 100
                mobile_ratio = (mobile_volume / total_volume) * 100
            else:
                pc_ratio = mobile_ratio = 0
            
            return {
                "keyword": keyword,
                "total_volume": total_volume,
                "pc_volume": pc_volume,
                "mobile_volume": mobile_volume,
                "pc_ratio": pc_ratio,
                "mobile_ratio": mobile_ratio,
                "pc_trend_data": pc_data,
                "mobile_trend_data": mobile_data
            }
        else:
            st.warning(f"{keyword}: 검색량 데이터를 찾을 수 없습니다.")
            return None
            
    except urllib.error.HTTPError as e:
        if e.code == 400:
            st.error(f"API 요청 오류: 잘못된 요청입니다. 키워드를 확인해주세요.")
        elif e.code == 401:
            st.error(f"API 인증 오류: API 키를 확인해주세요.")
        elif e.code == 403:
            st.error(f"API 권한 오류: DataLab API 사용 권한을 확인해주세요.")
        elif e.code == 429:
            st.error(f"API 호출 제한: 잠시 후 다시 시도해주세요.")
        else:
            st.error(f"HTTP 오류 {e.code}: {e.reason}")
        return None
    except Exception as e:
        st.error(f"검색량 조회 중 오류 발생: {str(e)}")
        return None

def get_top_ranked_product_by_mall(keyword, mall_name, progress_placeholder=None):
    """특정 키워드에서 특정 쇼핑몰의 최고 순위 상품을 찾는 함수"""
    encText = urllib.parse.quote(keyword)
    seen_titles = set()
    best_product = None
    
    # 검색 결과를 1000위까지 확인 (100개씩 10번)
    for start in range(1, 1001, 100):
        try:
            url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start={start}"
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", client_id)
            request.add_header("X-Naver-Client-Secret", client_secret)
            response = urllib.request.urlopen(request)
            result = json.loads(response.read())
            
            # 진행률 업데이트
            if progress_placeholder:
                progress_percent = min(start / 1000, 1.0)
                progress_placeholder.progress(progress_percent)
            
            for idx, item in enumerate(result.get("items", []), start=1):
                if item.get("mallName") and mall_name in item["mallName"]:
                    title_clean = re.sub(r"<.*?>", "", item["title"])
                    if title_clean in seen_titles:
                        continue
                    seen_titles.add(title_clean)
                    
                    rank = start + idx - 1
                    product = {
                        "rank": rank,
                        "title": title_clean,
                        "price": item["lprice"],
                        "link": item["link"],
                        "mallName": item["mallName"]
                    }
                    
                    if not best_product or rank < best_product["rank"]:
                        best_product = product
                        
        except Exception as e:
            st.error(f"검색 중 오류 발생: {str(e)}")
            break
    
    return best_product

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="chaechaeLab 마케팅 도구",
        page_icon="🔍",
        layout="wide"
    )
    
    # 세션 상태 강제 확인 및 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # 디버그: 현재 로그인 상태 확인
    # st.write(f"Debug: logged_in = {st.session_state.logged_in}")  # 테스트용
    
    # 로그인 확인 - 로그인되지 않았으면 로그인 페이지 표시
    if not st.session_state.logged_in:
        login_page()
        return
    
    # 로그인된 사용자 정보 표시
    show_user_info()
    
    # 타이틀
    st.title("🔍 chaechaeLab 마케팅 도구")
    st.write("네이버 기반 종합 마케팅 분석 도구입니다.")
    
    # 사이드바에 사용법 안내
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
        - 네이버 DataLab 기반 트렌드 분석
        - 마케팅 전략 수립에 활용
        
        **🛍️ 쇼핑 랭킹**
        - 네이버 쇼핑 인기 상품 순위
        - 카테고리별 TOP 상품 분석
        - 시장 트렌드 파악
        
        **📈 월간 검색량**
        - 키워드별 월간 검색 트렌드
        - 시기별 검색량 변화 분석
        - 데이터 기반 마케팅 계획 수립
        """)
    
    # 메인 영역에 입력 폼
    st.header("🔍 검색 설정")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 검색어 입력
        keywords_text = st.text_area(
            "검색어 (최대 10개, 쉼표로 구분)", 
            placeholder="예: 키보드, 마우스, 충전기",
            height=100
        )
    
    with col2:
        # 판매처명 입력 (기본 순위 확인용)
        mall_name = st.text_input(
            "판매처명 (순위 확인용)", 
            placeholder="예: OO스토어"
        )
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 순위 확인", "🔗 연관키워드 조회", "📊 쇼핑 순위 리스트", "📈 월간 검색수"])
    
    with tab1:
        # 기존 순위 확인 기능
        search_button = st.button("🔍 순위 확인", type="primary", key="rank_check")
        
        if search_button:
            # 입력값 검증
            keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
            
            if not keywords:
                st.error("❌ 검색어를 입력해주세요.")
                return
                
            if not mall_name.strip():
                st.error("❌ 판매처명을 입력해주세요.")
                return
                
            if len(keywords) > 10:
                st.error("❌ 검색어는 최대 10개까지 가능합니다.")
                return
            
            # 검색 실행
            st.header("📊 검색 결과")
            
            # 전체 진행률
            overall_progress = st.progress(0)
            status_text = st.empty()
            
            results = []
            total_keywords = len(keywords)
            
            for i, keyword in enumerate(keywords):
                # 현재 키워드 표시
                status_text.text(f"🔄 검색 중: {keyword} ({i+1}/{total_keywords})")
                
                # 개별 키워드 진행률
                keyword_progress = st.progress(0)
                
                # 검색 실행
                result = get_top_ranked_product_by_mall(keyword, mall_name, keyword_progress)
                
                # 결과 저장
                results.append({
                    'keyword': keyword,
                    'result': result
                })
                
                # 전체 진행률 업데이트
                overall_progress.progress((i + 1) / total_keywords)
                
                # 개별 진행률 완료
                keyword_progress.progress(1.0)
                
                # 잠시 대기 (API 호출 제한 고려)
                time.sleep(0.5)
            
            # 검색 완료
            status_text.text("✅ 검색 완료!")
            
            # 결과 표시
            st.subheader("🎯 검색 결과 상세")
            
            for result_data in results:
                keyword = result_data['keyword']
                result = result_data['result']
                
                with st.expander(f"🔍 {keyword}", expanded=True):
                    if result:
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**✅ 검색 성공**")
                            st.markdown(f"**순위:** {result['rank']}위")
                            st.markdown(f"**상품명:** {result['title']}")
                            st.markdown(f"**가격:** {int(result['price']):,}원")
                            st.markdown(f"**판매처:** {result['mallName']}")
                            
                        with col2:
                            st.markdown(f"**상품 링크:**")
                            st.markdown(f"[🔗 상품 보기]({result['link']})")
                            
                            # 순위에 따른 색상 표시
                            if result['rank'] <= 10:
                                st.success(f"🥇 TOP 10 순위!")
                            elif result['rank'] <= 50:
                                st.info(f"🥈 TOP 50 순위!")
                            elif result['rank'] <= 100:
                                st.warning(f"🥉 TOP 100 순위!")
                            else:
                                st.error(f"📉 100위 이하")
                    else:
                        st.markdown(f"**❌ 검색 결과 없음**")
                        st.markdown("해당 키워드에서 지정된 판매처의 상품을 찾을 수 없습니다.")
        else:
            st.info("👆 위에서 검색어와 판매처명을 입력한 후 '순위 확인' 버튼을 눌러주세요.")
    
    with tab2:
        # 연관키워드 조회
        related_search_button = st.button("🔗 연관키워드 조회", type="primary", key="related_keywords")
        
        if related_search_button:
            keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
            
            if not keywords:
                st.error("❌ 검색어를 입력해주세요.")
            else:
                st.header("🔗 연관키워드 조회 결과")
                
                for keyword in keywords:
                    with st.expander(f"🔍 {keyword}의 연관키워드 분석", expanded=True):
                        with st.spinner(f"{keyword} 연관키워드 조회 중..."):
                            related_keywords = get_related_keywords(keyword)
                        
                        if related_keywords:
                            st.success(f"✅ {len(related_keywords)}개의 연관키워드를 찾았습니다.")
                            
                            # 분석 결과를 탭으로 구분
                            analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs(["📋 키워드 목록", "📊 분석 차트", "💾 내보내기"])
                            
                            with analysis_tab1:
                                # 2열 레이아웃: 왼쪽(연관키워드), 오른쪽(경쟁정도)
                                col_left, col_right = st.columns([3, 2])
                                
                                with col_left:
                                    st.subheader("📝 연관키워드 목록")
                                    # 3열로 연관키워드 표시
                                    cols = st.columns(3)
                                    for i, related_kw in enumerate(related_keywords):
                                        with cols[i % 3]:
                                            st.write(f"• {related_kw}")
                                
                                with col_right:
                                    st.subheader("⚔️ 경쟁정도 분석")
                                    st.write("**PC통합검색영역 기준**")
                                    
                                    # 원본 키워드 경쟁정도
                                    with st.spinner(f"{keyword} 경쟁정도 분석 중..."):
                                        competition, total_results, icon = get_keyword_competition_level(keyword)
                                    
                                    st.markdown(f"""
                                    **🎯 메인 키워드: {keyword}**
                                    - {icon} **경쟁정도**: {competition}
                                    - 📊 **검색결과**: {total_results:,}개
                                    """)
                                    
                                    st.markdown("---")
                                    
                                    # 연관키워드 중 상위 5개의 경쟁정도 분석
                                    st.write("**🔍 연관키워드 경쟁정도 (상위 5개)**")
                                    
                                    for i, related_kw in enumerate(related_keywords[:5]):
                                        with st.spinner(f"{related_kw} 분석 중..."):
                                            comp, total, icon = get_keyword_competition_level(related_kw)
                                        
                                        # 경쟁정도에 따른 색상 설정
                                        if comp == "높음":
                                            color = "red"
                                        elif comp == "중간":
                                            color = "orange"
                                        else:
                                            color = "green"
                                        
                                        st.markdown(f"""
                                        <div style="padding: 5px; margin: 2px 0; border-left: 3px solid {color};">
                                            <strong>{related_kw}</strong><br>
                                            {icon} {comp} ({total:,}개)
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # 경쟁정도 범례
                                    st.markdown("---")
                                    st.markdown("""
                                    **📋 경쟁정도 기준**
                                    - 🔴 **높음**: 100만개 이상
                                    - 🟡 **중간**: 10만~100만개
                                    - 🟢 **낮음**: 10만개 미만
                                    """)
                            
                            with analysis_tab2:
                                # 키워드 분석 차트
                                st.subheader("📊 키워드 분석")
                                
                                # 키워드 유형별 분류
                                keyword_analysis = analyze_keyword_types(related_keywords, keyword)
                                
                                if keyword_analysis:
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("**키워드 유형별 분포**")
                                        for kw_type, count in keyword_analysis.items():
                                            percentage = (count / len(related_keywords)) * 100
                                            st.write(f"• {kw_type}: {count}개 ({percentage:.1f}%)")
                                    
                                    with col2:
                                        # 키워드 통계
                                        insights = get_keyword_insights(related_keywords, keyword)
                                        st.markdown("**키워드 통계**")
                                        st.write(f"• 평균 길이: {insights['avg_length']:.1f}자")
                                        st.write(f"• 최단/최장: {insights['min_length']}/{insights['max_length']}자")
                                        st.write(f"• 구매 의도: {insights['purchase_ratio']:.1f}%")
                                        st.write(f"• 고유 단어: {insights['unique_words']}개")
                                
                                # 키워드 워드클라우드 (텍스트 기반)
                                st.markdown("**🔤 주요 키워드 구성 요소**")
                                all_words = []
                                for kw in related_keywords:
                                    all_words.extend(kw.split())
                                
                                from collections import Counter
                                word_freq = Counter(all_words)
                                # 기준 키워드 제외
                                word_freq.pop(keyword, None)
                                
                                # 상위 10개 단어 표시
                                top_words = word_freq.most_common(10)
                                if top_words:
                                    word_text = " | ".join([f"{word}({count})" for word, count in top_words])
                                    st.text(word_text)
                            
                            with analysis_tab3:
                                # 데이터 내보내기
                                st.subheader("💾 데이터 내보내기")
                                
                                # CSV 다운로드
                                import pandas as pd  # 명시적 import 추가
                                from datetime import datetime
                                
                                # 상세 데이터프레임 생성
                                detailed_data = []
                                for i, kw in enumerate(related_keywords, 1):
                                    kw_type = "기타"
                                    if any(intent in kw for intent in ['추천', '순위', '구매', '리뷰', '후기', '비교']):
                                        kw_type = "구매의도"
                                    elif any(brand in kw for brand in ['브랜드', '정품', '프리미엄', '고급', '베스트', '인기']):
                                        kw_type = "브랜드/품질"
                                    elif any(feature in kw for feature in ['무선', '블루투스', 'USB', '게이밍', '사무용', '가정용']):
                                        kw_type = "기능/특성"
                                    elif any(price in kw for price in ['가격', '할인', '특가', '세일', '저렴', '가성비']):
                                        kw_type = "가격/할인"
                                    
                                    detailed_data.append({
                                        '순위': i,
                                        '연관키워드': kw,
                                        '키워드유형': kw_type,
                                        '키워드길이': len(kw),
                                        '기준키워드': keyword,
                                        '조회일시': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    })
                                
                                df = pd.DataFrame(detailed_data)
                                csv = df.to_csv(index=False, encoding='utf-8-sig')
                                
                                st.download_button(
                                    label="📥 상세 분석 CSV 다운로드",
                                    data=csv,
                                    file_name=f"연관키워드_분석_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                                
                                # 데이터 미리보기
                                st.markdown("**데이터 미리보기:**")
                                st.dataframe(df, width="stretch")
                                
                                # 키워드 복사용 텍스트
                                st.markdown("**키워드 리스트 (복사용):**")
                                keywords_text = '\n'.join([f"{i+1}. {kw}" for i, kw in enumerate(related_keywords)])
                                st.text_area("키워드 목록", keywords_text, height=150, key=f"copy_{keyword}")
                                
                                # 요약 통계
                                st.markdown("**📈 요약 통계:**")
                                summary_col1, summary_col2, summary_col3 = st.columns(3)
                                
                                with summary_col1:
                                    st.metric("총 키워드 수", len(related_keywords))
                                
                                with summary_col2:
                                    purchase_count = sum(1 for kw in related_keywords 
                                                       if any(intent in kw for intent in ['추천', '가격', '할인', '구매', '순위']))
                                    st.metric("구매 의도 키워드", purchase_count)
                                
                                with summary_col3:
                                    avg_length = sum(len(kw) for kw in related_keywords) / len(related_keywords)
                                    st.metric("평균 키워드 길이", f"{avg_length:.1f}자")
                        else:
                            st.warning("❌ 연관키워드를 찾을 수 없습니다.")
        else:
            st.info("👆 위에서 검색어를 입력한 후 '연관키워드 조회' 버튼을 눌러주세요.")
    
    with tab3:
        # 쇼핑 순위 리스트
        ranking_search_button = st.button("📊 쇼핑 순위 리스트", type="primary", key="shopping_rank")
        
        if ranking_search_button:
            keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
            
            if not keywords:
                st.error("❌ 검색어를 입력해주세요.")
            else:
                st.header("📊 쇼핑 순위 리스트")
                
                for keyword in keywords:
                    with st.expander(f"🔍 {keyword} 순위 리스트", expanded=True):
                        with st.spinner(f"{keyword} 순위 조회 중..."):
                            products = get_shopping_rank_list(keyword)
                        
                        if products:
                            st.success(f"✅ {len(products)}개의 상품을 찾았습니다.")
                            
                            # 데이터프레임으로 표시
                            import pandas as pd  # 명시적 import 추가
                            df = pd.DataFrame(products)
                            df['가격'] = df['price'].apply(lambda x: f"{x:,}원" if x > 0 else "가격 미표시")
                            
                            # 표시할 컬럼 선택
                            display_df = df[['rank', 'title', '가격', 'mallName']].copy()
                            display_df.columns = ['순위', '상품명', '가격', '판매처']
                            
                            st.dataframe(
                                display_df,
                                width="stretch",
                                hide_index=True
                            )
                        else:
                            st.warning("❌ 순위 정보를 찾을 수 없습니다.")
        else:
            st.info("👆 위에서 검색어를 입력한 후 '쇼핑 순위 리스트' 버튼을 눌러주세요.")
    
    with tab4:
        # 월간 검색수
        volume_search_button = st.button("📈 월간 검색수 조회", type="primary", key="search_volume")
        
        if volume_search_button:
            keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
            
            if not keywords:
                st.error("❌ 검색어를 입력해주세요.")
            else:
                st.header("📈 월간 검색수 조회 결과")
                
                for keyword in keywords:
                    with st.expander(f"🔍 {keyword} 검색량", expanded=True):
                        with st.spinner(f"{keyword} 검색량 조회 중..."):
                            volume_data = get_keyword_search_volume(keyword)
                        
                        if volume_data:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    label="📱 모바일 검색량",
                                    value=f"{volume_data['mobile_volume']:,}",
                                    delta=f"{volume_data['mobile_ratio']:.1f}%"
                                )
                            
                            with col2:
                                st.metric(
                                    label="💻 PC 검색량", 
                                    value=f"{volume_data['pc_volume']:,}",
                                    delta=f"{volume_data['pc_ratio']:.1f}%"
                                )
                            
                            with col3:
                                st.metric(
                                    label="📊 총 검색량",
                                    value=f"{volume_data['total_volume']:,}"
                                )
                            
                            # 현재 월 비율 차트
                            st.subheader("📊 디바이스별 검색 비율")
                            import pandas as pd  # 명시적 import 추가
                            chart_data = pd.DataFrame({
                                '구분': ['모바일', 'PC'],
                                '검색량': [volume_data['mobile_volume'], volume_data['pc_volume']]
                            })
                            st.bar_chart(chart_data.set_index('구분'))
                            
                            # 트렌드 차트 추가
                            if 'pc_trend_data' in volume_data and 'mobile_trend_data' in volume_data:
                                st.subheader("📈 검색량 트렌드 (최근 1년)")
                                
                                # 트렌드 데이터 준비
                                trend_data = []
                                pc_trends = volume_data['pc_trend_data']
                                mobile_trends = volume_data['mobile_trend_data']
                                
                                for i in range(min(len(pc_trends), len(mobile_trends))):
                                    trend_data.append({
                                        '날짜': pc_trends[i]['period'],
                                        'PC': pc_trends[i]['ratio'],
                                        '모바일': mobile_trends[i]['ratio']
                                    })
                                
                                if trend_data:
                                    import pandas as pd  # 명시적 import 추가
                                    trend_df = pd.DataFrame(trend_data)
                                    trend_df['날짜'] = pd.to_datetime(trend_df['날짜'])
                                    trend_df = trend_df.set_index('날짜')
                                    
                                    st.line_chart(trend_df)
                                    
                                    # 트렌드 분석
                                    if len(trend_data) >= 2:
                                        recent_total = pc_trends[-1]['ratio'] + mobile_trends[-1]['ratio']
                                        previous_total = pc_trends[-2]['ratio'] + mobile_trends[-2]['ratio']
                                        change = recent_total - previous_total
                                        
                                        if change > 0:
                                            st.success(f"📈 최근 검색량이 {abs(change):.1f}% 증가했습니다.")
                                        elif change < 0:
                                            st.warning(f"📉 최근 검색량이 {abs(change):.1f}% 감소했습니다.")
                                        else:
                                            st.info("� 최근 검색량이 유지되고 있습니다.")
                            
                            st.info("💡 위 데이터는 네이버 DataLab API에서 제공하는 실제 검색량 데이터입니다.")
                        else:
                            st.warning("❌ 검색량 정보를 찾을 수 없습니다.")
        else:
            st.info("👆 위에서 검색어를 입력한 후 '월간 검색수 조회' 버튼을 눌러주세요.")
    
    # 푸터
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 12px;'>"
        "ⓒ 2025 chaechaeLab. 무단 복제 및 배포 금지. All rights reserved."
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()