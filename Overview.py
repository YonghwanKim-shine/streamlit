import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="WT dashboard",
    page_icon="🍔",
    layout="wide"
)

### 📘 하단 영역 (배경 포함)

# 📘 이미지와 설명 텍스트 추가
image_paths = [
    "heatmap_images/heatmap_1.png",
    "heatmap_images/heatmap_2.png",
    "heatmap_images/heatmap_3.png",
    "heatmap_images/heatmap_4.png",
    "heatmap_images/heatmap_5.png"
]

# feature 이름 (하드코딩된 상태, 대체 해야함)
image_descriptions = [
    "X1",
    "X2",
    "X3",
    "X4",
    "X5"
]

# 📘 HTML 코드 생성 (f-string 방식)
image_html = ''.join([
    f"""
    <div class="image-item">
        <img src="{image_path}" alt="Image {i+1}">
        <p class="image-caption">{image_descriptions[i]}</p>
    </div>
    """ for i, image_path in enumerate(image_paths)
])



# 📘 CSS 스타일 정의
components.html(f"""
    <style>
    .section {{
        background-color: #F5F5F5;  
        padding: 30px;  
        border-radius: 15px;  
        margin-bottom: 20px; 
    }}
    .section-title {{
        font-size: 24px;
        color: #FF8C00;
    }}
    </style>
    </head>
    <body>
        <div class="section">
            <h1 class="section-title">📋 이미지 영역</h1>
            <div class="image-container">
                {image_html}
            </div>
        </div>
    </body>
    </html>
""", height = 600)
            #unsafe_allow_html=True)


#
# # 📘 박스 시작 (모든 이미지를 하나의 박스에 포함)
# st.markdown(f"""
#     <div class="section">
#         <h1 class="section-title">📋 이미지 영역</h1>
#         <div class="image-container">
#             {image_html}  <!-- 여기에 for문으로 만든 HTML이 들어감 -->
#         </div>
#     </div>
# """, unsafe_allow_html=True)