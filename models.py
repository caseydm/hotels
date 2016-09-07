import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import config

Base = declarative_base()


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False, unique=True)
    hotels = relationship('Hotel', backref='location', lazy='dynamic')


# models
class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone_number = Column(String)
    parking_fee = Column(String)
    location_id = Column(Integer, ForeignKey('locations.id'))


class Rate(Base):
    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True)
    price = Column(Numeric(6, 2))
    arrive = Column(Date, nullable=False)
    link = Column(String, nullable=False)
    updated = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    location = relationship('Location')
    hotel = relationship('Hotel')


# db operations
def db_setup():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


# note, you can create tables in app.py by importing Base
# and running Base.metadata.create_all(bind=db.engine)
