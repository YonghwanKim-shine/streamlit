import pandas as pd
import numpy as np
import gdown
import streamlit as st
from plotly.colors import make_colorscale
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events

st.set_page_config(
    page_title="WT Dashboard",
    page_icon="🍔",
    layout="wide"
)

# Google Drive 공유 링크
url = "https://drive.google.com/uc?id=1uKjg4ntkVCpzL9mJ2xI3SXJdP3h-3pRY"


def download_file(url, output_path):
    gdown.download(url, output_path, quiet=False)
    return output_path

@st.cache_data
def road_file():
    file_path = download_file(url, "temp_data_40000.csv")
    df_data = pd.read_csv(file_path)
    return df_data

# 데이터 불러오기
df_data = road_file()

# 'run_wf_xy'에서 Lot, Wafer, DieX, DieY 분리
df_data[['Lot', 'Wafer', 'DieX', 'DieY']] = df_data['run_wf_xy'].str.split('_', expand=True)

# Lot_Wafer 별 X0 평균 계산
lot_wafer_avg = (
    df_data.groupby(['Lot', 'Wafer'])['X0']
    .mean()
    .reset_index()
    .rename(columns={'X0': 'X0 평균'})
)

# Streamlit UI 구성
col1, col2 = st.columns([1, 2])

# 왼쪽 열: Lot_Wafer별 X0 평균값
with col1:
    st.subheader("Lot_Wafer별 X0 평균값")
    st.dataframe(lot_wafer_avg, height=600)

# 오른쪽 열: 로트 및 웨이퍼 선택 + 분석 결과
with col2:
    st.subheader("로트 및 웨이퍼 선택")
    selected_lot = st.selectbox("Lot을 선택하세요:", options=lot_wafer_avg["Lot"].unique())

    selected_wafer = st.selectbox(
        "Wafer를 선택하세요:",
        options=lot_wafer_avg[lot_wafer_avg["Lot"] == selected_lot]["Wafer"].unique()
    )

    st.subheader(f"{selected_lot}-{selected_wafer} X0 평균값")
    selected_avg = lot_wafer_avg[
        (lot_wafer_avg["Lot"] == selected_lot) & (lot_wafer_avg["Wafer"] == selected_wafer)
    ]["X0 평균"]
    st.write(f"X0 평균값: {selected_avg.values[0]:.2f}")
