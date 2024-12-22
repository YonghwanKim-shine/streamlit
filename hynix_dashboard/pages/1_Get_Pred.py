import pandas as pd
import gdown
import streamlit as st

# Google Drive 공유 링크
url_position_1 = "https://drive.google.com/uc?id=1ajvBW_OH96xtlJZ9aronGZsbtRJkuswp"
url_position_2 = "https://drive.google.com/uc?id=19YOKChOwa4S6ynO00SKauMPaZtfPuQkC"
url_position_3 = "https://drive.google.com/uc?id=1Q0S8UAyvX7cHsOAbhcS026y0EFHmByCK"
url_position_4 = "https://drive.google.com/uc?id=18KindmSQqoQuu4iV7ySE9q4cETC10Lf5"

# 파일 다운로드
@st.cache_data
def download_file(url, output_path):
    gdown.download(url, output_path, quiet=False)
    return output_path

file_path_1 = download_file(url_position_1, "position_1.csv")
file_path_2 = download_file(url_position_2, "position_2.csv")
file_path_3 = download_file(url_position_3, "position_3.csv")
file_path_4 = download_file(url_position_4, "position_4.csv")

df1 = pd.read_csv(file_path_1)
df2 = pd.read_csv(file_path_2)
df3 = pd.read_csv(file_path_3)
df4 = pd.read_csv(file_path_4)

st.write(df1.head())
st.write(df2.head())
st.write(df3.head())
st.write(df4.head())