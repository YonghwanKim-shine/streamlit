import pandas as pd
import numpy as np
import gdown
import streamlit as st
from plotly.colors import make_colorscale
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events
#
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



lot_wafer_dict = df_data.groupby('Lot')['Wafer'].apply(lambda x: sorted(map(str, map(int, x.unique())))).to_dict()


lot_list = lot_wafer_dict.keys()
# Lot_Wafer 별 X0 평균 계산
lot_wafer_avg = (
    df_data.groupby(['Lot', 'Wafer'])['X0']
    .mean()
    .reset_index()
    .rename(columns={'X0': 'X0 평균'}).sort_values(by='X0 평균', ascending=False)
)
data = []
for lot in lot_list:
    wafer_count = lot_wafer_dict[lot]
    for wafer in wafer_count:
        data.append({
            "Lot번호": lot,
            "Wafer번호": wafer
        })
#
df = pd.DataFrame(data)
# Streamlit UI 구성
col1, col2 = st.columns([1, 2])

# 왼쪽 열: Lot_Wafer별 X0 평균값
with col1:
    st.subheader("Lot_Wafer별 X0 평균값")
    st.dataframe(lot_wafer_avg, height=600)

# 오른쪽 열: 로트 및 웨이퍼 선택 + 분석 결과
with col2:
    # 로트 및 웨이퍼 선택
    st.subheader("로트 및 웨이퍼 선택")
    selected_lot = st.selectbox("Lot을 선택하세요:", options=df["Lot번호"].unique())

    selected_wafer = st.selectbox(
        "Wafer를 선택하세요:",
        options=df[df["Lot번호"] == selected_lot]["Wafer번호"].sort_values(ascending=True).unique()
    )

    # 컬럼 선택
    st.subheader("분석할 컬럼 선택")
    columns_to_analyze = st.multiselect(
        "분석할 컬럼을 선택하세요:",
        options=df_data.columns,
        default=[]
    )

