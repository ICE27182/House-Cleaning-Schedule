

from datetime import date
from os import PathLike # To be imported by other modules
from typing import Callable, TYPE_CHECKING, Self # `TYPE_CHECKING`, `Self` to be imported by other modules

type Name = str
type TaskName = str
type WeekYear = str
type TaskDate = None | date
type WeekNo = int
type Year = int
type Day = None | int

# mainly associated with database.Schedule
type ScheduleGenerator = Callable[[WeekYear], ScheduleGenerated]
type ScheduleGenerated = tuple[None | tuple[Name], TaskDate]
type ScheduleGet = dict[TaskName: ScheduleGenerated]
# mainly associated with database.Record
type RecordGet = dict[TaskName: tuple[dict[Name:bool], str]]
type RecordData = dict[WeekYear: RecordGet]

type NameList = dict[Name: float]

# html_utils
type RowNo = int
type ColNo = int

