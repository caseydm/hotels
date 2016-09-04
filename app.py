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
        email_results(rates)
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
                'date': res_date,
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
    rates.sort(key=lambda x: datetime.strptime(x['date'], '%A, %b %d'))

    return rates


def email_results(rates):
    # sendgrid setup
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

    # message
    message = 'Available dates for Ritz Lake Oconee:<br><br>'
    for rate in rates:
        message += '<b>Date:</b> {} <br><b>Rate:</b> {}'.format(
            rate['date'],
            '<a href=' + rate['link'] + '>' + rate['price'] + '</a><br><br>'
        )
    from_email = Email(os.environ.get('FROM_EMAIL'))
    subject = 'Ritz Hotel Rates'
    to_email = Email(os.environ.get('TO_EMAIL'))
    content = Content('text/html', message)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)


# run program
if __name__ == '__main__':
    main()
