"""
쇼핑 순위 리스트 모듈
"""
import streamlit as st
import pandas as pd
from utils.naver_api import search_naver_shopping
import re


def clean_html_tags(text):
    """HTML 태그 제거"""
    if text:
        return re.sub(r'<[^>]+>', '', text)
    return ""


def get_shopping_ranking(keyword, max_results=20):
    """네이버 쇼핑 순위 가져오기 (개선된 버전)"""
    rankings = []
    
    try:
        # API 상태 확인
        from utils.naver_api import validate_api_keys
        if not validate_api_keys():
            st.error("❌ 네이버 API 연결에 실패했습니다.")
            return rankings
        
        # 진행률 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 첫 번째 페이지부터 순위 수집
        pages_to_fetch = min(3, (max_results // 10) + 1)  # 필요한 페이지 수 계산
        
        for page in range(1, pages_to_fetch + 1):
            start = (page - 1) * 10 + 1
            progress_bar.progress(page / pages_to_fetch)
            status_text.text(f"쇼핑 순위 조회 중... {page}/{pages_to_fetch}페이지")
            
            data = search_naver_shopping(keyword, display=10, start=start, sort="sim")
            
            if data and 'items' in data:
                for idx, item in enumerate(data['items']):
                    rank = start + idx
                    if rank > max_results:
                        break
                        
                    title = clean_html_tags(item.get('title', ''))
                    price = int(item.get('lprice', 0))
                    mall_name = item.get('mallName', '정보없음')
                    link = item.get('link', '')
                    image = item.get('image', '')
                    
                    rankings.append({
                        'rank': rank,
                        'title': title,
                        'price': price,
                        'price_formatted': f"{price:,}원" if price > 0 else "가격정보없음",
                        'mall': mall_name,
                        'link': link,
                        'image': image
                    })
                    
                    if len(rankings) >= max_results:
                        break
            
            if len(rankings) >= max_results:
                break
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ 조회 완료! {len(rankings)}개 상품")
        
    except Exception as e:
        st.error(f"쇼핑 순위 조회 중 오류: {e}")
    
    return rankings


def analyze_shopping_trends(rankings):
    """쇼핑 트렌드 분석"""
    if not rankings:
        return {}
    
    # 가격 분석
    prices = [item['price'] for item in rankings if item['price'] > 0]
    
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
    else:
        avg_price = min_price = max_price = 0
    
    # 쇼핑몰 분석
    malls = [item['mall'] for item in rankings]
    mall_counts = {}
    for mall in malls:
        mall_counts[mall] = mall_counts.get(mall, 0) + 1
    
    top_malls = sorted(mall_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'total_products': len(rankings),
        'avg_price': avg_price,
        'min_price': min_price,
        'max_price': max_price,
        'price_range': max_price - min_price if max_price > 0 else 0,
        'top_malls': top_malls,
        'unique_malls': len(mall_counts)
    }


def show_shopping_ranking():
    """쇼핑 순위 리스트 페이지"""
    
    # 기능 설명
    st.markdown("""
    ### � 기능 설명
    - **인기 상품 순위**: 네이버 쇼핑의 실시간 인기 상품 조회
    - **가격대별 분석**: 최저가, 평균가, 최고가 분석
    - **쇼핑몰 분포**: 상위 랭킹 상품의 쇼핑몰 분포 현황
    - **시장 트렌드**: 상품별 가격 동향 및 판매자 분석
    """)
    
    st.markdown("---")
    
    # 검색 폼
    st.subheader("🔍 상품 검색 설정")
    with st.form("shopping_ranking_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            keyword = st.text_input(
                "상품 검색어 입력",
                placeholder="예: 무선키보드, 블루투스 이어폰, 게이밍 헤드셋",
                help="네이버 쇼핑에서 검색할 상품명을 입력하세요"
            )
        
        with col2:
            max_results = st.selectbox(
                "조회할 상품 수",
                options=[10, 20, 30, 50],
                index=1,
                help="조회할 최대 상품 개수"
            )
        
        with col3:
            sort_option = st.selectbox(
                "정렬 방식",
                options=["sim", "date", "asc", "dsc"],
                format_func=lambda x: {
                    "sim": "정확도순", 
                    "date": "날짜순", 
                    "asc": "가격낮은순", 
                    "dsc": "가격높은순"
                }[x],
                help="검색 결과 정렬 방식"
            )
        
        search_button = st.form_submit_button("🔍 쇼핑 순위 조회", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    if search_button and keyword:
        st.markdown(f"## 📊 '{keyword}' 쇼핑 순위 리스트")
        
        with st.spinner("쇼핑 순위를 조회하는 중..."):
            rankings = get_shopping_ranking(keyword, max_results)
        
        if rankings:
            # 트렌드 분석
            trends = analyze_shopping_trends(rankings)
            
            # 분석 요약
            st.subheader("📈 상품 분석 요약")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 상품 수", f"{trends['total_products']}개")
            
            with col2:
                st.metric("평균 가격", f"{trends['avg_price']:,.0f}원" if trends['avg_price'] > 0 else "정보없음")
            
            with col3:
                st.metric("최저가", f"{trends['min_price']:,}원" if trends['min_price'] > 0 else "정보없음")
            
            with col4:
                st.metric("최고가", f"{trends['max_price']:,}원" if trends['max_price'] > 0 else "정보없음")
            
            # 탭으로 결과 구분
            tab1, tab2, tab3 = st.tabs(["📋 순위 리스트", "📊 가격 분석", "🏪 쇼핑몰 분석"])
            
            with tab1:
                st.subheader("🏆 상품 순위")
                
                # 순위 리스트 표시
                for item in rankings:
                    rank = item['rank']
                    
                    # 순위별 아이콘
                    if rank <= 3:
                        rank_icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
                    elif rank <= 10:
                        rank_icon = "🏆"
                    else:
                        rank_icon = "📍"
                    
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        
                        with col1:
                            if item['image']:
                                try:
                                    st.image(item['image'], width=80)
                                except:
                                    st.write("🖼️")
                            else:
                                st.write("🖼️")
                        
                        with col2:
                            st.markdown(f"""
                            **{rank_icon} {rank}위** | {item['title']}  
                            **가격**: {item['price_formatted']} | **판매처**: {item['mall']}  
                            [🔗 상품 보기]({item['link']})
                            """)
                        
                        st.divider()
            
            with tab2:
                st.subheader("💰 가격 분포 분석")
                
                if trends['avg_price'] > 0:
                    # 가격 구간별 분포
                    price_ranges = []
                    range_counts = []
                    
                    min_p = trends['min_price']
                    max_p = trends['max_price']
                    range_size = (max_p - min_p) / 5 if max_p > min_p else 1
                    
                    for i in range(5):
                        range_start = min_p + (i * range_size)
                        range_end = min_p + ((i + 1) * range_size)
                        
                        count = sum(1 for item in rankings 
                                  if range_start <= item['price'] < range_end)
                        
                        price_ranges.append(f"{range_start:,.0f}~{range_end:,.0f}원")
                        range_counts.append(count)
                    
                    # 차트 데이터
                    price_df = pd.DataFrame({
                        '가격구간': price_ranges,
                        '상품수': range_counts
                    })
                    
                    st.bar_chart(price_df.set_index('가격구간'))
                    
                    # 가격 통계
                    st.markdown(f"""
                    **📊 가격 통계**
                    - 평균 가격: {trends['avg_price']:,.0f}원
                    - 가격 범위: {trends['price_range']:,.0f}원
                    - 최저가 대비 최고가: {(trends['max_price'] / trends['min_price']):.1f}배
                    """)
                else:
                    st.info("가격 정보가 있는 상품이 없습니다.")
            
            with tab3:
                st.subheader("🏪 쇼핑몰 분석")
                
                # 상위 쇼핑몰
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏆 TOP 쇼핑몰**")
                    for i, (mall, count) in enumerate(trends['top_malls'], 1):
                        percentage = (count / trends['total_products']) * 100
                        st.write(f"{i}. {mall}: {count}개 ({percentage:.1f}%)")
                
                with col2:
                    st.metric("총 쇼핑몰 수", f"{trends['unique_malls']}개")
                    
                    # 점유율이 높은 쇼핑몰 경고
                    if trends['top_malls'] and trends['top_malls'][0][1] / trends['total_products'] > 0.5:
                        st.warning(f"⚠️ '{trends['top_malls'][0][0]}'이 {(trends['top_malls'][0][1] / trends['total_products'] * 100):.1f}%를 점유하고 있어 독과점 상태입니다.")
                    else:
                        st.success("✅ 다양한 쇼핑몰에서 균형있게 판매되고 있습니다.")
                
                # 쇼핑몰별 분포 차트
                if len(trends['top_malls']) > 1:
                    mall_df = pd.DataFrame(trends['top_malls'], columns=['쇼핑몰', '상품수'])
                    st.bar_chart(mall_df.set_index('쇼핑몰'))
        
        else:
            st.warning(f"❌ '{keyword}'에 대한 쇼핑 순위를 찾을 수 없습니다.")
    
    elif search_button:
        st.error("❌ 검색할 상품명을 입력해주세요.")
    else:
        st.info("👆 상품명을 입력한 후 '쇼핑 순위 조회' 버튼을 눌러주세요.")