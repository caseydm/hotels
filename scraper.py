import time
import sys
from datetime import datetime, timedelta
from dateutil import relativedelta
from urllib.parse import urlparse, parse_qs, urlunparse
from robobrowser import RoboBrowser
from models import Rate, Hotel, Location, create_db_session
from utils import get_or_create
from constants import HOTELS_TO_SCRAPE


def main():
    try:
        # create db session
        session = create_db_session()

        # loop through list of hotels to scrape
        for item in HOTELS_TO_SCRAPE:
            # get or create a hotel linked to a location
            location = get_or_create(session, Location, city=item['city'])
            hotel = get_or_create(session, Hotel, name=item['name'], location=location)

            # create a hotel dictionary to pass to the other functions
            hotel = {'property_code': item['property_code'], 'object': hotel}

            # govt rates
            # get rates dictionary
            rates = get_rates(hotel, govt=True)

            # save to database
            save_results(rates, session, hotel, govt=True)
            time.sleep(3)

            # commercial rates
            # get rates dictionary
            rates = get_rates(hotel, govt=False)

            # save to database
            save_results(rates, session, hotel, govt=False)
            time.sleep(3)
        session.close()
    except () as e:
        print('Error: {}'.format(e))
        sys.exit(1)


def get_rates(hotel, govt):
    dates = build_dates()
    rates = []

    # get rates for this month and next month
    for d in dates:
        soup = get_soup(d['arrive'], d['depart'], hotel, govt)
        rates += parse_rates(soup, govt)
        time.sleep(2)

    # remove duplicates
    filtered = []

    for i in range(0, len(rates)):
        if rates[i] not in rates[i + 1:]:
            filtered.append(rates[i])

    rates = filtered

    return rates


def get_soup(arrive, depart, hotel, govt):
    if govt == True:
        rateCode = 'GOV'
    else:
        rateCode = 'none'

    browser = RoboBrowser(parser='html.parser')
    browser.open('http://www.marriott.com/reservation/availabilitySearch.mi?propertyCode=' + hotel['property_code'])

    form = browser.get_form(action='/reservation/availabilitySearch.mi?isSearch=false')

    form['fromDate'].value = arrive
    form['toDate'].value = depart
    form['flexibleDateSearch'] = 'true'
    form['clusterCode'] = rateCode

    # submit form
    browser.submit_form(form)

    return browser


def parse_rates(soup, govt):
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

            if govt == True:
                # append data to rates list
                rates.append({
                    'arrive': res_date,
                    'govt_rate': query['rate'][0],
                    'govt_rate_initial': query['rate'][0],
                    'govt_link': 'https://marriott.com' + urlunparse(parsed_url)
                })
            elif govt == False:
                # append data to rates list
                rates.append({
                    'arrive': res_date,
                    'commercial_rate': query['rate'][0],
                    'commercial_rate_initial': query['rate'][0],
                    'commercial_link': 'https://marriott.com' + urlunparse(parsed_url)
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


def save_results(rates, session, hotel, govt):

    for item in rates:
        rate = Rate(**item)

        try:
            # check if already in database
            q = session.query(Rate).filter(Rate.hotel==hotel['object'], Rate.arrive==rate.arrive).first()
            if q and govt == True:
                q.updated = datetime.utcnow()
                q.govt_rate = rate.govt_rate
                print(q.arrive, 'hotel updated')
            elif q and govt == False:
                q.updated = datetime.utcnow()
                q.commercial_rate = rate.commercial_rate
                print(q.arrive, 'hotel updated')
            else:
                hotel['object'].rates.append(rate)
                print('hotel saved successfully')
            session.commit()
        except:
            session.rollback()
            raise


# run program
if __name__ == '__main__':
    main()
