import streamlit as st

from streamlit_pages.check_results_page import show_check_results_page
from streamlit_pages.settings_page import show_settings_page
from streamlit_pages.upload_page import show_upload_page
from streamlit_pages.ui_main_pipeline import main

# Set up the Streamlit page title
st.title("Barbeque Discount Data Analysis")

# Sidebar navigation
st.sidebar.title("Navigation")
navigation = st.sidebar.radio("Go to", ["Upload Leaflets", "Run Data Extraction", "Manual Error Check", "Settings"])

# Show the selected page
if navigation == "Upload Leaflets":
    show_upload_page()
elif navigation == "Run Data Extraction":
    main()
elif navigation == "Manual Error Check":
    show_check_results_page()
elif navigation == "Settings":
    show_settings_page()
