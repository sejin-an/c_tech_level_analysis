import pandas as pd
import streamlit as st
import os
import glob

def find_pkl_files():
    data_folder = "data"
    if not os.path.exists(data_folder):
        return []
    pkl_files = glob.glob(os.path.join(data_folder, "*.pkl"))
    return [os.path.basename(f) for f in pkl_files]

def load_pkl_from_data_folder(filename):
    filepath = os.path.join("data", filename)
    try:
        df = pd.read_pickle(filepath)
        return df
    except Exception as e:
        st.error(f"파일 로드 실패 ({filename}): {e}")
        return None

def process_investment_performance_data(df):
    """투자성과 데이터 처리"""
    processed_data = []
    
    for _, row in df.iterrows():
        record_type = row['유형']
        
        if record_type == '투자':
            processed_data.append({
                'year': row['과제수행년도'],
                'ministry': row.get('사업_부처명', ''),
                'research_area': row.get('대분류', '기타'),
                'research_area_medium': row.get('중분류', ''),
                'research_area_small': row.get('소분류', ''),
                'project_type': row.get('연구개발단계', '기타'),
                'institute': row.get('연구수행주체', '기타'),
                'budget_billion': float(row.get('정부연구비(억원)', 0)),
                'project_count': 1,
                'performance_type': '투자',
                'performance_value': float(row.get('정부연구비(억원)', 0)),
                'performance_year': row['과제수행년도'],
                'project_id': row.get('과제고유번호', ''),
                'project_name': row.get('과제명', '')
            })
        
        elif record_type in ['논문', '특허']:
            processed_data.append({
                'year': row['과제수행년도'],
                'ministry': row.get('사업_부처명', ''),
                'research_area': row.get('대분류', '기타'),
                'research_area_medium': row.get('중분류', ''),
                'research_area_small': row.get('소분류', ''),
                'project_type': row.get('연구개발단계', '기타'),
                'institute': row.get('연구수행주체', '기타'),
                'budget_billion': 0,
                'project_count': 1,
                'performance_type': record_type,
                'performance_value': float(row.get('기여율(%)', 0)),
                'performance_year': row['성과발생년도'],
                'project_id': row.get('과제고유번호', ''),
                'project_name': row.get('과제명', '')
            })
    
    return pd.DataFrame(processed_data)

def process_commercialization_data(df):
    """사업화 데이터 처리"""
    processed_data = []
    
    for _, row in df.iterrows():
        processed_data.append({
            'year': row['과제수행년도'],
            'ministry': row.get('성과발생부처', ''),
            'research_area': row.get('분류명', '기타'),
            'research_area_medium': '',
            'research_area_small': '',
            'project_type': row.get('연구개발단계', '기타'),
            'institute': row.get('연구수행주체', '기타'),
            'budget_billion': 0,
            'project_count': 1,
            'performance_type': '사업화',
            'performance_value': float(row.get('당해년도매출액(백만원)', 0)),
            'performance_year': row['성과발생년도'],
            'project_id': row.get('과제고유번호', ''),
            'project_name': row.get('과제명-국문', ''),
            'company_name': row.get('업체명', ''),
            'employment': row.get('고용창출인원수(명)', 0)
        })
    
    return pd.DataFrame(processed_data)

def process_technology_fee_data(df):
    """기술료 데이터 처리"""
    processed_data = []
    
    for _, row in df.iterrows():
        processed_data.append({
            'year': row['과제수행년도'],
            'ministry': row.get('성과발생부처', ''),
            'research_area': row.get('분류명', '기타'),
            'research_area_medium': '',
            'research_area_small': '',
            'project_type': row.get('연구개발단계', '기타'),
            'institute': row.get('연구수행주체', '기타'),
            'budget_billion': 0,
            'project_count': 1,
            'performance_type': '기술료',
            'performance_value': float(row.get('당해연도 기술료(백만원)', 0)),
            'performance_year': row['성과발생년도'],
            'project_id': row.get('과제고유번호', ''),
            'project_name': row.get('과제명-국문', ''),
            'contract_name': row.get('기술실시계약명', '')
        })
    
    return pd.DataFrame(processed_data)

def clean_and_standardize_data(df):
    """데이터 정리 및 표준화"""
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(2020).astype(int)
    df['performance_year'] = pd.to_numeric(df['performance_year'], errors='coerce').fillna(2020).astype(int)
    
    # 이상값 제거
    df = df[df['year'] >= 2015]
    df = df[df['year'] <= 2025]
    df = df[df['performance_value'] >= 0]
    
    return df

def combine_all_data(investment_df, commercialization_df, tech_fee_df):
    """모든 데이터 통합"""
    all_dfs = []
    
    if investment_df is not None:
        processed_inv = process_investment_performance_data(investment_df)
        all_dfs.append(processed_inv)
    
    if commercialization_df is not None:
        processed_com = process_commercialization_data(commercialization_df)
        all_dfs.append(processed_com)
    
    if tech_fee_df is not None:
        processed_tech = process_technology_fee_data(tech_fee_df)
        all_dfs.append(processed_tech)
    
    if not all_dfs:
        return None
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    return clean_and_standardize_data(combined_df)

def display_data_summary(df, filename=None):
    """데이터 요약 정보 표시"""
    if filename:
        st.success(f"데이터 로드 완료: {filename}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 레코드", f"{len(df):,}개")
    with col2:
        st.metric("연도 범위", f"{df['year'].min()}~{df['year'].max()}")
    with col3:
        st.metric("부처 수", f"{df['ministry'].nunique()}개")
    with col4:
        if 'performance_type' in df.columns:
            st.metric("성과 유형", f"{df['performance_type'].nunique()}개")
        else:
            st.metric("연구분야 수", f"{df['research_area'].nunique()}개")
    
    # 성과 유형별 분포
    if 'performance_type' in df.columns:
        st.subheader("성과 유형별 분포")
        type_counts = df['performance_type'].value_counts()
        col1, col2 = st.columns(2)
        with col1:
            for ptype, count in type_counts.items():
                st.write(f"- **{ptype}**: {count:,}건")
        with col2:
            if len(type_counts) > 0:
                import plotly.express as px
                fig = px.pie(values=type_counts.values, names=type_counts.index, title="성과 유형 분포")
                st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def load_real_data_from_folder(filenames):
    """실제 데이터 파일들 로드"""
    investment_df = None
    commercialization_df = None
    tech_fee_df = None
    
    for filename in filenames:
        df = load_pkl_from_data_folder(filename)
        if df is None:
            continue
            
        # 파일명이나 컬럼으로 데이터 유형 판단
        if '투자성과' in filename or '유형' in df.columns:
            investment_df = df
        elif '사업화' in filename or '사업화명' in df.columns:
            commercialization_df = df
        elif '기술료' in filename or '기술료실시계약명' in df.columns:
            tech_fee_df = df
    
    return combine_all_data(investment_df, commercialization_df, tech_fee_df)