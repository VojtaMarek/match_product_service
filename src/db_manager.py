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
        self.Session = sessionmaker(bind=self.engine)

    def init_db(self):
        # Create all tables
        Base.metadata.create_all(self.engine)

    @handle_exception
    def insert(self, record):
        # Insert data into the database using ORM session if not exists
        session = self.Session()
        try:
            if record.id is None or self.get(record.__class__, record.id, None) is None:
                session.add(record)
                session.commit()
                session.refresh(record)
                return self.serialize(record)
        finally:
            # session.expunge_all()
            session.close()

    @handle_exception
    def get(self, model, id_, group_id):
        # Get data based on its type and ID.
        session = self.Session()
        try:
            if group_id and not id_:
                return [self.serialize(i) for i in session.query(model).filter_by(category=group_id).all()]
            elif id_:
                return self.serialize(session.query(model).filter_by(id=id_).first()) or None
            elif not id_:
                return [self.serialize(i) for i in session.query(model).all()]
        finally:
            session.close()

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
    db.insert(item)

    category = Category(name='book', id=1, parent_category='library')
    db.insert(category)

    product = Product(id='2', item_a='123', item_b='124', match_parameters=1, differ_parameters=2)
    db.insert(product)
