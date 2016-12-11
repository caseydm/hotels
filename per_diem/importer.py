import os
import csv
from models import PerDiemRate, create_db_session

session = create_db_session()

def import_per_diem():
    # open file
    csv_file = os.path.join(os.path.dirname(__file__), 'perdiem.csv')
    with open(csv_file) as f:
        reader = csv.reader(f)
        for row in reader:
            state = row[0]
            locality = row[1]
            county = row[2] 
            season_begin = row[3]
            season_end = row[4]
            max_lodging = row[5]
            local_meals = row[6]
            proportional_meals = row[7]
            max_per_diem_rate = row[8]
            effective_date = row[9]

            fields = state, locality, county, season_begin, season_end, \
                max_lodging, local_meals, proportional_meals, max_per_diem_rate, \
                effective_date

            # create rate
            rate = PerDiemRate(*fields)
            
            # add
            session.add(rate)

    # save to database
    session.commit()

import_per_diem()