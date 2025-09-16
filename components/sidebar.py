import streamlit as st

def create_sidebar(df):
    """사이드바 생성 및 필터 설정 반환"""
    st.sidebar.header("📋 필터 옵션")
    
    # 데이터 타입 변환 - 문자열로 통일
    if 'institute' in df.columns:
        df['institute'] = df['institute'].astype(str)
    if 'ministry' in df.columns:
        df['ministry'] = df['ministry'].astype(str)
    if 'research_area' in df.columns:
        df['research_area'] = df['research_area'].astype(str)
    if 'research_area_medium' in df.columns:
        df['research_area_medium'] = df['research_area_medium'].astype(str)
    if 'research_area_small' in df.columns:
        df['research_area_small'] = df['research_area_small'].astype(str)
    
    # 필터 설정 저장할 딕셔너리
    filter_config = {}
    
    # 연도 필터
    with st.sidebar.expander("📅 연도 (투자년도)", expanded=True):
        year_col = 'year'
        # 2018년 이후 데이터만 표시
        year_options = sorted([y for y in df['year'].unique() if y >= 2018])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체선택", key="year_all", use_container_width=True):
                for year in year_options:
                    st.session_state[f"year_{year}"] = True
        with col2:
            if st.button("전체해제", key="year_none", use_container_width=True):
                for year in year_options:
                    st.session_state[f"year_{year}"] = False
        
        # 연도 체크박스를 여러 열로 배치
        num_cols = 2  # 2열로 배치
        cols = st.columns(num_cols)
        
        selected_years = []
        for i, year in enumerate(year_options):
            with cols[i % num_cols]:
                default_value = st.session_state.get(f"year_{year}", True)
                if st.checkbox(f"{year}년", value=default_value, key=f"year_{year}"):
                    selected_years.append(year)
        
        # 필터 설정에 추가
        filter_config['selected_years'] = selected_years
        filter_config['year_column'] = 'year'  # 항상 투자년도 컬럼 사용
    
    # 부처 필터
    with st.sidebar.expander("🏛️ 부처", expanded=False):
        ministry_options = sorted(df['ministry'].unique())
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체선택", key="ministry_all", use_container_width=True):
                for ministry in ministry_options:
                    st.session_state[f"ministry_{ministry}"] = True
        with col2:
            if st.button("전체해제", key="ministry_none", use_container_width=True):
                for ministry in ministry_options:
                    st.session_state[f"ministry_{ministry}"] = False
        
        # 검색 필터 추가
        ministry_search = st.text_input("부처 검색", placeholder="검색어를 입력하세요")
        if ministry_search:
            filtered_ministries = [m for m in ministry_options if ministry_search.lower() in m.lower()]
        else:
            filtered_ministries = ministry_options
        
        # 부처 목록을 여러 열로 배치
        num_cols = 2  # 2열로 배치
        cols = st.columns(num_cols)
        
        selected_ministries = []
        for i, ministry in enumerate(filtered_ministries):
            with cols[i % num_cols]:
                default_value = st.session_state.get(f"ministry_{ministry}", True)
                if st.checkbox(ministry, value=default_value, key=f"ministry_{ministry}"):
                    selected_ministries.append(ministry)
        
        filter_config['selected_ministries'] = selected_ministries
    
    # 연구분야 필터
    with st.sidebar.expander("🔬 연구분야", expanded=False):
        tech_levels = []
        
        # 대분류
        if 'research_area' in df.columns:
            st.write("**대분류**")
            area_options = sorted(df['research_area'].unique())
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("전체선택", key="area_all", use_container_width=True):
                    for area in area_options:
                        st.session_state[f"area_{area}"] = True
            with col2:
                if st.button("전체해제", key="area_none", use_container_width=True):
                    for area in area_options:
                        st.session_state[f"area_{area}"] = False
            
            # 검색 필터 추가
            area_search = st.text_input("연구분야 검색", placeholder="검색어를 입력하세요")
            if area_search:
                filtered_areas = [a for a in area_options if area_search.lower() in a.lower()]
            else:
                filtered_areas = area_options
            
            # 연구분야 목록을 여러 열로 배치
            num_cols = 2  # 2열로 배치
            cols = st.columns(num_cols)
            
            selected_areas = []
            for i, area in enumerate(filtered_areas):
                with cols[i % num_cols]:
                    default_value = st.session_state.get(f"area_{area}", True)
                    if st.checkbox(area, value=default_value, key=f"area_{area}"):
                        selected_areas.append(area)
            
            filter_config['selected_areas'] = selected_areas
            
            if selected_areas:
                tech_levels.append("대분류")
        else:
            selected_areas = []
            filter_config['selected_areas'] = selected_areas
        
        # 중분류 - 대분류 선택에 따라 필터링
        if 'research_area_medium' in df.columns:
            st.write("**중분류**")
            filtered_medium = df[df['research_area'].isin(selected_areas)]['research_area_medium'].dropna().unique()
            medium_options = sorted(filtered_medium)
            
            if len(medium_options) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("전체선택", key="medium_all", use_container_width=True):
                        for medium in medium_options:
                            st.session_state[f"medium_{medium}"] = True
                with col2:
                    if st.button("전체해제", key="medium_none", use_container_width=True):
                        for medium in medium_options:
                            st.session_state[f"medium_{medium}"] = False
                
                # 검색 필터 추가
                medium_search = st.text_input("중분류 검색", placeholder="검색어를 입력하세요")
                if medium_search:
                    filtered_mediums = [m for m in medium_options if medium_search.lower() in m.lower()]
                else:
                    filtered_mediums = medium_options
                
                # 중분류 목록을 여러 열로 배치
                num_cols = 2  # 2열로 배치
                cols = st.columns(num_cols)
                
                selected_medium = []
                for i, medium in enumerate(filtered_mediums):
                    with cols[i % num_cols]:
                        default_value = st.session_state.get(f"medium_{medium}", True)
                        if st.checkbox(medium, value=default_value, key=f"medium_{medium}"):
                            selected_medium.append(medium)
                
                filter_config['selected_medium'] = selected_medium
                
                if selected_medium:
                    tech_levels.append("중분류")
            else:
                selected_medium = []
                filter_config['selected_medium'] = selected_medium
                st.info("대분류를 먼저 선택해주세요.")
        else:
            selected_medium = []
            filter_config['selected_medium'] = selected_medium
        
        # 소분류 - 중분류 선택에 따라 필터링
        if 'research_area_small' in df.columns:
            st.write("**소분류**")
            filtered_small = df[
                (df['research_area'].isin(selected_areas)) &
                (df['research_area_medium'].isin(selected_medium))
            ]['research_area_small'].dropna().unique()
            small_options = sorted(filtered_small)
            
            if len(small_options) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("전체선택", key="small_all", use_container_width=True):
                        for small in small_options:
                            st.session_state[f"small_{small}"] = True
                with col2:
                    if st.button("전체해제", key="small_none", use_container_width=True):
                        for small in small_options:
                            st.session_state[f"small_{small}"] = False
                
                # 검색 필터 추가
                small_search = st.text_input("소분류 검색", placeholder="검색어를 입력하세요")
                if small_search:
                    filtered_smalls = [s for s in small_options if small_search.lower() in s.lower()]
                else:
                    filtered_smalls = small_options
                
                # 소분류 목록을 여러 열로 배치
                num_cols = 2  # 2열로 배치
                cols = st.columns(num_cols)
                
                selected_small = []
                for i, small in enumerate(filtered_smalls):
                    with cols[i % num_cols]:
                        default_value = st.session_state.get(f"small_{small}", True)
                        if st.checkbox(small, value=default_value, key=f"small_{small}"):
                            selected_small.append(small)
                
                filter_config['selected_small'] = selected_small
                
                if selected_small:
                    tech_levels.append("소분류")
            else:
                selected_small = []
                filter_config['selected_small'] = selected_small
                if selected_medium:
                    st.info("중분류를 먼저 선택해주세요.")
        else:
            selected_small = []
            filter_config['selected_small'] = selected_small
        
        filter_config['tech_levels'] = tech_levels
    
    # 수행주체 필터
    with st.sidebar.expander("🏢 수행주체", expanded=False):
        institute_options = sorted(df['institute'].unique())
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체선택", key="institute_all", use_container_width=True):
                for institute in institute_options:
                    st.session_state[f"institute_{institute}"] = True
        with col2:
            if st.button("전체해제", key="institute_none", use_container_width=True):
                for institute in institute_options:
                    st.session_state[f"institute_{institute}"] = False
        
        # 검색 필터 추가
        institute_search = st.text_input("수행주체 검색", placeholder="검색어를 입력하세요")
        if institute_search:
            filtered_institutes = [i for i in institute_options if institute_search.lower() in i.lower()]
        else:
            filtered_institutes = institute_options
        
        # 수행주체 목록을 여러 열로 배치
        num_cols = 2  # 2열로 배치
        cols = st.columns(num_cols)
        
        selected_institutes = []
        for i, institute in enumerate(filtered_institutes):
            with cols[i % num_cols]:
                default_value = st.session_state.get(f"institute_{institute}", True)
                if st.checkbox(institute, value=default_value, key=f"institute_{institute}"):
                    selected_institutes.append(institute)
        
        filter_config['selected_institutes'] = selected_institutes
    
    return filter_config