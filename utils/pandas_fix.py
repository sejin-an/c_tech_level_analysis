import pandas as pd

def fix_pandas_compatibility():
    """pandas 2.0+ 호환성 문제 해결"""
    # iteritems가 없으면 items로 대체
    if not hasattr(pd.DataFrame, 'iteritems'):
        pd.DataFrame.iteritems = pd.DataFrame.items
    
    if not hasattr(pd.Series, 'iteritems'):
        pd.Series.iteritems = pd.Series.items