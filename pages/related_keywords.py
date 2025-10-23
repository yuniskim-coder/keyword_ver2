"""
연관 키워드 조회 페이지 - 네이버 광고센터 파워링크 캠페인 기반
"""
import streamlit as st
import pandas as pd
from utils.naver_api import get_powerlink_related_keywords


def format_number(num):
    """숫자를 천 단위로 포맷팅"""
    if num == 0:
        return "0"
    elif num < 1000:
        return str(num)
    elif num < 1000000:
        return f"{num/1000:.1f}K"
    else:
        return f"{num/1000000:.1f}M"


def get_competition_color(competition):
    """경쟁정도에 따른 색상 반환"""
    colors = {
        "HIGH": "#ff4444",
        "MEDIUM": "#ff8800", 
        "LOW": "#03C75A"
    }
    return colors.get(competition, "#666666")


def get_competition_text(competition):
    """경쟁정도 한글 변환"""
    texts = {
        "HIGH": "높음",
        "MEDIUM": "보통",
        "LOW": "낮음"
    }
    return texts.get(competition, competition)


def display_powerlink_keyword_card(keyword_data, index):
    """파워링크 키워드 카드 표시 - Streamlit 네이티브 컴포넌트 사용"""
    kw = keyword_data['keyword']
    monthly_searches = keyword_data['monthly_searches']
    competition = keyword_data['competition']
    avg_bid = keyword_data['avg_bid']
    relevance_score = keyword_data['relevance_score']
    
    # 관련성 점수에 따른 이모지와 텍스트
    if relevance_score >= 80:
        rank_emoji = "🔥"
        rank_text = "고관련"
        rank_color = "red"
    elif relevance_score >= 60:
        rank_emoji = "⭐"
        rank_text = "중관련"
        rank_color = "blue"
    else:
        rank_emoji = "📝"
        rank_text = "저관련"
        rank_color = "gray"
    
    competition_text = get_competition_text(competition)
    
    # 카드 제목과 순위
    st.markdown(f"#### {rank_emoji} **{index + 1}위: {kw}**")
    st.caption(f"{rank_text} (관련성 {relevance_score:.0f}%)")
    
    # 메트릭 정보를 4개 컬럼으로 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔍 월간 검색수",
            value=format_number(monthly_searches),
            help="월간 총 검색량"
        )
    
    with col2:
        # 경쟁정도에 따른 델타 색상
        if competition == "HIGH":
            delta_color = "inverse"
        elif competition == "MEDIUM":
            delta_color = "normal"
        else:
            delta_color = "normal"
            
        st.metric(
            label="⚔️ 경쟁정도",
            value=competition_text,
            help="광고 경쟁 수준"
        )
    
    with col3:
        st.metric(
            label="💰 평균 입찰가",
            value=f"{avg_bid:,}원",
            help="클릭당 평균 광고비"
        )
    
    with col4:
        st.metric(
            label="🎯 관련성",
            value=f"{relevance_score:.0f}%",
            help="기준 키워드와의 관련성"
        )
    
    # 구분선
    st.divider()


def display_powerlink_summary(keywords_data, base_keyword):
    """파워링크 키워드 요약 정보 표시"""
    if not keywords_data:
        return
    
    total_keywords = len(keywords_data)
    avg_searches = sum(kw['monthly_searches'] for kw in keywords_data) / total_keywords
    high_comp_count = sum(1 for kw in keywords_data if kw['competition'] == 'HIGH')
    avg_bid = sum(kw['avg_bid'] for kw in keywords_data) / total_keywords
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "추출된 키워드", 
            f"{total_keywords}개",
            help="파워링크 캠페인에서 추출된 연관키워드 수"
        )
    
    with col2:
        st.metric(
            "평균 월간검색수", 
            format_number(int(avg_searches)),
            help="연관키워드들의 평균 월간 검색량"
        )
    
    with col3:
        st.metric(
            "고경쟁 키워드", 
            f"{high_comp_count}개",
            help="경쟁정도가 '높음'인 키워드 수"
        )
    
    with col4:
        st.metric(
            "평균 입찰가", 
            f"{int(avg_bid):,}원",
            help="파워링크 캠페인 평균 입찰가"
        )


def show_related_keywords():
    """연관 키워드 조회 페이지 - 파워링크 캠페인 기반"""
    
    # 기능 설명
    st.markdown("""
    ### 📋 기능 설명
    - **파워링크 캠페인 기반**: 네이버 광고센터의 실제 광고 데이터 활용
    - **광고비 예측**: 평균 입찰가 정보로 광고비 예산 계획 가능
    - **경쟁 분석**: 키워드별 경쟁정도로 진입 난이도 파악
    - **우선순위 분석**: 검색량과 관련성을 종합한 키워드 우선순위 제공
    """)
    
    st.markdown("---")
    
    # 파워링크 특화 안내
    st.info("""
    💡 **파워링크 캠페인 연관키워드 특징**
    - ✅ 실제 광고 운영 데이터 기반으로 신뢰성 높음
    - 💰 입찰가 정보 포함으로 광고비 예측 가능
    - ⚔️ 경쟁정도 분석으로 진입 난이도 파악
    - 🎯 검색량과 관련성을 종합한 우선순위 제공
    """)
    
    # 검색 폼
    st.subheader("🔍 키워드 검색 설정")
    with st.form("powerlink_keyword_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            keyword = st.text_input(
                "기준 키워드 입력",
                placeholder="예: 무선키보드, 블루투스 헤드셋, 게이밍 마우스",
                help="파워링크 캠페인에서 연관키워드를 추출할 기준 키워드를 입력하세요"
            )
        
        with col2:
            max_keywords = st.selectbox(
                "추출 개수",
                options=[10, 20, 30],
                index=1,
                help="추출할 연관키워드 개수"
            )
        
        search_button = st.form_submit_button(
            "🔍 파워링크 연관키워드 조회", 
            type="primary",
            use_container_width=True
        )
    
    st.markdown("---")
    
    if search_button and keyword:
        st.markdown(f"## 🎯 '{keyword}' 파워링크 연관키워드 분석")
        
        with st.spinner("네이버 광고센터에서 파워링크 연관키워드를 조회하는 중..."):
            keywords_data = get_powerlink_related_keywords(keyword)
        
        if keywords_data:
            # 요약 정보
            st.markdown("### 📊 파워링크 키워드 요약")
            display_powerlink_summary(keywords_data[:max_keywords], keyword)
            
            st.markdown("---")
            
            # 탭으로 결과 구분
            tab1, tab2, tab3 = st.tabs(["🎯 키워드 카드", "📈 상세 데이터", "💾 내보내기"])
            
            with tab1:
                st.markdown("### 🔥 추천 연관키워드")
                st.markdown("관련성과 검색량을 종합하여 우선순위별로 정렬되었습니다.")
                
                # 키워드 카드 표시
                for i, keyword_data in enumerate(keywords_data[:max_keywords]):
                    display_powerlink_keyword_card(keyword_data, i)
            
            with tab2:
                st.markdown("### 📋 상세 데이터 테이블")
                
                # 데이터 테이블 준비
                table_data = []
                for i, kw_data in enumerate(keywords_data[:max_keywords]):
                    table_data.append({
                        '순위': i + 1,
                        '키워드': kw_data['keyword'],
                        '월간검색수': format_number(kw_data['monthly_searches']),
                        'PC검색수': format_number(kw_data['pc_searches']),
                        '모바일검색수': format_number(kw_data['mobile_searches']),
                        '경쟁정도': get_competition_text(kw_data['competition']),
                        '평균입찰가': f"{kw_data['avg_bid']:,}원",
                        '클릭률': f"{kw_data['click_rate']:.1f}%",
                        '관련성점수': f"{kw_data['relevance_score']:.0f}%"
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # 차트 분석
                st.markdown("### 📊 키워드 분석 차트")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    st.markdown("**경쟁정도 분포**")
                    comp_data = {}
                    for kw_data in keywords_data[:max_keywords]:
                        comp = get_competition_text(kw_data['competition'])
                        comp_data[comp] = comp_data.get(comp, 0) + 1
                    
                    comp_df = pd.DataFrame(list(comp_data.items()), columns=['경쟁정도', '개수'])
                    st.bar_chart(comp_df.set_index('경쟁정도'))
                
                with chart_col2:
                    st.markdown("**입찰가 분포**")
                    bid_ranges = {'~500원': 0, '500~1000원': 0, '1000~2000원': 0, '2000원+': 0}
                    
                    for kw_data in keywords_data[:max_keywords]:
                        bid = kw_data['avg_bid']
                        if bid < 500:
                            bid_ranges['~500원'] += 1
                        elif bid < 1000:
                            bid_ranges['500~1000원'] += 1
                        elif bid < 2000:
                            bid_ranges['1000~2000원'] += 1
                        else:
                            bid_ranges['2000원+'] += 1
                    
                    bid_df = pd.DataFrame(list(bid_ranges.items()), columns=['입찰가구간', '개수'])
                    st.bar_chart(bid_df.set_index('입찰가구간'))
            
            with tab3:
                st.markdown("### 💾 데이터 내보내기")
                
                # CSV 다운로드용 데이터 준비
                export_data = []
                for i, kw_data in enumerate(keywords_data[:max_keywords]):
                    export_data.append({
                        '순위': i + 1,
                        '기준키워드': keyword,
                        '연관키워드': kw_data['keyword'],
                        '월간검색수': kw_data['monthly_searches'],
                        'PC검색수': kw_data['pc_searches'],
                        '모바일검색수': kw_data['mobile_searches'],
                        '경쟁정도': kw_data['competition'],
                        '평균입찰가': kw_data['avg_bid'],
                        '클릭률': kw_data['click_rate'],
                        '관련성점수': kw_data['relevance_score']
                    })
                
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="📥 파워링크 연관키워드 CSV 다운로드",
                    data=csv,
                    file_name=f"powerlink_keywords_{keyword}.csv",
                    mime="text/csv"
                )
                
                # 마케팅 인사이트
                st.markdown("### 💡 광고 전략 제안")
                
                high_value_keywords = [kw for kw in keywords_data[:10] if kw['relevance_score'] >= 70 and kw['competition'] != 'HIGH']
                low_comp_keywords = [kw for kw in keywords_data[:10] if kw['competition'] == 'LOW']
                
                insight_col1, insight_col2 = st.columns(2)
                
                with insight_col1:
                    st.success(f"""
                    **🎯 우선 타겟 키워드**
                    - 고관련성 + 중저경쟁: {len(high_value_keywords)}개
                    - 추천: {', '.join([kw['keyword'] for kw in high_value_keywords[:3]])}
                    """)
                
                with insight_col2:
                    st.info(f"""
                    **💰 저경쟁 키워드 기회**
                    - 저경쟁 키워드: {len(low_comp_keywords)}개
                    - 진입 용이: {', '.join([kw['keyword'] for kw in low_comp_keywords[:3]])}
                    """)
        
        else:
            st.error("❌ 파워링크 연관키워드를 가져올 수 없습니다.")
            st.markdown("""
            **가능한 원인:**
            - 네이버 광고센터 API 일시적 오류
            - 해당 키워드의 파워링크 데이터 부족
            - API 호출 한도 초과
            """)
    
    elif search_button:
        st.warning("⚠️ 기준 키워드를 입력해주세요.")
    else:
        # 사용법 안내
        with st.expander("💡 파워링크 연관키워드 활용법", expanded=False):
            st.markdown("""
            ### 📋 연관키워드 조회 활용 방법
            
            **1️⃣ 기준 키워드 선정**
            - 메인 상품이나 서비스의 핵심 키워드 입력
            - 너무 광범위하지 않은 구체적인 키워드 권장
            - 예: `무선키보드`, `블루투스 헤드셋`, `게이밍 마우스`
            
            **2️⃣ 파워링크 데이터 분석**
            - **월간 검색량**: 키워드별 실제 검색 횟수
            - **경쟁정도**: 광고 경쟁의 치열함 (높음/보통/낮음)
            - **평균 입찰가**: 클릭당 예상 광고비
            - **관련성 점수**: 기준 키워드와의 연관성 (0~100%)
            
            **3️⃣ 키워드 우선순위 결정**
            - 🔥 **고관련 키워드**: 관련성 80% 이상, 메인 타겟
            - ⭐ **중관련 키워드**: 관련성 60~79%, 확장 타겟
            - 📝 **저관련 키워드**: 관련성 60% 미만, 롱테일 전략
            
            ### 💡 광고 전략 수립 팁
            - 🎯 **우선 타겟**: 고관련성 + 중저경쟁 키워드
            - 💰 **예산 효율**: 저경쟁 키워드로 진입 비용 절약
            - 📈 **확장 전략**: 중관련성 키워드로 노출 확대
            - 🔄 **지속 모니터링**: 정기적인 키워드 성과 분석
            """)


if __name__ == "__main__":
    show_related_keywords()