
from .type_aliases import WeekYear, WeekNo, Year, TaskDate, TaskName
from datetime import date

def tuple_to_weekyear(weekyear:tuple[WeekNo, Year]) -> WeekYear:
    
    week_no:WeekNo = weekyear[0]
    year:Year = weekyear[1]
    if not (0 < week_no <= 53 and 0 < year <= 9999):
        raise ValueError("week should be in [1, 53] and year should be in [1, 9999]")
    return f"{week_no} {year}"

def weekyear_to_tuple(weekyear:WeekYear) -> tuple[WeekNo, Year]:
    week_no, year = map(int, weekyear.split())
    if not (0 < week_no <= 53 and 0 < year <= 9999):
        raise ValueError("week should be in [1, 53] and year should be in [1, 9999]")
    return (week_no, year)


def weekyear_to_date(weekyear:WeekYear) -> date:
    """Return a `date` object of the given week. The day is default to Monday"""
    week_no, year = weekyear_to_tuple(weekyear)
    return date.fromisocalendar(year, week_no, 1)

def taskdate_to_str(task_date:TaskDate, weekyear:WeekYear) -> str:
    """
    Transform TaskDate to a more readable string.
        None -> date of Monday to Sunday
        `date` -> dd/mm/yyyy
    """
    week_no, year = weekyear_to_tuple(weekyear)
    if task_date is None:
        monday = date.fromisocalendar(year, week_no, 1)
        sunday = date.fromisocalendar(year, week_no, 7)
        return (
            f"{monday.day}/{monday.month}/{monday.year}" +
            " - " +
            f"{sunday.day}/{sunday.month}/{sunday.year}"
        )
    else:
        return f"{task_date.day}/{task_date.month}/{task_date.year}"

def taskname_to_url_part(taskname:TaskName) -> str:
    """
    Transform taskname to lowercase string connected with _, so it can be
    used as a variable name or a part of a url
    """
    return taskname.lower().replace(' ', '_')
