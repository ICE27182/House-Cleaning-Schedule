
from datetime import date
from os import PathLike
from typing import Callable

type Name = str
type TaskName = str
type WeekYear = str
type TaskDate = None | date
type WeekNo = int
type Year = int
type Day = None | int

type ScheduleGenerator = Callable[[WeekYear]]
type ScheduleGenerated = tuple[None | tuple[Name], TaskDate]
type ScheduleGet = dict[TaskName: ScheduleGenerated]

type RecordGet = dict[TaskName: tuple[dict[Name:bool], str]]
type RecordData = dict[WeekYear: RecordGet]

type RowNo = int
type ColNo = int

