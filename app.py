from flask import Flask, render_template
from models import Rate, db_setup

app = Flask(__name__)


@app.route('/')
def index():
    session = db_setup()
    rates = session.query(Rate).filter_by(hotel_id=1)
    session.close()
    return render_template('index.html', rates=rates)


if __name__ == '__main__':
    app.run()
