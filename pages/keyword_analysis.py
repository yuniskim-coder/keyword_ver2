"""
키워드 분석 페이지 - 네이버 키워드 도구 API 활용
"""
import streamlit as st
import pandas as pd
from utils.naver_api import get_keyword_competition_data


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
    if competition == "HIGH":
        return "#ff4444"
    elif competition == "MEDIUM":
        return "#ff8800"
    else:
        return "#03C75A"


def get_competition_text(competition):
    """경쟁정도 텍스트 변환"""
    competition_map = {
        "HIGH": "높음",
        "MEDIUM": "보통", 
        "LOW": "낮음"
    }
    return competition_map.get(competition, competition)


def display_keyword_metrics(data):
    """키워드 지표를 시각적으로 표시"""
    st.markdown("### 📊 키워드 상세 분석")
    
    # 메인 지표 카드들
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h4 style="margin: 0; font-size: 14px; opacity: 0.9;">월간 검색수 (PC)</h4>
            <h2 style="margin: 10px 0; font-size: 24px;">{format_number(data['monthly_pc_searches'])}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h4 style="margin: 0; font-size: 14px; opacity: 0.9;">월간 검색수 (모바일)</h4>
            <h2 style="margin: 10px 0; font-size: 24px;">{format_number(data['monthly_mobile_searches'])}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        competition_color = get_competition_color(data['competition_index'])
        competition_text = get_competition_text(data['competition_index'])
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {competition_color} 0%, {competition_color}cc 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h4 style="margin: 0; font-size: 14px; opacity: 0.9;">경쟁정도</h4>
            <h2 style="margin: 10px 0; font-size: 24px;">{competition_text}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_searches = data['monthly_pc_searches'] + data['monthly_mobile_searches']
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h4 style="margin: 0; font-size: 14px; opacity: 0.9;">총 월간 검색수</h4>
            <h2 style="margin: 10px 0; font-size: 24px;">{format_number(total_searches)}</h2>
        </div>
        """, unsafe_allow_html=True)


def display_detailed_stats(data):
    """상세 통계 테이블 표시"""
    st.markdown("### 📈 상세 통계")
    
    # 클릭 관련 지표
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💻 PC 지표")
        pc_df = pd.DataFrame({
            '지표': ['월간 검색수', '월평균 클릭수', '월평균 클릭률 (%)', '월평균 노출 광고수'],
            '값': [
                format_number(data['monthly_pc_searches']),
                format_number(data['monthly_pc_clicks']),
                f"{data['monthly_pc_ctr']:.2f}%",
                format_number(data['monthly_pc_ad_exposure'])
            ]
        })
        st.dataframe(pc_df, width=None, hide_index=True)
    
    with col2:
        st.markdown("#### 📱 모바일 지표")
        mobile_df = pd.DataFrame({
            '지표': ['월간 검색수', '월평균 클릭수', '월평균 클릭률 (%)', '월평균 노출 광고수'],
            '값': [
                format_number(data['monthly_mobile_searches']),
                format_number(data['monthly_mobile_clicks']),
                f"{data['monthly_mobile_ctr']:.2f}%",
                format_number(data['monthly_mobile_ad_exposure'])
            ]
        })
        st.dataframe(mobile_df, width=None, hide_index=True)


def display_comparison_chart(data):
    """PC vs 모바일 비교 차트"""
    st.markdown("### 📊 PC vs 모바일 비교")
    
    # 비교 데이터 준비
    comparison_data = {
        '플랫폼': ['PC', '모바일'],
        '월간 검색수': [data['monthly_pc_searches'], data['monthly_mobile_searches']],
        '월평균 클릭수': [data['monthly_pc_clicks'], data['monthly_mobile_clicks']],
        '클릭률(%)': [data['monthly_pc_ctr'], data['monthly_mobile_ctr']],
        '광고 노출수': [data['monthly_pc_ad_exposure'], data['monthly_mobile_ad_exposure']]
    }
    
    df = pd.DataFrame(comparison_data)
    
    # 차트 탭
    tab1, tab2, tab3, tab4 = st.tabs(["📈 검색수", "👆 클릭수", "📊 클릭률", "📺 광고노출"])
    
    with tab1:
        st.bar_chart(df.set_index('플랫폼')['월간 검색수'])
    
    with tab2:
        st.bar_chart(df.set_index('플랫폼')['월평균 클릭수'])
    
    with tab3:
        st.bar_chart(df.set_index('플랫폼')['클릭률(%)'])
    
    with tab4:
        st.bar_chart(df.set_index('플랫폼')['광고 노출수'])


def show_keyword_analysis():
    """키워드 분석 페이지 메인 함수"""
    
    # 기능 설명
    st.markdown("""
    ### 📋 기능 설명
    - **정밀 검색량 분석**: PC/모바일별 월간 검색수 제공
    - **광고 효과 예측**: 클릭률, 광고 노출수 등 광고 성과 지표
    - **경쟁 분석**: 키워드별 경쟁정도와 진입 난이도 평가
    - **ROI 계산**: 검색량 대비 클릭률로 광고 효율성 분석
    """)
    
    st.markdown("---")
    
    # API 상태 안내
    st.info("""
    💡 **키워드 분석 제공 데이터**
    - 📊 월간 검색수 (PC/모바일 별도 제공)
    - 🖱️ 월평균 클릭수 및 클릭률 분석  
    - ⚔️ 경쟁정도 (높음/보통/낮음) 평가
    - 📺 월평균 광고 노출수 통계
    - 🔄 실시간 네이버 광고 데이터 기반
    """)
    
    # 검색 폼
    st.subheader("🔍 키워드 분석 설정")
    with st.form("keyword_detailed_analysis_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            keyword = st.text_input(
                "분석할 키워드 입력",
                placeholder="예: 무선키보드, 블루투스 이어폰, 게이밍 마우스",
                help="분석하고 싶은 키워드를 입력하세요. 정확한 통계 데이터를 제공합니다."
            )
        
        with col2:
            analysis_depth = st.selectbox(
                "분석 깊이",
                options=["기본", "상세", "심화"],
                index=1,
                help="분석 수준을 선택하세요"
            )
        
        st.markdown("� **분석 항목**: 검색량 → 클릭률 → 경쟁정도 → 광고노출수 → 수익성 예측")
        
        search_button = st.form_submit_button("🔍 키워드 분석 시작", type="primary", width="stretch")
    
    st.markdown("---")
    
    if search_button and keyword:
        st.markdown(f"## 🎯 '{keyword}' 키워드 분석 결과")
        
        with st.spinner("키워드 데이터를 분석하는 중..."):
            keyword_data = get_keyword_competition_data(keyword)
        
        if keyword_data:
            # 성공 메시지
            st.success(f"✅ '{keyword_data['keyword']}' 키워드 분석이 완료되었습니다!")
            
            # 키워드 지표 표시
            display_keyword_metrics(keyword_data)
            
            st.markdown("---")
            
            # 상세 통계
            display_detailed_stats(keyword_data)
            
            st.markdown("---")
            
            # 비교 차트
            display_comparison_chart(keyword_data)
            
            st.markdown("---")
            
            # 인사이트 섹션
            st.markdown("### 🔍 키워드 인사이트")
            
            total_searches = keyword_data['monthly_pc_searches'] + keyword_data['monthly_mobile_searches']
            mobile_ratio = (keyword_data['monthly_mobile_searches'] / total_searches * 100) if total_searches > 0 else 0
            
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                st.info(f"""
                **🔥 검색 트렌드**
                - 총 월간 검색수: {format_number(total_searches)}회
                - 모바일 검색 비율: {mobile_ratio:.1f}%
                - 경쟁 수준: {get_competition_text(keyword_data['competition_index'])}
                """)
            
            with insight_col2:
                # 추천 사항
                if mobile_ratio > 70:
                    recommendation = "📱 모바일 중심의 광고 전략을 권장합니다."
                elif mobile_ratio < 30:
                    recommendation = "💻 PC 중심의 광고 전략을 권장합니다."
                else:
                    recommendation = "⚖️ PC와 모바일 균형 전략을 권장합니다."
                
                if keyword_data['competition_index'] == "HIGH":
                    competition_tip = "경쟁이 치열하니 롱테일 키워드 검토를 권장합니다."
                elif keyword_data['competition_index'] == "LOW":
                    competition_tip = "경쟁이 낮아 진입하기 좋은 키워드입니다."
                else:
                    competition_tip = "적당한 경쟁 수준으로 전략적 접근이 필요합니다."
                
                st.warning(f"""
                **💡 마케팅 제안**
                - {recommendation}
                - {competition_tip}
                """)
            
            # 데이터 다운로드
            st.markdown("### 💾 데이터 내보내기")
            
            # CSV 다운로드용 데이터 준비
            export_data = {
                '키워드': [keyword_data['keyword']],
                'PC_월간검색수': [keyword_data['monthly_pc_searches']],
                '모바일_월간검색수': [keyword_data['monthly_mobile_searches']],
                'PC_월평균클릭수': [keyword_data['monthly_pc_clicks']],
                '모바일_월평균클릭수': [keyword_data['monthly_mobile_clicks']],
                'PC_클릭률': [keyword_data['monthly_pc_ctr']],
                '모바일_클릭률': [keyword_data['monthly_mobile_ctr']],
                '경쟁정도': [keyword_data['competition_index']],
                'PC_광고노출': [keyword_data['monthly_pc_ad_exposure']],
                '모바일_광고노출': [keyword_data['monthly_mobile_ad_exposure']]
            }
            
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📥 CSV로 다운로드",
                data=csv,
                file_name=f"keyword_analysis_{keyword_data['keyword']}.csv",
                mime="text/csv"
            )
            
        else:
            st.error("❌ 키워드 데이터를 가져올 수 없습니다. 키워드를 확인하거나 잠시 후 다시 시도해주세요.")
            
            st.markdown("""
            **가능한 원인:**
            - 네이버 API 일시적 오류
            - 키워드가 존재하지 않음
            - API 호출 한도 초과
            """)


if __name__ == "__main__":
    show_keyword_analysis()