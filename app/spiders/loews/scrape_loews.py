import requests
import time
from app.spiders.loews.hotels import LOEWS_TEST


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


for item in LOEWS_TEST:
    commercial_rate = get_rate('12/18/2016', '12/19/2016', item['property_code'], item['url_code'])
    time.sleep(3)
    govt_rate = get_rate('12/18/2016', '12/19/2016', item['property_code'], item['url_code'], rate_type='GOVERNMENT')
    print('Government rate is: {}'.format(govt_rate))
    print('Commercial rate is: {}'.format(commercial_rate))
