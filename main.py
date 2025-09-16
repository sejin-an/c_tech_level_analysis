import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import subprocess

# 디버깅용 - plotly 설치 상태 확인
try:
    import plotly
    st.success(f"Plotly version: {plotly.__version__}")
except ImportError as e:
    st.error(f"Plotly import error: {e}")
    
    # 강제 설치 시도
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    st.info("Plotly installed, please refresh the page")
    st.stop()

import plotly.express as px

# pandas 호환성 수정
if not hasattr(pd.DataFrame, 'iteritems'):
    pd.DataFrame.iteritems = pd.DataFrame.items
if not hasattr(pd.Series, 'iteritems'):
    pd.Series.iteritems = pd.Series.items

# 로컬 모듈 import
from config import setup_page_config, setup_font
from data_generator import generate_sample_data
from components.sidebar import create_sidebar
from components.climate_analysis import render_climate_analysis
from components.institution_analysis import render_institution_analysis
from components.ministry_analysis import render_ministry_analysis
from components.performance_analysis import render_performance_analysis
from components.landscape_analysis import render_landscape_analysis
from components.region_analysis import render_region_analysis  # 지역 분석 모듈 추가
from components.data_table import render_data_table
from utils.data_filters import filter_dataframe

# 직접 성과 데이터 로드 함수
@st.cache_data
def load_performance_data():
    """성과 데이터 직접 로드"""
    data_path = os.path.join("data", "performance_output.pkl")
    
    if os.path.exists(data_path):
        try:
            df = pd.read_pickle(data_path)
            return df
        except Exception as e:
            st.error(f"데이터 로드 실패: {e}")
            return None
    else:
        st.warning(f"파일을 찾을 수 없습니다: {data_path}")
        return None

def render_performance_overview(filtered_df):
    """성과 개요 분석 - 성과 유형별 분리 버전"""
    st.subheader("🎯 R&D 성과 개요")
    
    # 공통 그래프 스타일 설정
    graph_config = {
        'font': {
            'family': 'Malgun Gothic, Arial, sans-serif',
            'size': 14,  # 기본 폰트 크기 증가
            'color': '#333333'  # 어두운 색상으로 변경
        },
        'title': {
            'font': {
                'size': 18,  # 제목 폰트 크기 증가
                'color': '#000000',  # 제목 색상 진하게
                'family': 'Malgun Gothic, Arial, sans-serif'
            }
        },
        'legend': {
            'font': {
                'size': 14,
                'color': '#333333'
            }
        },
        'colorway': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']  # 더 진한 색상표
    }
    
    # 성과 유형 구분
    monetary_types = ['사업화', '기술료', '투자']  # 금액 단위 성과
    count_types = ['논문', '특허']  # 건수 단위 성과

    # 성과 유형별 필터링
    monetary_df = filtered_df[filtered_df['performance_type'].isin(monetary_types)]
    count_df = filtered_df[filtered_df['performance_type'].isin(count_types)]

    # 성과 분석 시각화 - 금액 단위 성과
    if not monetary_df.empty:
        st.subheader("💰 금액 단위 성과 분석")
        col1, col2 = st.columns(2)
        
        with col1:
            # 연도별 금액 성과 추이
            yearly_monetary = monetary_df.groupby(['performance_year', 'performance_type'])['performance_value'].sum().reset_index()
            
            fig1 = px.line(
                yearly_monetary, 
                x='performance_year', 
                y='performance_value', 
                color='performance_type', 
                title="연도별 금액 성과 추이",
                markers=True,
                labels={
                    'performance_year': '연도', 
                    'performance_value': '성과값', 
                    'performance_type': '성과유형'
                }
            )
            
            # 선 및 마커 스타일 개선
            fig1.update_traces(
                line=dict(width=3),  # 선 굵기 증가
                marker=dict(size=10),  # 마커 크기 증가
                textfont=dict(size=14)  # 텍스트 크기 증가
            )
            
            fig1.update_layout(
                height=500, 
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                legend_title_text='성과유형',
                **graph_config,  # 공통 스타일 적용
                xaxis=dict(
                    tickfont=dict(size=14),
                    tickangle=0,
                    dtick=1  # 매년 표시
                ),
                yaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16))
                )
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 부처별 금액 성과 현황
            ministry_monetary = monetary_df.groupby(['ministry', 'performance_type'])['performance_value'].sum().reset_index()
            
            fig2 = px.bar(
                ministry_monetary, 
                x='ministry', 
                y='performance_value',
                color='performance_type', 
                title="부처별 금액 성과 현황",
                barmode='group',
                labels={
                    'ministry': '부처', 
                    'performance_value': '성과값', 
                    'performance_type': '성과유형'
                },
                text_auto='.1f'  # 자동 텍스트 표시
            )
            
            # 텍스트 포맷 개선
            fig2.update_traces(
                texttemplate='<b>%{text}</b>',  # 굵은 글씨
                textposition='outside',
                textfont=dict(size=14)  # 텍스트 크기 증가
            )
            
            fig2.update_layout(
                height=500, 
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                xaxis_tickangle=-30,  # 각도 조정
                legend_title_text='성과유형',
                **graph_config,  # 공통 스타일 적용
                xaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16))
                ),
                yaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16))
                )
            )
            st.plotly_chart(fig2, use_container_width=True)

    # 성과 분석 시각화 - 건수 단위 성과
    if not count_df.empty:
        st.subheader("📊 건수 단위 성과 분석")
        col3, col4 = st.columns(2)
        
        with col3:
            # 연도별 건수 성과 추이
            yearly_count = count_df.groupby(['performance_year', 'performance_type']).size().reset_index(name='count')
            
            fig3 = px.line(
                yearly_count, 
                x='performance_year', 
                y='count', 
                color='performance_type', 
                title="연도별 건수 성과 추이",
                markers=True,
                labels={
                    'performance_year': '연도', 
                    'count': '건수', 
                    'performance_type': '성과유형'
                },
                text='count'  # 텍스트 표시
            )
            
            # 선 및 마커 스타일 개선
            fig3.update_traces(
                line=dict(width=3),  # 선 굵기 증가
                marker=dict(size=10),  # 마커 크기 증가
                texttemplate='<b>%{text}</b>',  # 굵은 글씨
                textposition='top center',
                textfont=dict(size=14)  # 텍스트 크기 증가
            )
            
            fig3.update_layout(
                height=500, 
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                legend_title_text='성과유형',
                **graph_config,  # 공통 스타일 적용
                xaxis=dict(
                    tickfont=dict(size=14),
                    tickangle=0,
                    dtick=1  # 매년 표시
                ),
                yaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16))
                )
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            # 부처별 건수 성과 현황
            ministry_count = count_df.groupby(['ministry', 'performance_type']).size().reset_index(name='count')
            
            fig4 = px.bar(
                ministry_count, 
                x='ministry', 
                y='count',
                color='performance_type', 
                title="부처별 건수 성과 현황",
                barmode='group',
                labels={
                    'ministry': '부처', 
                    'count': '건수', 
                    'performance_type': '성과유형'
                },
                text='count'  # 텍스트 표시
            )
            
            # 텍스트 포맷 개선
            fig4.update_traces(
                texttemplate='<b>%{text}</b>',  # 굵은 글씨
                textposition='outside',
                textfont=dict(size=14)  # 텍스트 크기 증가
            )
            
            fig4.update_layout(
                height=500, 
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                xaxis_tickangle=-30,  # 각도 조정
                legend_title_text='성과유형',
                **graph_config,  # 공통 스타일 적용
                xaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16))
                ),
                yaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16))
                )
            )
            st.plotly_chart(fig4, use_container_width=True)

    # 추가 분석: 성과 유형별 기여도 분석
    st.subheader("🔍 성과 분포 분석")
    col5, col6 = st.columns(2)

    with col5:
        # 연구수행주체별 성과 비교 - 스택 바 차트
        if not monetary_df.empty:
            institute_monetary = monetary_df.groupby(['institute', 'performance_type'])['performance_value'].sum().reset_index()
            
            fig5 = px.bar(
                institute_monetary, 
                x='institute', 
                y='performance_value',
                color='performance_type', 
                title="연구수행주체별 금액 성과 비교",
                barmode='stack',
                labels={
                    'institute': '연구수행주체', 
                    'performance_value': '성과값', 
                    'performance_type': '성과유형'
                },
                text_auto='.1f'  # 자동 텍스트 표시
            )
            
            # 텍스트 포맷 개선
            fig5.update_traces(
                texttemplate='<b>%{text}</b>',  # 굵은 글씨
                textposition='inside',  # 스택 바는 내부에 텍스트
                textfont=dict(size=14, color='white')  # 텍스트 크기 및 색상 조정
            )
            
            fig5.update_layout(
                height=500, 
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                legend_title_text='성과유형',
                **graph_config,  # 공통 스타일 적용
                xaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16)),
                    tickangle=-30  # 각도 조정
                ),
                yaxis=dict(
                    tickfont=dict(size=14),
                    title=dict(font=dict(size=16))
                )
            )
            st.plotly_chart(fig5, use_container_width=True)

    with col6:
        # 연구분야별 성과 분포 - 파이 차트
        if 'performance_type' in filtered_df.columns:
            performance_types = filtered_df['performance_type'].unique()
            if len(performance_types) > 0:
                selected_type = st.selectbox(
                    "성과유형 선택", 
                    options=performance_types,
                    format_func=lambda x: f"{x} 유형 성과 분포"
                )
                
                type_data = filtered_df[filtered_df['performance_type'] == selected_type]
                area_performance = type_data.groupby('research_area')['performance_value'].sum().reset_index()
                
                fig6 = px.pie(
                    area_performance, 
                    values='performance_value', 
                    names='research_area',
                    title=f"{selected_type} 유형의 연구분야별 분포",
                    hole=0.4,
                    labels={
                        'research_area': '연구분야', 
                        'performance_value': '성과값' if selected_type in monetary_types else '건수'
                    }
                )
                
                # 텍스트 포맷 개선
                fig6.update_traces(
                    textinfo='label+percent+value',
                    texttemplate='<b>%{label}</b><br>%{percent}<br><b>%{value:.1f}</b>',
                    textfont=dict(size=14, color='#333333')  # 텍스트 크기 증가
                )
                
                fig6.update_layout(
                    height=500, 
                    margin=dict(t=80, b=50, l=50, r=50),
                    title_x=0.5,
                    title_y=0.95,
                    **graph_config  # 공통 스타일 적용
                )
                st.plotly_chart(fig6, use_container_width=True)
                                
def main():
    setup_page_config()
    setup_font()
    
    # 간소화된 헤더
    st.markdown("<h1 style='text-align: center;'>국가연구개발사업 투자분석 대시보드</h1>", unsafe_allow_html=True)
    
    # 데이터 로드
    with st.spinner("데이터를 로드 중..."):
        df = load_performance_data()
    
    if df is None:
        st.error("성과 데이터를 로드할 수 없습니다. 샘플 데이터를 사용합니다.")
        df = generate_sample_data()
    
    # 사이드바 생성 및 필터 값 받기
    filter_config = create_sidebar(df)
    
    # 성과 유형 필터 추가
    if 'performance_type' in df.columns:
        performance_types = sorted(df['performance_type'].unique())
        selected_performance_types = st.sidebar.multiselect(
            "성과 유형 선택",
            options=performance_types,
            default=performance_types
        )
        filter_config['selected_performance_types'] = selected_performance_types
    
    # 데이터 필터링
    filtered_df = filter_dataframe(df, filter_config)
    
    # 성과 유형 필터링
    if 'performance_type' in filtered_df.columns and 'selected_performance_types' in filter_config:
        filtered_df = filtered_df[filtered_df['performance_type'].isin(filter_config['selected_performance_types'])]
    
    if len(filtered_df) == 0:
        st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")
        return
    
    # 탭 구성으로 변경
    tab_titles = ["🌍 총괄 분석", "🏢 연구수행주체별 분석", "🔍 부처별 분석", "🗺️ 지역별 분석", "📈 성과 분석", "🌐 분포현황 분석", "📋 데이터 테이블"]
    tabs = st.tabs(tab_titles)
    
    # 각 탭에 해당하는 분석 내용 렌더링
    with tabs[0]:
        render_climate_analysis(filtered_df, filter_config)
    
    with tabs[1]:
        render_institution_analysis(filtered_df, filter_config)
    
    with tabs[2]:
        render_ministry_analysis(filtered_df, filter_config)
    
    with tabs[3]:
        render_region_analysis(filtered_df, filter_config)  # 지역 분석 렌더링
    
    with tabs[4]:
        # 실제 데이터의 경우 성과 개요 먼저 표시
        if 'performance_type' in filtered_df.columns:
            render_performance_overview(filtered_df)
            st.markdown("---")
        render_performance_analysis(filtered_df, filter_config)
    
    with tabs[5]:
        render_landscape_analysis(filtered_df, filter_config)
    
    with tabs[6]:
        render_data_table(filtered_df)

if __name__ == "__main__":
    main()