import streamlit as st
import pandas as pd
from PIL import Image

def show_check_results_page():
    # Load the data from csv file
    result_csv_path = 'pdf-files/results.csv'
    data = pd.read_csv(result_csv_path)

    # Ensure 'page_number' and 'categorization_all_same' columns are present in the dataframe
    if 'page_number' not in data.columns or 'categorization_all_same' not in data.columns:
        st.error("The dataframe must have 'page_number' and 'categorization_all_same' columns.")
        st.stop()

    # Get the unique page numbers
    unique_pages = sorted(data['page_number'].unique())

    # Initialize session state for current page index if not already set
    if 'current_page_index' not in st.session_state:
        st.session_state.current_page_index = 0

    # Navigation buttons for switching between images
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous Image") and st.session_state.current_page_index > 0:
            st.session_state.current_page_index -= 1
    with col2:
        if st.button("Next Image") and st.session_state.current_page_index < len(unique_pages) - 1:
            st.session_state.current_page_index += 1

    # Get the current page number based on session state index
    current_page_number = unique_pages[st.session_state.current_page_index]

    # Filter the dataframe based on the current page number and categorization_all_same == True
    filtered_data = data[(data['page_number'] == current_page_number) & (data['categorization_all_same'] == True)]
    # TODO Update Condition

    # Load the image corresponding to the current page number
    try:
        image_path = f'pdf-files/aldi/{current_page_number}'  # Assuming images are named with page numbers
        image = Image.open(image_path)
        st.sidebar.image(image, caption=f"Image for Page {current_page_number}", use_column_width=True)
    except FileNotFoundError:
        st.sidebar.warning(f"Image not found for page number {current_page_number}")

    # Set up the Streamlit page
    st.title("Supermarket Data Editing Tool")

    # Function to edit the dataframe row by row
    def edit_row(index, df, csv_path):
        with st.form(key=f"form_{index}"):
            st.write(f"Editing Row {index + 1}")

            # TODO Update Columns
            # Create editable input fields for each relevant column in the row
            product_name = st.text_input("Product Name", value=str(df.loc[index, "product_name"]))
            original_price = st.text_input("Original Price", value=str(df.loc[index, "original_price"]))
            discount_price = st.text_input("Discount Price", value=str(df.loc[index, "discount_price"]))
            percentage_discount = st.text_input("Percentage Discount", value=str(df.loc[index, "percentage_discount"]))
            discount_details = st.text_input("Discount Details", value=str(df.loc[index, "discount_details"]))
            date_collected = st.text_input("Date Collected", value=str(df.loc[index, "date_collected"]))
            calendar_week = st.text_input("Calendar Week", value=str(df.loc[index, "calendar_week"]))
            final_category = st.text_input("Final Category", value=str(df.loc[index, "final_category"]))

            # Button to save the changes for this row
            submitted = st.form_submit_button("Save Changes")

            if submitted:
                # Update the dataframe with the new values
                df.loc[index, "product_name"] = product_name
                df.loc[index, "original_price"] = original_price
                df.loc[index, "discount_price"] = discount_price
                df.loc[index, "percentage_discount"] = percentage_discount
                df.loc[index, "discount_details"] = discount_details
                df.loc[index, "date_collected"] = date_collected
                df.loc[index, "calendar_week"] = calendar_week
                df.loc[index, "final_category"] = final_category

                data.to_csv(csv_path, index=False)
                st.success(f"Row {index + 1} updated successfully!")

    # Display filtered rows and provide options for editing them
    if not filtered_data.empty:
        for idx in filtered_data.index:
            edit_row(idx, data, result_csv_path)

        # Display the updated dataframe after editing
        st.write("### Updated Dataframe")
        st.dataframe(filtered_data)
    else:
        st.write("No rows available for the current image with categorization_all_same == True.")
