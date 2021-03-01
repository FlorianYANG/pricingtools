import numpy as np
import datetime as dt
import pandas as pd

tseries = [dt.datetime(2020,1,1), dt.datetime(2020,1,2)]
t = pd.DataFrame([1,2],tseries, ['undl'])

print(t)