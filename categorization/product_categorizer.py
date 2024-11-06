# categorization/product_categorizer.py

import pandas as pd
from typing import Any
from PIL import Image

from openai_integration.models import CategorizationResult, ProductCategory
from openai_integration.openai_client import OpenAIClient


class ProductCategorizer:
    def __init__(self):
        pass

    def categorize_products(self, image: Image, data: pd.DataFrame, openai_client: OpenAIClient) -> pd.DataFrame:
        """
        Categorizes products
        Parameters:
            image (Image): Image data for potential future use (e.g., OCR or visual categorization).
            data (pd.DataFrame): DataFrame containing product information from OpenAI extraction.
            openai_client (OpenAIClient): OpenAI Client for interacting with OpenAI API.

        Returns:
            pd.DataFrame: DataFrame with an added 'Category' column for product categorization.
        """

        product_categories: list[ProductCategory] = []
        product_names = list(data['product_name'])
        step_size = 5
        for i in range(0, len(product_names), step_size):
            categorization_results = openai_client.categorize_products(product_names[i: i+step_size])
            product_categories.extend(categorization_results.categories)

        if len(data.index) == len(product_categories):
            data['Category'] = [c.value for c in product_categories]
        else:
            # TODO: maybe we should also have ChatGPT return the original product name,
            # so if the length doesn't match, we can still include the data for most of them.
            print(f"Length of the data {len(data.index)} and the assigned categories {len(product_categories)} do not match!")
            print(product_categories)

        return data
