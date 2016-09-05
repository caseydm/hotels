from flask import Flask, render_template
from models import Rate, Hotel, Location, db_setup

app = Flask(__name__)


@app.route('/')
def index():
    session = db_setup()
    hotels = session.query(Hotel).all()
    session.close()
    return render_template('index.html', hotels=hotels)

if __name__ == '__main__':
    app.run()
