import streamlit as st
import matplotlib.pyplot as plt

def setup_page_config():
    """페이지 기본 설정"""
    st.set_page_config(
        page_title="국가연구개발사업 투자분석 대시보드",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def setup_font():
    """한글 폰트 설정"""
    try:
        plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우용 
        plt.rcParams['axes.unicode_minus'] = False
    except:
        try:
            plt.rcParams['font.family'] = 'AppleGothic'  # Mac용
            plt.rcParams['axes.unicode_minus'] = False
        except:
            print("기본 폰트를 사용합니다. 한글이 깨질 수 있습니다.")

# 컬러 팔레트 정의
COLOR_SCHEMES = {
    'ministry': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
    'research_area': ['#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#ff9999', '#ff6666'],
    'climate_tech': ['#2E8B57', '#228B22', '#32CD32', '#90EE90', '#98FB98', '#F0FFF0'],
    'performance': ['green', 'skyblue', 'salmon', 'orange', 'purple', 'brown']
}

# 차트 기본 설정
CHART_CONFIG = {
    'height_small': 400,
    'height_medium': 500,
    'height_large': 600,
    'height_xlarge': 700,
    'height_xxlarge': 800,
    'margin': dict(l=0, r=0, b=0, t=40)
}