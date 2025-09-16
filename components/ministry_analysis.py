import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

def render_ministry_analysis(filtered_df, filter_config):
    """부처별 분석 렌더링"""
    st.header("🔍 부처별 분석")
    
    # NaN 및 문자열 'nan' 부처 제외
    filtered_df = filtered_df.dropna(subset=['ministry'])
    filtered_df = filtered_df[filtered_df['ministry'] != 'nan']
    filtered_df = filtered_df[filtered_df['ministry'] != 'NaN']
    filtered_df = filtered_df[filtered_df['ministry'] != 'None']
    
    # 바다 테마 색상 팔레트
    ocean_colors = ['#0077b6', '#00b4d8', '#90e0ef', '#48cae4', '#00a8e8', '#0096c7', '#023e8a', '#0096c7', '#00b4d8', '#48cae4']
    
    # 공통 그래프 스타일 설정
    graph_config = {
        'font': {
            'family': 'Malgun Gothic, Arial, sans-serif',
            'size': 14,
            'color': '#333333'
        },
        'title': {
            'font': {
                'size': 18,
                'color': '#000000',
                'family': 'Malgun Gothic, Arial, sans-serif'
            }
        },
        'colorway': ocean_colors
    }
    
    # 부처 목록 - 문자열로 변환하여 정렬 오류 방지
    ministry_list = [str(m) for m in filtered_df['ministry'].unique()]
    ministry_list = sorted(ministry_list)
    
    # 연도 목록 - 오름차순 정렬
    year_list = sorted([int(y) for y in filtered_df['year'].unique()])
    
    col1, col2 = st.columns(2)

    with col1:
        # 부처별 투자 총액
        ministry_budget = filtered_df.groupby('ministry')['budget_billion'].sum().reset_index()
        ministry_budget = ministry_budget.sort_values('budget_billion', ascending=False)
        
        fig1 = px.bar(
            ministry_budget, 
            y='ministry', 
            x='budget_billion',
            title="부처별 R&D 투자 총액",
            color='budget_billion',
            orientation='h',
            color_continuous_scale='Blues',
            text='budget_billion'
        )
        
        fig1.update_traces(
            texttemplate='<b>%{text:,.0f}억원</b>',
            textposition='outside',
            textfont=dict(size=14, color='#333333')
        )
        
        fig1.update_layout(
            height=500,
            margin=dict(t=80, b=50, l=50, r=50),
            title_x=0.5,
            title_y=0.95,
            **graph_config,
            xaxis=dict(
                title='투자 총액 (억원)',
                title_font=dict(size=16),
                tickfont=dict(size=14),
                tickformat=","  # 천단위 콤마
            ),
            yaxis=dict(
                title='부처',
                title_font=dict(size=16),
                tickfont=dict(size=14)
            )
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # 부처별 투자 비중 (파이 차트)
        fig2 = px.pie(
            ministry_budget, 
            values='budget_billion', 
            names='ministry',
            title="부처별 R&D 투자 비중", 
            hole=0.4,
            color_discrete_sequence=ocean_colors
        )
        
        fig2.update_traces(
            textinfo='label+percent',
            textfont=dict(size=14),
            hovertemplate='<b>%{label}</b><br>%{value:,.0f}억원<br>%{percent}'
        )
        
        fig2.update_layout(
            height=500,
            margin=dict(t=80, b=50, l=50, r=50),
            title_x=0.5,
            title_y=0.95,
            **graph_config,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5
            )
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 부처별 연도별 추이
    if len(filtered_df['year'].unique()) > 1:
        st.subheader("📈 부처별 투자 추이")
        
        # 부처별 연도별 집계
        ministry_year = filtered_df.groupby(['ministry', 'year'])['budget_billion'].sum().reset_index()
        
        # 상위 8개 부처만 선택
        top_ministries = ministry_budget.nlargest(8, 'budget_billion')['ministry'].tolist()
        ministry_year_filtered = ministry_year[ministry_year['ministry'].isin(top_ministries)]
        
        # 추이 시각화 1: 시계열 차트
        fig3 = px.line(
            ministry_year_filtered, 
            x='year', 
            y='budget_billion', 
            color='ministry',
            title="부처별 연도별 투자 추이", 
            markers=True, 
            line_shape='spline'
        )
        
        fig3.update_traces(
            line=dict(width=3),
            marker=dict(size=10)
        )
        
        fig3.update_layout(
            height=500,
            margin=dict(t=80, b=50, l=50, r=50),
            title_x=0.5,
            title_y=0.95,
            **graph_config,
            xaxis=dict(
                title='연도',
                title_font=dict(size=16),
                tickfont=dict(size=14),
                tickmode='array',
                tickvals=year_list,
                ticktext=[str(y) for y in year_list]
            ),
            yaxis=dict(
                title='투자액 (억원)',
                title_font=dict(size=16),
                tickfont=dict(size=14),
                tickformat=","  # 천단위 콤마
            ),
            legend=dict(
                title='부처',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            )
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # 추이 시각화 2: 애니메이션 바 차트
        st.subheader("🎬 부처별 투자 애니메이션")
        
        # 연도를 문자열로 변환
        ministry_year['year'] = ministry_year['year'].astype(str)
        
        fig_anim = px.bar(
            ministry_year, 
            x='ministry', 
            y='budget_billion',
            color='ministry',
            animation_frame='year',
            title="연도별 부처 투자액 변화",
            category_orders={
                'ministry': ministry_list,
                'year': [str(y) for y in year_list]  # 연도 순서 지정
            }
        )
        
        fig_anim.update_traces(
            texttemplate='<b>%{y:,.0f}</b>',
            textposition='outside',
            textfont=dict(size=14, color='#333333')
        )
        
        fig_anim.update_layout(
            height=500,
            margin=dict(t=80, b=100, l=50, r=50),
            title_x=0.5,
            title_y=0.95,
            **graph_config,
            xaxis=dict(
                title='부처',
                title_font=dict(size=16),
                tickfont=dict(size=14),
                tickangle=-45
            ),
            yaxis=dict(
                title='투자액 (억원)',
                title_font=dict(size=16),
                tickfont=dict(size=14),
                tickformat=","  # 천단위 콤마
            ),
            showlegend=False
        )
        
        # 연도 슬라이더 스타일 수정
        fig_anim.layout.sliders[0].currentvalue = {"prefix": "연도: "}
        
        st.plotly_chart(fig_anim, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # 부처별 연구분야 분포 (애니메이션)
        if 'research_area' in filtered_df.columns and len(filtered_df['year'].unique()) > 1:
            ministry_area_year = filtered_df.groupby(['ministry', 'research_area', 'year'])['budget_billion'].sum().reset_index()
            
            # 상위 연구분야 식별
            top_areas = filtered_df.groupby('research_area')['budget_billion'].sum().nlargest(5).index.tolist()
            ministry_area_year = ministry_area_year[ministry_area_year['research_area'].isin(top_areas)]
            
            # 상위 부처 필터링
            top_ministries = ministry_budget.nlargest(6, 'budget_billion')['ministry'].tolist()
            ministry_area_year = ministry_area_year[ministry_area_year['ministry'].isin(top_ministries)]
            
            # 연도를 문자열로 변환
            ministry_area_year['year'] = ministry_area_year['year'].astype(str)
            
            fig4 = px.bar(
                ministry_area_year, 
                x='ministry', 
                y='budget_billion',
                color='research_area',
                animation_frame='year',
                title="부처별 연구분야 투자 분포",
                barmode='stack',
                category_orders={
                    'ministry': top_ministries,
                    'year': [str(y) for y in year_list]  # 연도 순서 지정
                }
            )
            
            fig4.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config,
                xaxis=dict(
                    title='부처',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickangle=-45
                ),
                yaxis=dict(
                    title='정부연구비 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickformat=","  # 천단위 콤마
                ),
                legend=dict(
                    title='연구분야',
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            
            # 연도 슬라이더 스타일 수정
            fig4.layout.sliders[0].currentvalue = {"prefix": "연도: "}
            
            st.plotly_chart(fig4, use_container_width=True)
        elif 'research_area' in filtered_df.columns:
            # 단일 연도인 경우
            ministry_area = filtered_df.groupby(['ministry', 'research_area'])['budget_billion'].sum().reset_index()
            
            # 상위 연구분야 식별
            top_areas = filtered_df.groupby('research_area')['budget_billion'].sum().nlargest(5).index.tolist()
            ministry_area = ministry_area[ministry_area['research_area'].isin(top_areas)]
            
            # 상위 부처 필터링
            top_ministries = ministry_budget.nlargest(6, 'budget_billion')['ministry'].tolist()
            ministry_area = ministry_area[ministry_area['ministry'].isin(top_ministries)]
            
            fig4 = px.bar(
                ministry_area, 
                x='ministry', 
                y='budget_billion',
                color='research_area',
                title="부처별 연구분야 투자 분포",
                barmode='stack'
            )
            
            fig4.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config,
                xaxis=dict(
                    title='부처',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickangle=-45
                ),
                yaxis=dict(
                    title='정부연구비 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickformat=","  # 천단위 콤마
                ),
                legend=dict(
                    title='연구분야',
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    with col4:
        # 부처별 연구수행주체 분포 (애니메이션)
        if len(filtered_df['year'].unique()) > 1:
            ministry_institute_year = filtered_df.groupby(['ministry', 'institute', 'year'])['budget_billion'].sum().reset_index()
            
            # 상위 부처 필터링
            top_ministries = ministry_budget.nlargest(6, 'budget_billion')['ministry'].tolist()
            ministry_institute_year = ministry_institute_year[ministry_institute_year['ministry'].isin(top_ministries)]
            
            # 연도를 문자열로 변환
            ministry_institute_year['year'] = ministry_institute_year['year'].astype(str)
            
            fig5 = px.bar(
                ministry_institute_year, 
                x='ministry', 
                y='budget_billion',
                color='institute',
                animation_frame='year',
                title="부처별 연구수행주체 분포",
                barmode='stack',
                category_orders={
                    'ministry': top_ministries,
                    'year': [str(y) for y in year_list]  # 연도 순서 지정
                }
            )
            
            fig5.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config,
                xaxis=dict(
                    title='부처',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickangle=-45
                ),
                yaxis=dict(
                    title='정부연구비 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickformat=","  # 천단위 콤마
                ),
                legend=dict(
                    title='연구수행주체',
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            
            # 연도 슬라이더 스타일 수정
            fig5.layout.sliders[0].currentvalue = {"prefix": "연도: "}
            
            st.plotly_chart(fig5, use_container_width=True)
        else:
            # 단일 연도인 경우
            ministry_institute = filtered_df.groupby(['ministry', 'institute'])['budget_billion'].sum().reset_index()
            
            # 상위 부처 필터링
            top_ministries = ministry_budget.nlargest(6, 'budget_billion')['ministry'].tolist()
            ministry_institute = ministry_institute[ministry_institute['ministry'].isin(top_ministries)]
            
            fig5 = px.bar(
                ministry_institute, 
                x='ministry', 
                y='budget_billion',
                color='institute',
                title="부처별 연구수행주체 분포",
                barmode='stack'
            )
            
            fig5.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config,
                xaxis=dict(
                    title='부처',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickangle=-45
                ),
                yaxis=dict(
                    title='정부연구비 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickformat=","  # 천단위 콤마
                ),
                legend=dict(
                    title='연구수행주체',
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            st.plotly_chart(fig5, use_container_width=True)
    
    # 부처별 연구단계 교차 분석
    if 'project_type' in filtered_df.columns:
        st.subheader("🔄 부처 × 연구단계 분석")
        
        col5, col6 = st.columns(2)
        
        with col5:
            # 연구단계별 부처 분포 (애니메이션)
            if len(filtered_df['year'].unique()) > 1:
                type_ministry_year = filtered_df.groupby(['project_type', 'ministry', 'year'])['budget_billion'].sum().reset_index()
                
                # 상위 부처 필터링
                top_ministries = ministry_budget.nlargest(6, 'budget_billion')['ministry'].tolist()
                type_ministry_year = type_ministry_year[type_ministry_year['ministry'].isin(top_ministries)]
                
                # 연도를 문자열로 변환
                type_ministry_year['year'] = type_ministry_year['year'].astype(str)
                
                fig6 = px.bar(
                    type_ministry_year, 
                    x='project_type', 
                    y='budget_billion',
                    color='ministry',
                    animation_frame='year',
                    title="연구단계별 부처 분포",
                    barmode='stack',
                    category_orders={
                        'ministry': top_ministries,
                        'year': [str(y) for y in year_list]  # 연도 순서 지정
                    }
                )
                
                fig6.update_layout(
                    height=500,
                    margin=dict(t=80, b=50, l=50, r=50),
                    title_x=0.5,
                    title_y=0.95,
                    **graph_config,
                    xaxis=dict(
                        title='연구단계',
                        title_font=dict(size=16),
                        tickfont=dict(size=14)
                    ),
                    yaxis=dict(
                        title='정부연구비 (억원)',
                        title_font=dict(size=16),
                        tickfont=dict(size=14),
                        tickformat=","  # 천단위 콤마
                    ),
                    legend=dict(
                        title='부처',
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='center',
                        x=0.5
                    )
                )
                
                # 연도 슬라이더 스타일 수정
                fig6.layout.sliders[0].currentvalue = {"prefix": "연도: "}
                
                st.plotly_chart(fig6, use_container_width=True)
            else:
                type_ministry = filtered_df.groupby(['project_type', 'ministry'])['budget_billion'].sum().reset_index()
                
                # 상위 부처 필터링
                top_ministries = ministry_budget.nlargest(6, 'budget_billion')['ministry'].tolist()
                type_ministry = type_ministry[type_ministry['ministry'].isin(top_ministries)]
                
                fig6 = px.bar(
                    type_ministry, 
                    x='project_type', 
                    y='budget_billion',
                    color='ministry',
                    title="연구단계별 부처 분포",
                    barmode='stack'
                )
                
                fig6.update_layout(
                    height=500,
                    margin=dict(t=80, b=50, l=50, r=50),
                    title_x=0.5,
                    title_y=0.95,
                    **graph_config,
                    xaxis=dict(
                        title='연구단계',
                        title_font=dict(size=16),
                        tickfont=dict(size=14)
                    ),
                    yaxis=dict(
                        title='정부연구비 (억원)',
                        title_font=dict(size=16),
                        tickfont=dict(size=14),
                        tickformat=","  # 천단위 콤마
                    ),
                    legend=dict(
                        title='부처',
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='center',
                        x=0.5
                    )
                )
                st.plotly_chart(fig6, use_container_width=True)
        
        with col6:
            # 히트맵: 부처 × 연구단계
            ministry_type = filtered_df.groupby(['ministry', 'project_type'])['budget_billion'].sum().reset_index()
            
            # 상위 부처 필터링
            top_ministries = ministry_budget.nlargest(8, 'budget_billion')['ministry'].tolist()
            ministry_type = ministry_type[ministry_type['ministry'].isin(top_ministries)]
            
            # 피벗 테이블 생성
            pivot_df = ministry_type.pivot(index='ministry', columns='project_type', values='budget_billion').fillna(0)
            
            # 히트맵 생성
            fig7 = px.imshow(
                pivot_df,
                labels=dict(x="연구단계", y="부처", color="투자예산 (억원)"),
                text_auto='.0f',
                aspect="auto",
                color_continuous_scale='Blues',
                title="부처 × 연구단계 히트맵"
            )
            
            fig7.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config
            )
            st.plotly_chart(fig7, use_container_width=True)