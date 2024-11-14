import time

import streamlit as st
import shutil
import os

def show_settings_page():
    # Set paths for settings files
    SETTINGS_PATH = "settings/settings.py"
    DEFAULT_SETTINGS_PATH = "settings/default_settings.py"

    # Load settings from a given file
    def load_settings(file_path):
        settings = {}
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    settings[key] = value
        return settings

    # Save settings to a given file
    def save_settings(file_path, settings):
        with open(file_path, "w") as file:
            for key, value in settings.items():
                file.write(f'{key} = "{value}"\n')



    # Load current settings
    settings = load_settings(SETTINGS_PATH)

    # Streamlit Page
    st.title("Settings Management")

    # Editable fields for settings
    st.header("Edit Settings")
    for key in settings.keys():
        settings[key] = st.text_input(f"{key}:", value=settings[key])

    # Button to save settings
    if st.button("Save Settings"):
        save_settings(SETTINGS_PATH, settings)
        st.success("Settings saved successfully!")

    # Restore default settings with validation
    st.header("Restore Default Settings")
    restore_default_checkbox = st.checkbox("Confirm that you want to restore the default settings")

    if st.button("Restore Defaults"):
        if restore_default_checkbox:
            shutil.copy(DEFAULT_SETTINGS_PATH, SETTINGS_PATH)
            st.success("Default settings restored successfully! Page will reload...")
            time.sleep(3)
            st.rerun()
        else:
            st.warning("Please confirm that you want to restore the default settings by checking the box.")

