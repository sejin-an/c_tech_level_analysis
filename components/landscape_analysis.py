import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_landscape_analysis(filtered_df, filter_config):
    """R&D 투자 Landscape 분석 렌더링 - 사이드바 설정 기반"""
    st.header("🌐 R&D 투자 Landscape 분석")
    st.markdown("### 다차원 투자 패턴 분석")

    selected_years = filter_config['selected_years']
    is_multi_year = len(selected_years) > 1
    
    # 사이드바에서 선택된 기술분야 수준 가져오기
    tech_levels = filter_config.get('tech_levels', ['대분류'])
    
    if not tech_levels:
        st.warning("사이드바에서 기술 분야 수준을 선택해주세요.")
        return
    
    # 기술 분야 수준별 컬럼 매핑
    tech_column_mapping = {
        "대분류": "research_area",
        "중분류": "research_area_medium", 
        "소분류": "research_area_small"
    }
    
    # 모든 분석 차원 정의
    all_dimensions = ["기술분야 × 수행주체", "기술분야 × 연구단계", "부처 × 연구단계"]
    
    # 모든 시각화 방식 정의
    all_viz_methods = ["Heatmap", "Bubble Plot", "3D Surface", "Animation"]
    
    analysis_count = 1
    
    # 모든 분석 차원에 대해 처리
    for dimension in all_dimensions:
        # 기술분야 관련 차원인 경우 선택된 각 수준별로 분석
        if dimension.startswith("기술분야"):
            for tech_level in tech_levels:
                tech_col = tech_column_mapping[tech_level]
                
                # 데이터 존재 확인
                if tech_col not in filtered_df.columns or filtered_df[tech_col].isna().all():
                    st.info(f"{tech_level} 데이터가 없어서 {dimension} 분석을 건너뜁니다.")
                    continue
                
                if "수행주체" in dimension:
                    y_col = "institute"
                    full_dimension = f"기술분야({tech_level}) × 수행주체"
                else:  # 연구단계
                    if 'project_type' not in filtered_df.columns:
                        st.info(f"연구단계 데이터가 없어서 {dimension} 분석을 건너뜁니다.")
                        continue
                    y_col = "project_type"
                    full_dimension = f"기술분야({tech_level}) × 연구단계"
                
                st.subheader(f"{analysis_count}. {full_dimension}")
                _render_dimension_analysis(filtered_df, tech_col, y_col, full_dimension, all_viz_methods, is_multi_year)
                analysis_count += 1
        
        # 부처 × 연구단계
        elif dimension == "부처 × 연구단계":
            if 'project_type' in filtered_df.columns:
                st.subheader(f"{analysis_count}. 부처 × 연구단계")
                _render_dimension_analysis(filtered_df, "ministry", "project_type", "부처 × 연구단계", all_viz_methods, is_multi_year)
                analysis_count += 1
            else:
                st.info("연구단계 데이터가 없어서 부처 × 연구단계 분석을 건너뜁니다.")

def _render_dimension_analysis(filtered_df, x_col, y_col, dimension_name, viz_methods, is_multi_year):
    """특정 차원에 대한 모든 시각화 분석 - 2x2 격자 배치"""
    
    # 데이터 확인
    if x_col not in filtered_df.columns or y_col not in filtered_df.columns:
        st.warning(f"{dimension_name} 분석을 위한 데이터가 없습니다.")
        return
    
    # 결측값 제거
    analysis_df = filtered_df.dropna(subset=[x_col, y_col])
    if len(analysis_df) == 0:
        st.warning(f"{dimension_name} 분석을 위한 유효한 데이터가 없습니다.")
        return
    
    # 2x2 격자로 배치
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Heatmap")
        _render_heatmap(analysis_df, x_col, y_col, dimension_name)
        
        st.subheader("🎯 3D Surface")
        _render_3d_surface(analysis_df, x_col, y_col, dimension_name)
    
    with col2:
        st.subheader("🫧 Bubble Plot")
        _render_bubble_plot(analysis_df, x_col, y_col, dimension_name)
        
        st.subheader("🎬 Animation")
        if is_multi_year:
            _render_animation(analysis_df, x_col, y_col, dimension_name)
        else:
            st.info("애니메이션을 보려면 사이드바에서 여러 연도를 선택해주세요.")

def _render_heatmap(df, x_col, y_col, title):
    """히트맵 렌더링"""
    # budget_billion이 있으면 사용, 없으면 카운트
    if 'budget_billion' in df.columns:
        pivot_df = pd.pivot_table(df, values='budget_billion', index=y_col, columns=x_col, aggfunc='sum', fill_value=0)
        value_label = "투자예산 (억원)"
    else:
        # 카운트로 피벗 테이블 생성
        pivot_df = pd.pivot_table(df, values=df.columns[0], index=y_col, columns=x_col, aggfunc='count', fill_value=0)
        value_label = "건수"
    
    if pivot_df.empty:
        st.warning("히트맵을 위한 데이터가 없습니다.")
        return
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x=x_col, y=y_col, color=value_label),
        text_auto='.0f',
        aspect="auto",
        color_continuous_scale='Viridis',
        title=f"{title} - 히트맵"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def _render_bubble_plot(df, x_col, y_col, title):
    """버블 플롯 렌더링 - project_count 없을 때도 작동"""
    # 필요한 컬럼 확인 및 대체 로직
    agg_dict = {}
    
    if 'budget_billion' in df.columns:
        agg_dict['budget_billion'] = 'sum'
    
    # project_count가 없으면 count로 대체
    count_col = 'count'
    if 'project_count' in df.columns:
        agg_dict['project_count'] = 'sum'
        count_col = 'project_count'
    else:
        # 카운트 컬럼 추가
        df['count'] = 1
        agg_dict['count'] = 'sum'
    
    # 데이터 집계
    if agg_dict:
        grouped_data = df.groupby([x_col, y_col]).agg(agg_dict).reset_index()
    else:
        # 기본 집계
        grouped_data = df.groupby([x_col, y_col]).size().reset_index(name='count')
        count_col = 'count'
    
    if len(grouped_data) == 0:
        st.warning("버블 플롯을 위한 데이터가 없습니다.")
        return
    
    # 사이즈 컬럼 결정
    size_col = 'budget_billion' if 'budget_billion' in grouped_data.columns else count_col
    
    fig = px.scatter(
        grouped_data,
        x=x_col,
        y=y_col,
        size=size_col,
        color=size_col,
        hover_data={col: True for col in grouped_data.columns},
        size_max=60,
        color_continuous_scale='Viridis',
        title=f"{title} - 버블 플롯"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def _render_3d_surface(df, x_col, y_col, title):
    """3D Surface 렌더링"""
    # budget_billion이 있으면 사용, 없으면 카운트
    if 'budget_billion' in df.columns:
        pivot_df = pd.pivot_table(df, values='budget_billion', index=y_col, columns=x_col, aggfunc='sum', fill_value=0)
        z_label = "투자예산 (억원)"
    else:
        # 카운트로 피벗 테이블 생성
        pivot_df = pd.pivot_table(df, values=df.columns[0], index=y_col, columns=x_col, aggfunc='count', fill_value=0)
        z_label = "건수"
    
    if pivot_df.empty:
        st.warning("3D Surface를 위한 데이터가 없습니다.")
        return
    
    fig = go.Figure(data=[
        go.Surface(
            z=pivot_df.values,
            x=pivot_df.columns.tolist(),
            y=pivot_df.index.tolist(),
            colorscale='Viridis',
            opacity=0.8
        )
    ])
    
    fig.update_layout(
        title=f"{title} - 3D Surface",
        scene=dict(
            xaxis_title=x_col,
            yaxis_title=y_col,
            zaxis_title=z_label,
            xaxis=dict(tickangle=-45),
            yaxis=dict(tickangle=-45)
        ),
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

def _render_animation(df, x_col, y_col, title):
    """애니메이션 렌더링"""
    # 값 컬럼 선택
    value_col = 'budget_billion' if 'budget_billion' in df.columns else 'performance_value'
    if value_col not in df.columns:
        # 어떤 값 컬럼도 없으면 카운트 사용
        df['count'] = 1
        value_col = 'count'
        
    animation_df = df.groupby([x_col, y_col, 'year'])[value_col].sum().reset_index()
    
    if len(animation_df) == 0:
        st.warning("애니메이션을 위한 데이터가 없습니다.")
        return
    
    fig = px.scatter(
        animation_df,
        x=x_col,
        y=y_col,
        size=value_col,
        color=value_col,
        animation_frame='year',
        title=f"{title} - 연도별 변화",
        size_max=60,
        color_continuous_scale='Viridis',
        range_color=[0, animation_df[value_col].max()]
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)