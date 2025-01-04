
from .constants import NUM_FUTURE_WEEKS_SCHEDULE
from .type_aliases import TaskName, WeekYear, RecordGet, Name
from .html_utils import HtmlTable, html_p
from .type_utils import taskname_to_url_part
from .date_utils import get_today_weekyear, last_week_weekyear, next_week_weekyear
from .database import record, Record

from flask import Blueprint, render_template

more_info = Blueprint("more_info", __name__)

def _weekyear_diff_n_weeks(weekyear:WeekYear, n:int) -> WeekYear:
    """
    Get the `WeekYear` n weeks before or after weekyear
    """
    if n >= 0:
        for _ in range(n):
            weekyear = next_week_weekyear(weekyear)
    else:
        n = -n
        for _ in range(n):
            weekyear = last_week_weekyear(weekyear)
    return weekyear

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

    def get_html_table(self, record:Record, prior_weeks:int = 4, future_weeks:int = 5) -> str:
        # prior + current + future
        rows = prior_weeks + 1 + future_weeks
        this_weekyear = get_today_weekyear()
        table = HtmlTable(rows, 2, "center")
        # Prior weeks and current week
        for n in range(-prior_weeks, future_weeks + 1):
            weekyear = _weekyear_diff_n_weeks(this_weekyear, n)
            week:RecordGet = record[weekyear]
            # Garbages are not weekly, but twice a week or once a month
            if self.taskname not in week:
                continue
            task:tuple[dict[Name:bool], str] = week[self.taskname]
            # The First column
            for item in task[0].items():
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


def create_route(taskname:TaskName):
    def route():
        task = MoreInfo(taskname)
        return render_template(
            task.html_path,
            more_info_table = task.get_html_table(
                record, future_weeks=NUM_FUTURE_WEEKS_SCHEDULE
            )
        )
    return route

tasknames = (
    "House Vacuuming",
    "Kitchen Cleaning",
    "Basement Cleaning",
    "Plastic Garbage",
    "Organic Garbage",
    "Cardboard Garbage",
    "Toilet Cleaning",
)

for taskname in tasknames:
    more_info.add_url_rule(
        f"/{taskname_to_url_part(taskname)}",
        endpoint = taskname_to_url_part(taskname),
        view_func = create_route(taskname)
    )
