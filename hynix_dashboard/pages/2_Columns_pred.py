

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
url = "https://drive.google.com/uc?id=18ls7kxYzQu1HXFH-IozgUcJ24LU6zBlR"


def download_file(url, output_path):
    gdown.download(url, output_path, quiet=False)
    return output_path

@st.cache_data
def road_file():
    file_path = download_file(url, "temp_data_40000.csv")
    df = pd.read_csv(file_path)

    # df = pd.concat([df1,df2,df3,df4], axis=0)
    return df

# 목록 불러오는 기능
df = road_file()
df[['Lot', 'Wafer', 'DieX', 'DieY']] = df['run_wf_xy'].str.split('_', expand=True)
# Lot별로 각 Wafer 리스트 생성
lot_wafer_dict = df.groupby('Lot')['Wafer'].apply(lambda x: sorted(map(str, map(int, x.unique())))).to_dict()


lot_list = lot_wafer_dict.keys()

for lot in lot_list:
    wafer_count = lot_wafer_dict[lot]
    for wafer in range(1, wafer_count + 1):
        data.append({
            "Lot번호": lot,
            "Wafer번호": f"W{wafer}",
            "컬럼1": np.round(np.random.rand() * 100, 2),
            "컬럼2": np.round(np.random.rand() * 100, 2),
            "컬럼3": np.round(np.random.rand() * 100, 2),
        })
#
# 가로 열 배치
col1, col2 = st.columns([1, 2])  # 왼쪽이 더 넓은 비율로 설정

# 왼쪽 열: 전체 데이터 미리보기
with col1:
    st.subheader("Wafer별 Health값")
    st.dataframe(df["ufs_serial","X0"], height=600)
#
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
