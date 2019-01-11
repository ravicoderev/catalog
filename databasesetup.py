from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(250), nullable=False)

    # JSON Responses : Serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
        """ Retrurn object in serializable format """
        return{
            'category_id': self.category_id,
            'category_name': self.category_name
        }
engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread':False})


Base.metadata.create_all(engine)
