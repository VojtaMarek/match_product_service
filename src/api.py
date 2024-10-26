import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
import os

from db_manager import DatabaseManager
from reciever import Reciever, rabbitmq_host, queue_offer, queue_category
import config

db = DatabaseManager(os.environ.get('DB_URL') or config.DB_URL)
reciever = Reciever(rabbitmq_host, db)
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
        reciever.start_consuming()

        # TODO: look for the matching product

    except Exception as e:
        logger.error(f'Error while inserting data: {e}')
        raise e


async def startup_events():
    db.init_db()

    try:
        reciever.declare_queue(queue_offer)
        reciever.declare_queue(queue_category)
        reciever.bind_queue('amq.topic', queue_offer, 'oc.offer')
        reciever.bind_queue('amq.topic', queue_category, 'oc.category')
        reciever.consume(queue_offer)
        reciever.consume(queue_category)
    except Exception as e:
        logger.error(f'Error before starting consuming: {e}')
        raise e
    logger.info('Started.')


async def shutdown_events():
    reciever.stop_consuming()


@app.get("/")
async def root():
    return {"version": "0.1.0"}


@app.get("/products/{name}")
async def get_products(name: str):
    # TODO
    pass


@app.get("/run-worker")
async def get_products(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_worker)
    pass
