import streamlit as st
import zipfile
import os
import pandas as pd

# ZIP 파일 경로 및 출력 디렉토리
zip_file_path = "../data/position.zip"
output_dir = "../data"

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 압축 해제
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    # ZIP 파일 내부 파일 목록 확인
    file_list = zip_ref.namelist()

    # 파일 추출 및 저장
    for file_name in file_list:
        # 디렉토리 생성
        extracted_file_path = os.path.join(output_dir, file_name)
        os.makedirs(os.path.dirname(extracted_file_path), exist_ok=True)

        # 파일 추출
        with zip_ref.open(file_name) as source, open(extracted_file_path, 'wb') as target:
            target.write(source.read())



csv_files = ["../data/position_1.csv", "../data/position_2.csv", "../data/position_3.csv", "../data/position_4.csv"]
cache_file = "df.pkl"

# 캐시 파일이 존재하면 로드, 없으면 병합 후 저장
if os.path.exists(cache_file):
    df = pd.read_pickle(cache_file)
else:
    # 데이터프레임 병합
    dataframes = [pd.read_csv(file) for file in csv_files]
    df = pd.concat(dataframes, axis=0)  # 행 기준으로 병합

    # 병합된 데이터프레임 저장
    df.to_pickle(cache_file)

print(df)

# 목록 불러오는 기능
df[['Lot', 'Wafer', 'DieX', 'DieY']] = df['run_wf_xy'].str.split('_', expand=True)
#print(df)

lot_list = df['Lot'].unique()
print(lot_list)

wafer_list = df['Wafer'].unique()
wafer_list = sorted(list(map(int, wafer_list)))
print(wafer_list)


# 앞단
# 페이지 기본 설정
st.set_page_config(
    page_title="WT Dashboard",
    page_icon="🍔",
    layout="wide"
)

st.title("Get Pred")

selected_option = st.selectbox('Lot', lot_list)
#st.selectbox('Wafer', wafer_list)
st.write('Lot', selected_option)