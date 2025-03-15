import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re

# 세션 상태 초기화
if "data_list" not in st.session_state:
    st.session_state.data_list = []
if "memo_text" not in st.session_state:
    st.session_state.memo_text = ""

# 앱 UI
st.title("영수증 및 홈택스 데이터 관리")

# 1. 메모장 입력 및 처리
st.subheader("1. 메모장 입력 (붙여넣기)")
st.session_state.memo_text = st.text_area(
    "여기에 영수증 정보를 붙여넣으세요 (형식 예시: 날짜: 2025-03-20, 상호: (주)ABC마트, 계정과목: 소모품비, 구입처: ABC마트, 금액: 80,000원, 부가세: 8,000원, 비고: 물품 구입):",
    value=st.session_state.memo_text,
    height=200,
    key="memo_input"
)

if st.session_state.memo_text:
    # 메모장에서 데이터 파싱
    lines = st.session_state.memo_text.split("\n")
    current_set = None
    categorized_data = []

    for line in lines:
        line = line.strip()
        if not line or "항목 예시:" in line:  # 빈 줄 또는 "항목 예시:" 무시
            continue

        # 쉼표로 구분된 경우와 줄바꿈으로 구분된 경우 모두 처리
        if "," in line:
            items = [item.strip() for item in line.split(",")]
            if current_set is not None:  # 이전 세트가 존재하면 저장
                categorized_data.append(current_set)
            current_set = {"비고": "메모장 입력"}  # 새로운 세트 시작

            for item in items:
                if "날짜:" in item:
                    current_set["날짜"] = item.replace("날짜:", "").strip()
                elif "상호:" in item:
                    current_set["상호"] = item.replace("상호:", "").strip()
                elif "계정과목:" in item:
                    current_set["계정과목"] = item.replace("계정과목:", "").strip()
                elif "구입처:" in item:
                    current_set["구입처"] = item.replace("구입처:", "").strip()
                elif "금액:" in item:
                    current_set["금액"] = item.replace("금액:", "").strip()
                elif "부가세:" in item:
                    current_set["부가세"] = item.replace("부가세:", "").strip()
                elif "비고:" in item:
                    current_set["비고"] = item.replace("비고:", "").strip()
        else:
            # 줄바꿈으로 구분된 경우
            if "날짜:" in line:
                if current_set is not None:  # 이전 세트가 존재하면 저장
                    categorized_data.append(current_set)
                current_set = {"비고": "메모장 입력"}  # 새로운 세트 시작
                current_set["날짜"] = line.replace("날짜:", "").strip()
            elif current_set is not None:  # 현재 세트가 존재할 때만 데이터 추가
                if "상호:" in line:
                    current_set["상호"] = line.replace("상호:", "").strip()
                elif "계정과목:" in line:
                    current_set["계정과목"] = line.replace("계정과목:", "").strip()
                elif "구입처:" in line:
                    current_set["구입처"] = line.replace("구입처:", "").strip()
                elif "금액:" in line:
                    current_set["금액"] = line.replace("금액:", "").strip()
                elif "부가세:" in line:
                    current_set["부가세"] = line.replace("부가세:", "").strip()
                elif "비고:" in line:
                    current_set["비고"] = line.replace("비고:", "").strip()

    # 마지막 세트 추가
    if current_set is not None:
        categorized_data.append(current_set)

    # 디버깅 정보 표시
    if not categorized_data:
        st.warning("입력된 데이터에서 유효한 항목을 찾을 수 없습니다. 형식 예시를 확인해주세요.")
    else:
        st.subheader("파싱된 데이터:")
        for idx, data in enumerate(categorized_data):
            st.write(f"데이터 {idx + 1}: {data}")

        if st.button("메모장 데이터 추가"):
            st.session_state.data_list.extend(categorized_data)
            st.session_state.memo_text = ""  # 메모장 초기화
            st.success("메모장 데이터가 추가되었습니다!")
            st.experimental_rerun()  # 페이지 새로고침

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
        elif "상호:" in line:
            current_set["상호"] = line.replace("상호:", "").strip()
        elif "계정과목:" in line:
            current_set["계정과목"] = line.replace("계정과목:", "").strip()
        elif "구입처:" in line:
            current_set["구입처"] = line.replace("구입처:", "").strip()
        elif "금액:" in line:
            current_set["금액"] = line.replace("금액:", "").strip()
        elif "부가세:" in line:
            current_set["부가세"] = line.replace("부가세:", "").strip()
        elif "비고:" in line:
            current_set["비고"] = line.replace("비고:", "").strip()

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
            "상호": row.get("가맹점명", "알 수 없음"),
            "계정과목": "기타비용",  # 기본값 설정
            "구입처": row.get("가맹점명", "알 수 없음"),
            "금액": str(row.get("승인금액", "알 수 없음")) + "원",
            "부가세": str(row.get("부가세", "알 수 없음")) + "원",
            "비고": "홈택스 카드 지출"
        }
        hometax_data.append(data)

    if st.button("홈택스 데이터 추가"):
        st.session_state.data_list.extend(hometax_data)
        st.success("홈택스 데이터가 추가되었습니다!")

# 4. 데이터 표시 및 엑셀 저장
if st.session_state.data_list:
    st.subheader("분류된 데이터 목록")
    df = pd.DataFrame(st.session_state.data_list)
    # 엑셀 파일에 맞게 컬럼 순서 정렬
    columns_order = ["날짜", "상호", "계정과목", "구입처", "금액", "부가세", "비고"]
    df = df[columns_order]  # 필요한 컬럼만 선택하고 순서 정렬
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
