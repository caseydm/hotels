import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import config


Base = declarative_base()


# models
class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone_number = Column(String)
    parking_fee = Column(String)


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


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False, unique=True)


# db operations
def db_setup():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
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
                'price': rate.price
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
