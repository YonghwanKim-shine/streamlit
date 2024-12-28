import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from scipy.interpolate import make_interp_spline

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

# 데이터 생성
dates = pd.date_range(start="2020-11-07", end="2020-11-11")
values = np.random.rand(len(dates))

dummy_df = pd.DataFrame({
    "Date": dates,
    "Value": values
})


x = np.arange(len(dummy_df["Date"]))  # 정수형 x값
y = dummy_df["Value"]  # y값
spl = make_interp_spline(x, y, k=3)  # 곡선을 생성 (k=3: Cubic Spline)
x_new = np.linspace(x.min(), x.max(), 300)  # 곡선을 위한 세밀한 x축
y_new = spl(x_new)  # 곡선의 y값

# Matplotlib 그래프 생성
fig, ax = plt.subplots(figsize=(10, 6))

# 그라데이션 색상 정의
color_start = to_rgba("orange", 0.1)  # 밝은 주황색
color_end = to_rgba("orange", 0.9)    # 진한 주황색

# 그라데이션을 위한 색상 생성
for i, alpha in enumerate(np.linspace(0.1, 0.9, 100)):
    ax.fill_between(
        x_new,
        y_new,
        where=(y_new > 0),
        interpolate=True,
        color=to_rgba("orange", alpha),
        zorder=i
    )

# 곡선 형태의 라인 추가
ax.plot(x_new, y_new, color="orange", linewidth=2, label="Value")

# x축 레이블 설정
ax.set_xticks(np.arange(len(dummy_df["Date"])))
ax.set_xticklabels(dummy_df["Date"].dt.strftime("%Y-%m-%d"), rotation=45)

# 그래프 제목과 축 레이블 설정
#ax.set_title("Line Chart with Gradient Fill (Rounded Line)", fontsize=16)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Health", fontsize=12)

# Streamlit에 표시
st.pyplot(fig)