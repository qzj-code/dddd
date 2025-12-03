import os
import pandas as pd
import os

import pandas as pd

path = os.path.abspath(os.path.dirname(__file__))
df = pd.read_csv(f"{path}/airport.csv")
airport_to_city = dict(zip(df["AirportCode"], df["CityCode"]))


def get_city_code(airport_code):
    return airport_to_city.get(airport_code, airport_code)
print(get_city_code("PEK"))