import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import config

Base = declarative_base()


# db operations
def create_db_session():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


# models
class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    city = Column(String(50), nullable=False, unique=True)

    hotels = relationship('Hotel', back_populates='location')


class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    phone_number = Column(String(20))
    parking_fee = Column(String(10))
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)

    location = relationship('Location', back_populates='hotels')
    rates = relationship('Rate', back_populates='hotel')


class Rate(Base):
    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True)
    price = Column(Numeric(6, 2))
    arrive = Column(Date, nullable=False)
    link = Column(String(500), nullable=False)
    updated = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    hotel_id = Column(Integer, ForeignKey('hotels.id'), nullable=False)

    hotel = relationship('Hotel', back_populates='rates')


# note, you can create tables in app.py by importing Base
# and running Base.metadata.create_all(bind=db.engine)
