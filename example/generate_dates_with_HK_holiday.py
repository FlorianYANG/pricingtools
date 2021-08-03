import datetime
import schedule

start = datetime.datetime(2019,12,1)
end = datetime.datetime(2020,2,29)

obs = schedule.rolling(start, end, "m", holiday=schedule.holidays.dict_holiday['Hongkong'], adjustment="F")
# for d in obs:
    # print(d)

for i in range(5):
    print(schedule.yeardiff(start, end, i))