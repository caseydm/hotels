import os
import time
import sys
from datetime import datetime, timedelta
from dateutil import relativedelta
from urllib.parse import urlparse, parse_qs, urlunparse
from robobrowser import RoboBrowser
from sendgrid.helpers.mail import *
from models import Rate, Hotel, Location, db_setup


def main():
    try:
        hotel_name = Hotel(name='Ritz Carlton Lake Oconee')
        location = Location(city='Lake Oconee, GA')
        # name_query = session.query(Hotel).filter_by(name=rate['hotel']).first()
        # if name_query:
        #     hotel_name = name_query
        # else:
        #     hotel_name = Hotel(name=rate['hotel'])
        # location_query = session.query(Location).filter_by(city=rate['city']).first()
        # if location_query:
        #     location_name = location_query
        # else:
        #     location_name = Location(city=rate['city'])

        hotel = {'property_code': 'AHNRZ', 'name': hotel_name, 'city': location}
        rates = get_rates(hotel)
        session = db_setup()
        save_results(rates, session)
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

    # sort rates by date
    # rates.sort(key=lambda x: datetime.strptime(x['arrive'], '%A, %b %d'))

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


def parse_rates(soup, hotel):
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
            # res_date = res_date.strftime('%A, %b %d')

            # append data to rates list
            rates.append({
                'hotel': hotel['name'],
                'location': hotel['city'],
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
            q = session.query(Rate).filter(Rate.hotel==rate.hotel, Rate.arrive==rate.arrive)
            if q.count():
                q.update({
                    'updated': datetime.datetime.utcnow(),
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
