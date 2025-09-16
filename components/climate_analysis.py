import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_climate_analysis(filtered_df, filter_config):
    """기후변화 대응 기술 분석 렌더링"""
    st.header("🌍 기후변화대응 기술 총괄 분석")
    
    # 모든 데이터 사용 (이미 기후변화대응으로 필터링된 데이터라고 가정)
    climate_df = filtered_df
    
    if climate_df.empty:
        st.warning("기후변화 관련 데이터가 없습니다.")
        return
    
    # NaN 및 문자열 'nan' 수행주체 제외
    climate_df = climate_df.dropna(subset=['institute'])
    climate_df = climate_df[climate_df['institute'] != 'nan']  # 문자열 "nan" 제거
    climate_df = climate_df[climate_df['institute'] != 'NaN']  # 문자열 "NaN" 제거
    climate_df = climate_df[climate_df['institute'] != 'None']  # 문자열 "None" 제거
    
    # 오션 스타일 색상 팔레트
    ocean_colors = ['#0077b6', '#00b4d8', '#90e0ef', '#48cae4', '#00a8e8', '#0096c7']
    
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
    
    # 감축/적응 직접 필터링
    if 'research_area' in climate_df.columns:
        # 감축, 적응 키워드가 있는 데이터만 필터링
        climate_df['category'] = climate_df['research_area'].apply(
            lambda x: '감축' if '감축' in x else ('적응' if '적응' in x else None)
        )
        climate_df = climate_df[climate_df['category'].notna()]  # 감축/적응 분류된 데이터만 유지
    
    if climate_df.empty:
        st.warning("감축/적응 관련 데이터가 없습니다.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. 연도별 기후변화 투자 추이 (바차트 + 연평균증가율 꺾은선)
        # 연도별 감축/적응별 투자액 집계
        yearly_category = climate_df.groupby(['year', 'category'])['budget_billion'].sum().reset_index()
        yearly_total = climate_df.groupby('year')['budget_billion'].sum().reset_index()
        
        # 연평균증가율 계산
        yearly_total = yearly_total.sort_values('year')
        yearly_total['growth_rate'] = 0.0
        
        for i in range(1, len(yearly_total)):
            prev_value = yearly_total.iloc[i-1]['budget_billion']
            curr_value = yearly_total.iloc[i]['budget_billion']
            if prev_value > 0:
                yearly_total.loc[yearly_total.index[i], 'growth_rate'] = (curr_value / prev_value - 1) * 100
        
        # 서브플롯 생성 (두 개의 y축)
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 감축/적응별 스택 바 추가
        colors = {'감축': ocean_colors[0], '적응': ocean_colors[1]}
        for category in sorted(yearly_category['category'].unique()):
            cat_data = yearly_category[yearly_category['category'] == category]
            cat_data = cat_data.sort_values('year')
            
            fig1.add_trace(
                go.Bar(
                    x=cat_data['year'],
                    y=cat_data['budget_billion'],
                    name=category,
                    text=[f"{int(val):,}억원" for val in cat_data['budget_billion'].round(0)],
                    textposition='inside',
                    textfont=dict(size=14, color='white'),
                    hovertemplate='%{y:,.1f}억원',
                    marker_color=colors.get(category, ocean_colors[2])
                ),
                secondary_y=False
            )
        
        # 연평균증가율 꺾은선 추가
        fig1.add_trace(
            go.Scatter(
                x=yearly_total['year'],
                y=yearly_total['growth_rate'],
                name='연평균증가율',
                mode='lines+markers+text',
                line=dict(color='#219ebc', width=3),  # 오션 스타일 색상
                marker=dict(size=10),
                text=yearly_total['growth_rate'].round(1).astype(str) + '%',
                textposition='top center',
                textfont=dict(size=14),
                hovertemplate='%{y:.1f}%'
            ),
            secondary_y=True
        )
        
        # Y축 범위 계산 (최대값의 약 120%로 설정)
        max_budget = yearly_total['budget_billion'].max()
        y_max = max_budget * 1.2
        
        # 축 설정
        fig1.update_layout(
            barmode='stack',
            height=500,
            margin=dict(t=80, b=50, l=50, r=50),
            title_text='연도별 투자 추이 및 증감율',
            title_x=0.5,
            title_y=0.95,
            **graph_config,
            xaxis=dict(
                title='연도',
                tickfont=dict(size=14),
                tickangle=0,
                dtick=1
            ),
            legend=dict(
                font=dict(size=14, color='#333333'),
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            )
        )
        
        # Y축 제목 설정 및 범위 조정
        fig1.update_yaxes(
            title_text="정부연구비 (억원)",
            title_font=dict(size=16),
            tickfont=dict(size=14),
            tickformat=",",  # 천단위 콤마
            range=[0, y_max],  # Y축 범위 설정
            secondary_y=False
        )
        fig1.update_yaxes(
            title_text="연평균증가율 (%)",
            title_font=dict(size=16),
            tickfont=dict(size=14),
            secondary_y=True
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 2. 부처별 감축/적응 투자 (그룹 바)
        ministry_category = climate_df.groupby(['ministry', 'category'])['budget_billion'].sum().reset_index()
        ministry_total = climate_df.groupby('ministry')['budget_billion'].sum().reset_index()
        ministry_total = ministry_total.sort_values('budget_billion', ascending=False)
        
        # 상위 10개 부처만 선택
        top_ministries = ministry_total.head(10)['ministry'].tolist()
        ministry_category = ministry_category[ministry_category['ministry'].isin(top_ministries)]
        
        # 부처별 감축/적응 그룹 바차트
        fig2 = px.bar(
            ministry_category,
            x='ministry',
            y='budget_billion',
            color='category',
            barmode='group',
            text='budget_billion',
            color_discrete_map={'감축': ocean_colors[0], '적응': ocean_colors[1]}
        )
        
        # 총액 텍스트 추가
        annotations = []
        for i, row in ministry_total.iterrows():
            if row['ministry'] in top_ministries:
                annotations.append(
                    dict(
                        x=row['ministry'],
                        y=row['budget_billion'],
                        text=f"<b>{int(row['budget_billion']):,}억원</b>",
                        font=dict(size=16),
                        showarrow=True,
                        arrowhead=0,
                        arrowcolor="black",
                        arrowsize=0.3,
                        arrowwidth=1,
                        ax=0,
                        ay=-40
                    )
                )
        
        # Y축 범위 계산 (최대값의 약 130%로 설정)
        max_budget = ministry_total['budget_billion'].max()
        y_max = max_budget * 1.3  # 총액 텍스트를 위해 더 여유있게
        
        fig2.update_traces(
            texttemplate='<b>%{text:,.0f}억원</b>',
            textposition='outside',
            textfont=dict(size=14, color='#333333')
        )
        
        fig2.update_layout(
            height=500,
            margin=dict(t=80, b=50, l=50, r=50),
            title_text='부처별 투자규모 현황',
            title_x=0.5,
            title_y=0.95,
            annotations=annotations,
            **graph_config,
            xaxis=dict(
                title='부처',
                tickfont=dict(size=14),
                tickangle=-30
            ),
            yaxis=dict(
                title='정부연구비 (억원)',
                title_font=dict(size=16),
                tickfont=dict(size=14),
                tickformat=",",  # 천단위 콤마
                range=[0, y_max]  # Y축 범위 설정
            ),
            legend=dict(
                font=dict(size=14, color='#333333'),
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            )
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 기후변화 관련 상세 분석
    col3, col4 = st.columns(2)
    
    with col3:
        # 3. 수행주체별 분포 (2개의 파이차트 - 감축/적응)
        # 두 개의 서브플롯 생성
        fig3 = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "pie"}]],
            subplot_titles=('[감축 기술 수행주체별 분포]', '[적응 기술 수행주체별 분포]')
        )
        
        # 감축 파이차트
        mitigation_df = climate_df[climate_df['category'] == '감축']
        if not mitigation_df.empty:
            mitigation_inst = mitigation_df.groupby('institute')['budget_billion'].sum().reset_index()
            fig3.add_trace(
                go.Pie(
                    labels=mitigation_inst['institute'],
                    values=mitigation_inst['budget_billion'],
                    textinfo='label+percent+value',
                    texttemplate='<b>%{label}</b><br>%{percent}<br><b>%{value:,.0f}억원</b>',
                    textfont=dict(size=12, color='#333333'),
                    hole=0.4,
                    marker=dict(
                        colors=ocean_colors
                    )
                ),
                row=1, col=1
            )
        
        # 적응 파이차트
        adaptation_df = climate_df[climate_df['category'] == '적응']
        if not adaptation_df.empty:
            adaptation_inst = adaptation_df.groupby('institute')['budget_billion'].sum().reset_index()
            fig3.add_trace(
                go.Pie(
                    labels=adaptation_inst['institute'],
                    values=adaptation_inst['budget_billion'],
                    textinfo='label+percent+value',
                    texttemplate='<b>%{label}</b><br>%{percent}<br><b>%{value:,.0f}억원</b>',
                    textfont=dict(size=12, color='#333333'),
                    hole=0.4,
                    marker=dict(
                        colors=[c for c in reversed(ocean_colors)]  # 반대 색상 사용
                    )
                ),
                row=1, col=2
            )
        
        fig3.update_layout(
            height=500,
            margin=dict(t=80, b=50, l=50, r=50),
            title_text='연구수행주체별 투자분포 현황',
            title_x=0.5,
            title_y=0.95,
            **graph_config
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # 연구단계별 분포 (감축/적응 분할)
        if 'project_type' in climate_df.columns:
            # 연구단계 x 감축/적응 교차 테이블
            type_category = climate_df.groupby(['project_type', 'category'])['budget_billion'].sum().reset_index()
            
            fig4 = px.bar(
                type_category, 
                x='project_type', 
                y='budget_billion',
                color='category',
                text='budget_billion',
                barmode='group',
                color_discrete_map={'감축': ocean_colors[0], '적응': ocean_colors[1]}
            )
            
            # Y축 범위 계산 (최대값의 약 120%로 설정)
            max_budget = type_category.groupby('project_type')['budget_billion'].sum().max()
            y_max = max_budget * 1.2
            
            fig4.update_traces(
                texttemplate='<b>%{text:,.0f}억원</b>',
                textposition='outside',
                textfont=dict(size=14, color='#333333')
            )
            
            fig4.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_text='연구단계별 투자 현황',
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
                    tickformat=",",  # 천단위 콤마
                    range=[0, y_max]  # Y축 범위 설정
                ),
                legend=dict(
                    font=dict(size=14, color='#333333'),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("연구단계 데이터가 없습니다.")