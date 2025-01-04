

"""
Data are stored in json form, not SQL
But if you want, you can modify Record to adapt SQL, as long as
you can make sure the behavior of __getitem__ remains
"""
from .constants import LOOKBACK_WEEKS_FOR_SCHEDULING
from .type_aliases import WeekYear, Name, TaskName, Day, PathLike
from .type_aliases import NameList
from .type_aliases import ScheduleGenerator, ScheduleGenerated, ScheduleGet
from .type_aliases import RecordGet, RecordData
from .type_utils import weekyear_to_tuple, weekyear_to_date, taskdate_to_str
from .date_utils import week_difference, is_past, last_week_weekyear
from .namelist import namelist_all, namelist_toilet, updated_namelist

import json
import os.path
from datetime import date
from random import sample


class Schedule:
    def __init__(self, record=None) -> None:
        """
        You will have to add tasks with method `add_task` after initiation
        """
        # Okay, maybe i should have named it _tasks
        self.tasks:dict[TaskName: ScheduleGenerator] = {}
        self.record = record

    def add_task(self, taskname:TaskName, generator:ScheduleGenerator = None, 
                 person_needed:int = None, day:Day=None, namelist = namelist_all) -> None:
        """
        `taskname` can be any string, but be sure it is consistent with
        the one in `record`

        generator can be left as None, if and only if `person_needed`
        (and optionally `day` and namelist) is/are passed. Then a schedule
        generator will be generated automatically with 
        `Schedule._generator_template`.
        Or, you can pass a function like 
        `_generator_taskname(weekyear:WeekYear, booked:set[str] = set(), *)
        -> ScheduleGenerated`

        If the template is used, `day` being left as None means it will last
        for a whole week, instead of for only one specific day.
        `day` should an int ranging in [1, 7]. 1 is Monday
        """
        # Dealing with invalid arguments
        if generator is None == person_needed is None:
            raise ValueError(
                "Exactly one of `generator` and `person_needed` must be provided"
            )
        if (day is not None and not (1 <= day <= 7)):
            raise ValueError("day should be between 1 and 7")
        self.tasks[taskname] = (
                                    generator 
                                    if generator is not None else
                                    Schedule._generator_template(
                                        taskname, person_needed, day, namelist
                                    )
                               )
    
    @staticmethod
    def _generator_template(taskename:TaskName, 
                            person_needed:int, 
                            day:Day,
                            namelist:NameList) -> ScheduleGenerator:
        """
        Only works with weekly tasks
        Use self-defined generator if that is not the case 
            (e.g. toilet cleaning, garbage taking out)
        """
        def _get_names(
                last_week_names:set[str], 
                booked:set[str], 
                namelist:NameList) -> NameList:
            """
            Get people in the `namelist` that are preferably not in `booked`
            and `last_week_names`.
            If there are not enough people with some of them deducted, they
            will still be in the final list
            """
            people_not_booked = namelist.keys() - booked
            # Someone or someones have to do more than one task
            if len(people_not_booked) == 0:
                people_not_booked = namelist.keys()
            people = people_not_booked - last_week_names
            # Everyone not booked (or booked but has to be chosen) has
            # already done the same task last week, so they have to do it again
            if len(people) == 0:
                people = people_not_booked
            return {name:namelist[name] for name in people}

        # Here it's better if generator uses `schedule.record` instead of 
        # the global `record`, but i am too lazy to change it
        def generator(weekyear:WeekYear, booked:set[str] = set(), *, 
                      _taskname:TaskName = taskename, 
                      _namelist:NameList = namelist) -> ScheduleGenerated:
            week_no, year = weekyear_to_tuple(weekyear)
            record_last_weeek:RecordGet = record[last_week_weekyear(weekyear)]
            # `_taskname in record_last_weeek` is necessary 
            # becuase it can be a new task or there is simply a week in which
            # this task was deleted
            if (record_last_weeek == Record.RECORD_NO_FOUND or 
                _taskname not in record_last_weeek):
                last_week_names = set()
            else:
                last_week_names = record_last_weeek[_taskname][0].keys()
            names_to_choose_from:NameList = _get_names(last_week_names, 
                                                       booked, 
                                                       _namelist)
            names = sample(
                tuple(names_to_choose_from.keys()), 
                counts = map(lambda x:round(x), names_to_choose_from.values()),
                k = person_needed
            )
            task_date = (None if day is None else 
                         date.fromisocalendar(year, week_no, day))
            return (names, task_date)
        return generator
    
    def __getitem__(self, weekyear:WeekYear) -> ScheduleGet:
        """
        Generate schedule with given `weekyear`. 
        Past reocrd will be referenced if `self.record` is a `Record` instance
        """
        out:ScheduleGet = {}
        booked = set()
        if self.record is not None:
            global namelist_all, namelist_toilet
            namelist_all = updated_namelist(
                namelist_all, 
                self.record, 
                last_week_weekyear(weekyear), 
                LOOKBACK_WEEKS_FOR_SCHEDULING
            )
            namelist_toilet = updated_namelist(
                namelist_toilet, 
                self.record, 
                last_week_weekyear(weekyear), 
                LOOKBACK_WEEKS_FOR_SCHEDULING
            )
        for taskname, generator in self.tasks.items():
            out[taskname] = generator(weekyear, booked)
            if out[taskname][0] is not None:
                booked |= set(out[taskname][0])
        return out



class Record:
    NO_FOUND = "404_NO_FOUND :("
    RECORD_NO_FOUND:RecordGet = {NO_FOUND:()}

    def __init__(self, schedule:Schedule, path = None) -> None:
        self.data:RecordData = {}
        self.path = path or "Records.json"
        self.schedule = schedule
        self.read()
    
    @staticmethod
    # mainly for debug use
    def print_recordget(recordget:RecordGet) -> None:
        def parse_name_states(name_stats:dict[Name:bool]) -> str:
            out = []
            for name, state in name_states.items():
                if state:
                    out.append("\033[38;2;0;255;0m")
                else:
                    out.append("\033[38;2;255;0;0m")
                out.append(f"{name:^16}\033[0m\t")
            return "".join(out)

        for taskname, info in recordget.items():
            name_states = info[0]
            time = info[1]
            print(
                f"{taskname:24}\t{time:25}\t{parse_name_states(name_states)}"
            )
        print('-' * 80)
    
    @staticmethod
    # mainly for debug use
    def recordget_to_str(recordget:RecordGet) -> str:
        def parse_name_states(name_stats:dict[Name:bool]) -> str:
            out = []
            for name, state in name_stats.items():
                if state:
                    out.append("\033[38;2;0;255;0m")
                else:
                    out.append("\033[38;2;255;0;0m")
                out.append(f"{name:^16}\033[0m\t")
            return "".join(out)
        return "\n".join(
            (f"{taskname:24}\t{info[1]:25}\t{parse_name_states(info[0])}"
            for taskname, info in recordget.items())
        ) + '\n' + '-' * 80

    def print_weekyear(self, weekyear:WeekYear) -> None:
        Record.print_recordget(self[weekyear])
    
    def str_weekyear(self, weekyear:WeekYear) -> str:
        return Record.recordget_to_str(self[weekyear])

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


    def strip_past_records(self, path:PathLike|bool = True, threshold:int=54) -> None:
        """
        Delete old data up to `threshold` days before and store the deleted
        data at `path`.

        If threshold is negative, it will remove past, present and part of
        the future records that exceeds the threshold.

        The file on disk will not change until method `write` is called.

        Old data will be stored at `path` unless `path` is False. When `path`
        is True, old data will be store at the same directory with generated
        name indicating the time interval
        """
        def get_min_max(stripped:RecordData) -> tuple[date, date]:
            """Used to generate filename"""
            min = date.today()
            max = date(1, 1, 1)
            for weekyear in stripped.keys():
                weekyear = weekyear_to_date(weekyear)
                if weekyear < min:
                    min = weekyear
                if weekyear > max:
                    max = weekyear
            return (min, max)

        stripped = {}
        # Find old data and store them in `stripped`
        for weekyear in self.data.keys():
            if week_difference(date.today(), weekyear_to_date(weekyear)) > threshold:
                stripped[weekyear] = self.data[weekyear]
        # Delete old data
        for weekyear in stripped.keys():
            del self.data[weekyear]
        # Save old data to file
        if path != False and len(stripped) != 0:
            if path == True:
                min, max = get_min_max(stripped)
                path = f"{min} - {max}"
            with open(path, 'w') as json_file:
                json.dump(stripped, json_file)
    
    def strip_future_records(self, path:PathLike|bool = False, threshold:int=0) -> None:
        """
        Delete future data from `threshold` days onwards and store the deleted
        data at `path`.

        If threshold is negative, it will remove future, present and part of
        the past records that exceeds the threshold.

        The file on disk will not change until method `write` is called.

        Future data will be stored at `path` unless `path` is False. When `path`
        is True, future data will be store at the same directory with generated
        name indicating the time interval
        """
        def get_min_max(stripped:RecordData) -> tuple[date, date]:
            """Used to generate filename"""
            min = date(9999, 12, 31)
            max = date.today()
            for weekyear in stripped.keys():
                weekyear = weekyear_to_date(weekyear)
                if weekyear < min:
                    min = weekyear
                if weekyear > max:
                    max = weekyear
            return (min, max)

        stripped = {}
        # Find future data and store them in `stripped`
        for weekyear in self.data.keys():
            if week_difference(date.today(), weekyear_to_date(weekyear)) < -threshold:
                stripped[weekyear] = self.data[weekyear]
        # Delete future data
        for weekyear in stripped.keys():
            del self.data[weekyear]
        # Save future data to file
        if path != False and len(stripped) != 0:
            if path == True:
                min, max = get_min_max(stripped)
                path = f"{min} - {max}"
            with open(path, 'w') as json_file:
                json.dump(stripped, json_file)
    

    def __getitem__(self, weekyear:WeekYear) -> RecordGet:
        """
        Return the records for the given `weekyear`

        If the queried record cannot be found
            If a future or present `weekyear` is given, records will be 
            generated and returned
            If a past `weekyear` is given, `Record.RECORD_NO_FOUND` will return
        """
        if weekyear not in self.data:
            if is_past(weekyear):
                return Record.RECORD_NO_FOUND
            else:
                self.new_week(weekyear)
        return self.data[weekyear]


    def new_week(self, weekyear:WeekYear) -> None:
        """
        Add `weekyear` week to `record`. If this week has already existed,
        it will be updated. New week is generated with `schedule`
        """
        self.data[weekyear] = {}
        week_schedule:ScheduleGet = self.schedule[weekyear]
        for taskname, task_info in week_schedule.items():
            task_info:ScheduleGenerated
            # for example, plastic garbage is taken out twice a week so
            # there are weeks in which no one is assigned to this task,
            # leading to an empty task_info[0], which is supposed to be
            # a name list
            if task_info[0] is not None:
                self.data[weekyear][taskname] = (
                    {name:False for name in task_info[0]},
                    taskdate_to_str(task_info[1], weekyear)
                )
    


"""
Generators for tasks that is not weekly
"""
# Since we cannot access the nested function _get_names defined in 
# Schedule._generator_template
def _get_names_NAMELIST(last_week_names, booked:set[str]) -> NameList:
    people_not_booked = namelist_all.keys() - booked
    # Someone or someones have to do more than one job
    if len(people_not_booked) == 0:
        people_not_booked = namelist_all.keys()
    people = people_not_booked - last_week_names
    # All People not booked (or booked but has to be chosen) have
    # already done the same task last week, so they have to do it again
    if len(people) == 0:
        people = people_not_booked
    return {name:namelist_all[name] for name in people}
    
def _generator_plastic_garbage(weekyear:WeekYear, booked:set[str] = set()) -> ScheduleGenerated:
    week_no, year = weekyear_to_tuple(weekyear)
    # Odd week for plastic (At least before 2028/2029, becuase 2028 has 53
    # weeks, an odd number of weeks)
    if week_no % 2 == 1:
        record_last_weeek = record[last_week_weekyear(weekyear)]
        if (
            record_last_weeek == Record.RECORD_NO_FOUND or 
            "Plastic Garbage" not in record_last_weeek
        ):
            last_week_names = set()
        else:
            last_week_names = record_last_weeek["Plastic Garbage"][0].keys()
        names_to_choose_from = _get_names_NAMELIST(last_week_names, booked)
        names = sample(
            tuple(names_to_choose_from.keys()), 
            counts = map(lambda x:int(round(x)), names_to_choose_from.values()),
            k = 1
        )
        # Monday
        # The garbage will be collected on Tuseday, so the it should be 
        # taken out on Monday
        task_date = date.fromisocalendar(year, week_no, 1)
        return (names, task_date)
    else:
        return (None, None)

def _generator_organic_garbage(weekyear:WeekYear, booked:set[str] = set()) -> ScheduleGenerated:
    week_no, year = weekyear_to_tuple(weekyear)
    # Even week for organic (At least before 2028/2029, becuase 2028 has 53
    # weeks, an odd number of weeks)
    if week_no % 2 == 0:
        record_last_weeek = record[last_week_weekyear(weekyear)]
        if (
            record_last_weeek == Record.RECORD_NO_FOUND or
            "Organic Garbage" not in record_last_weeek
        ):
            last_week_names = set()
        else:
            last_week_names = record_last_weeek["Organic Garbage"][0].keys()
        names_to_choose_from = _get_names_NAMELIST(last_week_names, booked)
        names = sample(
            tuple(names_to_choose_from.keys()), 
            counts = map(lambda x:int(round(x)), names_to_choose_from.values()),
            k = 1
        )
        # Monday
        # The garbage will be collected on Tuseday, so the it should be 
        # taken out on Monday
        task_date = date.fromisocalendar(year, week_no, 1)
        return (names, task_date)
    else:
        return (None, None)
    
def _generator_cardboard_garbage(weekyear:WeekYear, booked:set[str] = set()) -> ScheduleGenerated:
    def _is_first_week_in_the_month(week_no, year) -> bool:
        """
        Carboards are taken out every the monday of the second week of the 
        month, so we check if this week is the first week of the month, of
        which we should take them out on sunday
        """
        if (
            week_no 
            in
            {date(year, i + 1, 7).isocalendar()[1] for i in range(12)}
        ):
            return True
        return False
        
    week_no, year = weekyear_to_tuple(weekyear)
    if _is_first_week_in_the_month(week_no, year):
        record_last_weeek = record[last_week_weekyear(weekyear)]
        if (
            record_last_weeek == Record.RECORD_NO_FOUND or
            "Cardboard Garbage" not in record_last_weeek
        ):
            last_week_names = set()
        else:
            last_week_names = record_last_weeek["Cardboard Garbage"][0].keys()
        names_to_choose_from = _get_names_NAMELIST(last_week_names, booked)
        names = sample(
            tuple(names_to_choose_from.keys()), 
            counts = map(lambda x:int(round(x)), names_to_choose_from.values()),
            k = 1
        )
        # Sunday
        # The garbage will be collected on Monday
        task_date = date.fromisocalendar(year, week_no, 7)
        return (names, task_date)
    else:
        return (None, None)


schedule = Schedule()
schedule.add_task("House Vacuuming", None, 2)
schedule.add_task("Kitchen Cleaning", None, 2)
schedule.add_task("Basement Cleaning", None, 1)
schedule.add_task("Plastic Garbage", _generator_plastic_garbage)
schedule.add_task("Organic Garbage", _generator_organic_garbage)
schedule.add_task("Cardboard Garbage", _generator_cardboard_garbage)
schedule.add_task("Toilet Cleaning", None, 1, None, namelist_toilet)

record = Record(schedule)
schedule.record = record