import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(
    page_title="WT Dashboard",
    page_icon="🍔",
    layout="wide"
)

st.title("📈Overview")


st.subheader("Trend")

## 실제 데이터로 변경해야함
dates = pd.date_range(start="2020-11-07", end="2020-11-11")
values = np.random.rand(len(dates))
dummy_df = pd.DataFrame({
    "Date": dates,
    "Value": values
})

# 주황색 그라데이션 설정
colors = [
    "rgba(255, 165, 0, 0.9)",  # 거의 투명한 주황색
    "rgba(255, 165, 0, 0.7)",  # 조금 더 진한 주황색
    "rgba(255, 165, 0, 0.5)",  # 중간 투명 주황색
    "rgba(255, 165, 0, 0.3)",  # 덜 투명한 주황색
    "rgba(255, 165, 0, 0.1)"   # 거의 불투명한 주황색
]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dummy_df["Date"],
    y=dummy_df["Value"],
    mode='lines',            # 라인 모드
    name='Value',
    fill='tozeroy',          # 아래로 채움
    fillcolor='rgba(135, 206, 250, 0.5)',  # 색상 및 투명도 설정
    line=dict(color='orange')  # 라인 색상 설정
))

# 그래프 레이아웃 설정
fig.update_layout(
    title="Line Chart with Filled Area",
    xaxis_title="Date",
    yaxis_title="Value",
    template="plotly_white"
)

# Streamlit 앱에 그래프 표시
st.title("Streamlit Line Chart with Filled Area")
st.plotly_chart(fig)