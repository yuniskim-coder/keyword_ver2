"""
네이버 API 관련 유틸리티
"""
import json
import urllib.request
import urllib.parse
import time
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
        # 1. 네이버 쇼핑에서 연관 키워드 추출
        for page in range(1, 4):  # 3페이지까지
            start = (page - 1) * 10 + 1
            data = search_naver_shopping(keyword, display=10, start=start)
            
            if data and 'items' in data:
                for item in data['items']:
                    title = item.get('title', '')
                    # 제목에서 키워드 추출
                    words = title.split()
                    for word in words:
                        # 유효한 키워드 필터링
                        if (len(word) >= 2 and 
                            keyword not in word and 
                            not word.isdigit() and
                            word not in ['상품', '제품', '용품', '아이템', '개', '원', '배송']):
                            related_keywords.add(word)
                            
                            if len(related_keywords) >= 30:
                                break
                    
                    if len(related_keywords) >= 30:
                        break
            
            if len(related_keywords) >= 30:
                break
        
        # 2. 검색 제안어 API (만약 사용 가능하다면)
        # 여기에 추가 API 호출 로직을 넣을 수 있습니다
        
    except Exception as e:
        print(f"연관 키워드 추출 오류: {e}")
    
    return list(related_keywords)[:20]  # 최대 20개 반환


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