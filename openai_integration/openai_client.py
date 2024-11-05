import base64

import pandas as pd
from openai import OpenAI

from categorization.categorization_system_prompt import CATEGORIZATION_SYSTEM_PROMPT
from categorization.categorization_user_prompt import CATEGORIZATION_USER_PROMPT
from leaflet_processing.constants import OPENAI_PROMPT
from .models import Results, CategorizationResult


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def extract(self, image_data: bytes) -> Results:
        """
        Extracts product information from an image by encoding it and sending it to the OpenAI API.
        """
        encoded_image = self._encode_image(image_data)
        return self._get_data_from_image(encoded_image)

    def _encode_image(self, image_data: bytes) -> str:
        """
        Encodes an image into a base64 string for API transmission.
        """
        return base64.b64encode(image_data).decode('utf-8')

    def _get_data_from_image(self, base64_image: str) -> Results:
        """
        Sends the base64-encoded image to OpenAI and receives extracted data.
        Results: Parsed structured data containing product information.
        """
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": OPENAI_PROMPT,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            response_format=Results,
        )
        
        # Extract and parse the response
        return response.choices[0]

    def categorize_products(self, products: pd.DataFrame) -> CategorizationResult:
        """
        Sends prompt to OpenAI to get product categorization for products
        :param products: product data
        :return: product categorization data
        """

        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": CATEGORIZATION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": self.build_product_categorization_prompt(products)
                }
            ],
            response_format=CategorizationResult,
            temperature=0.5
        )

        # Extract and parse the response
        return response.choices[0]

    @staticmethod
    def build_product_categorization_prompt(products: pd.DataFrame) -> str:
        prompt: str = CATEGORIZATION_USER_PROMPT
        for product in products:
            prompt+= product["product_name"] + "\n"

        return prompt
