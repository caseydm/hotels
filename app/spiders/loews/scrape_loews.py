import requests
import json
import time
import os
import ast


def getCookies(arrive, depart):
    cookies = {
        '__qca': 'P0-1205682135-1452906163124',
        '__atssc': 'google%3B4',
        'sat_ref': 'https://www.google.com/',
        'HeBSCMSPremium60': '2k9mj35bemloilmbh62od4cib2',
        '_browserData': 'U2FsdGVkX1%2F0YS7AQCgTq6sZzKS%2FWZzZkyLiVNfqL1WzysHe5yIkJOmnAb1szU8Cl8Lud5nmdVzO9WkpoheIOm8w5uLBkGeAJl4cMiWeMrCqxMQxieD8F4Y1yEXP9j5p3B47CNqDWLX0Ym%2BK4UwV7rinX5h1jxKhICzwLf3e6jaP5%2BrZNNQLm5APhV5Q8U6DSa%2FTh329oGw2ViN2wQwOKjYw0I0gGg7beABB2aI6oXnzaYHMyTKFAqbauZYex9XngxiXb9TjpqH4266RVyuCAm44%2BB%2FyazT6IFrEwo5AR9umB0FQmJBDlgABNGWP8lIUQ8P5B0RzayksXV94yYvWpwlgwcIfSzWIvtw5b9S3W2Sx2j2XyiZSEBHtjf6z8YB1ieekfajAtcma4bv%2Fi1zvDQUab%2B2G9Hal2FM2%2BJEmklUkkAk8o1Xbw5rr6AYwxE6tSHGQJgk%2FnrYJvDC7nNYSQFtiBHd8AMzEp2DoHRTmr9P7gTZL0ql4OQn8ywVyci2UiG4QgSU2VmTis%2BBccRBpRdwFs5IHJPPfOz0B4QvvOZo7mSn4v846xTwMKD6rYxoU4GbSlFy6mwIVyG1GzxYyyAy8G3VL6rRpLEjXdcZGSl0GznlPQ5jYD3K8atyrPjR7JC5D%2FFdc0P3OBHUUV1w0o9OiQ3TKfmZqwt4lNEDkP9i4o8m67xltfQhjWniqiyzLk0UlMvQeV0QyjVK1APHpzGyaWTCgeM%2BpUJc6nXReU0RhwEmwFxztTbxt2y0n5zkzkuveqmnFbLo0V21ZO0xAlA%3D%3D',
        '__atuvc': '15%7C2%2C0%7C3%2C13%7C4%2C8%7C5',
        '__atuvs': '56aecabcf40e4190002',
        's_cc': 'true',
        'PRUM_EPISODES': 's=1454296004767&r=https%3A//www.loewshotels.com/reservations/atlanta-hotel/checkin/'+ arrive + '/checkout/' + depart + '/rate_type/GOVERNMENT/adults/2/children/0',
        '__hebs_v': '%7B%22fv%22%3A1452906160000%2C%22r%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%2C%22s%22%3A1454295738000%2C%22e%22%3A1454297205000%2C%22v%22%3A9%2C%22pv%22%3A226%2C%22pvs%22%3A16%2C%22lv%22%3A1454296005000%7D',
        '__hebs_n': '%7B%22lp%22%3A%22%5C%2Fatlanta-hotel%22%2C%22pp%22%3A%22%5C%2Fen%5C%2Freservations%5C%2Fgetroomsrates%22%2C%22cp%22%3A%22%5C%2Freservations%5C%2Fatlanta-hotel%5C%2Fcheckin%5C%2F2016-01-31%5C%2Fcheckout%5C%2F2016-02-02%5C%2Frate_type%5C%2FGOVERNMENT%5C%2Fadults%5C%2F2%5C%2Fchildren%5C%2F0%22%7D',
        '__hebs_g': '%7B%22c%22%3A%22NA%22%2C%22cn%22%3A%22United+States%22%2C%22cc%22%3A%22US%22%2C%22cc3%22%3A%22USA%22%2C%22r%22%3A%22NV%22%2C%22ci%22%3A%22Las+Vegas%22%2C%22lat%22%3A36.173698425293%2C%22lon%22%3A-115.1242980957%7D',
        '__hebs_c': '%5B%5D',
        'mbox': 'PC#1452906162099-317200.17_47#1455505608|session#1454295740158-138131#1454297868|check#true#1454296068',
        's_fid': '6DED7CAF8BFCCF72-0DA85B48D697BFD0',
    }
    return cookies


def getHeaders(arrive, depart):
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
        'Referer': 'https://www.loewshotels.com/reservations/atlanta-hotel/checkin/' + arrive + '/checkout/' + depart + '/rate_type/GOVERNMENT/adults/2/children/0',
        'DNT': '1',
    }
    return headers


def get_rate(arrive, depart, govt=''):
    data = 'hotel=LATL&checkin=' + arrive + '&checkout=' + depart + '&adults%5B%5D=2&children%5B%5D=0&rate_type=GOVERNMENT&rate_code='
    response = requests.post('https://www.loewshotels.com/en/reservations/getavailability', headers=getHeaders(arrive, depart), cookies=getCookies(arrive, depart), data=data)
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


print(get_rate('12/18/2016', '12/19/2016'))
