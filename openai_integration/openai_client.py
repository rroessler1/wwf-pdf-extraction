import base64
import logging

import pandas as pd
from openai import OpenAI, RateLimitError

from categorization.categorization_system_prompt import CATEGORIZATION_SYSTEM_PROMPT
from categorization.categorization_user_prompt import CATEGORIZATION_USER_PROMPT
from validation.validation_system_prompt import VALIDATION_SYSTEM_PROMPT
from validation.validation_user_prompt import VALIDATION_USER_PROMPT
from leaflet_processing.constants import OPENAI_PROMPT
from .models import Results, CategorizationResult
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, before_sleep_log
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
NUM_RETRY_ATTEMPTS = 5
RETRY_WAIT_IN_SECS = 60 # as current rate limit is 3 requests per minute

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

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(NUM_RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_WAIT_IN_SECS),
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    def _get_data_from_image(self, base64_image: str) -> Results:
        """
        Sends the base64-encoded image to OpenAI and receives extracted data.
        Results: Parsed structured data containing product information.
        """
        response = self.client.beta.chat.completions.parse(
            model=MODEL,
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
        return response.choices[0].message.parsed

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(NUM_RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_WAIT_IN_SECS),
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    def categorize_products(self, products: List[str]) -> CategorizationResult:
        """
        Sends prompt to OpenAI to get product categorization for products
        :param products: product data
        :return: product categorization data
        """

        response = self.client.beta.chat.completions.parse(
            model=MODEL,
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
        return response.choices[0].message.parsed

    @staticmethod
    def build_product_categorization_prompt(products: List[str]) -> str:
        return CATEGORIZATION_USER_PROMPT + "\n".join(products)

    @staticmethod
    def build_product_data_validation_prompt(products: Results) -> str:
        return VALIDATION_USER_PROMPT + "\n" + products.__str__()

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(NUM_RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_WAIT_IN_SECS),
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    def validate_product_data(self, products: Results, image: bytes) -> Results:
        encoded_image = self._encode_image(image)
        response = self.client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": VALIDATION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self.build_product_data_validation_prompt(products),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
            response_format=Results,
        )

        # Extract and parse the response
        return response.choices[0].message.parsed
