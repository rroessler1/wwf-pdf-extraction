import base64
from openai import OpenAI
from leaflet_processing.constants import OPENAI_PROMPT
from .models import Results

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