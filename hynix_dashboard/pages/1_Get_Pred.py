import streamlit as st
import zipfile
import os
import pandas as pd


csv_files = ["hynix_dashboard/data/position_1.csv", "hynix_dashboard/data/position_2.csv", "hynix_dashboard/data/position_3.csv", 'hynix_dashboard/data/position_4.csv']
cache_file = "df.pkl"

# 캐시 파일이 존재하면 로드, 없으면 병합 후 저장
if os.path.exists(cache_file):
    print(f"{cache_file}에서 병합된 데이터프레임 불러오는 중...")
    df = pd.read_pickle(cache_file)
else:
    print("CSV 파일 병합 중...")
    # 데이터프레임 병합
    dataframes = [pd.read_csv(file) for file in csv_files]
    df = pd.concat(dataframes, axis=0)  # 행 기준으로 병합

    # 병합된 데이터프레임 저장
    df.to_pickle(cache_file)
    print(f"{cache_file}에 병합된 데이터프레임 저장 완료.")


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