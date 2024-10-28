from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'

    name = Column(String, primary_key=True)
    parent_category = Column(String, ForeignKey('categories.name'), nullable=True)


class Item(Base):
    __tablename__ = 'items'

    category = Column(String, ForeignKey('categories.name'), nullable=True, default=None)
    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    parameters = Column(String, nullable=True)
    # misc = Column(String, nullable=True)


class Product(Base):
    __tablename__ = 'products'

    id = Column(String, primary_key=True)
    item_a = Column(String, ForeignKey('items.id'))
    item_b = Column(String, ForeignKey('items.id'))
    match_parameters = Column(Integer)
    differ_parameters = Column(Integer)
