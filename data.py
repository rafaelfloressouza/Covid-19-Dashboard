import requests
import pandas as pd
from datetime import datetime
import constants as const
import ast
from dash.exceptions import PreventUpdate

# def get_all_data():
#     url = 'https://api.covid19api.com/all'
#     json_string = requests.get(url).json()
#     df = pd.DataFrame(json_string)
#     df = df[['Country', 'CountryCode', 'Confirmed', 'Deaths', 'Recovered', 'Date']]
#     print(df.memory_usage(index=True).sum())

def get_total_daily_df(country, label):
    url = 'https://api.covid19api.com/total/dayone/country/{country}/status/{label}'
    url = url.format(country=country, label=label)  # Getting data for respective country.

    json_string = requests.get(url).json()
    df = pd.DataFrame(json_string)

    df = df[['Cases', 'Date']]
    df['Daily'] = df['Cases'] - df['Cases'].shift()
    df['Daily'] = df['Daily'].apply(abs)
    df.fillna(value=0, inplace=True)
    return df

def get_data(country):
    data_dict = {}

    # Getting total cases, deaths, recovered.
    for label in const.LABELS:
        data_dict[label] = get_total_daily_df(country, label)
    return data_dict['confirmed'].to_json(), data_dict['recovered'].to_json(), data_dict['deaths'].to_json()


def get_summary():
    url = 'https://api.covid19api.com/summary'

    json_string = requests.get(url).json()
    df = pd.DataFrame(json_string['Countries'])
    df = df[['Country', 'CountryCode', 'Slug', 'TotalConfirmed', 'TotalDeaths', 'TotalRecovered']].to_json()

    return df
