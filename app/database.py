

"""
Data are stored in json form, so no SQL
But if you want, you can modify Record to wrapper class for SQL, as long as
you can make sure the behavior of __getitem__ remains

People names are stored in this file, in Schedule.names and _generator_.*
to be specific
"""
from .type_aliases import WeekYear, Name, TaskName, Day
from .type_aliases import PathLike
from .type_aliases import ScheduleGenerator, ScheduleGenerated, ScheduleGet
from .type_aliases import RecordGet, RecordData
from .type_utils import tuple_week_year, date_week_year, task_date_to_str

from abc import ABC, abstractmethod
import json
import os.path
from datetime import date, timedelta



class _Database(ABC):
    @abstractmethod
    def __getitem__():
        pass



class Schedule(_Database):
    names:tuple[Name] = (
        'Justin', 'Sam', 
        'Davide', 'Sasa', 
        'Nil', 'Waqar', 
        'Hannah', 'Isabelle', 
        'Korina', 'Evelin', 
        'Adarsh', 'Gregor', 
        'Swastika', 'Ismail',
        'Pati', 'Amina',
    )
    
    def __init__(self) -> None:
        """
        You will have to add tasks with method `add_task` after initiation
        """
        super().__init__()
        # Okay, maybe i should have named it _tasks
        self.tasks:dict[TaskName: ScheduleGenerator] = {}

    def add_task(self, taskname:TaskName, generator:ScheduleGenerator = None, 
                 person_needed:int = None, seed:int = None, day:Day=None) -> None:
        """
        Add task to instances

        `taskname` can be any string, but be sure it is consistent because it
        will be stored in `record` and thus used basically everywhere else.

        generator can be left as None, if `person_needed` and `seed` 
        (and optionally `day`) are passed in. Then a schedule generator will be
        generated automatically with `Schedule._generator_template`.
        Or, you can pass a function like 
        `def _generator_taskname(week_year:WeekYear) -> ScheduleGenerated`

        If generator is None, `person_needed` and `seed` will be used.
        `day` will also be used if it is not None. The three arguments should
        all be int (or None for day if the task last a whole week). 
        If `day` is not None, it should be an int in [1, 7].
        """
        # Dealing with invalid arguments
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
        self.tasks[taskname] = (
                                    generator 
                                    if generator is not None else
                                    Schedule._generator_template(
                                        person_needed, seed, day
                                    )
                               )
    
    @staticmethod
    def _generator_template(person_needed:int, seed:int, day:Day) -> ScheduleGenerator:
        """
        Only work with weekly tasks that involve every one in the house
        Use your own generator if that is not the case (e.g. toilet cleaning)
        """
        BOUND = len(Schedule.names)
        STEP = BOUND // person_needed
        # randomness does not really matter here, so anything will do
        seed = abs(seed + 5)
        seed = ((seed + 271) ^ (seed << 1))
        def generate(week_year:WeekYear) -> ScheduleGenerated:
            week_no, year = tuple_week_year(week_year)
            # seed is only used as an offset for now
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
        """
        (Update self.path and) Read file to self.data
        Return True if the file is read and False if not the case.
        self.data will remain the same if reading fails.

        `path` can be None, but self.path will update no matter reading 
        succeeds or not if `path` is not None.
        """
        if path is not None:
            self.path = path
        if not os.path.exists(self.path):
            return False
        with open(self.path, 'r') as json_file:
            try:
                self.data = json.load(json_file)
                return True
            # e.g. This is an empty file
            except Exception as err:
                print(err)
        return False
    
    def write(self, path:PathLike = None) -> None:
        """
        (Update self.path and) Write record to self.path

        self.path will remain the same if path is None.
        """
        if path is not None:
            self.path = path
        with open(self.path, 'w') as json_file:
            json.dump(self.data, json_file)
    
    def strip_old_data(self, path:PathLike|bool = True, threshold:int=365) -> None:
        """
        Delete old data up to `threshold` days before and store the deleted
        data at `path`.

        The file on disk will not change until method `write` is called.

        Old data will be stored at `path` unless `path` is False. When `path`
        is True, old data will be store at the same directory with generated
        name indicating the time interval
        """
        def get_min_max(stripped:RecordData) -> tuple[date, date]:
            """Used to generate filename"""
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
        # Find old data and store them in `stripped`
        for week_year in self.data.keys():
            if date.today() - date_week_year(week_year) > timedelta(threshold):
                stripped[week_year] = self.data[week_year]
        # Delete old data
        for week_year in stripped.keys():
            del self.data[week_year]
        # Save old data to file
        if path != False and len(stripped) != 0:
            if path == True:
                min, max = get_min_max(stripped)
                path = f"{min} - {max}"
            with open(path, 'w') as json_file:
                json.dump(stripped, json_file)
    
    def strip_future_data(self, path:PathLike|bool = False, threshold:int=0) -> None:
        """
        Delete future data from `threshold` days onwards and store the deleted
        data at `path`.

        The file on disk will not change until method `write` is called.

        Future data will be stored at `path` unless `path` is False. When `path`
        is True, future data will be store at the same directory with generated
        name indicating the time interval
        """
        def get_min_max(stripped:RecordData) -> tuple[date, date]:
            """Used to generate filename"""
            min = date(9999, 12, 31)
            max = date.today()
            for week_year in stripped.keys():
                week_year = date_week_year(week_year)
                if week_year < min:
                    min = week_year
                if week_year > max:
                    max = week_year
            return (min, max)

        stripped = {}
        # Find future data and store them in `stripped`
        for week_year in self.data.keys():
            if date_week_year(week_year) - date.today() > timedelta(threshold):
                stripped[week_year] = self.data[week_year]
        # Delete future data
        for week_year in stripped.keys():
            del self.data[week_year]
        # Save future data to file
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
        """
        Add `week_year` week to `record`. If this week has already existed,
        it will be updated. New week is generated with `schedule`
        """
        self.data[week_year] = {}
        week_schedule:ScheduleGet = self.schedule[week_year]
        for taskname, task_info in week_schedule.items():
            task_info:ScheduleGenerated
            # for example, plastic garbage is taken out twice a week so
            # there are weeks in which no one is assigned to this task,
            # leading to an empty task_info[0], which is supposed to be
            # a name list
            if task_info[0] is not None:
                self.data[week_year][taskname] = (
                    {name:False for name in task_info[0]},
                    task_date_to_str(task_info[1], week_year)
                )
    


"""
Generators for `schedule`
"""
def _generator_plastic_garbage(week_year:WeekYear) -> ScheduleGenerated:
    seed = 30
    # randomness does not really matter here, so anything will do
    seed = abs(seed + 5)
    seed = ((seed + 271) ^ (seed << 1))
    BOUND = len(Schedule.names)

    week_no, year = tuple_week_year(week_year)
    # Odd week for plastic
    if week_no % 2 == 1:
        index = seed + year * 12 + week_no // 2
        name_list = (Schedule.names[(index) % BOUND], )
        # Monday
        # The garbage will be collected on Tuseday
        task_date = date.fromisocalendar(year, week_no, 1)
        return (name_list, task_date)
    else:
        return (None, None)

def _generator_organic_garbage(week_year:WeekYear) -> ScheduleGenerated:
    seed = 8
    # randomness does not really matter here, so anything will do
    seed = abs(seed + 5)
    seed = ((seed + 271) ^ (seed << 1))
    BOUND = len(Schedule.names)

    week_no, year = tuple_week_year(week_year)
    # Even week for Organic
    if week_no % 2 == 0:
        index = seed + year * 12 + week_no // 2
        name_list = (Schedule.names[(index) % BOUND], )
        # Monday
        # The garbage will be collected on Tuseday
        task_date = date.fromisocalendar(year, week_no, 1)
        return (name_list, task_date)
    else:
        return (None, None)
    
def _generator_cardboard_garbage(week_year:WeekYear) -> ScheduleGenerated:
    seed = 5
    # randomness does not really matter here, so anything will do
    seed = abs(seed + 5)
    seed = ((seed + 271) ^ (seed << 1))
    BOUND = len(Schedule.names)

    # Carboard Garbage is collected every monday 
    # in the second week of the month
    def is_cardboard_pre_week() -> bool:
        """The first iso week in the month"""
        if (
            week_no 
            in
            {date(year, i + 1, 7).isocalendar()[1] for i in range(12)}
        ):
            return True
        return False
        
    week_no, year = tuple_week_year(week_year)
    if is_cardboard_pre_week():
        index = seed + year * 12 + week_no // 12
        name_list = (Schedule.names[(index) % BOUND], )
        # Sunday
        # The garbage will be collected on Monday
        task_date = date.fromisocalendar(year, week_no, 7)
        return (name_list, task_date)
    else:
        return (None, None)

def _generator_toilet_cleaning(week_year:WeekYear) -> ScheduleGenerated:
    seed = 6
    # randomness does not really matter here, so anything will do
    seed = abs(seed + 5)
    seed = ((seed + 271) ^ (seed << 1))
    # We need a separate name list here because not every one living in the
    # house use this toilet
    names = ("Waqar", "Isabelle", "Sam", "Evelin", "Amina", "Patti")
    BOUND = len(names)
    
    week_no, year = tuple_week_year(week_year)
    
    index = seed + year * 12 + week_no
    name_list = (names[(index) % BOUND], )
    return (name_list, None)

schedule = Schedule()
schedule.add_task("House Vacuuming", None, 2, 27, None)
schedule.add_task("Kitchen Cleaning", None, 2, 1, None)
schedule.add_task("Basement Cleaning", None, 1, 2, None)
schedule.add_task("Plastic Garbage", _generator_plastic_garbage)
schedule.add_task("Organic Garbage", _generator_organic_garbage)
schedule.add_task("Cardboard Garbage", _generator_cardboard_garbage)
schedule.add_task("Toilet Cleaning", _generator_toilet_cleaning)

record = Record(schedule)