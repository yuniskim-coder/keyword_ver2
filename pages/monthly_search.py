"""
월간 검색수 분석 모듈
"""
import streamlit as st
import pandas as pd
from utils.naver_api import get_datalab_trends
from datetime import datetime, timedelta
import json


def get_keyword_search_volume(keyword):
    """키워드의 월간 검색량 조회"""
    try:
        # 1년 전부터 현재까지
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        # PC 검색량
        pc_data = get_datalab_trends([keyword], start_date, end_date, "month", "pc")
        
        # 모바일 검색량  
        mobile_data = get_datalab_trends([keyword], start_date, end_date, "month", "mo")
        
        if pc_data and mobile_data and 'results' in pc_data and 'results' in mobile_data:
            pc_results = pc_data['results'][0]['data'] if pc_data['results'] else []
            mobile_results = mobile_data['results'][0]['data'] if mobile_data['results'] else []
            
            # 최근 월 데이터
            if pc_results and mobile_results:
                latest_pc = pc_results[-1]['ratio'] if pc_results else 0
                latest_mobile = mobile_results[-1]['ratio'] if mobile_results else 0
                
                # 상대적 검색량 계산 (임의의 기준값 적용)
                base_volume = 10000  # 기준 검색량
                pc_volume = int(latest_pc * base_volume / 100)
                mobile_volume = int(latest_mobile * base_volume / 100)
                total_volume = pc_volume + mobile_volume
                
                # 비율 계산
                pc_ratio = (pc_volume / total_volume * 100) if total_volume > 0 else 0
                mobile_ratio = (mobile_volume / total_volume * 100) if total_volume > 0 else 0
                
                return {
                    'pc_volume': pc_volume,
                    'mobile_volume': mobile_volume,
                    'total_volume': total_volume,
                    'pc_ratio': pc_ratio,
                    'mobile_ratio': mobile_ratio,
                    'pc_trend_data': pc_results,
                    'mobile_trend_data': mobile_results
                }
        
        return None
        
    except Exception as e:
        st.error(f"검색량 조회 중 오류: {e}")
        return None


def analyze_search_trends(pc_data, mobile_data):
    """검색 트렌드 분석"""
    analysis = {
        'trend_direction': '유지',
        'peak_month': None,
        'growth_rate': 0,
        'device_preference': 'balanced'
    }
    
    try:
        if len(pc_data) >= 2 and len(mobile_data) >= 2:
            # 최근 3개월 평균 vs 이전 3개월 평균
            recent_pc = sum(item['ratio'] for item in pc_data[-3:]) / 3
            previous_pc = sum(item['ratio'] for item in pc_data[-6:-3]) / 3
            
            recent_mobile = sum(item['ratio'] for item in mobile_data[-3:]) / 3
            previous_mobile = sum(item['ratio'] for item in mobile_data[-6:-3]) / 3
            
            recent_total = recent_pc + recent_mobile
            previous_total = previous_pc + previous_mobile
            
            # 성장률 계산
            if previous_total > 0:
                growth_rate = ((recent_total - previous_total) / previous_total) * 100
                analysis['growth_rate'] = growth_rate
                
                if growth_rate > 10:
                    analysis['trend_direction'] = '증가'
                elif growth_rate < -10:
                    analysis['trend_direction'] = '감소'
            
            # 피크 월 찾기
            all_data = [(pc_data[i]['period'], pc_data[i]['ratio'] + mobile_data[i]['ratio']) 
                       for i in range(min(len(pc_data), len(mobile_data)))]
            
            if all_data:
                peak_month = max(all_data, key=lambda x: x[1])
                analysis['peak_month'] = peak_month[0]
            
            # 디바이스 선호도
            avg_pc = sum(item['ratio'] for item in pc_data) / len(pc_data)
            avg_mobile = sum(item['ratio'] for item in mobile_data) / len(mobile_data)
            
            if avg_mobile > avg_pc * 1.5:
                analysis['device_preference'] = 'mobile'
            elif avg_pc > avg_mobile * 1.5:
                analysis['device_preference'] = 'pc'
    
    except Exception as e:
        print(f"트렌드 분석 오류: {e}")
    
    return analysis


def show_monthly_search():
    """월간 검색수 분석 페이지"""
    st.header("📈 월간 검색수 분석")
    
    # 검색 폼
    with st.form("monthly_search_form"):
        keywords_input = st.text_input(
            "키워드 입력",
            placeholder="분석할 키워드를 쉼표(,)로 구분하여 입력하세요",
            help="최대 5개까지 입력 가능합니다. 예: 무선키보드, 게이밍키보드, 기계식키보드"
        )
        
        search_button = st.form_submit_button("📊 월간 검색수 조회", type="primary", width="stretch")
    
    if search_button and keywords_input:
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        if len(keywords) > 5:
            st.error("❌ 최대 5개의 키워드만 입력 가능합니다.")
            return
        
        st.header("📊 월간 검색수 분석 결과")
        
        for keyword in keywords:
            with st.expander(f"🔍 {keyword} 검색량", expanded=True):
                with st.spinner(f"{keyword} 검색량 조회 중..."):
                    volume_data = get_keyword_search_volume(keyword)
                
                if volume_data:
                    # 메트릭 표시
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
                    
                    # 탭으로 상세 분석 구분
                    tab1, tab2, tab3 = st.tabs(["📊 디바이스 비율", "📈 트렌드 차트", "🔍 상세 분석"])
                    
                    with tab1:
                        st.subheader("📊 디바이스별 검색 비율")
                        
                        # 파이 차트 데이터
                        chart_data = pd.DataFrame({
                            '구분': ['모바일', 'PC'],
                            '검색량': [volume_data['mobile_volume'], volume_data['pc_volume']]
                        })
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.bar_chart(chart_data.set_index('구분'))
                        
                        with col2:
                            # 비율 표시
                            st.markdown(f"""
                            **📱 모바일**: {volume_data['mobile_ratio']:.1f}%  
                            **💻 PC**: {volume_data['pc_ratio']:.1f}%
                            
                            **주요 디바이스**: {'📱 모바일' if volume_data['mobile_ratio'] > volume_data['pc_ratio'] else '💻 PC'}
                            """)
                    
                    with tab2:
                        st.subheader("📈 검색량 트렌드 (최근 1년)")
                        
                        if 'pc_trend_data' in volume_data and 'mobile_trend_data' in volume_data:
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
                                analysis = analyze_search_trends(pc_trends, mobile_trends)
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    trend_icon = "📈" if analysis['trend_direction'] == '증가' else "📉" if analysis['trend_direction'] == '감소' else "➡️"
                                    st.info(f"{trend_icon} **트렌드**: {analysis['trend_direction']} ({analysis['growth_rate']:+.1f}%)")
                                
                                with col2:
                                    if analysis['peak_month']:
                                        st.info(f"🏆 **피크 월**: {analysis['peak_month']}")
                        else:
                            st.warning("트렌드 데이터를 가져올 수 없습니다.")
                    
                    with tab3:
                        st.subheader("🔍 상세 분석")
                        
                        # 검색 패턴 분석
                        if 'pc_trend_data' in volume_data and 'mobile_trend_data' in volume_data:
                            analysis = analyze_search_trends(
                                volume_data['pc_trend_data'], 
                                volume_data['mobile_trend_data']
                            )
                            
                            # 분석 결과 표시
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📊 검색 패턴**")
                                
                                device_pref = {
                                    'mobile': '📱 모바일 중심',
                                    'pc': '💻 PC 중심', 
                                    'balanced': '⚖️ 균형'
                                }
                                
                                st.write(f"• 선호 디바이스: {device_pref.get(analysis['device_preference'], '알 수 없음')}")
                                st.write(f"• 검색량 변화: {analysis['trend_direction']} ({analysis['growth_rate']:+.1f}%)")
                                
                                if analysis['peak_month']:
                                    st.write(f"• 최고 검색량: {analysis['peak_month']}")
                            
                            with col2:
                                st.markdown("**💡 마케팅 인사이트**")
                                
                                if analysis['device_preference'] == 'mobile':
                                    st.write("📱 모바일 최적화에 집중하세요")
                                elif analysis['device_preference'] == 'pc':
                                    st.write("💻 PC 환경 최적화에 집중하세요")
                                else:
                                    st.write("📱💻 모든 디바이스 최적화가 필요합니다")
                                
                                if analysis['trend_direction'] == '증가':
                                    st.write("📈 성장 트렌드를 활용한 적극적 마케팅 권장")
                                elif analysis['trend_direction'] == '감소':
                                    st.write("📉 새로운 키워드 발굴이 필요합니다")
                        
                        # 원시 데이터 다운로드
                        st.markdown("**📥 데이터 다운로드**")
                        
                        # CSV 데이터 준비
                        if 'pc_trend_data' in volume_data and 'mobile_trend_data' in volume_data:
                            export_data = []
                            pc_trends = volume_data['pc_trend_data']
                            mobile_trends = volume_data['mobile_trend_data']
                            
                            for i in range(min(len(pc_trends), len(mobile_trends))):
                                export_data.append({
                                    '날짜': pc_trends[i]['period'],
                                    'PC검색량': pc_trends[i]['ratio'],
                                    '모바일검색량': mobile_trends[i]['ratio'],
                                    '총검색량': pc_trends[i]['ratio'] + mobile_trends[i]['ratio'],
                                    '키워드': keyword
                                })
                            
                            if export_data:
                                export_df = pd.DataFrame(export_data)
                                csv = export_df.to_csv(index=False, encoding='utf-8-sig')
                                
                                st.download_button(
                                    label="📥 검색량 데이터 CSV 다운로드",
                                    data=csv,
                                    file_name=f"검색량_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime='text/csv'
                                )
                    
                    st.info("💡 위 데이터는 네이버 DataLab API에서 제공하는 상대적 검색량 데이터입니다.")
                else:
                    st.warning("❌ 검색량 정보를 찾을 수 없습니다.")
    
    elif search_button:
        st.error("❌ 분석할 키워드를 입력해주세요.")
    else:
        st.info("👆 키워드를 입력한 후 '월간 검색수 조회' 버튼을 눌러주세요.")
        
        # 사용 예시
        st.markdown("""
        ### 📋 사용 예시
        
        **단일 키워드**: `무선키보드`
        
        **여러 키워드**: `무선키보드, 게이밍키보드, 기계식키보드`
        
        **비교 분석**: 여러 키워드를 입력하면 각각의 검색량을 비교할 수 있습니다.
        """)