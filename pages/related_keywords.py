"""
연관 키워드 분석 모듈
"""
import streamlit as st
from utils.naver_api import search_naver_shopping, get_datalab_trends
from datetime import datetime, timedelta
import pandas as pd


def get_related_keywords_from_shopping(keyword, max_keywords=20):
    """네이버 쇼핑에서 연관 키워드 추출 (개선된 버전)"""
    related_keywords = set()
    
    try:
        # API 상태 확인
        from utils.naver_api import validate_api_keys
        if not validate_api_keys():
            st.error("❌ 네이버 API 연결에 실패했습니다.")
            return []
        
        # 진행률 표시
        progress_bar = st.progress(0)
        
        # 여러 페이지에서 상품 제목 수집
        for page in range(1, 6):  # 5페이지까지
            start = (page - 1) * 10 + 1
            progress_bar.progress(page / 5)
            
            data = search_naver_shopping(keyword, display=10, start=start)
            
            if data and 'items' in data:
                for item in data['items']:
                    title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                    
                    # 제목에서 의미있는 단어 추출
                    words = title.split()
                    
                    for word in words:
                        # 키워드 필터링 개선
                        if (len(word) >= 2 and 
                            keyword not in word and 
                            not word.isdigit() and
                            word not in ['상품', '제품', '용품', '아이템', '개', '원', '배송', '무료', '빠른', '당일', '택배']):
                            
                            # 특수문자 제거
                            clean_word = ''.join(c for c in word if c.isalnum() or c in ['/', '-', '+'])
                            if len(clean_word) >= 2:
                                related_keywords.add(clean_word)
                                
                                if len(related_keywords) >= max_keywords:
                                    break
                    
                    if len(related_keywords) >= max_keywords:
                        break
            
            if len(related_keywords) >= max_keywords:
                break
        
        progress_bar.progress(1.0)
        
    except Exception as e:
        st.error(f"연관 키워드 추출 중 오류: {e}")
        return []
    
    return list(related_keywords)[:max_keywords]


def get_keyword_insights(keywords, base_keyword):
    """키워드 인사이트 분석"""
    if not keywords:
        return {}
    
    # 기본 통계
    avg_length = sum(len(kw) for kw in keywords) / len(keywords)
    min_length = min(len(kw) for kw in keywords)
    max_length = max(len(kw) for kw in keywords)
    
    # 구매 의도 키워드 비율
    purchase_keywords = ['추천', '순위', '구매', '리뷰', '후기', '비교', '가격', '할인', '특가']
    purchase_count = sum(1 for kw in keywords if any(pk in kw for pk in purchase_keywords))
    purchase_ratio = (purchase_count / len(keywords)) * 100
    
    # 고유 단어 수
    all_words = set()
    for kw in keywords:
        all_words.update(kw.split())
    
    return {
        'avg_length': avg_length,
        'min_length': min_length,
        'max_length': max_length,
        'purchase_ratio': purchase_ratio,
        'unique_words': len(all_words)
    }


def show_related_keywords():
    """연관 키워드 분석 페이지"""
    st.header("🔗 연관 키워드 분석")
    
    # 검색 폼
    with st.form("keyword_analysis_form"):
        keyword = st.text_input(
            "분석할 키워드 입력",
            placeholder="예: 무선키보드",
            help="연관 키워드를 분석할 기본 키워드를 입력하세요"
        )
        
        max_keywords = st.slider("추출할 연관 키워드 수", min_value=10, max_value=50, value=20)
        
        search_button = st.form_submit_button("🔍 연관 키워드 분석", type="primary", width="stretch")
    
    if search_button and keyword:
        st.header(f"📊 '{keyword}' 연관 키워드 분석 결과")
        
        with st.spinner("연관 키워드를 분석하는 중..."):
            related_keywords = get_related_keywords_from_shopping(keyword, max_keywords)
        
        if related_keywords:
            # 탭으로 결과 구분
            tab1, tab2, tab3 = st.tabs(["📋 키워드 목록", "📊 분석 차트", "💾 내보내기"])
            
            with tab1:
                st.subheader("🔤 추출된 연관 키워드")
                
                # 3열로 키워드 표시
                cols = st.columns(3)
                for i, related_kw in enumerate(related_keywords):
                    with cols[i % 3]:
                        st.write(f"• {related_kw}")
            
            with tab2:
                st.subheader("📈 키워드 분석")
                
                # 키워드 통계
                insights = get_keyword_insights(related_keywords, keyword)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("평균 길이", f"{insights['avg_length']:.1f}자")
                
                with col2:
                    st.metric("최단/최장", f"{insights['min_length']}/{insights['max_length']}자")
                
                with col3:
                    st.metric("구매 의도", f"{insights['purchase_ratio']:.1f}%")
                
                with col4:
                    st.metric("고유 단어", f"{insights['unique_words']}개")
                
                # 키워드 길이 분포
                st.subheader("📊 키워드 길이 분포")
                length_data = [len(kw) for kw in related_keywords]
                length_df = pd.DataFrame({
                    '길이': length_data
                })
                st.bar_chart(length_df['길이'].value_counts().sort_index())
            
            with tab3:
                st.subheader("💾 데이터 내보내기")
                
                # CSV 데이터 준비
                export_data = []
                for i, kw in enumerate(related_keywords, 1):
                    kw_type = "기타"
                    if any(intent in kw for intent in ['추천', '순위', '구매', '리뷰', '후기', '비교']):
                        kw_type = "구매의도"
                    elif any(intent in kw for intent in ['방법', '하는법', '사용법', '가이드']):
                        kw_type = "정보성"
                    
                    export_data.append({
                        '순위': i,
                        '연관키워드': kw,
                        '길이': len(kw),
                        '유형': kw_type,
                        '분석일시': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                df = pd.DataFrame(export_data)
                
                # CSV 다운로드
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV 파일 다운로드",
                    data=csv,
                    file_name=f"연관키워드_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv'
                )
                
                # 데이터 미리보기
                st.subheader("📊 데이터 미리보기")
                st.dataframe(df, width='stretch')
        
        else:
            st.warning("❌ 연관키워드를 찾을 수 없습니다.")
    
    elif search_button:
        st.error("❌ 분석할 키워드를 입력해주세요.")
    else:
        st.info("👆 키워드를 입력한 후 '연관 키워드 분석' 버튼을 눌러주세요.")