import streamlit as st
import pandas as pd
import numpy as np
from streamlit_lightweight_charts import renderLightweightCharts
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

# 곡선 형태 데이터 생성 (보간법 적용)
x = np.arange(len(dummy_df["Date"]))  # 정수형 x값
y = dummy_df["Value"]  # y값
spl = make_interp_spline(x, y, k=3)  # Cubic Spline 보간
x_new = np.linspace(x.min(), x.max(), 300)  # 세밀한 x축
y_new = spl(x_new)  # 곡선의 y값

# Streamlit Lightweight Charts의 데이터 형식으로 변환
price_volume_area_data = [
    {"time": dummy_df["Date"].iloc[int(idx)].strftime("%Y-%m-%d"), "value": val}
    for idx, val in zip(np.linspace(0, len(dummy_df) - 1, len(x_new)), y_new)
]

# 차트 옵션
ChartOptions = {
    "layout": {
        "background": {
            "type": 'solid',
            "color": 'white'
        },
        "textColor": 'black',
    }
}

# 데이터 시리즈 설정
priceVolumeSeries = [
    {
        "type": 'Area',
        "data": price_volume_area_data,  # 데이터 적용
        "options": {
            "topColor": 'rgba(255, 165, 0, 0.56)',  # 밝은 주황색
            "bottomColor": 'rgba(255, 165, 0, 0.04)',  # 투명한 주황색
            "lineColor": 'rgba(255, 165, 0, 1)',  # 진한 주황색
            "lineWidth": 2,
        }
    }
]

# Streamlit 앱 렌더링
st.subheader("Weekly Health Trend")

renderLightweightCharts([
    {
        "chart": ChartOptions,
        "series": priceVolumeSeries
    }
], 'priceAndVolume')


# # 주황색 그라데이션 설정
# colors = [
#     "rgba(255, 165, 0, 0.9)",  # 거의 투명한 주황색
#     "rgba(255, 165, 0, 0.7)",  # 조금 더 진한 주황색
#     "rgba(255, 165, 0, 0.5)",  # 중간 투명 주황색
#     "rgba(255, 165, 0, 0.3)",  # 덜 투명한 주황색
#     "rgba(255, 165, 0, 0.1)"   # 거의 불투명한 주황색
# ]
#
# fig = go.Figure()
#
# for i in range(len(colors)):
#     fig.add_trace(go.Scatter(
#         x=dummy_df["Date"],
#         y=dummy_df["Value"] * (1 - 0.1 * i),  # 점점 낮아지는 곡선
#         mode='lines',
#         line=dict(width=0),  # 라인 숨김
#         fill='tonexty',
#         fillcolor=colors[i],
#         name=f"Layer {i+1}"
#     ))
#
# # 메인 라인 추가
# fig.add_trace(go.Scatter(
#     x=dummy_df["Date"],
#     y=dummy_df["Value"],
#     mode='lines',
#     line=dict(color="orange", width=2),  # 메인 라인 색상
#     name="Main Line"
# ))
#
# # 레이아웃 설정
# fig.update_layout(
#     #title="Line Chart with Orange Gradient Fill",
#     xaxis_title="Date",
#     yaxis_title="Health",
#     template="plotly_white"
# )
#
# # Streamlit에 그래프 표시
# st.plotly_chart(fig)