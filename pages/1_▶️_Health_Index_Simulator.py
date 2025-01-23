from select import select

import pandas as pd
import numpy as np
import gdown
import streamlit as st
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from streamlit_plotly_events import plotly_events
from scipy.interpolate import griddata
import requests
import base64
from io import BytesIO

st.set_page_config(
    page_title="WT Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 설정
def load_css(file_name):
    with open(file_name, "r", encoding = 'utf-8') as f:
        return f"<style>{f.read()}</style>"


css = load_css('hynix_dashboard/pages/Health_Index.css')
st.markdown(css, unsafe_allow_html=True)

# Streamlit 상태

#slot 상태 업데이트 체크
if "coordinate_slots" not in st.session_state:
    st.session_state["coordinate_slots"] = {
        "position 1": None,
        "position 2": None,
        "position 3": None,
        "position 4": None
    }
#선택값 변경 상태 체크
if "last_selected_lot" not in st.session_state:
    st.session_state["last_selected_lot"] = None
if "last_selected_wafer" not in st.session_state:
    st.session_state["last_selected_wafer"] = None
#slot 선택 활성화 여부 체크
if "active_slot" not in st.session_state:
    st.session_state["active_slot"] = None

# 데이터 불러오기
url_position_1 = "https://drive.google.com/uc?id=1Pks1l3ykarM457ehCJE_GODLVcX4stjL"

def download_file(url, output_path):
    gdown.download(url, output_path, quiet=False)
    return output_path

@st.cache_data
def load_file():
    file_path_1 = download_file(url_position_1, "simulation_data.csv")
    df1 = pd.read_csv(file_path_1)
    return df1

# 목록 불러오는 기능
df = load_file()
df[['Lot', 'Wafer', 'DieX', 'DieY']] = df['run_wf_xy'].str.split('_', expand=True)
lot_list = df['Lot'].unique()

# 페이지 기본 설정
st.title("🧮 Health Index Simulator")

# 상단 웨이퍼 선택 ui

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        selected_option_lot = st.selectbox('Lot', lot_list)
    with col2:
        filtered_wafer_list = sorted(
            map(int, df[df['Lot'] == selected_option_lot]['Wafer'].unique())
        )
        filtered_wafer_list = list(map(str, filtered_wafer_list))
        selected_option_wafer = st.selectbox('Wafer', filtered_wafer_list)

# 선택 값 변경 확인 및 슬롯 초기화
if (st.session_state["last_selected_lot"] != selected_option_lot or
    st.session_state["last_selected_wafer"] != selected_option_wafer):
    # 선택 값이 변경되면 슬롯 리셋
    st.session_state["coordinate_slots"] = {
        "position 1": None,
        "position 2": None,
        "position 3": None,
        "position 4": None,
    }
    st.session_state["last_selected_lot"] = selected_option_lot
    st.session_state["last_selected_wafer"] = selected_option_wafer
    st.session_state["active_slot"] = None
    st.session_state["ready_to_execute"] = False


# wafer 히트맵

# 좌표 단위 맞추기
df['DieX'] = df['DieX'].astype(int) - 12
df['DieY'] = df['DieY'].astype(int) - 11

condition = (df['Lot'] == selected_option_lot) & (df['Wafer'] == selected_option_wafer)
heatmap_data_mean = df[condition][['DieX', 'DieY', 'health_mean']]
heatmap_data_p1 = df[condition][['DieX', 'DieY', 'health_p1']]
heatmap_data_p2 = df[condition][['DieX', 'DieY', 'health_p2']]
heatmap_data_p3 = df[condition][['DieX', 'DieY', 'health_p3']]
heatmap_data_p4 = df[condition][['DieX', 'DieY', 'health_p4']]

# generate mask
pos_list = list(df.groupby(['DieX', 'DieY'])[['ufs_serial']].count().index)
mask = np.full((22, 55), False)

for i in pos_list:
    x, y = i
    mask[y, x] = True
#보간법
def interpolation(matrix, mask):
    from scipy.interpolate import griddata

    rows, cols = matrix.shape

    interpolation_mask = mask & np.isnan(matrix)

    valid_mask = ~np.isnan(matrix)
    x_valid, y_valid = np.meshgrid(np.arange(cols), np.arange(rows))
    points = np.array([x_valid[valid_mask], y_valid[valid_mask]]).T
    values = matrix[valid_mask]

    interp_points = np.array([x_valid[interpolation_mask], y_valid[interpolation_mask]]).T

    interpolated_values = griddata(points, values, interp_points, method='nearest')

    matrix[interpolation_mask] = interpolated_values
    return matrix

#메인 히트맵
main_matrix = np.full((22, 55), np.nan)
for i in heatmap_data_mean.values:
    x, y, c = int(i[0]), int(i[1]), i[2]
    main_matrix[y, x] = c
main_matrix = interpolation(main_matrix, mask)

#position 1~4 히트맵
position_1_matrix = np.full((22, 55), np.nan)
for i in heatmap_data_p1.values:
    x, y, c = int(i[0]), int(i[1]), i[2]
    position_1_matrix[y, x] = c
#보간
position_1_matrix = interpolation(position_1_matrix, mask)

position_2_matrix = np.full((22, 55), np.nan)
for i in heatmap_data_p2.values:
    x, y, c = int(i[0]), int(i[1]), i[2]
    position_2_matrix[y, x] = c
position_2_matrix = interpolation(position_2_matrix, mask)

position_3_matrix = np.full((22, 55), np.nan)
for i in heatmap_data_p3.values:
    x, y, c = int(i[0]), int(i[1]), i[2]
    position_3_matrix[y, x] = c
position_3_matrix = interpolation(position_3_matrix, mask)

position_4_matrix = np.full((22, 55), np.nan)
for i in heatmap_data_p4.values:
    x, y, c = int(i[0]), int(i[1]), i[2]
    position_4_matrix[y, x] = c
position_4_matrix = interpolation(position_4_matrix, mask)

#grid 생성
def make_grid(matrix, mask):
    n_rows, n_cols = matrix.shape
    shapes = []
    for i in range(n_rows):
        for j in range(n_cols):
            shapes.append(
                dict(
                    type="rect",
                    x0=j - 0.5,
                    x1=j + 0.5,
                    y0=i - 0.5,
                    y1=i + 0.5,
                    line=dict(
                        color="black",
                        width=0.1
                    )
                )
            )
    mask_f = mask.reshape(-1)

    for i in range(len(mask_f)):
        if mask_f[i] == False:
            shapes[i]['line']['width'] = 0
    return shapes

#히트맵 스케일 정규화
all_matrices = [position_1_matrix, position_2_matrix, position_3_matrix, position_4_matrix]
global_zmin = min(np.nanmin(matrix) for matrix in all_matrices)
global_zmax = max(np.nanmax(matrix) for matrix in all_matrices)

#큰 히트맵 생성
def create_heatmap(matrix, mask):
    #matrix = interpolation(matrix)
    heatmap_fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            zmin=0,
            zmax=0.007164373344815149,
            colorscale='Reds',
            colorbar=dict(
                #title="Value",
                tickfont=dict(color="black"))
        )
    )
    heatmap_fig.update_layout(
        shapes = make_grid(matrix, mask),
        xaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
        yaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
        width=500,
        height=400,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return heatmap_fig

#작은 히트맵 생성
def create_small_heatmap(matrix, mask):
    # matrix = interpolation(matrix)
    heatmap_fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            zmin = 0,
            zmax = 0.007164373344815149,
            colorscale='Reds',
            showscale = False,
            colorbar=dict(
                #title="Value",
                tickfont=dict(color="black"))
        )
    )
    heatmap_fig.update_layout(
        shapes=make_grid(matrix, mask),
        xaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
        yaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
        width=200,
        height=200,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return heatmap_fig
#
#컬러값 반환
def get_color_from_z(z_value, colormap, norm):
    """
    z값에 따른 컬러맵에서 색상을 반환 (HEX 형식)
    """
    if z_value is None:
        return "#FFFFFF"
    rgba_color = colormap(norm(z_value))  # RGBA 값
    hex_color = f"#{int(rgba_color[0]*255):02x}{int(rgba_color[1]*255):02x}{int(rgba_color[2]*255):02x}"
    return hex_color

#히트맵 레이아웃
with st.container():
    col1, col2 = st.columns(2)
    # 메인 히트맵 출력
    with col1:
        st.subheader("Selected Wafer's Heatmap")
        selected_matrix = None
        #활성화된 슬롯이 없을 때
        if st.session_state["active_slot"] is None:
            st.markdown(
                """
                <div style="display: flex; justify-content: center; align-items: center; height: 400px;">
                    <p style="font-size: 30px; color: gray;">Select Die Position!😀</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            heatmap_fig = None
        # 활성화된 슬롯별 보여줄 heatmap
        else:
            if st.session_state["active_slot"] == "position 1":
                selected_matrix = position_1_matrix
            elif st.session_state["active_slot"] == "position 2":
                selected_matrix = position_2_matrix
            elif st.session_state["active_slot"] == "position 3":
                selected_matrix = position_3_matrix
            elif st.session_state["active_slot"] == "position 4":
                selected_matrix = position_4_matrix
            else:
                selected_matrix = None
        # 보여줄 heatmap이 있을 때 (왼쪽 메인 히트맵 출력)
        if selected_matrix is not None:
            heatmap_fig = create_heatmap(selected_matrix, mask)
            selected_points = plotly_events(
                heatmap_fig,
                click_event=True,
                hover_event=False,
                select_event=False,
                override_width="500px",
            )

            # 클릭 이벤트 처리
            if selected_points:
                point = selected_points[0]
                x, y = int(point["x"]), int(point["y"])
                z = selected_matrix[y, x]
                # 중복값 체크
                already_selected = any(
                    slot and slot["x"] == x and slot["y"] == y
                    for slot_key, slot in st.session_state["coordinate_slots"].items()
                    if slot_key != st.session_state["active_slot"]  # 다른 active_slot에 선택된 좌표만 고려
                )

                if already_selected:
                    st.warning(f"X={x}, Y={y} is already selected!")

                else:
                    # die 선택에서 받아올 색상값들
                    colormap = plt.get_cmap('Reds')
                    norm = Normalize(vmin=global_zmin, vmax=global_zmax)
                    hex_color = get_color_from_z(z, colormap, norm)

                    # 선택된 좌표와 색상 저장
                    st.session_state["coordinate_slots"][st.session_state["active_slot"]] = {
                        "x": x,
                        "y": y,
                        "z": z,
                        "color": hex_color,
                    }
    # 작은 히트맵 출력
    with col2:
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write("Heatmap - Position 1")
            heatmap_1_fig = create_small_heatmap(position_1_matrix, mask)
            st.plotly_chart(heatmap_1_fig, use_container_width=True, key="heatmap_1")
        with subcol2:
            st.write("Heatmap - Position 2")
            heatmap_2_fig = create_small_heatmap(position_2_matrix, mask)
            st.plotly_chart(heatmap_2_fig, use_container_width=True, key="heatmap_2")
        subcol3, subcol4 = st.columns(2)
        with subcol3:
            st.write("Heatmap - Position 3")
            heatmap_3_fig = create_small_heatmap(position_3_matrix, mask)
            st.plotly_chart(heatmap_3_fig, use_container_width=True, key="heatmap_3")
        with subcol4:
            st.write("Heatmap - Position 4")
            heatmap_4_fig = create_small_heatmap(position_4_matrix, mask)
            st.plotly_chart(heatmap_4_fig, use_container_width=True, key="heatmap_4")

# die 좌표 선택하기
st.subheader("Select Die Position")
# 모든 슬롯이 채워졌는지 확인
all_slots_filled = True
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        for slot_key, current_value in st.session_state["coordinate_slots"].items():
            current_value = st.session_state["coordinate_slots"][slot_key]
            with st.container():

                subcol1, subcol2 = st.columns([2, 1])
                with subcol1:
                    #current_value값이 있을 때
                    if current_value:
                        #색상 출력
                        hex_color = current_value["color"]
                        #선택된 좌표 출력
                        st.markdown(
                            f"""
                            <div style="
                                background-color: {hex_color};
                                background-size: cover;
                                background-position: center;
                                padding: 10px;
                                border-radius: 5px;
                            ">
                                <p style="
                                    margin: 0; 
                                    color: white; 
                                    font-size: 14px; 
                                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* 그림자 설정 */
                                    font-weight: bold; /* 필요에 따라 추가 */
                                ">
                                    {slot_key}: X={current_value['x']}, Y={current_value['y']}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    #선택된 좌표가 없을 때
                    else:
                        st.markdown(
                            f"""
                            <div style="
                                background-size: cover;
                                background-position: center;
                                padding: 10px;
                                border-radius: 5px;
                            ">
                                <p style="margin: 0; color: black; font-size: 14px;">
                                    {slot_key}: Select one Die
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        all_slots_filled = False
                with subcol2:
                    # 선택된 좌표가 있으면 삭제버튼 활성화
                    if current_value:
                        # 삭제 버튼을 눌렀을 때
                        if st.button(f"DELETE", key=f"delete_{slot_key}"):
                            #해당 slot_key 값 -> None
                            st.session_state["coordinate_slots"][slot_key] = None
                            #active_slot이 현재 슬롯과 동일하면 초기화
                            if st.session_state.get("active_slot") == slot_key:
                                st.session_state["active_slot"] = None
                            #슬롯 상태 확인
                            st.session_state["ready_to_execute"] = all(
                                value is not None for value in st.session_state["coordinate_slots"].values()
                            )
                            st.rerun()
                    else:
                        # 좌표 선택 버튼
                        if st.button(f"SELECT", key=f"select_{slot_key}"):
                            st.session_state["active_slot"] = slot_key
                            #슬롯 상태 확인
                            st.session_state["ready_to_execute"] = all(
                                value is not None for value in st.session_state["coordinate_slots"].values()
                            )
                            st.rerun()
    with col2:
        st.session_state["ready_to_execute"] = all(
            value is not None for value in st.session_state["coordinate_slots"].values()
        )
        z_mean = None
        # 실행 영역
        with st.container():
            if st.session_state["ready_to_execute"]:
                if st.button("RUN🏃‍♀️"):
                    z_values = [
                        coord["z"]
                        for coord in st.session_state["coordinate_slots"].values()
                        if coord is not None
                    ]
                    z_mean = sum(z_values) / len(z_values)
            else:
                st.button("RUN🏃‍♀️", disabled=True)
            #bad die threshold
            threshold = 0.007164373344815149
            #전체 health 평균
            health_mean = df["health_mean"].mean()
            #label 없애기
            st.markdown(
                """
                <style>
                div.stMetric > label {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            if z_mean is not None and threshold - z_mean < 0:
                z_mean_ratio = ((z_mean - health_mean) / health_mean) * 100
                with st.container():
                    metric_1, metric_2 = st.columns(2)
                    with metric_1:
                        st.subheader("Health vs.Average")
                        st.metric(
                            label=" ",
                            value=f"{z_mean:.4f}",
                            delta=f"{z_mean_ratio:.2f}%",
                            delta_color="inverse"
                        )
                    with metric_2:
                        st.subheader("Healthy")
                        st.metric(
                            label=" ",
                            value="❌"
                        )
            elif z_mean is not None and threshold - z_mean >= 0:
                z_mean_ratio = ((z_mean - health_mean) / health_mean) * 100
                with st.container():
                    metric_1, metric_2 = st.columns(2)
                    with metric_1:
                        st.subheader("Health vs.Average")
                        st.metric(
                            label=" ",
                            value=f"{z_mean:.4f}",
                            delta=f"{z_mean_ratio:.4f}%",
                            delta_color="inverse"
                        )
                    with metric_2:
                        st.subheader("Healthy")
                        st.metric(
                            label=" ",
                            value="⭕️"
                        )
            else:
                with st.container():
                    metric_1, metric_2 = st.columns(2)
                    with metric_1:
                        st.subheader("Health vs.Average")
                        st.metric(
                            label=" ",
                            value="❓"
                        )
                    with metric_2:
                        st.subheader("Healthy")
                        st.metric(
                            label=" ",
                            value="❓"
                        )