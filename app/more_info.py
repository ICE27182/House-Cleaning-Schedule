
from .type_aliases import TaskName
from .type_utils import taskname_to_var_name
from .database import record, schedule, Record, Schedule
from flask import Blueprint, render_template

more_info = Blueprint("more_info", __name__)
MORE_INFO_URL_PREFIX = "/cleaning_schedules/more_info"

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

    def html_table(self, record:Record, schedule:Schedule, prior_weeks:int = 3, future_weeks:int = 5) -> str:
        return """
<table class="more_info_table">
    <tr>
        <td>
            <p>a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0</p>
            <p>a1</p>
        </td> 
        <td>
            <p>b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0</p>
            <p>b1</p>
        </td> 
        <td>
            <p>c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0</p>
            <p>c1</p>
        </td>

    </tr>
    <tr>
        <td>
            <p>d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0</p>
            <p>d1</p>
        </td> 
        <td>
            <p>e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0</p>
            <p>e1</p>
        </td> 
        <td>
            <p>f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0</p>
            <p>f1</p>
        </td>

    </tr>
    <tr>
        <td>
            <p>g0g0g0g0g0g0g0g0g0g0g0g0g0g0g0g0</p>
            <p>g1</p>
        </td> 
        <td>
            <p>h0h0h0h0h0h0h0h0h0h0h0h0h0h0h0h0</p>
            <p>h1</p>
        </td> 
        <td>
            <p>i0i0i0i0i0i0i0i0i0i0i0i0i0i0i0i0</p>
            <p>i1</p>
        </td>

    </tr>
</table>
"""


tasknames = (
    "House Vaccuming",
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
            more_info_table = task.html_table(record, schedule)
        )
    return route

for taskname in tasknames:
    more_info.add_url_rule(
        f"/{taskname_to_var_name(taskname)}",
        endpoint = taskname_to_var_name(taskname),
        view_func = create_route(taskname)
    )

