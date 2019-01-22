from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(250), nullable=False)
    user_email = Column(String(250), nullable=False)
    user_picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email            
        }


class Category(Base):
    __tablename__ = 'category'

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    user = relationship(User)

    # JSON Responses : Serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
        """ Return object in serializable format """
        return{
            'category_id': self.category_id,
            'category_name': self.category_name
        }


class Item(Base):
    __tablename__ = 'item'

    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(80), nullable=False)
    item_description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.category_id', ondelete='CASCADE'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'item_id': self.item_id,
            'item_name': self.item_name,
            'item_description': self.item_description            
        }


engine = create_engine('sqlite:///sportscatalogitems.db', connect_args={'check_same_thread': False})


Base.metadata.create_all(engine)
