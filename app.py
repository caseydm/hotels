from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import Rate, Location

# app setup
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


@app.route('/')
def index():
    # rates = db.session.query(Rate).filter_by(hotel_id=1)
    locations = db.session.query(Location).all()
    return render_template('index.html', locations=locations)


if __name__ == '__main__':
    app.run()
