import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_region_analysis(filtered_df, filter_config):
    """지역별 투자분포 분석 렌더링"""
    st.header("🗺️ 지역별 투자분포 분석")
    
    # NaN 및 문자열 'nan' 수행주체 제외
    filtered_df = filtered_df.dropna(subset=['institute'])
    filtered_df = filtered_df[filtered_df['institute'] != 'nan']
    filtered_df = filtered_df[filtered_df['institute'] != 'NaN']
    filtered_df = filtered_df[filtered_df['institute'] != 'None']
    
    # 오션 스타일 색상 팔레트
    ocean_colors = ['#0077b6', '#00b4d8', '#90e0ef', '#48cae4', '#00a8e8', '#0096c7']
    
    # 그래프 스타일 설정
    graph_config = {
        'font': {'family': 'Malgun Gothic, Arial, sans-serif', 'size': 14, 'color': '#333333'},
        'title': {'font': {'size': 18, 'color': '#000000', 'family': 'Malgun Gothic, Arial, sans-serif'}},
        'colorway': ocean_colors
    }
    
    # 지역 정보 확인 및 준비
    has_region_data = 'region' in filtered_df.columns
    has_country_data = 'country' in filtered_df.columns
    
    if not has_region_data and not has_country_data:
        # 지역 데이터가 없는 경우 institute의 첫 두 글자로 지역 추정
        filtered_df['estimated_region'] = filtered_df['institute'].str[:2]
        region_map = {
            '서울': '서울', '부산': '부산', '대구': '대구', '인천': '인천', '광주': '광주',
            '대전': '대전', '울산': '울산', '세종': '세종', '경기': '경기', '강원': '강원',
            '충북': '충북', '충남': '충남', '전북': '전북', '전남': '전남', '경북': '경북',
            '경남': '경남', '제주': '제주'
        }
        filtered_df['estimated_region'] = filtered_df['estimated_region'].map(
            lambda x: region_map.get(x, '기타')
        )
        region_col = 'estimated_region'
        region_title = "추정 지역별"
        region_note = "(주의: 기관명 첫 두 글자 기준)"
    elif has_region_data:
        region_col = 'region'
        region_title = "지역별"
        region_note = ""
    else:
        region_col = 'country'
        region_title = "국가별"
        region_note = ""
    
    # 연구수행주체별 지역 정보 집계
    if 'budget_billion' in filtered_df.columns:
        # 지역별 투자 총액
        region_budget = filtered_df.groupby(region_col)['budget_billion'].sum().reset_index()
        region_budget = region_budget.sort_values('budget_billion', ascending=False)
        
        # 지역별 과제수 (프로젝트 카운트 컬럼이 없을 경우 1로 계산)
        if 'project_count' in filtered_df.columns:
            region_projects = filtered_df.groupby(region_col)['project_count'].sum().reset_index()
        elif 'project_id' in filtered_df.columns and filtered_df['project_id'].nunique() > 1:
            region_projects = filtered_df.groupby(region_col)['project_id'].nunique().reset_index()
            region_projects.rename(columns={'project_id': 'project_count'}, inplace=True)
        else:
            # 각 행을 별도 프로젝트로 간주
            filtered_df['temp_project_count'] = 1
            region_projects = filtered_df.groupby(region_col)['temp_project_count'].sum().reset_index()
            region_projects.rename(columns={'temp_project_count': 'project_count'}, inplace=True)
        
        # 지역별 수행주체 수
        region_institutes = filtered_df.groupby(region_col)['institute'].nunique().reset_index()
        region_institutes.rename(columns={'institute': 'institute_count'}, inplace=True)
        
        # 데이터 병합
        region_data = pd.merge(region_budget, region_projects, on=region_col)
        region_data = pd.merge(region_data, region_institutes, on=region_col)
        
        # '기타'가 너무 많은 경우 필터링 (추정 지역인 경우만)
        if region_col == 'estimated_region' and '기타' in region_data[region_col].values:
            other_ratio = region_data[region_data[region_col] == '기타']['budget_billion'].values[0] / region_data['budget_billion'].sum()
            if other_ratio > 0.5:  # 기타가 전체의 50% 이상인 경우
                st.warning("추정 지역 데이터의 신뢰도가 낮습니다. 'region' 컬럼을 추가하는 것을 권장합니다.")
    else:
        st.warning("투자 예산 데이터가 없습니다.")
        return
    
    # 지역 목록 - 문자열로 변환하여 정렬 오류 방지
    region_list = [str(r) for r in filtered_df[region_col].unique()]
    region_list = sorted(region_list)
    
    # 연도 목록 - 오름차순 정렬
    year_list = sorted([int(y) for y in filtered_df['year'].unique()])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 연도별 지역 데이터 집계 (산점도 트래킹용)
        if len(filtered_df['year'].unique()) > 1:
            # 프로젝트 카운트 컬럼이 없는 경우 임시 컬럼 생성
            if 'project_count' not in filtered_df.columns:
                filtered_df['temp_project_count'] = 1
                project_count_col = 'temp_project_count'
            else:
                project_count_col = 'project_count'
            
            # 지역별 연도별 집계
            region_year_data = filtered_df.groupby([region_col, 'year']).agg({
                'budget_billion': 'sum',
                project_count_col: 'sum'
            }).reset_index()
            
            # 컬럼명 변경
            if project_count_col == 'temp_project_count':
                region_year_data.rename(columns={'temp_project_count': 'project_count'}, inplace=True)
            
            # 상위 지역만 선택
            top_regions = region_data.nlargest(6, 'budget_billion')[region_col].tolist()
            region_year_data_filtered = region_year_data[region_year_data[region_col].isin(top_regions)]
            
            # 산점도 트래킹 그래프 (지역별 경로 추적)
            fig1 = px.line(
                region_year_data_filtered,
                x='budget_billion',
                y='project_count',
                color=region_col,
                markers=True,
                line_dash=region_col,
                hover_name=region_col,
                hover_data=['year', 'budget_billion', 'project_count'],
                labels={
                    'budget_billion': '투자 총액 (억원)',
                    'project_count': '과제수',
                    region_col: '지역',
                    'year': '연도'
                },
                title=f"{region_title} 투자 패턴 추이 {region_note}"
            )
            
            # 각 지역별 첫 연도와 마지막 연도 강조
            for region in top_regions:
                region_data_filtered = region_year_data_filtered[region_year_data_filtered[region_col] == region].sort_values('year')
                
                if len(region_data_filtered) > 0:
                    # 첫 연도 (시작점)
                    first_year = region_data_filtered.iloc[0]
                    # 마지막 연도 (종료점)
                    last_year = region_data_filtered.iloc[-1]
                    
                    # 시작점 추가 (큰 마커와 연도 텍스트)
                    fig1.add_trace(go.Scatter(
                        x=[first_year['budget_billion']],
                        y=[first_year['project_count']],
                        mode='markers+text',
                        marker=dict(size=12, color=fig1.data[top_regions.index(region)].line.color),
                        text=[str(first_year['year'])],
                        textposition="top center",
                        showlegend=False,
                        hovertemplate=f"{region} ({first_year['year']})<br>투자 총액: {first_year['budget_billion']:,.0f}억원<br>과제수: {first_year['project_count']:,}<extra></extra>"
                    ))
                    
                    # 종료점 추가 (큰 마커와 연도 텍스트)
                    fig1.add_trace(go.Scatter(
                        x=[last_year['budget_billion']],
                        y=[last_year['project_count']],
                        mode='markers+text',
                        marker=dict(size=12, color=fig1.data[top_regions.index(region)].line.color),
                        text=[str(last_year['year'])],
                        textposition="top center",
                        showlegend=False,
                        hovertemplate=f"{region} ({last_year['year']})<br>투자 총액: {last_year['budget_billion']:,.0f}억원<br>과제수: {last_year['project_count']:,}<extra></extra>"
                    ))
                    
                    # 화살표 추가 (마지막 데이터 포인트에)
                    if len(region_data_filtered) > 1:
                        # 마지막 두 지점 사이의 방향 계산
                        second_last = region_data_filtered.iloc[-2]
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
                                arrowcolor=fig1.data[top_regions.index(region)].line.color
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
                    title='지역',
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            # 단일 연도인 경우 버블 차트
            fig1 = px.scatter(
                region_data,
                x='budget_billion',
                y='project_count',
                size='institute_count',
                color=region_col,
                hover_name=region_col,
                text=region_col,
                title=f"{region_title} R&D 투자 버블 분석 {region_note}",
                labels={
                    'budget_billion': '투자 총액 (억원)',
                    'project_count': '과제수',
                    'institute_count': '수행주체 수',
                    region_col: '지역'
                },
                size_max=60
            )
            
            fig1.update_traces(
                textposition='top center',
                textfont=dict(size=12, color='#333333')
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
                )
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 지역별 연구분야 분포 - 애니메이션
        if 'research_area' in filtered_df.columns and len(filtered_df['year'].unique()) > 1:
            region_area_year = filtered_df.groupby([region_col, 'research_area', 'year'])['budget_billion'].sum().reset_index()
            
            # 상위 연구분야 식별
            top_areas = filtered_df.groupby('research_area')['budget_billion'].sum().nlargest(5).index.tolist()
            region_area_year = region_area_year[region_area_year['research_area'].isin(top_areas)]
            
            # 연도를 문자열로 변환
            region_area_year['year'] = region_area_year['year'].astype(str)
            
            fig2 = px.bar(
                region_area_year,
                x=region_col,
                y='budget_billion',
                color='research_area',
                animation_frame='year',
                title=f"{region_title} 연구분야 분포 {region_note}",
                barmode='stack',
                category_orders={
                    region_col: region_list,
                    'year': [str(y) for y in year_list]  # 연도 순서 지정
                }
            )
            
            fig2.update_layout(
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
            fig2.layout.sliders[0].currentvalue = {"prefix": "연도: "}
            
            st.plotly_chart(fig2, use_container_width=True)
        elif 'research_area' in filtered_df.columns:
            # 단일 연도 데이터
            region_area = filtered_df.groupby([region_col, 'research_area'])['budget_billion'].sum().reset_index()
            
            # 상위 연구분야 식별
            top_areas = filtered_df.groupby('research_area')['budget_billion'].sum().nlargest(5).index.tolist()
            region_area = region_area[region_area['research_area'].isin(top_areas)]
            
            fig2 = px.bar(
                region_area,
                x=region_col,
                y='budget_billion',
                color='research_area',
                title=f"{region_title} 연구분야 분포 {region_note}",
                barmode='stack',
                category_orders={region_col: region_list}
            )
            
            fig2.update_layout(
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
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("연구분야 데이터가 없습니다.")
    
    # 지역별 수행주체 분석
    st.subheader(f"{region_title} 주요 연구수행주체 분석 {region_note}")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # 지역별 수행주체 분포 - 애니메이션 (지역 기준)
        if len(filtered_df['year'].unique()) > 1:
            # 각 지역별로 상위 수행주체 선택
            # 각 지역별로 투자액 상위 5개 수행주체 선택
            top_institutes_by_region = {}
            for region in filtered_df[region_col].unique():
                region_data_filtered = filtered_df[filtered_df[region_col] == region]
                top_institutes = region_data_filtered.groupby('institute')['budget_billion'].sum().nlargest(5).index.tolist()
                top_institutes_by_region[region] = top_institutes
            
            # 모든 상위 수행주체 목록 생성
            all_top_institutes = []
            for institutes in top_institutes_by_region.values():
                all_top_institutes.extend(institutes)
            all_top_institutes = list(set(all_top_institutes))
            
            # 연도별 지역-수행주체 데이터 생성
            region_institute_year_data = []
            for year in filtered_df['year'].unique():
                year_data = filtered_df[filtered_df['year'] == year]
                
                for region in filtered_df[region_col].unique():
                    if region in top_institutes_by_region:
                        region_institutes = top_institutes_by_region[region]
                        
                        for institute in region_institutes:
                            budget = year_data[(year_data[region_col] == region) & (year_data['institute'] == institute)]['budget_billion'].sum()
                            if budget > 0:  # 투자액이 있는 경우만 추가
                                region_institute_year_data.append({
                                    'year': year,
                                    region_col: region,
                                    'institute': institute,
                                    'budget_billion': budget
                                })
            
            if region_institute_year_data:
                region_institute_year_df = pd.DataFrame(region_institute_year_data)
                
                # 연도를 문자열로 변환
                region_institute_year_df['year'] = region_institute_year_df['year'].astype(str)
                
                fig3 = px.bar(
                    region_institute_year_df,
                    x=region_col,
                    y='budget_billion',
                    color='institute',
                    animation_frame='year',
                    title=f"{region_title} 주요 수행주체 분포 {region_note}",
                    barmode='stack',
                    category_orders={
                        region_col: region_list,
                        'year': [str(y) for y in year_list]  # 연도 순서 지정
                    }
                )
                
                fig3.update_layout(
                    height=500,
                    margin=dict(t=80, b=100, l=50, r=50),
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
                fig3.layout.sliders[0].currentvalue = {"prefix": "연도: "}
                
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("지역별 주요 수행주체 데이터가 없습니다.")
        else:
            # 단일 연도 데이터 - 지역별 상위 수행주체
            # 각 지역별로 투자액 상위 5개 수행주체 선택
            region_institute_data = []
            
            for region in filtered_df[region_col].unique():
                region_data_filtered = filtered_df[filtered_df[region_col] == region]
                top_institutes = region_data_filtered.groupby('institute')['budget_billion'].sum().nlargest(5)
                
                for institute, budget in top_institutes.items():
                    region_institute_data.append({
                        region_col: region,
                        'institute': institute,
                        'budget_billion': budget
                    })
            
            if region_institute_data:
                region_institute_df = pd.DataFrame(region_institute_data)
                
                fig3 = px.bar(
                    region_institute_df,
                    x=region_col,
                    y='budget_billion',
                    color='institute',
                    title=f"{region_title} 주요 수행주체 분포 {region_note}",
                    barmode='stack',
                    category_orders={region_col: region_list}
                )
                
                fig3.update_layout(
                    height=500,
                    margin=dict(t=80, b=100, l=50, r=50),
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
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("지역별 주요 수행주체 데이터가 없습니다.")
    
    with col4:
        # 연구단계별 지역 분포 - 애니메이션
        if 'project_type' in filtered_df.columns and len(filtered_df['year'].unique()) > 1:
            region_type_year = filtered_df.groupby([region_col, 'project_type', 'year'])['budget_billion'].sum().reset_index()
            
            # 연도를 문자열로 변환
            region_type_year['year'] = region_type_year['year'].astype(str)
            
            fig4 = px.bar(
                region_type_year,
                x=region_col,
                y='budget_billion',
                color='project_type',
                animation_frame='year',
                title=f"{region_title} 연구단계 분포 {region_note}",
                barmode='stack',
                category_orders={
                    region_col: region_list,
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
                ),
                legend=dict(
                    title='연구단계',
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
        elif 'project_type' in filtered_df.columns:
            # 단일 연도 데이터
            region_type = filtered_df.groupby([region_col, 'project_type'])['budget_billion'].sum().reset_index()
            
            fig4 = px.bar(
                region_type,
                x=region_col,
                y='budget_billion',
                color='project_type',
                title=f"{region_title} 연구단계 분포 {region_note}",
                barmode='stack',
                category_orders={region_col: region_list}
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
                ),
                legend=dict(
                    title='연구단계',
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            # 지역별 과제당 평균 예산
            region_avg = region_data.copy()
            region_avg['avg_budget_per_project'] = region_avg['budget_billion'] / region_avg['project_count']
            region_avg = region_avg.sort_values('avg_budget_per_project', ascending=False)
            
            fig4 = px.bar(
                region_avg,
                x=region_col,
                y='avg_budget_per_project',
                color=region_col,
                title=f"{region_title} 과제당 평균 예산 {region_note}",
                text='avg_budget_per_project',
                category_orders={region_col: region_list}
            )
            
            fig4.update_traces(
                texttemplate='<b>%{text:.1f}억원</b>',
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
                    title='과제당 평균 예산 (억원)',
                    title_font=dict(size=16),
                    tickfont=dict(size=14)
                )
            )
            st.plotly_chart(fig4, use_container_width=True)