import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def generate_sample_data():
    """샘플 데이터 생성 함수"""
    np.random.seed(42)
    
    years = list(range(2020, 2025))
    ministries = ['과기부', '산업부', '환경부', '농림부', '국토부', '보건복지부']
    research_areas = ['기후변화대응', 'AI/빅데이터', '바이오헬스', '에너지', '소재부품', '우주항공']
    project_types = ['기초연구', '응용연구', '개발연구', '기타']
    institutes = ['대학', '출연연', '기업', '기타']
    
    data = []
    
    for year in years:
        for ministry in ministries:
            for area in research_areas:
                for ptype in project_types:
                    for institute in institutes:
                        if area == '기후변화대응':
                            budget_base = np.random.normal(150, 50)
                            project_count = np.random.poisson(8)
                        else:
                            budget_base = np.random.normal(100, 30)
                            project_count = np.random.poisson(5)
                        
                        if institute == '대학':
                            budget_mult = 1.5 if ptype == '기초연구' else 0.8
                        elif institute == '출연연':
                            budget_mult = 1.3 if ptype in ['기초연구', '응용연구'] else 0.9
                        elif institute == '기업':
                            budget_mult = 1.7 if ptype in ['응용연구', '개발연구'] else 0.5
                        else:
                            budget_mult = 1.0
                        
                        year_factor = 1 + (year - 2020) * 0.1
                        budget = max(10, budget_base * budget_mult * year_factor)
                        
                        data.append({
                            'year': year,
                            'ministry': ministry,
                            'research_area': area,
                            'project_type': ptype,
                            'institute': institute,
                            'budget_billion': round(budget, 1),
                            'project_count': max(1, int(project_count * budget_mult * 0.8)),
                            'success_rate': round(np.random.uniform(0.6, 0.9), 2)
                        })
    
    return pd.DataFrame(data)