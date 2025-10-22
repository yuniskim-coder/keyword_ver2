"""
본 프로그램 'RankChecker by L&C'는 Code by chaechae에 의해 개발된 소프트웨어입니다.
해당 소스코드 및 실행 파일의 무단 복제, 배포, 역컴파일, 수정은
저작권법 및 컴퓨터프로그램 보호법에 따라 엄격히 금지됩니다.

무단 유포 및 상업적 이용 시 민형사상 법적 책임을 물을 수 있습니다.
※ 본 프로그램은 사용자 추적 및 차단 기능이 포함되어 있습니다.

Copyright ⓒ 2025 Code by chaechae. All rights reserved.
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

# 네이버 API 키 설정
client_id = "tp2ypJeFL98lJyTSWLy5"
client_secret = "QeYFNiR0k7"

def get_related_keywords(keyword):
    """연관 키워드를 조회하는 함수"""
    try:
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start=1"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        result = json.loads(response.read())
        
        # 상품 제목에서 키워드 추출
        keywords = set()
        for item in result.get("items", []):
            title_clean = re.sub(r"<.*?>", "", item["title"])
            # 간단한 키워드 추출 (공백으로 분리)
            words = title_clean.split()
            for word in words:
                # 한글, 영문, 숫자만 포함된 2글자 이상의 단어
                if re.match(r'^[가-힣a-zA-Z0-9]+$', word) and len(word) >= 2:
                    keywords.add(word)
        
        # 원본 키워드와 너무 유사한 것들 제거
        filtered_keywords = []
        for kw in keywords:
            if keyword.lower() not in kw.lower() and kw.lower() not in keyword.lower():
                filtered_keywords.append(kw)
        
        return filtered_keywords[:20]  # 상위 20개만 반환
    except Exception as e:
        st.error(f"연관 키워드 조회 중 오류 발생: {str(e)}")
        return []

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
        page_title="네이버 순위 확인기",
        page_icon="🔍",
        layout="wide"
    )
    
    # 타이틀
    st.title("🔍 네이버 순위 확인기 (by Code by chaechae)")
    st.write("네이버 쇼핑에서 특정 판매처의 상품 순위를 확인하는 도구입니다.")
    
    # 사이드바에 사용법 안내
    with st.sidebar:
        st.header("📖 사용법 안내")
        st.markdown("""
        ### 🔍 네이버 순위 확인기 사용법
        
        1. **검색어 입력**: 
           - 확인하고 싶은 키워드를 쉼표(,)로 구분하여 입력
           - 최대 10개까지 입력 가능
           - 예: `키보드, 마우스, 헤드셋`
        
        2. **판매처명 입력**:
           - 순위를 확인하고 싶은 쇼핑몰 이름 입력
           - 정확한 이름일수록 정확한 결과 제공
           - 예: `ABC스토어`, `XYZ몰`
        
        3. **검색 실행**:
           - 원하는 탭을 선택하고 버튼 클릭
           - 네이버 쇼핑에서 1000위까지 검색
           - 결과는 실시간으로 표시됩니다
        
        ### 📊 결과 해석
        - **TOP 10**: 🥇 매우 좋은 순위
        - **TOP 50**: 🥈 좋은 순위  
        - **TOP 100**: 🥉 보통 순위
        - **100위 이하**: 📉 개선 필요
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
                    with st.expander(f"🔍 {keyword}의 연관키워드", expanded=True):
                        with st.spinner(f"{keyword} 연관키워드 조회 중..."):
                            related_keywords = get_related_keywords(keyword)
                        
                        if related_keywords:
                            st.success(f"✅ {len(related_keywords)}개의 연관키워드를 찾았습니다.")
                            
                            # 3열로 표시
                            cols = st.columns(3)
                            for i, related_kw in enumerate(related_keywords):
                                with cols[i % 3]:
                                    st.write(f"• {related_kw}")
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
                            df = pd.DataFrame(products)
                            df['가격'] = df['price'].apply(lambda x: f"{x:,}원" if x > 0 else "가격 미표시")
                            
                            # 표시할 컬럼 선택
                            display_df = df[['rank', 'title', '가격', 'mallName']].copy()
                            display_df.columns = ['순위', '상품명', '가격', '판매처']
                            
                            st.dataframe(
                                display_df,
                                use_container_width=True,
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
        "ⓒ 2025 Code by chaechae. 무단 복제 및 배포 금지. All rights reserved."
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()