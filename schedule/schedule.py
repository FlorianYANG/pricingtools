# should make sure all the date is datetime.datetime

import datetime
import re


OFFSET_UNIT = ['D', 'B', 'W', 'M', 'Y']
ADJUSTMENT_TYPE = ['P', 'MP', 'F', 'MF', 'N']
ADJUSTMENT_TYPE_FULL = {"PRECEDING": "P",
                        "MODIFIEDPRECEDING": "MP",
                        "FOLLOWING": "F",
                        "MODIFIEDFOLLOWING": "MF",
                        "NONE": "N"}

_DAYS_IN_MONTH = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _is_leap(year):
    "year -> 1 if leap year, else 0."
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _days_in_month(year, month):
    "year, month -> number of days in that month in that year."
    assert 1 <= month <= 12, month
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]


def _is_month_end(d):
    return d.day == _days_in_month(d.year, d.month)


def _offset_amount_parser(amount: str):
    "parsing string like 1D, 2W, 3M, return number and letter"
    pattern = re.compile("(\d*)(\w+)")
    res = pattern.findall(amount)
    return res[0]


def apply_offset(d, amount, unit):
    if unit == "D":
        offset = datetime.timedelta(days=amount)
        return d + offset
    if unit == "W":
        offset = datetime.timedelta(weeks=amount)
        return d + offset
    if unit == "M":
        new_month = (d.month - 1 + amount) % 12 + 1
        max_day = _days_in_month(d.year, new_month)
        if d.day > max_day:
            return d.replace(year=d.year + (d.month - 1 + amount) // 12, month=new_month, day=max_day)
        else:
            return d.replace(year=d.year + (d.month - 1 + amount) // 12, month=new_month)
    if unit == "Y":
        if not _is_leap(d.year + amount) and d.month == 2 and d.day == 29:
            return d.replace(year=d.year + amount, day=28)
        else:
            return d.replace(year=d.year + amount)
    raise (ValueError, "rolling method is not correct, must end with one of D,W,M,Y")


def apply_adjustment(d, holiday, adjustment):
    # apply business day adjustment, P, MP, F, MF, N
    adjustment = adjustment.upper()
    if adjustment in ADJUSTMENT_TYPE_FULL:
        adjustment = ADJUSTMENT_TYPE_FULL[adjustment]
    elif adjustment not in ADJUSTMENT_TYPE:
        raise ValueError
    # weekend
    while d.weekday() in (5,6) or d in holiday:
        if adjustment == "P":
            d = d - datetime.timedelta(days=1)
        if adjustment == "F":
            d = d + datetime.timedelta(days=1)
        if adjustment == "MP":
            nd = d - datetime.timedelta(days=1)
            if nd.month != d.month:
                adjustment = "F"
            else:
                d = nd
        if adjustment == "MF":
            nd = d + datetime.timedelta(days=1)
            if nd.month != d.month:
                adjustment = "P"
            else:
                d = nd
        if adjustment == "N":
            return None

    return d


def apply_bd_offset(d, holiday, amount):
    # offset like -2BD doesnt need adjustment
    # need to understand case when amount = 0 // means only want to do BD adjustment
    if amount < 0:
        offset = datetime.timedelta(days=-1)
        amount = -amount
    elif amount == 0:
        if d.weekday() not in (5, 6) and d not in holiday:
            return d
        else:
            amount = 1
            offset = datetime.timedelta(days=1)
    else:
        offset = datetime.timedelta(days=1)
    # holiday must be sequence, how to use collection ??
    if not holiday:
        holiday = []
    elif not isinstance(holiday, list):
        raise ValueError

    while amount > 0:
        d = d + offset
        # weekend ??
        if d.weekday() not in (5, 6) and d not in holiday:
            amount -= 1

    return d


def offset(d: datetime, amount, unit=None, holiday=None, adjustment=None):
    if not isinstance(d, datetime.datetime) or not isinstance(d, datetime.date):
        raise ValueError
    # if amount is int, must have type
    if isinstance(amount, int) and not isinstance(unit, str) and type not in OFFSET_UNIT:
        raise ValueError
    # if amount is str, ignore type, acceptable input: B, 2D, M, 12W, 1Y
    if isinstance(amount, str):
        tmp = amount
        amount, unit = _offset_amount_parser(tmp)
        if unit not in OFFSET_UNIT:
            raise ValueError
        amount = 1 if amount == '' else int(amount)
        unit = unit.upper()
        if tmp[0] == "-":
            amount = -amount
    # unit = B, special treatment, combine offset and holiday together
    if unit == "B":
        d = apply_bd_offset(d, holiday, amount)
    # unit != B offset first and then adjust
    else:
        d = apply_offset(d, amount, unit)
        d = apply_adjustment(d, holiday, adjustment)

    return d


def rolling(start, end, amount, unit=None, holiday=None, adjustment=None):
    # if amount is int, must have type
    if isinstance(amount, int) and not isinstance(unit, str) and type not in OFFSET_UNIT:
        raise ValueError
    # if amount is str, ignore type, acceptable input: B, 2D, M, 12W, 1Y
    if isinstance(amount, str):
        tmp = amount
        amount, unit = _offset_amount_parser(tmp)
        unit = unit.upper()

        if unit not in OFFSET_UNIT:
            raise ValueError
        amount = 1 if amount == '' else int(amount)
        if tmp[0] == "-":
            amount = -amount

    obs = [apply_bd_offset(start, holiday, 0)]
    i = 1
    d = offset(start, amount, unit, holiday, adjustment)
    while d <= end:
        obs.append(d)
        i += 1
        d = offset(start, i * amount, unit, holiday, adjustment)

    return obs


class schedule:
    pass


def _has_leap_day(start, end):
    if _is_leap(start.year) and start.month<=2 and datetime.datetime(start.year,2,29)<end:
        return True
    y = start.year
    for i in range(4):
        y = y + 1
        if y > end.year: return False
        if _is_leap(y) and datetime.datetime(y,2,29)<end: return True
    return False

def yeardiff(start, end, convention):
    """
    :param convention:
        0 30/360 EU
        1 30/360 US
        2 Act/360
        3 Act/365
        4 Act/365L
        5 Act/Act ISDA
        6 Act/Act https://www.isda.org/a/NIJEE/ICMA-Rule-Book-Rule-251-reproduced-by-permission-of-ICMA.pdf
    :return:
    """
    if start > end: start, end = end, start

    if convention == 0 or convention == 1:
        y1, m1, d1 = start.year, start.month, start.day
        y2, m2, d2 = end.year, end.month, end.day
        if start.day == 31: d1 = 30
        if start.day == 30 and end.day == 31: d2 = 30

        if convention == 1:
            if _is_month_end(start) and start.month == 2:
                d1 = 30
                if _is_month_end(end) and end.month == 2:
                    d2 = 30
        return (y2-y1) + (m2-m1) / 12 + (d2-d1) / 360

    elif convention == 2:
        return (end - start).days / 360
    elif convention == 3:
        return (end - start).days / 365
    elif convention == 4:
        pass
    elif convention == 5:
        if end.year == start.year:
            return (end - start).days / 366 if _is_leap(start.year) else (end - start).days/365
        else:
            a = (datetime.datetime(start.year, 12, 31) - start).days
            a = a / 366 if _is_leap(start.year) else a / 365
            b = (end - datetime.datetime(end.year, 1, 1)).days + 1
            b = b / 366 if _is_leap(end.year) else b / 365
            return end.year - start.year - 1 + a + b
    elif convention == 6:
        pass
    else:
        raise ValueError

if __name__ == "__main__":
    import holidays
    start = datetime.datetime(2019,12,1)
    end = datetime.datetime(2020,2,29)

    obs = rolling(start, end, "m", holiday=holidays.dict_holiday['Hongkong'], adjustment="F")
    # for d in obs:
        # print(d)

    for i in range(5):
        print(yeardiff(start, end, i))

