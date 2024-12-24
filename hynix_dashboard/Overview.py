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

# 라인차트
st.subheader("Weekly Health Chart")
dates = pd.date_range(start="2020-11-07", end="2020-11-11")
values = np.random.rand(len(dates))
dummy_df = pd.DataFrame({
    "Date": dates,
    "Value": values
})
st.line_chart(data=dummy_df.set_index("Date"))

# 주요 변수
st.subheader("웨이퍼별 로스율 예측값")

# Lot번호_Wafer번호_예측값 데이터 생성
lot_numbers = [f"Lot{i}" for i in range(1, 21)]
wafer_numbers = [f"W{i}" for i in range(1, 21)]
data = []

for lot in lot_numbers:
    for wafer in wafer_numbers:
        pred_value = np.round(np.random.rand(), 3)  # 랜덤 예측값 생성
        data.append([lot, wafer, pred_value])

loss_df = pd.DataFrame(data, columns=["Lot번호", "Wafer번호", "예측값"])
st.dataframe(loss_df, height=400)

# 특정 웨이퍼 선택
st.subheader("웨이퍼 데이터 상세 분석")
selected_wafer = st.selectbox(
    "웨이퍼를 선택하세요:",
    options=loss_df["Wafer번호"].unique()
)

# 컬럼 지정
columns_to_analyze = st.multiselect(
    "분석할 컬럼을 선택하세요:",
    options=["예측값"],
    default=["예측값"]
)

if columns_to_analyze:
    # 전체 데이터 기반 평균값
    overall_avg = loss_df[columns_to_analyze].mean().to_frame(name="전체 평균")

    # 선택한 웨이퍼의 데이터 기반 평균값
    wafer_data = loss_df[loss_df["Wafer번호"] == selected_wafer]
    wafer_avg = wafer_data[columns_to_analyze].mean().to_frame(name=f"{selected_wafer} 평균")

    # 데이터프레임 출력
    st.write("### 전체 데이터 기반 평균값")
    st.dataframe(overall_avg)

    st.write(f"### {selected_wafer} 데이터 기반 평균값")
    st.dataframe(wafer_avg)
