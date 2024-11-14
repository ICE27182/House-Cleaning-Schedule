

from .type_aliases import WeekYear, Name, TaskName, TaskDate, Day
from .type_aliases import PathLike
from .type_aliases import ScheduleGenerator, ScheduleGenerated, ScheduleGet
from .type_aliases import RecordGet, RecordData
from .type_utils import tuple_week_year, date_week_year, str_week_year, task_date_to_str

from types import MethodType
from typing import Self
from abc import ABC, abstractmethod

from flask import Flask
import json
import os.path
from datetime import date, timedelta

class _Database(ABC):
    @abstractmethod
    def __getitem__():
        pass

class Schedule(_Database):
    names:tuple[Name] = ('Gregor', 'Swastika', 'Ismail', 'Isabelle', 'Korina', 'Evelin', 'Adarsh', 'Sasa', 'Nil', 'Waqar', 'Amina', 'Justin', 'Sam', 'Davide')
    def __init__(self, ) -> None:
        super().__init__()
        self.tasks:dict[TaskName: ScheduleGenerator] = {}

    def add_task(self, taskname:TaskName, generator:ScheduleGenerator = None, 
                 person_needed:int = None, seed:int = None, day:Day=None) -> None:
        # MODIFY_FLAG
        if not (
            (generator is None) and (None not in (person_needed, seed))
            or
            (generator is not None) and ((None,) * 2 == (person_needed, seed))
        ):
            raise ValueError(
                "Either generator alone or both person_needed and seed must be provided."
            )
        if (day is not None and not (1 <= day <= 7)):
            raise ValueError("day should be between 1 and 7")
        
        self.tasks[taskname] = (generator or 
                                Schedule._generator_template(person_needed, seed, day))
    
    @staticmethod
    def _generator_template(person_needed:int, seed:int, day:Day) -> ScheduleGenerated:
        """
        Only work with weekly tasks that involve every one in the house
        Use your own generator if that is not the case
        """
        BOUND = len(Schedule.names)
        STEP = BOUND // person_needed
        # seed will be an offset of index
        seed = abs(seed) + 5
        # randomness does not really matter here, so anything will do
        seed = ((seed + 271) ^ (seed << 1))
        def generate(week_year:WeekYear) -> (
            dict[TaskName:tuple[None|tuple[Name], TaskDate]]
        ):
            week_no, year = tuple_week_year(week_year)
            # seed is just used as an offset for now
            index = seed + year * 12 + week_no
            name_list = tuple((Schedule.names[(index + i * STEP) % BOUND]
                         for i in range(person_needed)))
            task_date = (None if day is None else 
                         date.fromisocalendar(year, week_no, day))
            return (name_list, task_date)
        return generate
    

    def __getitem__(self, week_year:WeekYear) -> ScheduleGet:
        out:ScheduleGet = {}
        for taskname, generator in self.tasks.items():
            out[taskname] = generator(week_year)
        return out



class Record(_Database):
    def __init__(self, schedule:Schedule, path = None) -> None:
        super().__init__()
        self.data:RecordData = {}
        self.path = path or "Records.json"
        self.schedule = schedule
        self.read()
    
    def read(self, path:PathLike = None) -> bool:
        if path is not None:
            self.path = path
        if not os.path.exists(self.path):
            return False
        with open(self.path, 'r') as json_file:
            try:
                self.data = json.load(json_file)
                return True
            # MODIFY_FLAG except ?:
            except:
                pass
        return False
    
    def write(self, path:PathLike = None) -> None:
        if path is not None:
            self.path = path
        with open(self.path, 'w') as json_file:
            json.dump(self.data, json_file)
    
    def strip_data(self, path:PathLike|bool = True, threshold:int=365) -> None:
        def get_min_max(stripped:RecordData) -> tuple[date, date]:
            min = date.today()
            max = date(1, 1, 1)
            for week_year in stripped.keys():
                week_year = date_week_year(week_year)
                if week_year < min:
                    min = week_year
                if week_year > max:
                    max = week_year
            return (min, max)

        stripped = {}
        for week_year in self.data.keys():
            if date.today() - date_week_year(week_year) > timedelta(threshold):
                stripped[week_year] = self.data[week_year]
        for week_year in stripped.keys():
            del self.date[week_year]
        if path != False and len(stripped) != 0:
            if path == True:
                min, max = get_min_max(stripped)
                path = f"{min} - {max}"
            with open(path, 'w') as json_file:
                json.dump(stripped, json_file)

    def __getitem__(self, week_year:WeekYear) -> RecordGet:
        if week_year not in self.data:
            self.new_week(week_year)
        return self.data[week_year]

    def new_week(self, week_year:WeekYear) -> None:
        self.data[week_year] = {}
        week_schedule:ScheduleGet = self.schedule[week_year]
        for taskname, task_info in week_schedule.items():
            task_info:ScheduleGenerated
            if task_info[0] is not None:
                self.data[week_year][taskname] = (
                    {name:False for name in task_info[0]},
                    task_date_to_str(task_info[1], week_year)
                )
    


def _generator_plastic_garbage(week_year:WeekYear) -> ScheduleGenerated:
    seed = 3
    person_needed = 1
    # seed will be an offset of index
    seed = abs(seed) + 5
    # randomness does not really matter here, so anything will do
    seed = ((seed + 271) ^ (seed << 1))
    BOUND = len(Schedule.names)

    week_no, year = tuple_week_year(week_year)
    # Odd week for plastic
    if week_no % 2 == 1:
        index = seed + year * 12 + week_no // 2
        name_list = (Schedule.names[(index) % BOUND], )
        task_date = date.fromisocalendar(year, week_no, 1)
        return (name_list, task_date)
    else:
        return (None, None)

def _generator_organic_garbage(week_year:WeekYear) -> ScheduleGenerated:
    seed = 4
    # seed will be an offset of index
    seed = abs(seed) + 5
    # randomness does not really matter here, so anything will do
    seed = ((seed + 271) ^ (seed << 1))
    BOUND = len(Schedule.names)

    week_no, year = tuple_week_year(week_year)
    # Even week for Organic
    if week_no % 2 == 0:
        index = seed + year * 12 + week_no // 2
        name_list = (Schedule.names[(index) % BOUND], )
        task_date = date.fromisocalendar(year, week_no, 1)
        return (name_list, task_date)
    else:
        return (None, None)
    
def _generator_cardboard_garbage(week_year:WeekYear) -> ScheduleGenerated:
    seed = 5
    # seed will be an offset of index
    seed = abs(seed) + 5
    # randomness does not really matter here, so anything will do
    seed = ((seed + 271) ^ (seed << 1))
    BOUND = len(Schedule.names)

    def is_cardboard_pre_week() -> bool:
        """The first iso week in the month"""
        if week_no in {date(year, i + 1, 7).isocalendar()[1] for i in range(12)}:
            return True
        return False
        
    week_no, year = tuple_week_year(week_year)
    if is_cardboard_pre_week():
        index = seed + year * 12 + week_no // 12
        name_list = (Schedule.names[(index) % BOUND], )
        task_date = date.fromisocalendar(year, week_no, 7)
        return (name_list, task_date)
    else:
        return (None, None)

def _generator_toilet_cleaning(week_year:WeekYear) -> ScheduleGenerated:
    seed = 6
    # seed will be an offset of index
    seed = abs(seed) + 5
    # randomness does not really matter here, so anything will do
    seed = ((seed + 271) ^ (seed << 1))
    names = ("Waqar", "Isabelle", "Sam", "Evelin", "Amina",)
    BOUND = len(names)
    
    week_no, year = tuple_week_year(week_year)
    
    index = seed + year * 12 + week_no
    name_list = (names[(index) % BOUND], )
    return (name_list, None)

schedule = Schedule()
schedule.add_task("House Vaccuming", None, 2, 0, None)
schedule.add_task("Kitchen Cleaning", None, 2, 1, None)
schedule.add_task("Basement Cleaning", None, 1, 2, None)
schedule.add_task("Plastic Garbage", _generator_plastic_garbage)
schedule.add_task("Organic Garbage", _generator_organic_garbage)
schedule.add_task("Cardboard Garbage", _generator_cardboard_garbage)
schedule.add_task("Toilet Cleaning", _generator_toilet_cleaning)

record = Record(schedule)