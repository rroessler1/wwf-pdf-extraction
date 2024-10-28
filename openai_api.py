import base64
from openai import OpenAI


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
        response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": '''
You are a helpful assistant that will help me extract information from leaflets of various Swiss grocery stores. Extract the following content in CSV format: the name of the product, the original price, the discounted price, the percentage discount (if available), discount details (if available), the weight (if available), and other details such as country of origin (if available). Here is the example CSV structure:

product, original_price, discount_price, percentage_discount, discount_details, weight, details
schweins-schulterbraten, 1.49 CHF, .99 CHF, 33%, pro 100g, ca. 1 kg, Schweiz, ...

                ''',
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
        )
        return response.choices[0]
