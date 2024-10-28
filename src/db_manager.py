import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

import config

from models import Base, Item, Category, Product

logger = logging.getLogger(__name__)


# decorator logging database operations
def handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'An error occurred: {e}')
            raise e
    return wrapper


class DatabaseManager:
    def __init__(self, db_url):
        # Set up the engine and metadata
        self.engine = create_engine(url=db_url+'?charset=utf8', echo=True, future=True)
        self.session = sessionmaker(bind=self.engine)

    def init_db(self):
        # Create all tables
        Base.metadata.create_all(self.engine)

    @handle_exception
    def insert(self, record, pk):
        # Insert data into the database using ORM session if not exists
        with self.session() as session:
            pk_value = getattr(record, pk)
            if pk_value is None or self.get_one(record.__class__, **{pk: pk_value}) is None:
                session.add(record)
                session.commit()
                session.refresh(record)
                return self.serialize(record)

    @handle_exception
    def get_one(self, model, **kwargs) -> dict:
        # Get one record based on kwargs
        with self.session() as session:
            ret = session.query(model).filter_by(**kwargs).first()
            return self.serialize(ret) or None

    @handle_exception
    def get_more(self, model, **kwargs) -> list[dict]:
        # Get data based on kwargs.
        with self.session() as session:
            return [self.serialize(i) for i in session.query(model).filter_by(**kwargs).all()]

    @staticmethod
    def serialize(values) -> dict:
        if not values:
            print('No value fetched from DB.')
            return dict()
        return {k: v for k, v in values.__dict__.items() if not k.startswith('_')}

    @staticmethod
    def serialize_data(values: dict, keys) -> dict:
        if not values:
            logger.debug('No value fetched.')
            return dict()

        if 'parameters' in values.keys():
            if isinstance(values['parameters'], dict):
                values['parameters'] = json.dumps(values['parameters'])

        res = dict()
        for k, v in values.items():
            if k in keys and type(v) is str:
                res[k] = v
        return res


if __name__ == '__main__':
    db = DatabaseManager(os.environ.get('DB_URL') or config.DB_URL)
    db.init_db()

    item = Item(name='item', id='123')
    db.insert(item, 'id')

    category = Category(name='book', parent_category='library')
    db.insert(category, 'name')

    product = Product(id='2', item_a='123', item_b='124', match_parameters=1, differ_parameters=2)
    db.insert(product, 'id')