"""
When an offer is matched with another, create a product, check how many
parameters they have in common and how many differ, and store that
information.
"""
import json

from db_manager import DatabaseManager
from models import Product, Item, Category
import os
import config
import requests
import logging


db = DatabaseManager(os.environ.get('DB_URL') or config.DB_URL)
auth_token = config.AUTH_TOKEN
logger = logging.getLogger(__name__)


def get_match_ids(id_: str) -> list | None:
    try:
        url = f'http://localhost:5000/offer-matches/{id_}'
        response = requests.get(url, headers=auth_token)
        res = response.json()
        return list(res.get('matching_offers', [])) or None
    except Exception as e:
        logger.debug(f'Error while matching offers: {e}')
        return None


def create_product_(item_a: dict, item_b: dict) -> bool:
    params_a = unpack_parameters(item_a.get('parameters', ''))
    params_b = unpack_parameters(item_b.get('parameters', ''))

    all_keys = list(set(params_a.keys()) | set(params_b.keys()))
    match_params, differ_params = 0, 0
    for key in all_keys:
        if params_a.get(key) != params_b.get(key):
            differ_params += 1
        else:
            match_params += 1

    product = Product(item_a=item_a.get('id'), item_b=item_b.get('id'), match_parameters=match_params,
                      differ_parameters=differ_params)
    return db.insert(product, 'id')


def unpack_parameters(param_str: str) -> dict:
    return json.loads(param_str)


def create_product(item_a_id: str) -> Product | None:
    # search for matching offers and product
    created = None
    match_list = get_match_ids(item_a_id)
    match_list.remove(item_a_id)  # remove the item itself
    if item_a := db.get_one(Item, id=item_a_id):
        for item_b_id in match_list:
            item_b = db.get_one(Item, id=item_b_id)
            if item_b:
                is_created = (bool(db.get_one(Product, item_a=item_a_id, item_b=item_b_id)) or
                              bool(db.get_one(Product, item_a=item_b_id, item_b=item_a_id)))
                if is_created:
                    logger.debug(f'Product already created for {item_a_id} and {item_b_id}')

                elif created := create_product_(item_a, item_b):  # standard behavior
                    logger.debug(f'Product created for {item_a_id} and {item_b_id}: {created}')
    return created


if __name__ == "__main__":
    create_product('feaa400a-d304-4f55-b045-51b1daec8e0c')