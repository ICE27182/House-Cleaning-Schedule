

from .type_aliases import WeekYear, TaskDate, WeekNo, Year
from .type_utils import tuple_week_year, str_week_year

from datetime import timedelta, date

def week_year_difference(week_year1:WeekYear, week_year2:WeekYear) -> timedelta:
    date1 = tuple_week_year(week_year1)
    date2 = tuple_week_year(week_year2)
    date1 = date.fromisocalendar(date1[1], date1[0], 4)
    date2 = date.fromisocalendar(date2[1], date2[0], 4)
    return date1 - date2

def todays_week_year() -> WeekYear:
    return str_week_year(date.today().isocalendar()[:2])



def tuple_next_week_year(week_no:WeekNo, year:Year) -> tuple[WeekNo, Year]:
    # Dec 28
    # https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://en.wikipedia.org/wiki/ISO_week_date%23:~:text%3DThe%2520number%2520of%2520weeks%2520in,week%2520of%2520the%2520following%2520year.&ved=2ahUKEwjkx-n6hdeJAxVjgf0HHUUFOcAQFnoECBgQAw&usg=AOvVaw3DA1N2wXenxVazXqbpimaq
    total_week_num = date(year, 12, 28).isocalendar()[1]
    if week_no + 1 > total_week_num:
        week_no, year = 1, year + 1
    else:
        week_no += 1
    return week_no, year