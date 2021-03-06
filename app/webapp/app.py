from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import contains_eager
from app.models import Location, Rate, Hotel
from datetime import datetime, timedelta

# app setup
app = Flask(__name__)
app.config.from_object('app.config')
db = SQLAlchemy(app)


@app.route('/')
def index():
    locations = db.session.query(Location).order_by(Location.city).all()
    return render_template('index.html', locations=locations)


@app.route('/<city>')
def hotel_list(city):
    location = db.session.query(Location).filter_by(city=city).first()
    hotels = db.session.query(Hotel).\
        join(Location).\
        join(Rate).\
        options(contains_eager(Hotel.rates)).\
        filter(Location.city == city).\
        filter(Rate.arrive > datetime.utcnow() - timedelta(days=1)).\
        order_by(Rate.arrive)

    return render_template('hotel_list.html', location=location, hotels=hotels)


if __name__ == '__main__':
    app.run()
