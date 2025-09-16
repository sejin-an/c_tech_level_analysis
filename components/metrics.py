import streamlit as st

def display_metrics(filtered_df):
    """주요 메트릭 표시"""
    col1, col2 = st.columns(2)

    with col1:
        total_budget = filtered_df['budget_billion'].sum() if 'budget_billion' in filtered_df.columns else 0
        st.metric("총 투자예산", f"{total_budget:,.0f}억원")

    with col2:
        if 'project_count' in filtered_df.columns:
            total_projects = filtered_df['project_count'].sum()
            st.metric("총 과제수", f"{total_projects:,}개")
        else:
            # 과제 ID가 있다면 유일한 ID 개수로 과제 수 추정
            if 'project_id' in filtered_df.columns:
                total_projects = filtered_df['project_id'].nunique()
                st.metric("총 과제수", f"{total_projects:,}개")
            else:
                # 아니면 레코드 수를 표시
                st.metric("총 레코드 수", f"{len(filtered_df):,}개")

    col3, col4 = st.columns(2)
    
    with col3:
        if 'success_rate' in filtered_df.columns and not filtered_df['success_rate'].isna().all():
            avg_success_rate = filtered_df['success_rate'].mean()
            st.metric("평균 성공률", f"{avg_success_rate:.1%}")
        elif 'performance_type' in filtered_df.columns:
            # 성과 유형 개수 표시
            perf_types = filtered_df['performance_type'].nunique()
            st.metric("성과 유형 수", f"{perf_types}개")
        else:
            st.metric("성과 데이터", "정보 없음")

    with col4:
        # 기후변화 관련 데이터 확인
        if 'research_area' in filtered_df.columns:
            climate_data = filtered_df[filtered_df['research_area'].str.contains('기후|환경|에너지', na=False, case=False)]
            if not climate_data.empty and 'budget_billion' in filtered_df.columns:
                climate_budget = climate_data['budget_billion'].sum()
                climate_ratio = (climate_budget / total_budget * 100) if total_budget > 0 else 0
                st.metric("기후변화 관련 비중", f"{climate_ratio:.1f}%")
            else:
                st.metric("기후변화 관련 비중", "0.0%")
        else:
            st.metric("기후변화 관련 비중", "데이터 없음")

def display_performance_metrics(filtered_df):
    """성과 메트릭 표시 (실제 데이터용)"""
    if 'performance_type' not in filtered_df.columns:
        return
    
    performance_types = filtered_df['performance_type'].unique()
    cols = st.columns(len(performance_types))
    
    for i, ptype in enumerate(performance_types):
        ptype_data = filtered_df[filtered_df['performance_type'] == ptype]
        
        with cols[i]:
            if ptype == '투자':
                value = ptype_data['performance_value'].sum()
                st.metric(f"{ptype} 총액", f"{value:,.0f}억원")
            elif ptype in ['사업화', '기술료']:
                value = ptype_data['performance_value'].sum()
                st.metric(f"{ptype} 총액", f"{value:,.0f}백만원")
            else:  # 논문, 특허
                if len(ptype_data) > 0:
                    value = ptype_data['performance_value'].mean()
                    st.metric(f"{ptype} 평균", f"{value:.1f}%")
                else:
                    st.metric(f"{ptype}", "데이터 없음")