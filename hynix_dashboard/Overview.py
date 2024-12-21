import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# 페이지 기본 설정
st.set_page_config(
    page_title="Wafer Test Overview",
    page_icon="https://img.icons8.com/emoji/48/000000/hamburger-emoji.png",
    layout="wide"
)


# GitHub Personal Access Token (PAT)
github_token = "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"

username = "jiyoung-data"
repo = "hynix-streamlit"

# 앞단


image_paths = [
    "hynix_dashboard/heatmap_images/heatmap_1.png",
    "hynix_dashboard/heatmap_images/heatmap_2.png",
    "hynix_dashboard/heatmap_images/heatmap_3.png",
    "hynix_dashboard/heatmap_images/heatmap_4.png",
    "hynix_dashboard/heatmap_images/heatmap_5.png"
]


### feature 이름 (하드코딩된 상태, 대체 해야함)
image_descriptions = [
    "X1",
    "X2",
    "X3",
    "X4",
    "X5"
]
# GitHub API에서 이미지 가져오기
@st.cache_data
def fetch_image_from_github(username, repo, path, token):
    # GitHub API URL
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Base64로 인코딩된 이미지 데이터 추출
        image_data = response.json().get("content")
        if image_data:
            try:
                return BytesIO(base64.b64decode(image_data))
            except Exception as e:
                st.error(f"Decoding Error: {e}")
                return None
    else:
        st.error(f"Error {response.status_code}: Unable to fetch {path}")
        return None

# Streamlit UI
st.title("WT Dashboard")

cols = st.columns(len(image_paths))

# 이미지 출력
for i, image_path in enumerate(image_paths):
    with cols[i]:
        image_bytes = fetch_image_from_github(username, repo, image_path, github_token)
        if image_bytes:
            image = Image.open(image_bytes)
            st.image(image, caption=image_descriptions[i], width=150)
