import time
import sys
from datetime import datetime
from random import randint
from urllib.parse import urlparse, parse_qs, urlunparse
from robobrowser import RoboBrowser
from models import Rate, Hotel, Location, create_db_session
from utils import get_or_create, build_dates
from constants import US_RITZ_HOTELS


def main():
    try:
        # create db session
        session = create_db_session()

        # loop through list of hotels to scrape
        for item in US_RITZ_HOTELS:
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
            time.sleep(randint(2, 5))

            # commercial rates
            # get rates dictionary
            rates = get_rates(hotel, govt=False)

            # save to database
            save_results(rates, session, hotel, govt=False)
            time.sleep(randint(4, 60))
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
        time.sleep(randint(2, 5))

    # remove duplicates
    filtered = []

    for i in range(0, len(rates)):
        if rates[i] not in rates[i + 1:]:
            filtered.append(rates[i])

    rates = filtered

    return rates


def get_soup(arrive, depart, hotel, govt):
    if govt is True:
        rateCode = 'GOV'
    else:
        rateCode = 'none'

    browser = RoboBrowser(parser='html.parser')
    browser.open('http://www.marriott.com/reservation/availabilitySearch.mi?propertyCode=' + hotel['property_code'])

    time.sleep(1)

    form = browser.get_form(action='/reservation/availabilitySearch.mi?isSearch=false')

    try:
        form['fromDate'].value = arrive
        form['toDate'].value = depart
        form['flexibleDateSearch'] = 'true'
        form['clusterCode'] = rateCode
    except TypeError:
        print(browser.parsed)

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
                    'govt_link': 'https://marriott.com' + urlunparse(parsed_url)
                })
            elif govt == False:
                # append data to rates list
                rates.append({
                    'arrive': res_date,
                    'commercial_rate': query['rate'][0],
                    'commercial_link': 'https://marriott.com' + urlunparse(parsed_url)
                })

    return rates


def save_results(rates, session, hotel, govt):

    for item in rates:
        rate = Rate(**item)

        try:
            # check if already in database
            q = session.query(Rate).filter(Rate.hotel==hotel['object'], Rate.arrive==rate.arrive).first()

            # update inital rate
            if q:
                if 'govt_rate' in item and q.govt_rate_initial is None:
                    q.govt_rate_initial = rate.govt_rate
                elif 'commercial_rate' in item and q.commercial_rate_initial is None:
                    q.commercial_rate_initial = rate.commercial_rate

            if q and govt is True:
                q.updated = datetime.utcnow()
                q.govt_rate = rate.govt_rate
                print(q.arrive, 'hotel updated')
            elif q and govt is False:
                q.updated = datetime.utcnow()
                q.commercial_rate = rate.commercial_rate
                print(q.arrive, 'hotel updated')
            else:
                if govt is True:
                    rate.govt_rate_initial = rate.govt_rate
                elif govt is False:
                    rate.commercial_rate_initial = rate.commercial_rate
                hotel['object'].rates.append(rate)
                print('hotel saved successfully')
            session.commit()
        except:
            session.rollback()
            raise


# run program
if __name__ == '__main__':
    main()
