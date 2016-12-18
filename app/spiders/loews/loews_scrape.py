import requests
import time
import logging
import sys
from random import randint
from datetime import datetime, timedelta
from app.models import Rate, Hotel, Location, create_db_session
from app.spiders.utils import get_or_create


def scrape_loews(HOTELS_TO_SCRAPE):
    # logging setup
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(levelname)s:%(message)s'
    )

    for item in HOTELS_TO_SCRAPE:
        # dates = build_dates()
        dates = ['1/1/2017']

        for d in dates:
            arrive = d
            next_day = datetime.strptime(d, '%m/%d/%Y') + timedelta(days=1)
            depart = datetime.strftime(next_day, '%m/%d/%Y')

            # get commercial rate
            commercial_rate = get_rate(
                arrive,
                depart,
                item['property_code'],
                item['url_code']
            )

            time.sleep(randint(3, 5))

            # get government rate
            govt_rate = get_rate(
                arrive,
                depart,
                item['property_code'],
                item['url_code'],
                rate_type='GOVERNMENT'
            )

            # build links
            link_root = 'https://www.loewshotels.com/reservations/{}'.format(item['url_code'])
            link_dates = '/checkin/{}/checkout/{}'.format(link_date(arrive), link_date(depart))
            govt_link = link_root + link_dates + '/rate_type/GOVERNMENT/adults/2/children/0'
            commercial_link = link_root + link_dates + '/adults/2/children/0'

            save_result(arrive, govt_rate, commercial_rate, item, govt_link, commercial_link)

            time.sleep(randint(3, 5))
        logging.info(item['name'] + ' processed successfully')
    return None


def get_headers(arrive, depart, url_code, rate_type=''):
    headers = {
        'Origin': 'https://www.loewshotels.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Cache-Control': 'max-age=0',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://www.loewshotels.com/reservations/' + url_code + '/checkin/' + arrive + '/checkout/' + depart + '/rate_type/' + rate_type + '/adults/2/children/0',
        'DNT': '1',
    }
    return headers


def get_rate(arrive, depart, property_code, url_code, rate_type=''):
    data = 'hotel={}&checkin={}&checkout={}&adults%5B%5D=2&children%5B%5D=0&rate_type={}&rate_code=' \
        .format(property_code, arrive, depart, rate_type)
    response = requests.post(
        'https://www.loewshotels.com/en/reservations/getavailability',
        headers=get_headers(arrive, depart, url_code, rate_type),
        data=data
    )
    response_json = response.json()

    # check for government rate not available string
    warning = 'We couldn’t find any availability for the special offer'
    govt_not_available = False

    if type(response_json['warnings']) is dict:
        if warning in response_json['warnings']['AVAILABILITY']:
            govt_not_available = True 

    if response_json['status'] is True and govt_not_available is False:
        # get list of available rates
        rates = parse_rates(response_json['rooms'])
        # select lowest
        rate = min(rates)
    else:
        rate = None
    return rate


def parse_rates(df):
    rates = []
    for key, value in df.items():
        if key == 'rate' and type(value) == int:
            rates.append(value)
        if isinstance(df[key], dict):
            rates += parse_rates(df[key])
    return rates


def save_result(arrive, govt_rate, commercial_rate, item, govt_link, commercial_link):
    # create db session
    session = create_db_session()

    # get location and hotel
    location = get_or_create(session, Location, city=item['city'])
    hotel = get_or_create(session, Hotel, name=item['name'], location=location)

    rate = Rate()

    # check if already in database
    q = session.query(Rate).filter(Rate.hotel==hotel, Rate.arrive==arrive).first()

    # update if already exists
    if q:
        q.updated = datetime.utcnow()
        q.govt_rate = govt_rate
        q.commercial_rate = commercial_rate

        # update initial rates if not already
        if govt_rate and q.govt_rate_initial is None:
            q.govt_rate_initial = govt_rate
        elif commercial_rate and q.commercial_rate_initial is None:
            q.commercial_rate_initial = commercial_rate
    else:
        # new hotel rate
        rate.location = location
        rate.hotel = hotel
        rate.arrive = datetime.strptime(arrive, '%m/%d/%Y')
        rate.govt_rate = govt_rate
        rate.govt_rate_initial = govt_rate
        rate.commercial_rate_initial = commercial_rate
        rate.commercial_rate = commercial_rate
        rate.govt_link = govt_link
        rate.commercial_link = commercial_link
        session.add(rate)

    session.commit()
    session.close()


def link_date(d):
    n = datetime.strptime(d, '%m/%d/%Y')
    formatted = datetime.strftime(n, '%Y-%m-%d')
    return formatted


def build_dates():
    base = datetime.today()
    date_list = []
    for x in range(0, 30):
        d = base + timedelta(days=x)
        d = datetime.strftime(d, '%m/%d/%Y')
        date_list.append(d)
    return date_list
