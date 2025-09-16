import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

def render_institution_analysis(filtered_df, filter_config):
    """연구수행주체별 분석 렌더링"""
    st.header("🏢 주체별 분석")
    
    # NaN 및 문자열 'nan' 수행주체 제외
    filtered_df = filtered_df.dropna(subset=['institute'])
    filtered_df = filtered_df[filtered_df['institute'] != 'nan']  # 문자열 "nan" 제거
    filtered_df = filtered_df[filtered_df['institute'] != 'NaN']  # 문자열 "NaN" 제거
    filtered_df = filtered_df[filtered_df['institute'] != 'None']  # 문자열 "None" 제거
    
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
    
    col1, col2 = st.columns(2)

    with col1:
        # 1. 연구수행주체별 투자 총액 및 과제수 (산점도 추이 트래킹)
        # 투자 총액 계산
        institute_budget = filtered_df.groupby(['institute', 'year'])['budget_billion'].sum().reset_index()
        
        # 과제수 계산
        if 'project_count' in filtered_df.columns:
            institute_projects = filtered_df.groupby(['institute', 'year'])['project_count'].sum().reset_index()
        elif 'project_id' in filtered_df.columns:
            institute_projects = filtered_df.groupby(['institute', 'year'])['project_id'].nunique().reset_index()
            institute_projects.rename(columns={'project_id': 'project_count'}, inplace=True)
        else:
            institute_projects = filtered_df.groupby(['institute', 'year']).size().reset_index(name='project_count')
        
        # 데이터 병합
        institute_combined = pd.merge(institute_budget, institute_projects, on=['institute', 'year'])
        
        # 상위 5개 연구수행주체만 선택
        top_institutes = filtered_df.groupby('institute')['budget_billion'].sum().nlargest(5).index.tolist()
        institute_combined = institute_combined[institute_combined['institute'].isin(top_institutes)]
        
        # 산점도 추이 트래킹 그래프 (주체별 경로 추적)
        fig1 = px.line(
            institute_combined,
            x='budget_billion',
            y='project_count',
            color='institute',
            markers=True,
            line_dash='institute',
            hover_name='institute',
            hover_data=['year', 'budget_billion', 'project_count'],
            labels={
                'budget_billion': '투자 총액 (억원)',
                'project_count': '과제수',
                'institute': '연구수행주체',
                'year': '연도'
            },
            title="연구수행주체별 투자 총액 및 과제수 추이"
        )
        
        # 각 주체별 첫 연도와 마지막 연도 강조
        for institute in top_institutes:
            inst_data = institute_combined[institute_combined['institute'] == institute].sort_values('year')
            
            if len(inst_data) > 0:
                # 첫 연도 (시작점)
                first_year = inst_data.iloc[0]
                # 마지막 연도 (종료점)
                last_year = inst_data.iloc[-1]
                
                # 시작점 추가 (큰 마커와 연도 텍스트)
                fig1.add_trace(go.Scatter(
                    x=[first_year['budget_billion']],
                    y=[first_year['project_count']],
                    mode='markers+text',
                    marker=dict(size=12, color=fig1.data[top_institutes.index(institute)].line.color),
                    text=[str(first_year['year'])],
                    textposition="top center",
                    showlegend=False,
                    hovertemplate=f"{institute} ({first_year['year']})<br>투자 총액: {first_year['budget_billion']:,.0f}억원<br>과제수: {first_year['project_count']:,}<extra></extra>"
                ))
                
                # 종료점 추가 (큰 마커와 연도 텍스트)
                fig1.add_trace(go.Scatter(
                    x=[last_year['budget_billion']],
                    y=[last_year['project_count']],
                    mode='markers+text',
                    marker=dict(size=12, color=fig1.data[top_institutes.index(institute)].line.color),
                    text=[str(last_year['year'])],
                    textposition="top center",
                    showlegend=False,
                    hovertemplate=f"{institute} ({last_year['year']})<br>투자 총액: {last_year['budget_billion']:,.0f}억원<br>과제수: {last_year['project_count']:,}<extra></extra>"
                ))
                
                # 화살표 추가 (마지막 데이터 포인트에)
                if len(inst_data) > 1:
                    # 마지막 두 지점 사이의 방향 계산
                    second_last = inst_data.iloc[-2]
                    dx = last_year['budget_billion'] - second_last['budget_billion']
                    dy = last_year['project_count'] - second_last['project_count']
                    
                    # 방향 벡터 정규화 및 스케일링
                    magnitude = (dx**2 + dy**2)**0.5
                    if magnitude > 0:  # 0으로 나누기 방지
                        dx = dx / magnitude * 5  # 화살표 길이 스케일 조정
                        dy = dy / magnitude * 5
                        
                        fig1.add_annotation(
                            x=last_year['budget_billion'],
                            y=last_year['project_count'],
                            ax=last_year['budget_billion'] + dx,
                            ay=last_year['project_count'] + dy,
                            xref="x", yref="y",
                            axref="x", ayref="y",
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            arrowcolor=fig1.data[top_institutes.index(institute)].line.color
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
                title='과제수',
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
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # 2. 연구수행주체별 과제당 평균 예산 (시계열 애니메이션)
        if 'budget_billion' in filtered_df.columns:
            # 연도별 과제당 평균 예산 계산
            if 'project_count' in filtered_df.columns:
                institute_yearly_avg = filtered_df.groupby(['institute', 'year']).agg({
                    'budget_billion': 'sum',
                    'project_count': 'sum'
                }).reset_index()
                institute_yearly_avg['avg_budget_per_project'] = institute_yearly_avg['budget_billion'] / institute_yearly_avg['project_count']
            elif 'project_id' in filtered_df.columns:
                institute_yearly_avg = filtered_df.groupby(['institute', 'year']).agg({
                    'budget_billion': 'sum',
                    'project_id': pd.Series.nunique
                }).reset_index()
                institute_yearly_avg['avg_budget_per_project'] = institute_yearly_avg['budget_billion'] / institute_yearly_avg['project_id']
                institute_yearly_avg.rename(columns={'project_id': 'project_count'}, inplace=True)
            else:
                institute_yearly_counts = filtered_df.groupby(['institute', 'year']).size().reset_index(name='project_count')
                institute_yearly_budget = filtered_df.groupby(['institute', 'year'])['budget_billion'].sum().reset_index()
                institute_yearly_avg = pd.merge(institute_yearly_budget, institute_yearly_counts, on=['institute', 'year'])
                institute_yearly_avg['avg_budget_per_project'] = institute_yearly_avg['budget_billion'] / institute_yearly_avg['project_count']
            
            # 상위 연구수행주체만 선택
            institute_yearly_avg = institute_yearly_avg[institute_yearly_avg['institute'].isin(top_institutes)]
            
            # 애니메이션 바 차트
            fig2 = px.bar(
                institute_yearly_avg,
                x='institute',
                y='avg_budget_per_project',
                color='institute',
                animation_frame='year',
                animation_group='institute',
                range_y=[0, institute_yearly_avg['avg_budget_per_project'].max() * 1.2],
                title="연구수행주체별 과제당 평균 예산 (연도별)",
                text='avg_budget_per_project'
            )
            
            fig2.update_traces(
                texttemplate='<b>%{text:.1f}억원</b>',
                textposition='outside',
                textfont=dict(size=14, color='#333333')
            )
            
            fig2.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config,
                xaxis=dict(
                    title='연구수행주체',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickangle=-30
                ),
                yaxis=dict(
                    title='과제당 평균 예산 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14)
                )
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # 3. 연구수행주체별 연구단계 분포 (시계열 애니메이션)
        if 'project_type' in filtered_df.columns:
            # 연구수행주체 x 연구단계 x 연도 교차 테이블
            institute_type_year = filtered_df.groupby(['institute', 'project_type', 'year'])['budget_billion'].sum().reset_index()
            
            # 상위 연구수행주체만 선택
            institute_type_year = institute_type_year[institute_type_year['institute'].isin(top_institutes)]
            
            # 애니메이션 그래프
            fig3 = px.bar(
                institute_type_year, 
                x='institute', 
                y='budget_billion',
                color='project_type',
                animation_frame='year',
                animation_group='institute',
                barmode='stack',
                title="연구수행주체별 연구단계 분포 (연도별)",
                text='budget_billion'
            )
            
            fig3.update_traces(
                texttemplate='<b>%{text:,.0f}</b>',
                textposition='inside',
                textfont=dict(size=12, color='white')
            )
            
            fig3.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config,
                xaxis=dict(
                    title='연구수행주체',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickangle=-30
                ),
                yaxis=dict(
                    title='정부연구비 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickformat=","  # 천단위 콤마
                ),
                legend=dict(
                    font=dict(size=14, color='#333333'),
                    title='연구단계',
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("연구단계 데이터가 없습니다.")
    
    with col4:
        # 4. 지역별 분석 (region 컬럼이 있는 경우)
        if 'region' in filtered_df.columns:
            # 지역별 투자 분석
            region_budget = filtered_df.groupby('region')['budget_billion'].sum().reset_index()
            region_budget = region_budget.sort_values('budget_billion', ascending=False)
            
            fig4 = px.bar(
                region_budget,
                x='region',
                y='budget_billion',
                color='region',
                title="지역별 R&D 투자 분포",
                text='budget_billion'
            )
            
            fig4.update_traces(
                texttemplate='<b>%{text:,.0f}억원</b>',
                textposition='outside',
                textfont=dict(size=14, color='#333333')
            )
            
            fig4.update_layout(
                height=500,
                margin=dict(t=80, b=50, l=50, r=50),
                title_x=0.5,
                title_y=0.95,
                **graph_config,
                xaxis=dict(
                    title='지역',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickangle=-30
                ),
                yaxis=dict(
                    title='정부연구비 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    tickformat=","  # 천단위 콤마
                )
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            # 지역 정보가 없는 경우, 국가별 정보를 확인 (cross-country 분석 가능성)
            if 'country' in filtered_df.columns:
                country_budget = filtered_df.groupby('country')['budget_billion'].sum().reset_index()
                country_budget = country_budget.sort_values('budget_billion', ascending=False)
                
                fig4 = px.bar(
                    country_budget,
                    x='country',
                    y='budget_billion',
                    color='country',
                    title="국가별 R&D 투자 분포",
                    text='budget_billion'
                )
                
                fig4.update_traces(
                    texttemplate='<b>%{text:,.0f}억원</b>',
                    textposition='outside',
                    textfont=dict(size=14, color='#333333')
                )
                
                fig4.update_layout(
                    height=500,
                    margin=dict(t=80, b=50, l=50, r=50),
                    title_x=0.5,
                    title_y=0.95,
                    **graph_config,
                    xaxis=dict(
                        title='국가',
                        title_font=dict(size=16),
                        tickfont=dict(size=14),
                        tickangle=-30
                    ),
                    yaxis=dict(
                        title='정부연구비 (억원)',
                        title_font=dict(size=16),
                        tickfont=dict(size=14),
                        tickformat=","  # 천단위 콤마
                    )
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                # institute의 첫 두 글자로 지역 임시 추정 (예: 서울대, 부산대 등)
                filtered_df['estimated_region'] = filtered_df['institute'].str[:2]
                region_map = {
                    '서울': '서울', '부산': '부산', '대구': '대구', '인천': '인천', '광주': '광주',
                    '대전': '대전', '울산': '울산', '세종': '세종', '경기': '경기', '강원': '강원',
                    '충북': '충북', '충남': '충남', '전북': '전북', '전남': '전남', '경북': '경북',
                    '경남': '경남', '제주': '제주'
                }
                
                # 알려진 지역 접두사만 매핑
                filtered_df['estimated_region'] = filtered_df['estimated_region'].map(
                    lambda x: region_map.get(x, '기타')
                )
                
                region_est_budget = filtered_df.groupby('estimated_region')['budget_billion'].sum().reset_index()
                region_est_budget = region_est_budget.sort_values('budget_billion', ascending=False)
                
                # '기타'가 너무 큰 경우 제외
                if '기타' in region_est_budget['estimated_region'].values:
                    other_ratio = region_est_budget[region_est_budget['estimated_region'] == '기타']['budget_billion'].values[0] / region_est_budget['budget_billion'].sum()
                    if other_ratio < 0.5:  # 기타가 전체의 50% 미만인 경우만 표시
                        fig4 = px.bar(
                            region_est_budget,
                            x='estimated_region',
                            y='budget_billion',
                            color='estimated_region',
                            title="추정 지역별 R&D 투자 분포 (주의: 기관명 첫 두 글자 기준)",
                            text='budget_billion'
                        )
                        
                        fig4.update_traces(
                            texttemplate='<b>%{text:,.0f}억원</b>',
                            textposition='outside',
                            textfont=dict(size=14, color='#333333')
                        )
                        
                        fig4.update_layout(
                            height=500,
                            margin=dict(t=80, b=50, l=50, r=50),
                            title_x=0.5,
                            title_y=0.95,
                            **graph_config,
                            xaxis=dict(
                                title='추정 지역',
                                title_font=dict(size=16),
                                tickfont=dict(size=14),
                                tickangle=-30
                            ),
                            yaxis=dict(
                                title='정부연구비 (억원)',
                                title_font=dict(size=16),
                                tickfont=dict(size=14),
                                tickformat=","  # 천단위 콤마
                            )
                        )
                        st.plotly_chart(fig4, use_container_width=True)
                    else:
                        st.info("지역 정보를 추정할 수 없습니다. 지역 분석을 위해서는 'region' 또는 'country' 컬럼이 필요합니다.")
                else:
                    st.info("지역 정보를 추정할 수 없습니다. 지역 분석을 위해서는 'region' 또는 'country' 컬럼이 필요합니다.")