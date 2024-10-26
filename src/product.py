"""
When an offer is matched with another, create a product, check how many
parameters they have in common and how many differ, and store that
information.
"""
from db_manager import DatabaseManager
from models import Product
import os
import config
import httpx
import asyncio
import requests
import logging


db = DatabaseManager(os.environ.get('DB_URL') or config.DB_URL)
token = config.AUTH_TOKEN
logger = logging.getLogger(__name__)


def try_match(id_: str):
    try:
        url = f'http://localhost:5000/offer-matches/{id_}'
        headers = token
        response = requests.get(url, headers=headers)
        print(response.json())
    except Exception as e:
        logger.debug(f'Error while matching offers: {e}')


def create_product(offer_id: str, match_id: str):
    pass


async def fetch_data(id_: str):
    url = f'http://0.0.0.0:5000/offer-matches/{id_}'
    headers = token

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            print("Response JSON:", response.json())

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting: {e}")


if __name__ == "__main__":
    # asyncio.run(fetch_data('ed87340d-3703-45b1-a7f8-5fa7d22fc9e9'))
    try_match('ed87340d-3703-45b1-a7f8-5fa7d22fc9e9')

