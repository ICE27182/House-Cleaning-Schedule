
from .url_prefixes import MORE_INFO_URL_PREFIX
from .constants import LOOKBACK_WEEKS_FOR_SCHEDULING, NUM_FUTURE_WEEKS_SCHEDULE
from .type_aliases import TaskName, WeekYear, RecordGet, Name, ScheduleGet
from .html_utils import HtmlTable, html_a, html_p
from .type_utils import taskname_to_url_part
from .date_utils import get_today_weekyear, last_week_weekyear, next_week_weekyear
from .database import record, schedule, Record, Schedule
from flask import Blueprint, render_template

more_info = Blueprint("more_info", __name__)

def _week_year_n_week_diff(week_year:WeekYear, n:int) -> WeekYear:
    if n >= 0:
        for _ in range(n):
            week_year = next_week_weekyear(week_year)
    else:
        n = -n
        for _ in range(n):
            week_year = last_week_weekyear(week_year)
    return week_year
class MoreInfo:
    def __init__(self, taskname:TaskName, html_path:str=None) -> None:
        self.taskname = taskname
        self.html_path = (
            html_path or 
            ("/cleaning_schedules/more_info/" +
            MoreInfo.html_filename_format(taskname) +
            ".html")
        )
    @staticmethod
    def html_filename_format(taskname:str) -> str:
        return taskname.lower().replace(' ', '_')

    def html_table(self, record:Record, schedule:Schedule, prior_weeks:int = 4, future_weeks:int = 5) -> str:
        # prior + current + future
        rows = prior_weeks + 1 + future_weeks
        this_week_year = get_today_weekyear()
        table = HtmlTable(rows, 2, "center")
        # Prior weeks and current week
        for n in range(-prior_weeks, future_weeks + 1):
            week_year = _week_year_n_week_diff(this_week_year, n)
            week:RecordGet = record[week_year]
            # Garbages are not weekly, but twice a week or once a month
            if self.taskname not in week:
                continue
            task:tuple[dict[Name:bool], str] = week[self.taskname]
            # The First column
            for no, item in enumerate(task[0].items()):
                name, state = item
                table[n + prior_weeks, 0] += html_p(
                    name,
                    ("green" if state else "red") +
                    (" more_info_current_week" if n == 0 else "")
                )
            # The Second Column
            table[n + prior_weeks, 1] += html_p(
                task[1],
                "more_info_current_week" if n == 0 else None
            )
        return str(table)


tasknames = (
    "House Vacuuming",
    "Kitchen Cleaning",
    "Basement Cleaning",
    "Plastic Garbage",
    "Organic Garbage",
    "Cardboard Garbage",
    "Toilet Cleaning",
)


def create_route(taskname:TaskName):
    def route():
        task = MoreInfo(taskname)
        return render_template(
            task.html_path,
            more_info_table = task.html_table(record, schedule, future_weeks=NUM_FUTURE_WEEKS_SCHEDULE)
        )
    return route

for taskname in tasknames:
    more_info.add_url_rule(
        f"/{taskname_to_url_part(taskname)}",
        endpoint = taskname_to_url_part(taskname),
        view_func = create_route(taskname)
    )

