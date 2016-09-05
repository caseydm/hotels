import sys
from freezegun import freeze_time
from app import build_dates, parse_rates
from bs4 import BeautifulSoup


# ensure second set of dates is always in next month
# set datetime.now() using freeze_time(date)
@freeze_time('2016-07-01')
def test_date_beginning_month():
    dates = build_dates()
    assert dates[0]['arrive'] == '07/01/2016'
    assert dates[0]['depart'] == '07/02/2016'
    assert dates[1]['arrive'] == '08/01/2016'
    assert dates[1]['depart'] == '08/02/2016'


@freeze_time('2017-01-31')
def test_date_end_month():
    dates = build_dates()
    assert dates[0]['arrive'] == '01/31/2017'
    assert dates[0]['depart'] == '02/01/2017'
    assert dates[1]['arrive'] == '02/28/2017'
    assert dates[1]['depart'] == '03/01/2017'


def test_parse_rates():
    data = open(sys.path[0] + '/tests/test_data_october_2016.html').read()
    soup = BeautifulSoup(data, 'html.parser')

    rates = parse_rates(soup)

    for rate in rates:
        if rate['date'] == 'Sunday, Oct 02':
            assert rate['price'] == '224.25'
            assert rate['link'] == 'https://marriott.com/reservation/availabilitySearch.mi?isSearch=false&isRateCalendar=false&clusterCode=GOV&corporateCode=GOV&groupCode=&numberOfRooms=1&numberOfGuests=1&incentiveType_Number=&incentiveType=false&useRewardsPoints=false&propertyCode=AHNRZ&fromDate=10/02/16&toDate=10/03/16&costView=isNightlyRateView&ratePlanCode=GVTR&rate=224.25'
        if rate['date'] == 'Wednesday, Oct 26':
            assert rate['price'] == '269.25'
            assert rate['link'] == 'https://marriott.com/reservation/availabilitySearch.mi?isSearch=false&isRateCalendar=false&clusterCode=GOV&corporateCode=GOV&groupCode=&numberOfRooms=1&numberOfGuests=1&incentiveType_Number=&incentiveType=false&useRewardsPoints=false&propertyCode=AHNRZ&fromDate=10/26/16&toDate=10/27/16&costView=isNightlyRateView&ratePlanCode=GVTS&rate=269.25'

    assert len(rates) == 9
