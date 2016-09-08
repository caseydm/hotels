import time
import sys
from datetime import datetime, timedelta
from dateutil import relativedelta
from urllib.parse import urlparse, parse_qs, urlunparse
from robobrowser import RoboBrowser
from models import Rate, Hotel, Location, db_setup
from utils import get_or_create
from settings import HOTELS


def main():
    try:
        session = db_setup()
        for H in HOTELS:
            location = get_or_create(session, Location, city=H['city'])
            location.hotel = get_or_create(session, Hotel, name=H['name'])
            hotel = {'property_code': H['property_code'], 'object': location.hotel}
            rates = get_rates(hotel)
            save_results(rates, session)
            time.sleep(3)
        session.close()
    except () as e:
        print('Error: {}'.format(e))
        sys.exit(1)


def get_rates(hotel):
    dates = build_dates()
    rates = []

    # get rates for this month and next month
    for d in dates:
        soup = get_soup(d['arrive'], d['depart'], hotel)
        rates += parse_rates(soup, hotel)
        time.sleep(2)

    # remove duplicates
    filtered = []

    for i in range(0, len(rates)):
        if rates[i] not in rates[i + 1:]:
            filtered.append(rates[i])

    rates = filtered

    return rates


def get_soup(arrive, depart, hotel):
    browser = RoboBrowser(parser='html.parser')
    browser.open('http://www.marriott.com/reservation/availabilitySearch.mi?propertyCode=' + hotel['property_code'])

    form = browser.get_form(action='/reservation/availabilitySearch.mi?isSearch=false')

    form['fromDate'].value = arrive
    form['toDate'].value = depart
    form['flexibleDateSearch'] = 'true'
    form['clusterCode'] = 'GOV'

    # submit form
    browser.submit_form(form)

    return browser


def parse_rates(soup):
    # get calendar links
    table = soup.find('table')
    urls = table.find_all('a', class_='t-no-decor')

    rates = []

    # loop through urls and parse each query string
    for item in urls:
        if len(item["class"]) == 1:
            # strip newlines and tabs
            raw_url = item['href'].replace('\n', '').replace('\t', '').replace(' ', '')
            parsed_url = urlparse(raw_url)
            query = parse_qs(parsed_url.query)

            # convert date to datetime format
            res_date = query['fromDate'][0]
            res_date = datetime.strptime(res_date, '%m/%d/%y')

            rates = []

            # append data to rates list
            rates.append({
                'arrive': res_date,
                'price': query['rate'][0],
                'link': 'https://marriott.com' + urlunparse(parsed_url)
            })

    return rates


def build_dates():
    dates = []
    today = datetime.now()
    next_month = today + relativedelta.relativedelta(months=1)

    # now
    dates.append({
        'arrive': today.strftime('%m/%d/%Y'),
        'depart': (today + timedelta(days=1)).strftime('%m/%d/%Y')
    })

    # next month
    dates.append({
        'arrive': next_month.strftime('%m/%d/%Y'),
        'depart': (next_month + timedelta(days=1)).strftime('%m/%d/%Y')
    })

    return dates


def save_results(rates, session):

    for item in rates:
        rate = Rate(**item)

        try:
            # check if already in database
            q = session.query(Rate).filter(Rate.hotel==rate.hotel, Rate.arrive==rate.arrive)
            if q.count():
                q.update({
                    'updated': datetime.utcnow(),
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


# run program
if __name__ == '__main__':
    main()
