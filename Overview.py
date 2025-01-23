import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit import container
from streamlit_plotly_events import plotly_events
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import base64

# 페이지 레이아웃 설정
st.set_page_config(
    page_title="WT Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS 설정
def load_css(file_name):
    with open(file_name, "r", encoding='utf-8') as f:
        return f"<style>{f.read()}</style>"


css = load_css('hynix_dashboard/pages/overview.css')
st.markdown(css, unsafe_allow_html=True)

st.title("📈 OverView")
st.markdown("## Trend")

# Google Drive 링크 및 데이터 다운로드 함수
url = "https://drive.google.com/uc?id=1G8PbWznfU6G3b756Bdm--iLUK_oBcqTd"


def download_file(url, output_path):
    import gdown
    gdown.download(url, output_path, quiet=False)
    return output_path


@st.cache_data
def load_file():
    file_path = download_file(url, "dashboard_data.csv")
    df_data = pd.read_csv(file_path)
    return df_data


# 데이터 로드
df_data = load_file()

# 데이터 처리 및 bad_ratio 계산
df_data[['Lot', 'Wafer', 'DieX', 'DieY']] = df_data['run_wf_xy'].str.split('_', expand=True)
df_data.loc[:, 'DieX'] = df_data.loc[:, 'DieX'].astype(int) - 12
df_data.loc[:, 'DieY'] = df_data.loc[:, 'DieY'].astype(int) - 11
df_data['Bad'] = df_data['health'] > 0.007164373344815149
df_data["X1086"] = pd.to_datetime(df_data["X1086"], format='%Y%m%d')

wafer_bad_stats = (
    df_data.groupby(['Lot', 'Wafer'])
    .agg(total_count=('health', 'count'), bad_count=('Bad', 'sum'))
    .reset_index()
)
wafer_bad_stats['bad_ratio'] = (wafer_bad_stats['bad_count'] / wafer_bad_stats['total_count'])*100

# 상위 10개 Wafer 추출
top_10_bad_wafers = wafer_bad_stats.sort_values(by='bad_ratio', ascending=False).head(10)

# 초기 상태 설정
if "selected_wafer" not in st.session_state:
    st.session_state.selected_wafer = {
        "Lot": top_10_bad_wafers.iloc[0]["Lot"],
        "Wafer": top_10_bad_wafers.iloc[0]["Wafer"],
    }



dates = pd.date_range(
    start=df_data["X1086"].min(),
    end=df_data["X1086"].max()
)  # 날짜만 남김

values = df_data.groupby("X1086")["health"].mean().values
dummy_df = pd.DataFrame({
    "Date": dates,
    "Value": values
})
dummy_df["Date"] = pd.to_datetime(dummy_df["Date"])
dummy_df.set_index("Date", inplace=True)
dummy_df.index = dummy_df.index.strftime('%Y-%m-%d')

# 첫 번째 container
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Weekly Health Trend")
        date_fig = go.Figure()
        date_fig.add_trace(go.Scatter(
            x=dummy_df.index,
            y=dummy_df["Value"],
            mode='lines+markers',
            name="Line",
            line=dict(color="#FF731C", width=2))
        )
        # y축 범위 지정
        y_min = dummy_df["Value"].min() * 0.9  # 최소값의 90%
        y_max = dummy_df["Value"].max() * 1.1
        date_fig.update_yaxes(
            range=[y_min, y_max],
            tickfont=dict(color="black"))
        date_fig.update_xaxes(
            tickangle=0,
            tickformat='%Y-%m-%d',
            tickmode='array',
            tickvals=dummy_df.index,
            tickfont=dict(color="black"))
        date_fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),  # 모든 방향의 여백을 최소화
            height=400  # 그래프 높이 조정
        )
        st.plotly_chart(date_fig)

    with col2:
        st.subheader("Daily Defect Rate")

        dates = pd.to_datetime(sorted(df_data["X1086"].unique(), reverse=True)).strftime('%Y-%m-%d')
        selected_date_str = st.selectbox('Date', dates)
        selected_date = pd.to_datetime(selected_date_str)
        today_bad_health = df_data[df_data["X1086"] == selected_date]["health"].mean()
        yesterday_date = selected_date - pd.Timedelta(days=1)

        if yesterday_date in df_data["X1086"].unique():
            yesterday_bad_health = df_data[df_data["X1086"] == yesterday_date]["health"].mean()
        else:
            yesterday_bad_health = None

        # 오늘과 어제의 불량률 계산
        if yesterday_bad_health is not None:
            rate_diff = (today_bad_health * 10000) - (yesterday_bad_health * 10000)  # 상승/하락 계산
            st.metric(label="Selected Date's rate", value=f"{today_bad_health * 10000:.2f} ppm",
                      delta=f"{rate_diff:.2f} ppm")
            st.metric(label="Previous Date's rate", value=f"{yesterday_bad_health * 10000:.2f} ppm")
        else:
            st.metric(label="Selected Date's rate", value=f"{today_bad_health * 10000:.2f} ppm", delta=0)
            st.metric(label="Previous Date's rate", value="-")

# 두 번째 container
st.markdown("## Insight")
col_left, col_right = st.columns([1, 1])

important_features_select = ["X1049", "X1085", "X561", "X592", "X1071"]  # 여기에 원하는 5개 컬럼 이름 입력


# 중요 피처 계산 함수
def calculate_important_features(selected_lot, selected_wafer, feature_columns):
    selected_wafer_data = df_data[(df_data['Lot'] == selected_lot) & (df_data['Wafer'] == selected_wafer)]
    important_features = {
        feature: [df_data[feature].mean(), selected_wafer_data[feature].mean()]
        for feature in feature_columns
    }
    return important_features


# 중요 피처 계산
important_features = calculate_important_features(
    st.session_state.selected_wafer["Lot"],
    st.session_state.selected_wafer["Wafer"],
    important_features_select
)

def calculate_anomaly_features(selected_lot, selected_wafer):
    selected_wafer_data = df_data[(df_data['Lot'] == selected_lot) & (df_data['Wafer'] == selected_wafer)]

    numeric_data = df_data.select_dtypes(include=[np.number])
    selected_numeric_data = selected_wafer_data.select_dtypes(include=[np.number])

    overall_mean = numeric_data.mean()
    selected_mean = selected_numeric_data.mean()

    percent_diff = (selected_mean - overall_mean).abs() / overall_mean
    top_anomalies = percent_diff.nlargest(5).index
    return {feature: [overall_mean[feature], selected_mean[feature]] for feature in top_anomalies}




if "anomaly_features" not in st.session_state:
    st.session_state.anomaly_features = calculate_anomaly_features(
        st.session_state.selected_wafer["Lot"],
        st.session_state.selected_wafer["Wafer"]
    )

with col_left:
    # Bad Wafer Top 10
    st.subheader("Bad Wafer Top 10")
    st.info("Select the bar chart of a Wafer for further detailed view ")
    # top_10_bad_wafers = top_10_bad_wafers.sort_values(by="bad_ratio", ascending=False)
    labels = [f"Lot: {lot}, Wafer: {wafer}" for lot, wafer in zip(top_10_bad_wafers['Lot'], top_10_bad_wafers['Wafer'])]
    values = top_10_bad_wafers['bad_ratio'].values

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker=dict(color='#FF731C'),
        # 소수점 2번째자리까지
        text=[f"{label},                                                                                                                                                                      {value:.2f}%" for label, value in zip(labels, values)],
        textposition='inside',
        textfont={"color":"black"}
    ))

    fig.update_yaxes(autorange="reversed")
    fig.update_yaxes(autorange="reversed", showticklabels=False)
    fig.update_layout(
        title="Top 10 Bad Wafer by Bad Ratio",
        xaxis_title="Bad Ratio",
        yaxis_title="Lot & Wafer",
        template="plotly_white"

    )

    # 클릭 이벤트 처리
    selected_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
    )

    # 클릭된 데이터 처리
    # 클릭된 데이터 처리
    # 클릭된 데이터 처리
    # 클릭 이벤트 처리
    if selected_points:
        selected_label = selected_points[0]["y"]
        selected_lot, selected_wafer = selected_label.split(", ")
        st.session_state.selected_wafer = {
            "Lot": selected_lot.split(": ")[1],
            "Wafer": selected_wafer.split(": ")[1],
        }

        # 클릭 이벤트 이후 anomaly_features 업데이트
        st.session_state.anomaly_features = calculate_anomaly_features(
            st.session_state.selected_wafer["Lot"],
            st.session_state.selected_wafer["Wafer"]
        )

        # 업데이트 확인


with col_right:

    # Wafer's Heatmap and Metrics in a single column
    # st.subheader(
    #     f"**Selected Wafer:** Lot {st.session_state.selected_wafer['Lot']}, Wafer {st.session_state.selected_wafer['Wafer']}")

    # Create two main sections for heatmap and metrics
    st.subheader("Selected Wafer & Anomaly Feature's Value")
    st.success(
       f"✅ Selected Wafer : Lot {st.session_state.selected_wafer['Lot']}, Wafer {st.session_state.selected_wafer['Wafer']}")
    heatmap_col, metrics_col = st.columns([2, 1])  # 비율 조정
    # Heatmap Section
    with heatmap_col:
        # st.subheader("Heatmap")
        selected_lot = st.session_state.selected_wafer["Lot"]
        selected_wafer_number = st.session_state.selected_wafer["Wafer"]
        heatmap_data = df_data[(df_data['Lot'] == selected_lot) & (df_data['Wafer'] == selected_wafer_number)]
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


        # 히트맵 생성 함수
        def create_heatmap(matrix, mask):
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
            heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=matrix,
                    colorscale='Reds',
                    zmin=0,
                    zmax=0.007164373344815149,
                    colorbar=dict(
                        #title="Value",
                        tickfont=dict(color="black")
                    )
                )
            )

            for i in range(len(mask_f)):
                if mask_f[i] == False:
                    shapes[i]['line']['width'] = 0
            heatmap_fig.update_layout(
                shapes=shapes,
                xaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
                yaxis=dict(showticklabels=False,showgrid=False,showline=False,zeroline=False),
                margin=dict(l=0, r=0, t=0, b=0)
            )

            return heatmap_fig


        # 히트맵 출력
        heatmap_fig = create_heatmap(heatmap_matrix, mask)
        st.plotly_chart(heatmap_fig, use_container_width=True)

    # Metrics Section
    with metrics_col:
        # st.subheader("Anomaly Features")
        # anomaly_features를 사용하여 상위 4개 st.metric 생성
        # anomaly_features를 사용하여 상위 4개 st.metric 생성
        for i, (key, values) in enumerate(st.session_state.anomaly_features.items()):

            if i >= 4:  # 상위 4개까지만 표시
                break
            if values[0] == 0:
                delta = 0
            else:
                delta = (values[1] - values[0]) / values[0]
            # values[0]은 전체 평균, values[1]은 선택된 웨이퍼 평균
            # delta_symbol = "▲" if delta > 0 else "▼"
            # delta_value = abs(delta) * 100  # delta의 절대값을 계산 후 퍼센트 변환

            # st.metric 생성
            st.metric(
                label=key,  # 피처 이름
                value=f"{values[1]:.4f}",
                # value=f"{values[1] * 100:.1f}%",  # 선택된 웨이퍼 평균값
                # delta=f"{delta_symbol} {delta_value:.1f}%"  # 변화량 표시
                delta=f"{delta * 100:.2f}%"
            )

st.markdown("### Featured Feature's Value")

# 중요 피처 시각화
# Total 값을 1로 고정하고 Selected 값을 Total 대비 퍼센티지로 계산
# 중요 피처
features = list(important_features.keys())
total_values = [v[0] for v in important_features.values()]
selected_values = [v[1] for v in important_features.values()]

# Total을 1로 정규화
normalized_selected_values = [sel / tot if tot != 0 else 0 for sel, tot in zip(selected_values, total_values)]

# 중요 피처 Figure 생성
important_fig = go.Figure(
    data=[
        go.Bar(
            x=features,
            y=normalized_selected_values,
            name="Wafer-to-Overall Mean Ratio",
            marker=dict(color="orange")
        )
    ]
)

important_fig.update_layout(
    title="Important Features",
    xaxis=dict(
        title=dict(
            text="Features",
            font=dict(color="black", size=16)
        ),
        tickfont=dict(color="black", size=14),
    ),
    yaxis=dict(
        title=dict(
            text="Value",
            font=dict(color="black", size=16)
        ),
        tickfont=dict(color="black", size=14),
    ),
    barmode="group",
    template="plotly_white",
    showlegend=True
)

# anomaly 피처
features = list(st.session_state.anomaly_features.keys())
total_values = [v[0] for v in st.session_state.anomaly_features.values()]
selected_values = [v[1] for v in st.session_state.anomaly_features.values()]

# Total을 1로 정규화
normalized_selected_values = [sel / tot if tot != 0 else 0 for sel, tot in zip(selected_values, total_values)]

# Anomaly Figure 생성
anomaly_fig = go.Figure(
    data=[
        
        go.Bar(
            x=features,
            y=normalized_selected_values,
            name="Wafer-to-Overall Mean Ratio",
            marker=dict(color="orange")
        )
    ]
)

anomaly_fig.update_layout(
    title="Anomaly Features",
    xaxis=dict(
        title=dict(
            text="Features",  # x축 제목
            font=dict(color="black", size=16)  # x축 제목의 색상과 크기
        ),
        tickfont=dict(color="black", size=14),  # x축 값(레이블)의 색상과 크기
    ),
    yaxis=dict(
        title=dict(
            text="Value",  # y축 제목
            font=dict(color="black", size=16)  # y축 제목의 색상과 크기
        ),
        tickfont=dict(color="black", size=14),  # y축 값(레이블)의 색상과 크기
    ),
    barmode="group",
    template="plotly_white",
    showlegend=True
)

# 차트 출력
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(important_fig, use_container_width=True)

with col2:
    st.plotly_chart(anomaly_fig, use_container_width=True)

