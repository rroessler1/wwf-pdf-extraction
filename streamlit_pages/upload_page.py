import streamlit as st
import os
from datetime import date
from calendar import week as calendar_week

def show_upload_page():
    # Set up the Streamlit page
    st.title("Leaflet Upload")

    # File uploader for PDF and image files
    uploaded_file = st.file_uploader("Upload your file", type=["pdf", "jpg", "jpeg", "png"])

    # Dropdown for selecting a supermarket
    supermarkets = ["Aldi", "Coop", "Denner", "Lidl", "Migros", "Volg"]
    selected_supermarket = st.radio("Select a supermarket", supermarkets)

    # Date picker for choosing a date
    selected_date = st.date_input("Choose a date", value=date.today())

    # Display selected inputs
    st.write("### Selected Options")
    st.write("Supermarket:", selected_supermarket)
    st.write("Date:", selected_date)

    # Placeholder for further processing
    if uploaded_file and st.button("Process Data"):
        # Calculate the calendar week and year
        calendar_week_number = selected_date.isocalendar()[1]
        year = selected_date.year

        # Create the folder path
        base_folder = "pdf-files"
        folder_name = f"{selected_supermarket}_KW{calendar_week_number}_{year}"
        target_folder = os.path.join(base_folder, folder_name)

        # Ensure the folder is unique
        counter = 1
        while os.path.exists(target_folder):
            target_folder = os.path.join(base_folder, f"{folder_name}_{counter}")
            counter += 1

        # Create the folder
        os.makedirs(target_folder, exist_ok=True)

        # Process the uploaded file
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == "pdf":
            # Save PDF with the original name
            target_file_path = os.path.join(target_folder, uploaded_file.name)
        else:
            # Save images with the next available number as the filename
            existing_files = [f for f in os.listdir(target_folder) if f.split('.')[-1].lower() in ["jpg", "jpeg", "png"]]
            existing_numbers = [int(f.split('.')[0]) for f in existing_files if f.split('.')[0].isdigit()]
            next_number = 1 if not existing_numbers else max(existing_numbers) + 1
            target_file_path = os.path.join(target_folder, f"{next_number}.{file_extension}")

        # Save the file
        with open(target_file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"File saved successfully to {target_file_path}")



