import base64

from openai import OpenAI
from pydantic import BaseModel

from constants import OPENAI_PROMPT


class GroceryProduct(BaseModel):
    product_name: str
    original_price: str
    discount_price: str
    percentage_discount: float
    discount_details: str


class Results(BaseModel):
    all_products: list[GroceryProduct]


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def extract(self, image) -> str:
        encoded_image = self._encode_image(image)
        return self.get_data_from_image(encoded_image)

    # Function to encode the image
    def _encode_image(self, image):
        return base64.b64encode(image).decode('utf-8')

    def get_data_from_image(self, base64_image):
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
                    "url":  f"data:image/png;base64,{base64_image}"
                },
                },
            ],
            }
        ],
        response_format=Results,
        )
        return response.choices[0]
