import requests
import time
from datetime import datetime
from app.spiders.loews.hotels import LOEWS_TEST
from app.models import Rate, Hotel, Location, create_db_session
from app.spiders.utils import get_or_create


def scrape_loews(HOTELS_TO_SCRAPE):
    for item in HOTELS_TO_SCRAPE:
        arrive = '12/18/2016'
        depart = '12/19/2016'

        # get commercial rate
        commercial_rate = get_rate(
            arrive,
            depart,
            item['property_code'],
            item['url_code']
        )

        time.sleep(3)

        # get government rate
        govt_rate = get_rate(
            arrive,
            depart,
            item['property_code'],
            item['url_code'],
            rate_type='GOVERNMENT'
        )

        # build links
        link_root = 'https://www.loewshotels.com/reservations/{}/'.format(item['url_code'])
        link_dates = '/checkin/{}/checkout/{}'.format(arrive, depart)
        govt_link = link_root + link_dates + '/rate_type/GOVERNMENT/adults/2/children/0'
        commercial_link = link_root + link_dates + '/rate_type//adults/2/children/0'

        save_result(arrive, govt_rate, commercial_rate, item, govt_link, commercial_link)

        print('Government rate is: {}'.format(govt_rate))
        print('Commercial rate is: {}'.format(commercial_rate))
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

    # get list of available rates
    rates = parse_rates(response_json['rooms'])
    # select lowest
    rate = min(rates)
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

    rate.location = location
    rate.hotel = hotel
    rate.arrive = datetime.strptime(arrive, '%m/%d/%Y')
    rate.govt_rate = govt_rate
    rate.commercial_rate = commercial_rate
    rate.govt_link = govt_link
    rate.commercial_link = commercial_link

    session.add(rate)
    session.commit()
    session.close()


scrape_loews(LOEWS_TEST)
