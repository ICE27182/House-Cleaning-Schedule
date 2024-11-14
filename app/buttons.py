

from .type_aliases import RecordGet, TaskName
from .type_utils import taskname_to_var_name
from .current import current
from .cleaning_schedules import CLEANING_SCHEDULES_URL_PREFIX

from flask import Blueprint, redirect


buttons = Blueprint("buttons", __name__)
BUTTONS_URL_PREFIX = "/buttons"

class Button:
    def __init__(self, taskname:TaskName, no:int = 0) -> None:
        self.taskname = taskname
        self.no = no
        buttons.add_url_rule(
            f"/{taskname_to_var_name(taskname)}",
            endpoint = taskname_to_var_name(taskname),
            view_func= self._create_route()
        ) 

    def _create_route(self):
        def route():
            taskname = taskname_to_var_name(self.taskname)
            this_week:RecordGet = current.current_week_record()
            name = tuple(this_week[taskname][0].keys())[self.no]
            this_week[taskname][0][name] = not this_week[taskname][0][name]
            return redirect(CLEANING_SCHEDULES_URL_PREFIX)
        return route

    def get_url(self):
        return BUTTONS_URL_PREFIX + f"/{taskname_to_var_name(self.taskname)}"

