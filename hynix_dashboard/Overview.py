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
lot_numbers = [f"Lot{i}" for i in range(1, 21)]  # Lot 번호
wafer_numbers = [f"W{i}" for i in range(1, 21)]  # Wafer 번호
data = []

for lot in lot_numbers:
    for wafer in wafer_numbers:
        pred_value = np.round(np.random.rand(), 3)  # 랜덤 예측값 생성
        data.append([lot, wafer, pred_value])

loss_df = pd.DataFrame(data, columns=["Lot번호", "Wafer번호", "예측값"])

# 스크롤 가능한 테이블 표시
st.dataframe(loss_df, height=400)
