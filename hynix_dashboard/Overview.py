import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# 페이지 기본 설정
st.set_page_config(
    page_title="WT dashboard",
    page_icon="🍔",
    layout="wide"
)


# GitHub Personal Access Token (PAT)
github_token = "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"

username = "jiyoung-data"
repo = "hynix-streamlit"

# 앞단

## 📘 하단 영역 (배경 포함)

### 📘 이미지와 설명 텍스트 추가
# image_paths = [
#     "https://raw.githubusercontent.com/jiyoung-data/hynix-streamlit/main/hynix_dashboard/heatmap_images/heatmap_1.png",
#     "https://raw.githubusercontent.com/jiyoung-data/hynix-streamlit/main/hynix_dashboard/heatmap_images/heatmap_2.png",
#     "https://raw.githubusercontent.com/jiyoung-data/hynix-streamlit/main/hynix_dashboard/heatmap_images/heatmap_3.png",
#     "https://raw.githubusercontent.com/jiyoung-data/hynix-streamlit/main/hynix_dashboard/heatmap_images/heatmap_4.png",
#     "https://raw.githubusercontent.com/jiyoung-data/hynix-streamlit/main/hynix_dashboard/heatmap_images/heatmap_5.png"
# ]

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

# # 📘 함수: GitHub API에서 이미지 가져오기
# def fetch_image_from_github(username, repo, path, token):
#     url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"
#     headers = {"Authorization": f"token {token}"}
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         # Base64로 인코딩된 이미지 데이터 디코딩
#         image_data = response.json().get("content")
#         if image_data:
#             return BytesIO(base64.b64decode(image_data))
#     else:
#         st.error(f"Error {response.status_code}: Unable to fetch {path}")
#         return None
#
# # 📘 Streamlit UI
# st.title("WT Dashboard")
#
# # 📘 하단 영역: 이미지 출력
# st.markdown("### 📋 이미지 영역")
# cols = st.columns(len(image_paths))  # 이미지 갯수만큼 열 생성
#
# for i, image_path in enumerate(image_paths):
#     with cols[i]:
#         # GitHub에서 이미지 가져오기
#         image_bytes = fetch_image_from_github(USERNAME, REPO, image_path, GITHUB_TOKEN)
#         if image_bytes:
#             image = Image.open(image_bytes)
#             st.image(image, caption=image_descriptions[i], width=150)



# GitHub API에서 이미지 가져오기
def fetch_image_from_github(username, repo, path, token):
    # GitHub API URL
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)

    # 디버깅: 요청 정보 출력
    st.write(f"Request URL: {url}")
    st.write(f"Response Status Code: {response.status_code}")

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

# ### 📘 HTML 코드 생성 (f-string 방식)
# image_html = ''.join([
#     f"""
#     <div class="image-item">
#         <img src="{image_path}" alt="Image {i+1}">
#         <p class="image-caption">{image_descriptions[i]}</p>
#     </div>
#     """ for i, image_path in enumerate(image_paths)
# ])
#


# ### 📘 CSS 스타일 정의
# st.markdown(f"""
#     <div class="section">
#         <h1 class="section-title">📋 이미지 영역</h1>
#         <div class="image-container">
#             {image_html}
#         </div>
#     </div>
# """, unsafe_allow_html=True)



