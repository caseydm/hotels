from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import Location

# app setup
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


@app.route('/')
def index():
    # rates = db.session.query(Rate).filter_by(hotel_id=1)
    locations = db.session.query(Location).all()
    return render_template('index.html', locations=locations)


@app.route('/<city>')
def hotel_list(city):
    location = db.session.query(Location).filter_by(city=city).first()
    hotels = location.hotels
    return render_template('hotel_list.html', location=location, hotels=hotels)


if __name__ == '__main__':
    app.run()
