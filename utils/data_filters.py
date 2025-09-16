import pandas as pd

def filter_dataframe(df, filter_config):
    """필터 설정에 따라 데이터프레임 필터링"""
    filtered_df = df.copy()
    
    # 연도 필터
    if 'selected_years' in filter_config and filter_config['selected_years']:
        # 연도 컬럼 선택 (투자년도 또는 성과발생년도)
        year_col = filter_config.get('year_column', 'year')
        if year_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[year_col].isin(filter_config['selected_years'])]
    
    # 부처 필터
    if 'selected_ministries' in filter_config and filter_config['selected_ministries']:
        filtered_df = filtered_df[filtered_df['ministry'].isin(filter_config['selected_ministries'])]
    
    # 연구분야 필터
    if 'selected_areas' in filter_config and filter_config['selected_areas']:
        filtered_df = filtered_df[filtered_df['research_area'].isin(filter_config['selected_areas'])]
    
    # 연구분야(중분류) 필터
    if 'selected_medium' in filter_config and filter_config['selected_medium'] and 'research_area_medium' in filtered_df.columns:
        # 중분류가 선택되었고, 중분류 컬럼이 있는 경우에만 필터링
        filtered_df = filtered_df[filtered_df['research_area_medium'].isin(filter_config['selected_medium'])]
    
    # 연구분야(소분류) 필터
    if 'selected_small' in filter_config and filter_config['selected_small'] and 'research_area_small' in filtered_df.columns:
        # 소분류가 선택되었고, 소분류 컬럼이 있는 경우에만 필터링
        filtered_df = filtered_df[filtered_df['research_area_small'].isin(filter_config['selected_small'])]
    
    # 수행주체 필터
    if 'selected_institutes' in filter_config and filter_config['selected_institutes']:
        filtered_df = filtered_df[filtered_df['institute'].isin(filter_config['selected_institutes'])]
    
    return filtered_df