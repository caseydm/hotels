from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import contains_eager
from models import Location, Rate, Hotel
from datetime import datetime

# app setup
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


@app.route('/')
def index():
    locations = db.session.query(Location).all()
    return render_template('index.html', locations=locations)


@app.route('/<city>')
def hotel_list(city):
    location = db.session.query(Location).filter_by(city=city).first()
    hotels = db.session.query(Hotel).\
        join(Location).\
        join(Rate).\
        options(contains_eager(Hotel.rates)).\
        filter(Location.city == city).\
        filter(Rate.arrive >= datetime.now())

    print(hotels)
    return render_template('hotel_list.html', location=location, hotels=hotels)


if __name__ == '__main__':
    app.run()
