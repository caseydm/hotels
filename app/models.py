import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from app import config

Base = declarative_base()


# db operations
def create_db_session():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def reset_db():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return None


# models
class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    city = Column(String(50), nullable=False, unique=True)
    per_diem_rate = Column(Numeric(6, 2))

    hotels = relationship('Hotel', back_populates='location')


class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    phone_number = Column(String(20))
    parking_fee = Column(String(10))
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)

    location = relationship('Location', back_populates='hotels')
    rates = relationship('Rate', back_populates='hotel', order_by='Rate.arrive', lazy='joined')


class Rate(Base):
    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True)
    govt_rate = Column(Numeric(6, 2))
    govt_rate_initial = Column(Numeric(6, 2))
    commercial_rate = Column(Numeric(6, 2))
    commercial_rate_initial = Column(Numeric(6, 2))
    arrive = Column(Date, nullable=False)
    govt_link = Column(String(500))
    commercial_link = Column(String(500))
    updated = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    hotel_id = Column(Integer, ForeignKey('hotels.id'), nullable=False)

    hotel = relationship('Hotel', back_populates='rates')
