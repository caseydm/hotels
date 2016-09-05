from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import Hotel
from config import SQLALCHEMY_DATABASE_URI

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()


@app.route('/')
def index():
    # hotels = Hotel.query.all()
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
