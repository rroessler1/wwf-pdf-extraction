import io
import streamlit as st
import os
import zipfile

from datetime import date
from calendar import week as calendar_week
from settings.constants import PROCESSABLE_FILE_EXTENSIONS


def show_upload_page():
    # File uploader for PDF and image files
    uploaded_file = st.file_uploader("Upload your zipfile", type=["zip"])

    # Placeholder for further processing
    if uploaded_file and st.button("Process Data"):
        st.success(f"Here are the files to process: {get_files_in_zip(uploaded_file)}")

def get_files_in_zip(uploaded_zipfile):
    with zipfile.ZipFile(io.BytesIO(uploaded_zipfile.read())) as zf:
        file_list = zf.namelist()
        print("Files in zip:", file_list)
        return [f for f in file_list if do_process_file(f)]


def do_process_file(file_name):
    _, ext = os.path.splitext(file_name)
    print(ext)
    return str.lower(ext) in PROCESSABLE_FILE_EXTENSIONS
