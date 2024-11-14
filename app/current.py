
from .url_prefixes import BUTTONS_URL_PREFIX, CLEANING_SCHEDULES_URL_PREFIX
from .type_aliases import RecordGet, WeekYear, Name, TaskName
from .type_utils import taskname_to_var_name
from .more_info import MORE_INFO_URL_PREFIX
from .date_utils import todays_week_year, tuple_week_year, tuple_next_week_year, str_week_year
from .html_utils import HtmlTable, html_a, html_p
from .database import record


from flask import Blueprint, redirect


buttons = Blueprint("buttons", __name__)

class Button:
    def __init__(self, taskname:TaskName, no:int = 0) -> None:
        self.taskname = taskname
        self.no = no
        buttons.add_url_rule(
            f"/{taskname_to_var_name(taskname)}{no}",
            endpoint = f"{taskname_to_var_name(taskname)}{no}",
            view_func= self._create_route()
        ) 

    def _create_route(self):
        def button_route():
            this_week:RecordGet = current.current_week_record()
            name = tuple(this_week[self.taskname][0].keys())[self.no]
            this_week[self.taskname][0][name] = not this_week[self.taskname][0][name]
            return redirect(CLEANING_SCHEDULES_URL_PREFIX)
        return button_route

    def get_url(self):
        return f"{CLEANING_SCHEDULES_URL_PREFIX}{BUTTONS_URL_PREFIX}/{taskname_to_var_name(self.taskname)}{self.no}"



all_buttons = {
    "House Vaccuming": (Button("House Vaccuming", 0),  Button("House Vaccuming", 1)),
    "Kitchen Cleaning": (Button("Kitchen Cleaning", 0),  Button("Kitchen Cleaning", 1)),
    "Basement Cleaning": (Button("Basement Cleaning"),),
    "Plastic Garbage": (Button("Plastic Garbage"),),
    "Organic Garbage": (Button("Organic Garbage"),),
    "Cardboard Garbage": (Button("Cardboard Garbage"),),
    "Toilet Cleaning": (Button("Toilet Cleaning"),),
}

class Current:
    def __init__(self) -> None:
        self.week_no, self.year = tuple_week_year(todays_week_year())
    
    def this_week(self) -> None:
        self.week_no, self.year = tuple_week_year(todays_week_year())
    
    def next_week(self):
        self.week_no, self.year = tuple_next_week_year(self.week_no, self.year)
    
    def current_week_record(self) -> RecordGet:
        return record[str_week_year((self.week_no, self.year))]
    
    def week_year(self) -> str:
        return str_week_year((self.week_no, self.year))

    def html_table(self, week_year:WeekYear) -> str: 
        week:RecordGet = record[week_year]
        table = HtmlTable(len(week), 4, "center")
        for row_no, item in enumerate(week.items()):
            taskname, task = item
            task:tuple[dict[Name:bool], str]
            # The first column
            table[row_no, 0] = html_p(taskname, "taskname")
            # The second column
            for no, item in enumerate(task[0].items()):
                name, state = item
                table[row_no, 1] += html_p(html_a(
                    all_buttons[taskname][no].get_url(), 
                    name,
                    "green" if state else "red",
                ))
            # The Third Column
            table[row_no, 2] += html_p(task[1])
            # The Forth Column
            table[row_no, 3] += html_a(
                CLEANING_SCHEDULES_URL_PREFIX + MORE_INFO_URL_PREFIX + f"/{taskname_to_var_name(taskname)}",
                "More Info"
            )
        return str(table)
current = Current()
