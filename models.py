import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import config


Base = declarative_base()


# models
class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    hotelName = Column(String)
    govtRateOffered = Column(Boolean, nullable=False)
    govtRateByPhone = Column(Boolean)
    phoneNumber = Column(String)
    parkingFee = Column(String)


class Rate(Base):
    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True)
    standardRate = Column(Numeric(6, 2))
    govtRate = Column(Numeric(6, 2))
    standardAvailable = Column(Boolean, nullable=False)
    govtAvailable = Column(Boolean, nullable=False)
    arrive = Column(Date, nullable=False)
    depart = Column(Date, nullable=False)
    updated = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    location = relationship('Location')
    hotel = relationship('Hotel')


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False, unique=True)


# db operations
def db_setup():
    engine = create_engine('postgresql://{0}:{1}@localhost:5433/hotels'.format(config.DB_USER, config.DB_PASS))
    db_create_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def db_create_tables(engine):
    return Base.metadata.create_all(engine)


def save_hotel(item, session):

    rate = Rate(**item)

    try:
        q = session.query(Rate).filter(Rate.hotel==rate.hotel, Rate.arrive==rate.arrive, Rate.depart==rate.depart)
        if q.count():
            q.update({
                'updated': datetime.datetime.utcnow(),
                'standardRate': rate.standardRate,
                'govtRate': rate.govtRate,
                'standardAvailable': rate.standardAvailable,
                'govtAvailable': rate.govtAvailable
                })
        else:
            session.add(rate)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        print('hotel saved successfully')
    return rate
