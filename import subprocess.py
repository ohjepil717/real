import subprocess
import sys

# 필요한 라이브러리 리스트
REQUIRED_LIBS = ["streamlit", "pandas", "openpyxl"]

def install_packages():
    """필요한 패키지를 설치하는 함수"""
    for lib in REQUIRED_LIBS:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", lib], check=True)
            print(f"{lib} 설치 완료 ✅")
        except subprocess.CalledProcessError:
            print(f"{lib} 설치 실패 ❌")

def main():
    """주 프로그램 실행"""
    print("📦 필수 패키지를 설치합니다...")
    install_packages()
    print("✅ 모든 패키지 설치 완료!")
    
    # 여기에 여러분의 Streamlit 앱 코드 작성
    import streamlit as st
    import pandas as pd

    st.title('내 Streamlit 앱')
    
    df = pd.DataFrame({
        'Column 1': [1, 2, 3, 4],
        'Column 2': [10, 20, 30, 40]
    })
    
    st.write('데이터프레임:')
    st.write(df)
    
    # 엑셀 파일로 저장 기능 추가
    df.to_excel('output.xlsx', index=False)
    st.write('엑셀 파일로 저장되었습니다: output.xlsx')

if __name__ == "__main__":
    main()
