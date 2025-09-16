import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_performance_analysis(filtered_df, filter_config):
    """R&D 투자 성과 분석 렌더링"""
    st.header("📈 성과 분석")
    
    if 'performance_type' in filtered_df.columns:
        # 실제 데이터의 경우 성과 유형별 분석
        render_real_performance_analysis(filtered_df)
    else:
        # 샘플 데이터의 경우 기본 성과 분석
        render_basic_performance_analysis(filtered_df)

def render_real_performance_analysis(filtered_df):
    """실제 데이터 성과 분석"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 성과 유형별 건수
        performance_counts = filtered_df['performance_type'].value_counts().reset_index()
        performance_counts.columns = ['performance_type', 'count']
        
        fig1 = px.bar(performance_counts, x='performance_type', y='count',
                     title="성과 유형별 건수",
                     color='performance_type',
                     color_discrete_sequence=px.colors.qualitative.Set1)
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 연도별 성과 추이
        yearly_performance = filtered_df.groupby(['performance_year', 'performance_type']).size().reset_index(name='count')
        
        fig2 = px.line(yearly_performance, x='performance_year', y='count',
                      color='performance_type',
                      title="연도별 성과 발생 추이",
                      markers=True)
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # 부처별 성과 분석
    col3, col4 = st.columns(2)
    
    with col3:
        # 부처별 성과 현황
        ministry_performance = filtered_df.groupby(['ministry', 'performance_type']).agg({
            'performance_value': 'sum'
        }).reset_index()
        
        fig3 = px.bar(ministry_performance, x='ministry', y='performance_value',
                     color='performance_type',
                     title="부처별 성과 현황",
                     barmode='group')
        fig3.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # 연구수행주체별 성과
        institute_performance = filtered_df.groupby(['institute', 'performance_type']).size().reset_index(name='count')
        
        fig4 = px.bar(institute_performance, x='institute', y='count',
                     color='performance_type',
                     title="연구수행주체별 성과 건수",
                     barmode='stack')
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

def render_basic_performance_analysis(filtered_df):
    """기본 성과 분석 (샘플 데이터용)"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 연도별 성공률 추이
        if 'success_rate' in filtered_df.columns:
            yearly_success = filtered_df.groupby('year')['success_rate'].mean().reset_index()
            
            fig1 = px.line(yearly_success, x='year', y='success_rate',
                          title="연도별 평균 성공률 추이",
                          markers=True, line_shape='spline')
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 연구분야별 성공률
        if 'success_rate' in filtered_df.columns:
            area_success = filtered_df.groupby('research_area')['success_rate'].mean().reset_index()
            area_success = area_success.sort_values('success_rate', ascending=False)
            
            fig2 = px.bar(area_success, x='research_area', y='success_rate',
                         title="연구분야별 평균 성공률",
                         color='success_rate',
                         color_continuous_scale='Greens')
            fig2.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)
    
    # ROI 분석
    col3, col4 = st.columns(2)
    
    with col3:
        # 부처별 효율성
        ministry_efficiency = filtered_df.groupby('ministry').agg({
            'budget_billion': 'sum',
            'project_count': 'sum'
        }).reset_index()
        ministry_efficiency['efficiency'] = ministry_efficiency['project_count'] / ministry_efficiency['budget_billion']
        ministry_efficiency = ministry_efficiency.sort_values('efficiency', ascending=False)
        
        fig3 = px.bar(ministry_efficiency, x='ministry', y='efficiency',
                     title="부처별 투자 효율성 (과제수/예산)",
                     color='efficiency',
                     color_continuous_scale='Blues')
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # 연구수행주체별 성과
        institute_summary = filtered_df.groupby('institute').agg({
            'budget_billion': 'sum',
            'project_count': 'sum',
            'success_rate': 'mean' if 'success_rate' in filtered_df.columns else lambda x: 0
        }).reset_index()
        
        fig4 = px.scatter(institute_summary, x='budget_billion', y='project_count',
                         size='success_rate' if 'success_rate' in filtered_df.columns else 'budget_billion',
                         color='institute',
                         title="연구수행주체별 투자 vs 성과",
                         hover_data=['success_rate'] if 'success_rate' in filtered_df.columns else [])
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)