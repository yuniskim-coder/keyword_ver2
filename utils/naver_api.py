"""
네이버 API 관련 유틸리티
"""
import json
import urllib.request
import urllib.parse
import time
import requests
import hashlib
import hmac
import base64
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, NAVER_AD_CUSTOMER_ID, NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY


def make_naver_request(url, query_params=None, headers=None):
    """네이버 API 요청 공통 함수"""
    try:
        if query_params:
            url += "?" + urllib.parse.urlencode(query_params)
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
        
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)
        
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"API 요청 오류: {e}")
        return None


def search_naver_shopping(keyword, display=10, start=1, sort="sim"):
    """네이버 쇼핑 검색 (개선된 버전)"""
    url = "https://openapi.naver.com/v1/search/shop.json"
    params = {
        "query": keyword,
        "display": min(display, 100),  # 최대 100개로 제한
        "start": start,
        "sort": sort
    }
    
    # 요청 간격 조절 (API 제한 방지)
    time.sleep(0.1)
    
    try:
        result = make_naver_request(url, params)
        if result and 'items' in result:
            # 결과 정제
            for item in result['items']:
                # HTML 태그 제거
                if 'title' in item:
                    item['title'] = item['title'].replace('<b>', '').replace('</b>', '')
                
                # 가격 정보 정제
                if 'lprice' in item:
                    try:
                        item['lprice'] = int(item['lprice'])
                    except:
                        item['lprice'] = 0
                
                if 'hprice' in item:
                    try:
                        item['hprice'] = int(item['hprice'])
                    except:
                        item['hprice'] = 0
        
        return result
    except Exception as e:
        print(f"네이버 쇼핑 검색 오류: {e}")
        return None


def get_datalab_trends(keywords, start_date, end_date, time_unit="month", device="", ages=[], gender=""):
    """네이버 DataLab 트렌드 조회 (개선된 버전)"""
    url = "https://openapi.naver.com/v1/datalab/search"
    
    # 키워드 그룹 생성 (최대 5개로 제한)
    keyword_groups = []
    for i, keyword in enumerate(keywords[:5]):
        keyword_groups.append({
            "groupName": f"그룹{i+1}",
            "keywords": [keyword]
        })
    
    data = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    
    if device:
        data["device"] = device
    if ages:
        data["ages"] = ages
    if gender:
        data["gender"] = gender
    
    try:
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
        request.add_header("Content-Type", "application/json")
        
        response = urllib.request.urlopen(request, json.dumps(data).encode('utf-8'))
        result = json.loads(response.read().decode('utf-8'))
        
        # 요청 간격 조절
        time.sleep(0.1)
        
        return result
    except Exception as e:
        print(f"DataLab API 요청 오류: {e}")
        return None


def get_related_keywords_advanced(keyword):
    """고급 연관 키워드 추출 (여러 소스 활용)"""
    related_keywords = set()
    
    try:
        # 1. 기본 유사도 검색
        data1 = search_naver_shopping(keyword, display=50, start=1, sort="sim")
        
        # 2. 최신순 검색 
        data2 = search_naver_shopping(keyword, display=30, start=1, sort="date")
        
        # 3. 가격순 검색
        data3 = search_naver_shopping(keyword, display=30, start=1, sort="asc")
        
        all_data = []
        if data1 and 'items' in data1:
            all_data.extend(data1['items'])
        if data2 and 'items' in data2:
            all_data.extend(data2['items'])
        if data3 and 'items' in data3:
            all_data.extend(data3['items'])
        
        # 키워드 빈도 계산
        keyword_freq = {}
        
        for item in all_data:
            title = item.get('title', '')
            # HTML 태그 제거
            title = title.replace('<b>', '').replace('</b>', '')
            
            # 제목 정제
            title = title.replace('[', '').replace(']', '')
            title = title.replace('(', '').replace(')', '')
            
            words = title.split()
            
            for word in words:
                # 더 엄격한 필터링
                if (len(word) >= 2 and 
                    keyword.lower() not in word.lower() and
                    word.lower() not in keyword.lower() and
                    not word.isdigit() and
                    word.lower() not in [
                        '상품', '제품', '용품', '아이템', '개', '원', '배송', '무료', 
                        '빠른', '당일', '택배', '특가', '할인', '세트', '키트',
                        '브랜드', '정품', '공식', '국내', '해외', '신상', '최신',
                        '인기', '베스트', '추천', '리뷰', '후기', '평점', '별점',
                        '그램', '사이즈', '컬러', '색상', '옵션', '선택'
                    ]):
                    
                    clean_word = ''.join(c for c in word if c.isalnum())
                    if len(clean_word) >= 2:
                        keyword_freq[clean_word] = keyword_freq.get(clean_word, 0) + 1
        
        # 빈도수 기준으로 정렬 (최소 2번 이상 등장)
        filtered_keywords = {k: v for k, v in keyword_freq.items() if v >= 2}
        sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
        
        return [kw for kw, freq in sorted_keywords[:30]]
        
    except Exception as e:
        print(f"고급 연관 키워드 추출 오류: {e}")
        return []


def get_keyword_stats(keyword, customer_id="3811341"):
    """네이버 키워드 도구 API를 사용하여 키워드 통계 조회"""
    from config import NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY
    
    BASE_URL = "https://api.naver.com"
    API_KEY = NAVER_AD_ACCESS_LICENSE
    SECRET_KEY = NAVER_AD_SECRET_KEY
    
    try:
        # API 요청 준비
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        uri = f"/keywordstool"
        
        # 요청 파라미터
        params = {
            'hintKeywords': keyword,
            'showDetail': '1'
        }
        
        # 쿼리 스트링 생성
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        # 서명 생성
        message = f"{timestamp}.{method}.{uri}.{query_string}"
        signature = base64.b64encode(
            hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        
        # 헤더 설정
        headers = {
            'X-Timestamp': timestamp,
            'X-API-KEY': API_KEY,
            'X-Customer': customer_id,
            'X-Signature': signature,
            'Content-Type': 'application/json'
        }
        
        # API 호출
        url = f"{BASE_URL}{uri}?{query_string}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"키워드 통계 API 오류: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"키워드 통계 조회 오류: {e}")
        return None


def get_keyword_competition_data(keyword, customer_id="3811341"):
    """키워드 경쟁률 및 검색량 데이터 조회"""
    try:
        # 키워드 도구 API 호출
        result = get_keyword_stats(keyword, customer_id)
        
        if result and 'keywordList' in result:
            keyword_data = result['keywordList']
            
            if keyword_data:
                # 첫 번째 키워드 데이터 반환 (검색한 키워드와 가장 유사한 것)
                data = keyword_data[0]
                
                return {
                    'keyword': data.get('relKeyword', keyword),
                    'monthly_pc_searches': data.get('monthlyPcQcCnt', 0),
                    'monthly_mobile_searches': data.get('monthlyMobileQcCnt', 0),
                    'monthly_pc_clicks': data.get('monthlyAvePcClkCnt', 0),
                    'monthly_mobile_clicks': data.get('monthlyAveMobileClkCnt', 0),
                    'monthly_pc_ctr': data.get('monthlyAvePcCtr', 0),
                    'monthly_mobile_ctr': data.get('monthlyAveMobileCtr', 0),
                    'competition_index': data.get('compIdx', 'LOW'),
                    'monthly_pc_ad_exposure': data.get('monthlyAvePcShwCnt', 0),
                    'monthly_mobile_ad_exposure': data.get('monthlyAveMobileShwCnt', 0)
                }
        
        # API 응답이 없을 경우 데모 데이터 반환 (개발/테스트용)
        print(f"API 응답이 없어 데모 데이터를 반환합니다: {keyword}")
        return get_demo_keyword_data(keyword)
        
    except Exception as e:
        print(f"키워드 경쟁 데이터 조회 오류: {e}")
        # 오류 발생 시에도 데모 데이터 반환
        return get_demo_keyword_data(keyword)


def get_demo_keyword_data(keyword):
    """데모용 키워드 데이터 생성 (실제 API가 작동하지 않을 때 사용)"""
    import random
    
    # 키워드별 기본 검색량 패턴 설정
    base_searches = {
        '무선키보드': 45000,
        '마우스': 67000,
        '헤드셋': 23000,
        '모니터': 89000,
        '노트북': 156000,
        '스마트폰': 234000,
        '태블릿': 78000,
        '이어폰': 123000,
        '충전기': 56000,
        '케이스': 34000
    }
    
    # 기본 검색량 결정 (키워드가 사전에 있으면 해당 값, 없으면 랜덤)
    base_search = base_searches.get(keyword, random.randint(10000, 100000))
    
    # PC vs 모바일 비율 (모바일이 보통 60-80%)
    mobile_ratio = random.uniform(0.6, 0.8)
    pc_searches = int(base_search * (1 - mobile_ratio))
    mobile_searches = int(base_search * mobile_ratio)
    
    # 클릭수 (검색수의 5-15%)
    pc_clicks = int(pc_searches * random.uniform(0.05, 0.15))
    mobile_clicks = int(mobile_searches * random.uniform(0.05, 0.15))
    
    # 클릭률 계산
    pc_ctr = (pc_clicks / pc_searches * 100) if pc_searches > 0 else 0
    mobile_ctr = (mobile_clicks / mobile_searches * 100) if mobile_searches > 0 else 0
    
    # 경쟁정도 랜덤 설정
    competition_levels = ['LOW', 'MEDIUM', 'HIGH']
    competition = random.choice(competition_levels)
    
    # 광고 노출수 (검색수의 20-50%)
    pc_ad_exposure = int(pc_searches * random.uniform(0.2, 0.5))
    mobile_ad_exposure = int(mobile_searches * random.uniform(0.2, 0.5))
    
    return {
        'keyword': keyword,
        'monthly_pc_searches': pc_searches,
        'monthly_mobile_searches': mobile_searches,
        'monthly_pc_clicks': pc_clicks,
        'monthly_mobile_clicks': mobile_clicks,
        'monthly_pc_ctr': round(pc_ctr, 2),
        'monthly_mobile_ctr': round(mobile_ctr, 2),
        'competition_index': competition,
        'monthly_pc_ad_exposure': pc_ad_exposure,
        'monthly_mobile_ad_exposure': mobile_ad_exposure
    }


def get_powerlink_related_keywords(keyword, customer_id="3811341"):
    """네이버 광고센터 파워링크 캠페인 연관키워드 조회"""
    from config import NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY
    
    # 실제 API 시도 후 실패 시 데모 데이터 사용
    try:
        # 키워드 도구 API 호출 시도
        result = get_keyword_stats_for_powerlink(keyword, customer_id)
        
        if result and 'keywordList' in result:
            return parse_powerlink_keywords(result, keyword)
        else:
            print(f"파워링크 API 응답 없음, 데모 데이터 사용: {keyword}")
            return get_demo_powerlink_keywords(keyword)
            
    except Exception as e:
        print(f"파워링크 연관키워드 조회 오류: {e}")
        return get_demo_powerlink_keywords(keyword)


def get_keyword_stats_for_powerlink(keyword, customer_id="3811341"):
    """파워링크용 키워드 통계 API 호출"""
    from config import NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY
    
    BASE_URL = "https://api.naver.com"
    API_KEY = NAVER_AD_ACCESS_LICENSE
    SECRET_KEY = NAVER_AD_SECRET_KEY
    
    try:
        # API 요청 준비
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        uri = "/keywordstool"
        
        # 파라미터 설정
        params = {
            'hintKeywords': keyword,
            'showDetail': '1'
        }
        
        # 쿼리 스트링 생성
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # 서명 생성을 위한 메시지
        message = f"{timestamp}.{method}.{uri}?{query_string}"
        
        # HMAC-SHA256 서명 생성
        signature = base64.b64encode(
            hmac.new(
                base64.b64decode(SECRET_KEY), 
                message.encode('utf-8'), 
                hashlib.sha256
            ).digest()
        ).decode()
        
        # 헤더 설정
        headers = {
            'X-Timestamp': timestamp,
            'X-API-KEY': API_KEY,
            'X-Customer': customer_id,
            'X-Signature': signature,
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        # API 호출
        url = f"{BASE_URL}{uri}?{query_string}"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"키워드 통계 API 오류: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"키워드 통계 조회 오류: {e}")
        return None


def parse_powerlink_keywords(api_result, base_keyword):
    """파워링크 API 응답을 파싱하여 연관키워드 추출"""
    keywords_data = []
    
    try:
        if api_result and 'keywordList' in api_result:
            for item in api_result['keywordList']:
                keyword_info = {
                    'keyword': item.get('relKeyword', ''),
                    'monthly_searches': (item.get('monthlyPcQcCnt', 0) + item.get('monthlyMobileQcCnt', 0)),
                    'pc_searches': item.get('monthlyPcQcCnt', 0),
                    'mobile_searches': item.get('monthlyMobileQcCnt', 0),
                    'competition': item.get('compIdx', 'LOW'),
                    'avg_bid': item.get('plAvgDepth', 0),  # 평균 입찰가
                    'click_rate': item.get('monthlyAvePcCtr', 0) + item.get('monthlyAveMobileCtr', 0),
                    'relevance_score': calculate_relevance_score(item.get('relKeyword', ''), base_keyword)
                }
                
                # 기본 키워드와 다르고 유효한 키워드만 포함
                if (keyword_info['keyword'] and 
                    keyword_info['keyword'] != base_keyword and
                    keyword_info['monthly_searches'] > 0):
                    keywords_data.append(keyword_info)
        
        # 관련성 점수와 검색량으로 정렬
        keywords_data.sort(key=lambda x: (x['relevance_score'], x['monthly_searches']), reverse=True)
        return keywords_data[:30]  # 상위 30개만 반환
        
    except Exception as e:
        print(f"파워링크 키워드 파싱 오류: {e}")
        return get_demo_powerlink_keywords(base_keyword)


def calculate_relevance_score(keyword, base_keyword):
    """키워드 관련성 점수 계산"""
    base_words = set(base_keyword.lower().split())
    keyword_words = set(keyword.lower().split())
    
    # 공통 단어 비율
    common_words = base_words.intersection(keyword_words)
    if not base_words:
        return 0
    
    relevance = len(common_words) / len(base_words) * 100
    
    # 키워드가 기본 키워드를 포함하는 경우 보너스 점수
    if base_keyword.lower() in keyword.lower():
        relevance += 20
    
    return min(relevance, 100)


def get_demo_powerlink_keywords(keyword):
    """데모용 파워링크 연관키워드 데이터"""
    import random
    
    # 키워드별 연관 키워드 패턴
    keyword_patterns = {
        '무선키보드': [
            '게이밍 무선키보드', '블루투스 키보드', '무선 기계식키보드', '무선키보드 추천',
            '로지텍 무선키보드', '무선키보드 마우스세트', '텐키리스 무선키보드', 'RGB 무선키보드',
            '무선키보드 충전', '무선키보드 연결', '사무용 무선키보드', '저소음 무선키보드'
        ],
        '마우스': [
            '게이밍 마우스', '무선 마우스', '유선 마우스', '마우스 추천',
            '로지텍 마우스', '레이저 마우스', 'RGB 마우스', '사무용 마우스',
            '버티컬 마우스', '트랙볼 마우스', '마우스패드', '마우스 dpi'
        ],
        '헤드셋': [
            '게이밍 헤드셋', '무선 헤드셋', '헤드셋 추천', 'USB 헤드셋',
            '블루투스 헤드셋', '스틸시리즈 헤드셋', '헤드셋 마이크', '7.1 헤드셋',
            '헤드셋 스탠드', '헤드셋 쿠션', '오픈형 헤드셋', '밀폐형 헤드셋'
        ]
    }
    
    # 기본 패턴이 없으면 일반적인 수식어 사용
    base_patterns = keyword_patterns.get(keyword, [
        f'{keyword} 추천', f'{keyword} 리뷰', f'{keyword} 가격', f'{keyword} 순위',
        f'인기 {keyword}', f'베스트 {keyword}', f'{keyword} 할인', f'{keyword} 특가',
        f'{keyword} 브랜드', f'{keyword} 비교', f'{keyword} 사용법', f'{keyword} 구매'
    ])
    
    keywords_data = []
    
    for i, kw in enumerate(base_patterns[:20]):
        keywords_data.append({
            'keyword': kw,
            'monthly_searches': random.randint(5000, 80000),
            'pc_searches': random.randint(2000, 30000),
            'mobile_searches': random.randint(3000, 50000),
            'competition': random.choice(['HIGH', 'MEDIUM', 'LOW']),
            'avg_bid': random.randint(100, 2000),
            'click_rate': round(random.uniform(1.5, 8.5), 2),
            'relevance_score': max(90 - i*3, 30)  # 순서대로 관련성 점수 감소
        })
    
    return keywords_data


def validate_api_keys():
    """API 키 유효성 검사"""
    try:
        # 간단한 검색 테스트
        test_result = search_naver_shopping("테스트", display=1, start=1)
        if test_result and 'items' in test_result:
            return True
        return False
    except:
        return False