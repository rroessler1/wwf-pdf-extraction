import streamlit as st

def show_upload_page():
    # Set up the Streamlit page
    st.title("Leaflet Upload")

    # File uploader for PDF and image files
    uploaded_file = st.file_uploader("Upload your file", type=["pdf", "jpg", "jpeg", "png"])

    # Dropdown for selecting a supermarket
    supermarkets = ["Aldi", "Coop", "Denner", "Lidl", "Migros", "Volg"]
    selected_supermarket = st.radio("Select a supermarket", supermarkets)

    # Date picker for choosing a date
    selected_date = st.date_input("Choose a date")

    # Display selected inputs
    st.write("### Selected Options")
    st.write("Supermarket:", selected_supermarket)
    st.write("Date:", selected_date)

    # Placeholder for further processing
    if uploaded_file and st.button("Process Data"):
        st.write("Processing document for:", selected_supermarket, "on", selected_date)
        # TODO put the file in the right directory

