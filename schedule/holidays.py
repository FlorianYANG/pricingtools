import json
import pandas
import datetime


def ts2dt(ts):
    # convert timestamp to datetime
    return datetime.datetime(ts.year, ts.month, ts.day)


df = pandas.read_excel("holiday.xlsx", dtype = datetime.datetime)
dict_holiday = {}
for col in df.columns:
    series = df[col].dropna().to_list()
    dict_holiday[col] = [ts2dt(ts) for ts in series]

