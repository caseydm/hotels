import os
import time
import sys
from datetime import datetime, timedelta
from dateutil import relativedelta
from urllib.parse import urlparse, parse_qs, urlunparse
from robobrowser import RoboBrowser
import sendgrid
from sendgrid.helpers.mail import *


def main():
    try:
        rates = get_rates()
        for rate in rates:
            print(rate['date'], rate['price'], rate['link'])
        save_results(rates)
    except (AttributeError, TypeError) as e:
        print('Error: {}'.format(e))
        sys.exit(1)


def get_soup(arrive, depart):
    browser = RoboBrowser(parser='html.parser')
    browser.open('http://www.marriott.com/reservation/availabilitySearch.mi?propertyCode=AHNRZ')

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

            # convert date to friendly format
            res_date = query['fromDate'][0]
            res_date = datetime.strptime(res_date, '%m/%d/%y')
            res_date = res_date.strftime('%A, %b %d')

            # append data to rates list
            rates.append({
                'hotel': 'Ritz Carlton Lake Oconee',
                'city': 'Lake Oconee, GA',
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


def get_rates():
    dates = build_dates()
    rates = []

    # get rates for this month and next month
    for d in dates:
        soup = get_soup(d['arrive'], d['depart'])
        rates += parse_rates(soup)
        time.sleep(2)

    # remove duplicates
    filtered = []

    for i in range(0, len(rates)):
        if rates[i] not in rates[i + 1:]:
            filtered.append(rates[i])

    rates = filtered

    # sort rates by date
    rates.sort(key=lambda x: datetime.strptime(x['arrive'], '%A, %b %d'))

    return rates


def save_results(rates, session):

    for rate in rates:
        nameQuery = session.query(Hotel).filter_by(hotelName=rate['hotel']).first()
        if nameQuery:
            hotelName = nameQuery
        else:
            hotelName = Hotel(hotelName=rate['hotel'])
        location = session.query(Location).filter_by(city=rate['city']).first()


# run program
if __name__ == '__main__':
    main()
