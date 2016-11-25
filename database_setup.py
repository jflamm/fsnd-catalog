from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name' : self.name,
           'id' : self.id,
       }

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name' : self.name,
           'id' : self.id,
       }

class CategoryItem(Base):
    __tablename__ = 'items'

    title = Column(String(80), nullable = False)
    description = Column(String(500), nullable = False)
    id = Column(Integer, primary_key = True)
    category_id = Column(Integer,ForeignKey('categories.id'))
    category = relationship(Category)
    user_id = Column(Integer,ForeignKey('users.id'))
    user = relationship(User)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'title' : self.title,
           'description' : self.description,
           'id' : self.id,
       }

engine = create_engine('postgresql:///catalog')
Base.metadata.create_all(engine)
