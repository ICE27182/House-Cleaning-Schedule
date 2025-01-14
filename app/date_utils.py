

from .type_aliases import WeekYear
from .type_utils import weekyear_to_tuple, tuple_to_weekyear, weekyear_to_date

from datetime import timedelta, date

def week_difference(date1:date, date2:date) -> int:
    """
    Return 0 if the `date1` and `date2` are in the same week
    Return a positive integer if `date1` is after `date2` 
        e.g. date1 = date(2024, 12, 21), date2 = date(2024, 8, 5)
    Return a negative integer if `date1` is before `date2`
        e.g. date1 = date(2024, 8, 5), date2 = date(2024, 12, 21)
    """
    year1, week_no1, _ = date.isocalendar(date1)
    year2, week_no2, _ = date.isocalendar(date2)
    date1 = date.fromisocalendar(year1, week_no1, 1)
    date2 = date.fromisocalendar(year2, week_no2, 1)
    difference:timedelta = date1 - date2
    return difference.days // 7

def get_today_weekyear() -> WeekYear:
    year, week_no = date.today().isocalendar()[:2]
    return tuple_to_weekyear((week_no, year))

def next_week_weekyear(weekyear:WeekYear) -> WeekYear:
    """Get `WeekYear` one week after the given week"""
    week_no, year = weekyear_to_tuple(weekyear)
    # Dec 28
    # https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://en.wikipedia.org/wiki/ISO_week_date%23:~:text%3DThe%2520number%2520of%2520weeks%2520in,week%2520of%2520the%2520following%2520year.&ved=2ahUKEwjkx-n6hdeJAxVjgf0HHUUFOcAQFnoECBgQAw&usg=AOvVaw3DA1N2wXenxVazXqbpimaq
    total_week_num = date(year, 12, 28).isocalendar()[1]
    if week_no + 1 > total_week_num:
        week_no, year = 1, year + 1
    else:
        week_no += 1
    return tuple_to_weekyear((week_no, year))

def last_week_weekyear(weekyear:WeekYear) -> WeekYear:
    monday = weekyear_to_date(weekyear)
    last_monday = monday - timedelta(7)
    year, week_no, _ = last_monday.isocalendar()
    return tuple_to_weekyear((week_no, year))

def is_present(weekyear:WeekYear) -> bool:
    """Return True if the given `weekyear` is the curent week"""
    return week_difference(date.today(), weekyear_to_date(weekyear)) == 0

def is_past(weekyear:WeekYear) -> bool:
    """Return True if the given `weekyear` is before the current week"""
    return week_difference(date.today(), weekyear_to_date(weekyear)) > 0

def is_future(weekyear:WeekYear) -> bool:
    """Return True if the given `weekyear` is after the current week"""
    return week_difference(date.today(), weekyear_to_date(weekyear)) < 0

def get_weekyear_no(weekyear:WeekYear) -> int:
    """
    Get the number of weeks past since date(1/1/1)
    """
    return week_difference(weekyear_to_date(weekyear), date(1, 1, 1))