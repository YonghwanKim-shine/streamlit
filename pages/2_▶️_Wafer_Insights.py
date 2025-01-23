import pathlib
import pandas as pd
import numpy as np
import gdown
import streamlit as st
from plotly.colors import make_colorscale
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.set_page_config(
    page_title="WT Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# CSS 설정 함수
def load_css(file_name):
    with open(file_name, "r", encoding='utf-8') as f:
        return f"<style>{f.read()}</style>"

# CSS 파일 로드
css = load_css('hynix_dashboard/pages/columns_pred_style.css')
st.markdown(css, unsafe_allow_html=True)

# Google Drive 공유 링크
url = "https://drive.google.com/uc?id=1G8PbWznfU6G3b756Bdm--iLUK_oBcqTd"

def download_file(url, output_path):
    gdown.download(url, output_path, quiet=False)
    return output_path

@st.cache_data
def load_file():
    file_path = download_file(url, "dashboard_data.csv")
    df_data = pd.read_csv(file_path)
    return df_data

# 데이터 불러오기
df_data = load_file()

# 'run_wf_xy'에서 Lot, Wafer, DieX, DieY 분리
df_data[['Lot', 'Wafer', 'DieX', 'DieY']] = df_data['run_wf_xy'].str.split('_', expand=True)
df_data.loc[:, 'DieX'] = df_data.loc[:, 'DieX'].astype(int) - 12
df_data.loc[:, 'DieY'] = df_data.loc[:, 'DieY'].astype(int) - 11
# Lot별 Wafer 딕셔너리 생성
lot_wafer_dict = df_data.groupby('Lot')['Wafer'].apply(lambda x: sorted(map(str, map(int, x.unique())))).to_dict()

# Streamlit 상태 관리 초기화
if "selected_feature_name" not in st.session_state:
    st.session_state.selected_feature_name = "X1049"  # 초기 선택 컬럼
if "recent_click" not in st.session_state:
    st.session_state.recent_click = None

# Streamlit UI 구성
st.title("💡Wafer Insights")

# 로트 및 웨이퍼 선택 가로 레이아웃
col1, col2 = st.columns([1, 1])

with col1:
    selected_lot = st.selectbox("Lot", options=list(lot_wafer_dict.keys()))

with col2:
    selected_wafer = st.selectbox(
        "Wafer",
        options=sorted(lot_wafer_dict.get(selected_lot, []), key=lambda x: int(x))
    )


# 중요 피처 할당
important_features_select = ["X1049", "X1085", "X561", "X592", "X1071"]

# 중요 피처 계산 함수
def calculate_important_features(selected_lot, selected_wafer, feature_columns):
    selected_wafer_data = df_data[(df_data['Lot'] == selected_lot) & (df_data['Wafer'] == selected_wafer)]
    important_features = {
        feature: [df_data[feature].mean(), selected_wafer_data[feature].mean()]
        for feature in feature_columns
    }
    return important_features

# anomaly feature 계산 함수
def calculate_anomaly_features(selected_lot, selected_wafer):
    selected_wafer_data = df_data[(df_data['Lot'] == selected_lot) & (df_data['Wafer'] == selected_wafer)]

    numeric_data = df_data.select_dtypes(include=[np.number])
    selected_numeric_data = selected_wafer_data.select_dtypes(include=[np.number])

    overall_mean = numeric_data.mean()
    selected_mean = selected_numeric_data.mean()

    percent_diff = (selected_mean - overall_mean).abs() / overall_mean
    top_anomalies = percent_diff.nlargest(5).index
    return {feature: [overall_mean[feature], selected_mean[feature]] for feature in top_anomalies}

# 중요 피처와 이상 피처 데이터 계산
important_features = calculate_important_features(selected_lot, selected_wafer, important_features_select)
anomaly_features = calculate_anomaly_features(selected_lot, selected_wafer)

# 중요 피처 및 이상 피처 클릭 이벤트 처리
st.markdown("### Featured Feature's Value")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    features = list(important_features.keys())

    # total_values를 1로 고정
    total_values = [1 for _ in important_features.values()]

    # selected_values를 퍼센티지로 계산
    selected_values = [
        (v[1] / v[0]  if v[0] != 0 else 0) for v in important_features.values()
    ]

    # Figure 생성
    important_fig = go.Figure(
        data=[

            go.Bar(
                x=features,
                y=selected_values,
                name="Wafer-to-Overall Mean Ratio",
                marker=dict(color="orange")
            )
        ]
    )

    # Layout 설정
    important_fig.update_layout(
        title="Important Feature",
        xaxis_title="Features",
        yaxis_title="Value",
        barmode="group",
        template="plotly_white",
        showlegend=True
    )

    important_clicked = plotly_events(important_fig, click_event=True)

with chart_col2:
    features = list(anomaly_features.keys())

    # total_values를 1로 고정
    total_values = [1 for _ in anomaly_features.values()]

    # selected_values를 퍼센티지로 계산
    selected_values = [
        (v[1] / v[0]  if v[0] != 0 else 0) for v in anomaly_features.values()
    ]

    # Figure 생성
    anomaly_fig = go.Figure(
        data=[

            go.Bar(
                x=features,
                y=selected_values,
                name="Wafer-to-Overall Mean Ratio",
                marker=dict(color="orange")
            )
        ]
    )

    # Layout 설정
    anomaly_fig.update_layout(
        title="Anomaly Feature",
        xaxis_title="Features",
        yaxis_title="Value",
        barmode="group",
        template="plotly_white",
        showlegend=True
    )

    anomaly_clicked = plotly_events(anomaly_fig, click_event=True)

# 클릭 이벤트 처리 후 상태 업데이트
last_click_event = None

if important_clicked and important_clicked[0].get('x'):
    last_click_event = {"feature_name": important_clicked[0]['x'], "source": "important"}

if anomaly_clicked and anomaly_clicked[0].get('x'):
    last_click_event = {"feature_name": anomaly_clicked[0]['x'], "source": "anomaly"}

# 상태 업데이트
if last_click_event:
    st.session_state.selected_feature_name = last_click_event["feature_name"]
    st.session_state.recent_click = last_click_event["source"]

# 히트맵 및 메트릭스, 박스플롯 레이아웃
main_col1, main_col2 = st.columns([1, 1])

# Heatmap 및 Metrics Section
with main_col1:
    heatmap_col, metrics_col = st.columns([2, 1])

    with heatmap_col:
        st.markdown("### HeatMap")
        heatmap_data = df_data[(df_data['Lot'] == selected_lot) & (df_data['Wafer'] == selected_wafer)]
        heatmap_matrix = np.full((22, 55), np.nan)

        for i in heatmap_data[['DieX', 'DieY', 'health']].values:
            x, y, c = int(i[0]), int(i[1]), i[2]
            heatmap_matrix[y, x] = c

        # generate mask
        pos_list = list(df_data.groupby(['DieX', 'DieY'])[['ufs_serial']].count().index)
        mask = np.full((22, 55), False)

        for i in pos_list:
            x, y = i
            mask[y, x] = True

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

        heatmap_matrix = interpolation(heatmap_matrix, mask)

        def create_heatmap(matrix, mask):
            # z_mean = np.nanmean(matrix)  # NaN을 제외한 평균 계산
            # z_std = np.nanstd(matrix)  # NaN을 제외한 표준편차 계산
            #
            #
            # zmax_value = z_mean + z_std
            zmax_value = 0.007164373344815149
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
                                width=1
                            )
                        )
                    )

            mask_f = mask.reshape(-1)

            for i in range(len(mask_f)):
                if mask_f[i] == False:
                    shapes[i]['line']['width'] = 0

            heatmap_fig = go.Figure(data=go.Heatmap(
                z=matrix,
                colorscale="Reds",
                zmin=0,
                zmax=zmax_value,
                colorbar=dict(
                #title="Value",
                tickfont=dict(color="black"))
            ))
            heatmap_fig.update_layout(
                shapes=shapes,
                xaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
                yaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
                width=400,
                height=430,
            )
            return heatmap_fig

        heatmap_fig = create_heatmap(heatmap_matrix, mask)
        st.plotly_chart(heatmap_fig, use_container_width=True)

    with metrics_col:
        st.markdown("### Metrics")
        for i, (key, values) in enumerate(anomaly_features.items()):
            if i >= 4:
                break
            if values[0] == 0:
                delta = 0
            else:
                delta = (values[1] - values[0]) / values[0]

            st.metric(
                label=key,
                value=f"{values[1]:.4f}",
                delta=f"{delta*100:.2f}%"
            )

# 박스플롯 Section
with main_col2:
    st.markdown("### Box Plot")

    filtered_data = df_data[(df_data['Lot'] == selected_lot) & (df_data['Wafer'] == selected_wafer)]

    total_values = df_data[st.session_state.selected_feature_name]
    selected_values = filtered_data[st.session_state.selected_feature_name]

    box_fig = go.Figure()
    box_fig.add_trace(go.Box(
        y=selected_values,
        name=f"Selected ({st.session_state.selected_feature_name})",
        marker_color="orange"
    ))
    box_fig.add_trace(go.Box(
        y=total_values,
        name="Total",
        marker_color="tomato"
    ))
    box_fig.update_layout(
        yaxis=dict(
            #title="Value",
            tickfont=dict(color="black",size=12),
            titlefont=dict(color="black")
        ),
        xaxis=dict(
            tickfont=dict(color="black", size=12),
            titlefont=dict(color="black")
        ),
        template="plotly_white",
        width=800,
        height=430,
    )
    st.plotly_chart(box_fig, use_container_width=True)
