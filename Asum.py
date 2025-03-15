import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re
from PIL import Image
import pytesseract
import os

# 세션 상태 초기화
if "data_list" not in st.session_state:
    st.session_state.data_list = []

# 앱 UI
st.title("영수증 및 홈택스 데이터 관리")

# 계정과목 드롭다운 (자영업자용)
account_subjects = [
    "매출원가", "일반관리비", "광고비", "운반비", "수수료", "임차료", "소모품비", "지급수수료",
    "여비교통비", "통신비", "전기료", "수도료", "가스비", "기타비용"
]

# 1. 영수증 사진 업로드 및 처리
st.subheader("1. 영수증 사진 업로드")
uploaded_image = st.file_uploader("영수증 사진을 업로드하세요 (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_image:
    # 이미지에서 텍스트 추출
    image = Image.open(uploaded_image)
    text = pytesseract.image_to_string(image, lang='kor+eng')

    # 추출된 텍스트 표시
    st.text_area("추출된 텍스트:", value=text, height=200)

    # 텍스트에서 정보 추출
    date = re.search(r'\d{4}-\d{2}-\d{2}', text)
    amount = re.search(r'(\d{1,3}(,\d{3})*원|\d+원)', text)
    store = re.search(r'(주)?[\w가-힣\s]+', text)

    extracted_data = {
        "날짜": date.group() if date else "알 수 없음",
        "사업자": store.group() if store else "알 수 없음",
        "금액": amount.group() if amount else "알 수 없음",
        "부가세": "알 수 없음",  # 부가세는 추가 로직 필요
        "비고": "영수증 사진"
    }

    # 계정과목 선택
    account_subject = st.selectbox("계정과목 선택:", account_subjects, key="account_from_image")
    extracted_data["계정과목"] = account_subject

    if st.button("영수증 데이터 추가"):
        st.session_state.data_list.append(extracted_data)
        st.success("영수증 데이터가 추가되었습니다!")

# 2. 텍스트 파일 업로드 및 처리
st.subheader("2. 텍스트 파일 업로드")
uploaded_txt = st.file_uploader("텍스트 파일을 업로드하세요 (TXT)", type=["txt"])

if uploaded_txt:
    # 텍스트 파일 읽기
    text = uploaded_txt.read().decode("utf-8")
    st.text_area("텍스트 파일 내용:", value=text, height=200)

    # 텍스트에서 정보 추출
    lines = text.split("\n")
    current_set = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "날짜:" in line:
            current_set["날짜"] = line.replace("날짜:", "").strip()
        elif "사업자:" in line:
            current_set["사업자"] = line.replace("사업자:", "").strip()
        elif "금액:" in line:
            current_set["금액"] = line.replace("금액:", "").strip()
        elif "부가세:" in line:
            current_set["부가세"] = line.replace("부가세:", "").strip()
        elif "비고:" in line:
            current_set["비고"] = line.replace("비고:", "").strip()

    # 계정과목 선택
    account_subject = st.selectbox("계정과목 선택:", account_subjects, key="account_from_txt")
    current_set["계정과목"] = account_subject

    if st.button("텍스트 데이터 추가"):
        st.session_state.data_list.append(current_set)
        st.success("텍스트 데이터가 추가되었습니다!")

# 3. 홈택스 데이터 업로드 및 처리
st.subheader("3. 홈택스 카드 지출 데이터 업로드 (CSV)")
uploaded_csv = st.file_uploader("홈택스에서 다운로드한 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_csv:
    # CSV 파일 읽기
    df_hometax = pd.read_csv(uploaded_csv)
    st.dataframe(df_hometax)

    # 필요한 컬럼 추출 (홈택스 CSV 형식에 따라 조정 필요)
    hometax_data = []
    for _, row in df_hometax.iterrows():
        data = {
            "날짜": row.get("거래일자", "알 수 없음"),
            "사업자": row.get("가맹점명", "알 수 없음"),
            "금액": str(row.get("승인금액", "알 수 없음")) + "원",
            "부가세": str(row.get("부가세", "알 수 없음")) + "원",
            "비고": "홈택스 카드 지출"
        }

        # 계정과목 선택
        account_subject = st.selectbox(f"계정과목 선택 (거래: {data['사업자']}):", account_subjects, key=f"hometax_{_}")
        data["계정과목"] = account_subject
        hometax_data.append(data)

    if st.button("홈택스 데이터 추가"):
        st.session_state.data_list.extend(hometax_data)
        st.success("홈택스 데이터가 추가되었습니다!")

# 4. 데이터 표시 및 엑셀 저장
if st.session_state.data_list:
    st.subheader("분류된 데이터 목록")
    df = pd.DataFrame(st.session_state.data_list)
    st.dataframe(df)

    # 엑셀 다운로드 버튼
    if st.button("엑셀로 저장"):
        filename = f"expense_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label="엑셀 파일 다운로드",
            data=buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success(f"엑셀 파일이 준비되었습니다: {filename}")
