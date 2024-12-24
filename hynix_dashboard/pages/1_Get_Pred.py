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
url_position_1 = "https://drive.google.com/uc?id=14AON6Oam_0Z-u5RhHojFAexrVef1Sg2S"
# url_position_2 = "https://drive.google.com/uc?id=19YOKChOwa4S6ynO00SKauMPaZtfPuQkC"
# url_position_3 = "https://drive.google.com/uc?id=1Q0S8UAyvX7cHsOAbhcS026y0EFHmByCK"
# url_position_4 = "https://drive.google.com/uc?id=18KindmSQqoQuu4iV7ySE9q4cETC10Lf5"

# 파일 다운로드

def download_file(url, output_path):
    gdown.download(url, output_path, quiet=False)
    return output_path

@st.cache_data
def road_file():
    file_path_1 = download_file(url_position_1, "position_1.csv")
    # file_path_2 = download_file(url_position_2, "position_2.csv")
    # file_path_3 = download_file(url_position_3, "position_3.csv")
    # file_path_4 = download_file(url_position_4, "position_4.csv")

    df1 = pd.read_csv(file_path_1)
    # df2 = pd.read_csv(file_path_2)
    # df3 = pd.read_csv(file_path_3)
    # df4 = pd.read_csv(file_path_4)

    # df = pd.concat([df1,df2,df3,df4], axis=0)
    return df1

# 목록 불러오는 기능
df = road_file()
df[['Lot', 'Wafer', 'DieX', 'DieY']] = df['run_wf_xy'].str.split('_', expand=True)
#print(df)

lot_list = df['Lot'].unique()

wafer_list = df['Wafer'].unique()
wafer_list = sorted(list(map(int, wafer_list)))
wafer_list = list(map(str, wafer_list))


# 왼쪽 페이지
# 페이지 기본 설정
st.title("Get Pred")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        #st.subheader("Lot 선택")
        selected_option_lot = st.selectbox('Lot', lot_list)
    with col2:
        #st.subheader("Wafer 선택")
        selected_option_wafer = st.selectbox('Wafer', wafer_list)

# st.write('선택된 Lot', selected_option_lot)
# st.write('선택된 Wafer', selected_option_wafer)

# 오른쪽 페이지
# 좌표 단위 맞춰주기

df.loc[:, 'DieX'] = df.loc[:, 'DieX'].astype(int)-12
df.loc[:, 'DieY'] = df.loc[:, 'DieY'].astype(int)-11

condition = (df['Lot'] == selected_option_lot) & (df['Wafer'] == selected_option_wafer)

##수정 예정
heatmap_data = df[condition].loc[:,['DieX','DieY','X5']]

matrix = np.full((22, 55), np.nan)
for i in heatmap_data.values:
    x, y, c = map(int,i)
    matrix[y, x] = c

def create_heatmap(matrix):
    cmap = plt.get_cmap('coolwarm')
    colorscale = make_colorscale([cmap(i) for i in np.linspace(0, 1, 256)])

    heatmap_fig = go.Figure(
        data=go.Heatmap(z=matrix, colorscale='rdylbu_r')
    )
    heatmap_fig.update_layout(
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        width=500,
        height=400,
        margin=dict(l=30, r=10, t=10, b=10)
    )
    return heatmap_fig


# 좌표 클릭 기록 관리
if "clicked_points" not in st.session_state:
    st.session_state["clicked_points"] = []

# 실행 버튼 상태 관리
if "run_button_enabled" not in st.session_state:
    st.session_state["run_button_enabled"] = False


# 좌측: 히트맵 출력
with st.container():
    col1, col2 = st.columns(2)

    # 왼쪽: 히트맵 출력
    with col1:
        st.subheader("wafer의 히트맵")
        heatmap_fig = create_heatmap(matrix)
        selected_points = plotly_events(heatmap_fig, click_event=True)
        st.plotly_chart(heatmap_fig)

        # 클릭 이벤트 처리
        if selected_points:
            point = selected_points[0]
            x, y = int(point['x']), int(point['y'])
            z = matrix[y, x] if 0 <= y < matrix.shape[0] and 0 <= x < matrix.shape[1] else None

            # 좌표 추가 (최대 4개까지)
            if len(st.session_state["clicked_points"]) < 4:
                st.session_state["clicked_points"].append({"x": x, "y": y, "z": z})

            # 실행 버튼 활성화 조건 확인
            if len(st.session_state["clicked_points"]) == 4:
                st.session_state["run_button_enabled"] = True

    # 오른쪽: 클릭 결과와 삭제 기능
    with col2:
        st.subheader("클릭 결과")
        for i, point in enumerate(st.session_state["clicked_points"]):
            st.write(f"{i+1}. x={point['x']}, y={point['y']}, z={point['z']}")
            # 삭제 버튼
            if st.button(f"삭제 {i+1}", key=f"delete_{i}"):
                st.session_state["clicked_points"].pop(i)
                st.session_state["run_button_enabled"] = False  # 실행 버튼 비활성화
                st.experimental_rerun()  # UI 갱신

        # 실행하기 버튼
        if st.session_state["run_button_enabled"]:
            if st.button("실행하기"):
                st.success("실행 완료!")
        else:
            st.button("실행하기", disabled=True)