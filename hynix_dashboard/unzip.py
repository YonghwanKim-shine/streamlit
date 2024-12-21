import streamlit as st
import zipfile
import os
import pandas as pd

# ZIP 파일 경로 및 출력 디렉토리
zip_file_path = "data/position.zip"
output_dir = "data"

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