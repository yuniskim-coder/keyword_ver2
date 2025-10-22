"""
본 프로그램 'RankChecker by L&C'는 Link&Co, Inc.에 의해 개발된 소프트웨어입니다.
해당 소스코드 및 실행 파일의 무단 복제, 배포, 역컴파일, 수정은
저작권법 및 컴퓨터프로그램 보호법에 따라 엄격히 금지됩니다.

무단 유포 및 상업적 이용 시 민형사상 법적 책임을 물을 수 있습니다.
※ 본 프로그램은 사용자 추적 및 차단 기능이 포함되어 있습니다.

Copyright ⓒ 2025 Link&Co. All rights reserved.
Unauthorized reproduction or redistribution is strictly prohibited. 
"""

import streamlit as st
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
import time

# 네이버 API 키 설정
client_id = "tp2ypJeFL98lJyTSWLy5"
client_secret = "QeYFNiR0k7"

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
    st.title("🔍 네이버 순위 확인기 (by 링크앤코)")
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
           - '순위 확인' 버튼 클릭
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
        # 판매처명 입력
        mall_name = st.text_input(
            "판매처명", 
            placeholder="예: OO스토어"
        )
        
        # 검색 버튼
        search_button = st.button("🔍 순위 확인", type="primary", use_container_width=True)
    
    # 메인 영역
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
        # 초기 화면 - 빈 공간으로 처리
        st.info("� 위에서 검색어와 판매처명을 입력한 후 '순위 확인' 버튼을 눌러주세요.")
    
    # 푸터
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 12px;'>"
        "ⓒ 2025 링크앤코. 무단 복제 및 배포 금지. All rights reserved."
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()