"""
순위 확인 기능 모듈
"""
import streamlit as st
import re
from utils.naver_api import search_naver_shopping
from config import SEARCH_CONFIG


def clean_html_tags(text):
    """HTML 태그 제거"""
    if text:
        return re.sub(r'<[^>]+>', '', text)
    return ""


def get_seller_name(mall_name, lprice, hprice):
    """판매처명 추출"""
    if mall_name and mall_name.strip():
        return mall_name.strip()
    elif lprice and hprice:
        return f"가격대: {lprice:,}~{hprice:,}원"
    else:
        return "정보없음"


def search_product_rank(keyword, seller_name, max_pages=100):
    """상품 순위 검색 (개선된 버전)"""
    results = []
    items_per_page = SEARCH_CONFIG["items_per_page"]
    
    # API 상태 확인
    with st.spinner("API 연결 상태 확인 중..."):
        from utils.naver_api import validate_api_keys
        if not validate_api_keys():
            st.error("❌ 네이버 API 연결에 실패했습니다. API 키를 확인해주세요.")
            return results
    
    # 진행률 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for page in range(1, min(max_pages + 1, 21)):  # 최대 20페이지로 제한 (API 제한 고려)
        start = (page - 1) * items_per_page + 1
        
        try:
            # 진행률 업데이트
            progress = page / min(max_pages, 20)
            progress_bar.progress(progress)
            status_text.text(f"검색 중... {page}/{min(max_pages, 20)}페이지")
            
            data = search_naver_shopping(keyword, display=items_per_page, start=start)
            
            if not data or 'items' not in data or not data['items']:
                break
            
            for idx, item in enumerate(data['items']):
                rank = start + idx
                title = clean_html_tags(item.get('title', ''))
                mall_name = item.get('mallName', '')
                lprice = int(item.get('lprice', 0))
                hprice = int(item.get('hprice', 0))
                
                current_seller = get_seller_name(mall_name, lprice, hprice)
                
                # 판매처명 매칭 개선 (부분 일치 + 대소문자 무시)
                if (seller_name.lower() in current_seller.lower() or 
                    current_seller.lower() in seller_name.lower()):
                    
                    results.append({
                        'rank': rank,
                        'title': title,
                        'seller': current_seller,
                        'price': f"{lprice:,}원" if lprice > 0 else "가격정보없음",
                        'link': item.get('link', ''),
                        'image': item.get('image', '')
                    })
                    
                    if len(results) >= 10:  # 최대 10개 결과만 수집
                        progress_bar.progress(1.0)
                        status_text.text(f"✅ 검색 완료! {len(results)}개 상품 발견")
                        return results
        
        except Exception as e:
            st.error(f"검색 중 오류 발생 (페이지 {page}): {str(e)}")
            break
    
    # 완료
    progress_bar.progress(1.0)
    if results:
        status_text.text(f"✅ 검색 완료! {len(results)}개 상품 발견")
    else:
        status_text.text("❌ 해당 판매처의 상품을 찾을 수 없습니다.")
    
    return results


def show_rank_checker():
    """순위 확인기 페이지"""
    st.header("🎯 네이버 쇼핑 순위 확인")
    
    # 검색 폼
    with st.form("rank_search_form"):
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
                help="정확한 판매처명일수록 정확한 결과"
            )
        
        search_button = st.form_submit_button("🔍 순위 확인", type="primary", width="stretch")
    
    if search_button and keywords_text and seller_name:
        keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
        
        if len(keywords) > SEARCH_CONFIG["max_keywords"]:
            st.error(f"❌ 최대 {SEARCH_CONFIG['max_keywords']}개의 키워드만 입력 가능합니다.")
            return
        
        st.header(f"📊 '{seller_name}' 순위 결과")
        
        for keyword in keywords:
            with st.expander(f"🔍 '{keyword}' 검색 결과", expanded=True):
                with st.spinner(f"'{keyword}' 순위 검색 중..."):
                    results = search_product_rank(keyword, seller_name)
                
                if results:
                    st.success(f"✅ {len(results)}개의 상품을 찾았습니다!")
                    
                    for result in results:
                        rank = result['rank']
                        
                        # 순위별 아이콘
                        if rank <= 10:
                            rank_icon = "🥇"
                            rank_color = "success"
                        elif rank <= 50:
                            rank_icon = "🥈"
                            rank_color = "info"
                        elif rank <= 100:
                            rank_icon = "🥉"
                            rank_color = "warning"
                        else:
                            rank_icon = "📉"
                            rank_color = "error"
                        
                        st.markdown(f"""
                        **{rank_icon} {rank}위** | {result['title']}  
                        **판매처**: {result['seller']} | **가격**: {result['price']}
                        """)
                else:
                    st.warning(f"❌ '{keyword}'에서 '{seller_name}' 상품을 찾을 수 없습니다.")
    
    elif search_button:
        st.error("❌ 검색어와 판매처명을 모두 입력해주세요.")
    else:
        st.info("👆 검색어와 판매처명을 입력한 후 '순위 확인' 버튼을 눌러주세요.")