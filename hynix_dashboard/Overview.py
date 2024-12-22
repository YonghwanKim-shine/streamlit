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

## 실제 데이터로 변경해야함
dates = pd.date_range(start="2020-11-07", end="2020-11-11")
values = np.random.rand(len(dates))
dummy_df = pd.DataFrame({
    "Date": dates,
    "Value": values
})

# 라인 차트 표시
st.line_chart(data=dummy_df.set_index("Date"))

# 주요 변수
st.subheader("Important Features Heatmap")
#