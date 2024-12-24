import streamlit as st
import pandas as pd
import numpy as np

# 페이지 기본 설정
st.set_page_config(
    page_title="WT Dashboard",
    page_icon="🍔",
    layout="wide"
)

st.title("Wafer Test Overview")






## 실제 데이터로 변경해야함
dates = pd.date_range(start="2020-11-07", end="2020-11-11")
values = np.random.rand(len(dates))
dummy_df = pd.DataFrame({
    "Date": dates,
    "Value": values
})
# 라인 차트 표시
st.line_chart(data=dummy_df.set_index("Date"))



# 임시 데이터 생성
np.random.seed(42)  # 재현성을 위해 시드 설정
lot_numbers = [f"Lot{i}" for i in range(1, 11)]  # Lot 번호
data = []

for lot in lot_numbers:
    wafer_count = np.random.randint(5, 15)  # 각 Lot의 웨이퍼 개수 랜덤 생성
    for wafer in range(1, wafer_count + 1):
        data.append({
            "Lot번호": lot,
            "Wafer번호": f"W{wafer}",
            "컬럼1": np.round(np.random.rand() * 100, 2),
            "컬럼2": np.round(np.random.rand() * 100, 2),
            "컬럼3": np.round(np.random.rand() * 100, 2),
        })

# 데이터프레임 생성
df = pd.DataFrame(data)

# 가로 열 배치
col1, col2 = st.columns([2, 1])  # 왼쪽이 더 넓은 비율로 설정

# 왼쪽 열: 전체 데이터 미리보기
with col1:
    st.subheader("전체 데이터 미리보기")
    st.dataframe(df, height=600)

# 오른쪽 열: 로트 및 웨이퍼 선택 + 분석 결과
with col2:
    # 로트 및 웨이퍼 선택
    st.subheader("로트 및 웨이퍼 선택")
    selected_lot = st.selectbox("Lot을 선택하세요:", options=df["Lot번호"].unique())

    selected_wafer = st.selectbox(
        "Wafer를 선택하세요:",
        options=df[df["Lot번호"] == selected_lot]["Wafer번호"].unique()
    )

    # 컬럼 선택
    st.subheader("분석할 컬럼 선택")
    columns_to_analyze = st.multiselect(
        "분석할 컬럼을 선택하세요:",
        options=["컬럼1", "컬럼2", "컬럼3"],
        default=["컬럼1", "컬럼2"]
    )

    if columns_to_analyze:
        # 전체 데이터 기반 평균값
        overall_avg = df[columns_to_analyze].mean().to_frame(name="전체 평균")

        # 선택한 Lot, Wafer 데이터 기반 평균값
        selected_data = df[(df["Lot번호"] == selected_lot) & (df["Wafer번호"] == selected_wafer)]
        wafer_avg = selected_data[columns_to_analyze].mean().to_frame(name=f"{selected_lot}-{selected_wafer} 평균")

        # 분석 결과 출력
        st.write("### 전체 데이터 기반 평균값")
        st.dataframe(overall_avg)

        st.write(f"### {selected_lot}-{selected_wafer} 데이터 기반 평균값")
        st.dataframe(wafer_avg)
