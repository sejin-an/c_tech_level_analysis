import pandas as pd
import os

def convert_excel_to_pkl(excel_file_path):
    """엑셀 파일을 PKL 파일들로 변환"""
    
    try:
        # 엑셀 파일에서 모든 시트 읽기
        excel_data = pd.read_excel(excel_file_path, sheet_name=None)
        
        # data 폴더 생성
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # 시트별로 PKL 파일 생성
        sheet_mapping = {
            'Sheet1': '투자성과',  # 또는 실제 시트명
            'Sheet2': '사업화',
            'Sheet3': '기술료'
        }
        
        for sheet_name, pkl_name in sheet_mapping.items():
            if sheet_name in excel_data:
                df = excel_data[sheet_name]
                pkl_path = f'data/{pkl_name}.pkl'
                df.to_pickle(pkl_path)
                print(f"✅ {sheet_name} → {pkl_path} (레코드: {len(df):,}개)")
            else:
                print(f"❌ {sheet_name} 시트를 찾을 수 없습니다.")
        
        # 전체 시트 목록 출력
        print(f"\n발견된 시트: {list(excel_data.keys())}")
        
    except Exception as e:
        print(f"❌ 변환 실패: {e}")

def main():
    print("엑셀 파일을 PKL로 변환")
    print("=" * 40)
    
    # 엑셀 파일 경로 입력
    excel_path = input("엑셀 파일 경로를 입력하세요: ").strip().strip('"')
    
    if not os.path.exists(excel_path):
        print("❌ 파일이 존재하지 않습니다.")
        return
    
    convert_excel_to_pkl(excel_path)
    print("\n변환 완료!")

if __name__ == "__main__":
    main()