import streamlit as st
import pandas as pd
from datetime import datetime

def render_data_table(filtered_df):
    """상세 투자 데이터 테이블 렌더링"""
    st.subheader("📋 상세 투자 데이터")
    
    # Raw 데이터 표시
    display_df = filtered_df.copy()
    display_df = display_df.sort_values(['year', 'budget_billion'], ascending=[False, False])
    
    # 컬럼명 한글화
    column_mapping = {
        'year': '연도',
        'ministry': '부처', 
        'research_area': '연구분야(대)',
        'research_area_medium': '연구분야(중)',
        'research_area_small': '연구분야(소)',
        'project_type': '연구단계',
        'institute': '수행주체',
        'budget_billion': '투자예산(억원)',
        'project_count': '과제수',
        'performance_type': '성과유형',
        'performance_value': '성과값',
        'performance_year': '성과발생년도',
        'project_id': '과제번호',
        'project_name': '과제명'
    }
    
    # 존재하는 컬럼만 매핑
    existing_columns = {k: v for k, v in column_mapping.items() if k in display_df.columns}
    display_df = display_df.rename(columns=existing_columns)
    
    # 성공률이 있으면 퍼센트로 표시
    if 'success_rate' in filtered_df.columns:
        display_df = display_df.rename(columns={'success_rate': '성공률'})
        display_df['성공률'] = (display_df['성공률'] * 100).round(1)
    
    # 검색 기능
    search_term = st.text_input("데이터 검색 (부처, 연구분야, 연구단계 등)", "")
    
    if search_term:
        search_mask = display_df.astype(str).apply(
            lambda row: row.str.contains(search_term, case=False, na=False).any(), axis=1
        )
        filtered_display_df = display_df[search_mask]
        st.dataframe(filtered_display_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 요약 정보
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("표시된 레코드", f"{len(display_df):,}개")
    with col2:
        st.metric("총 투자예산", f"{display_df.get('투자예산(억원)', pd.Series([0])).sum():,.0f}억원")
    with col3:
        st.metric("총 과제수", f"{display_df.get('과제수', pd.Series([0])).sum():,}개")
    
    # 다운로드 기능
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df(display_df)
    
    st.download_button(
        label="📥 데이터 CSV 다운로드",
        data=csv,
        file_name=f'국가연구개발투자분석_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )