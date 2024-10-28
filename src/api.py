import asyncio
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
import os

from db_manager import DatabaseManager
from receiver import Receiver, rabbitmq_host, queue_offer, queue_category, db
from models import Product, Item

receiver = Receiver(rabbitmq_host, db)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_events()
    yield
    await shutdown_events()

app = FastAPI(
    lifespan=lifespan,
    docs_url='/docs'
)


def run_worker():
    try:
        receiver.start_consuming()
    except Exception as e:
        logger.error(f'Error while inserting data: {e}')
        raise e


async def startup_events():
    db.init_db()

    try:
        receiver.declare_queue(queue_offer)
        receiver.declare_queue(queue_category)
        receiver.bind_queue('amq.topic', queue_offer, 'oc.offer')
        receiver.bind_queue('amq.topic', queue_category, 'oc.category')
        receiver.consume(queue_offer)
        receiver.consume(queue_category)
    except Exception as e:
        logger.error(f'Error before starting consuming: {e}')
        raise e
    logger.info('Started.')


async def shutdown_events():
    receiver.stop_consuming()


@app.get("/")
async def root():
    return {"version": "0.1.0"}


@app.get("/product/{name}")
async def get_products(name: str):
    name = name.lower().strip()
    all_items = db.get_more(Item)
    first_related_item = None
    for item in all_items:
        if name in str(all_items[0]).lower():
            first_related_item = item
            break

    product_and_items = None
    if first_related_item:
        items_related_product = (db.get_more(Product, item_a=first_related_item.get('id')) +
                                 db.get_more(Product, item_b=first_related_item.get('id')))
        product_item_ids = []
        for product in items_related_product:
            product_item_ids += [v for k, v in product.items() if k.startswith('item_')]
        product_items = [db.get_one(Item, id=id_) for id_ in product_item_ids]
        product_and_items = dict(product=items_related_product, items=product_items)

    ret = json.dumps(product_and_items, indent=4) if product_and_items else None
    if not ret:
        return {"message": "No product found."}, 404
    return product_and_items, 200


@app.get("/run-worker")
async def get_products(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_worker)
    pass
