# Leaflet Product Extractor

## Overview

The Leaflet Product Extractor is a Python-based application designed to extract product information from leaflets of various Swiss grocery stores. It leverages OpenAI's API to analyze images of the leaflets and extract essential product details, including product names, prices, discounts, and more.


### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt

2. **Install Poppler** (required for PDF processing):

    macOS:
    ```bash
    brew install poppler
    ```
## Project Structure

├──leaflet-product-extractor/\
│   ├── __init__.py \
│   ├── leaflet_processing/ \
│   ├── leaflet_reader.py # Handles reading and image extraction from leaflets \
├──  openai_integration/ \
│   ├── __init__.py \
│   ├── openai_client.py # Interacts with OpenAI's \API \
│   ├── models.py # Pydantic models for structured \data \
├──  result_handling/ \
│   ├── __init__.py \
│   ├── result_saver.py # Saves extracted data to \Excel files \
├──  categorization/ \
│   ├── __init__.py \
│   ├── product_categorizer.py # Categorizes \products based on extracted data \
├──  main_pipeline.py # Orchestrates the entire \extraction process \
├── requirements.txt # Dependencies \
├── README.md # Project documentation\
