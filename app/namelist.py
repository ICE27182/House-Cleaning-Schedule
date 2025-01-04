

from .type_aliases import NameList, PathLike, WeekYear
from .date_utils import week_difference, last_week_weekyear, is_past
from .type_utils import weekyear_to_date

import re

DEFAULT_OFFSET = 16.0
DEFAULT_PENALTY = 1.0

def read_namelist(path:PathLike) -> NameList:
    """
    The file should be names separated by white space (single or multiple 
    space/newline)
    Name started with # will be ignored (Note that for "# Alex", "Alex" will
    still be stored becuase there is a white space between # and Alex, meaning
    they will be recognized as a name starting with "#" and a name "Alex")
    """
    namelist = {}
    with open(path, "r") as file:
        file = file.read()
        names = re.split(r"\s+", file)
        for name in names:
            if name.startswith("#"): continue
            namelist[name] = DEFAULT_OFFSET
    return namelist

def updated_namelist(namelist:NameList, 
                     record, 
                     up_to_weekyear:WeekYear, 
                     threshold:int=3) -> NameList:
    from .database import RecordGet, Record
    record:Record
    namelist = {name:DEFAULT_OFFSET for name in namelist.keys()}
    # Similar to
    # i = n
    # while n - i <= m
    #     do_something(...)
    #     i -= 1
    weekyear = up_to_weekyear
    while week_difference(
        weekyear_to_date(up_to_weekyear),
        weekyear_to_date(weekyear)
    ) <= threshold:
        recordget:RecordGet = record[weekyear]
        if recordget != Record.RECORD_NO_FOUND:
            # loop through all tasks
            for info in recordget.values():
                # loop through all persons assigned to each task in `weekyear`
                for name, stat in info[0].items():
                    if name not in namelist: continue
                    # Bad if there is a `False` in the past records
                    if is_past(weekyear):
                        if not stat: namelist[name] += DEFAULT_PENALTY
                        # Some rather random constants here for fulfilling
                        # tasks assigned, so people who has done more before
                        # won't have to do as much in the future
                        elif namelist[name] > DEFAULT_OFFSET: 
                            namelist[name] -= 0.25
                        elif namelist[name] >= 1.0: 
                            namelist[name] -= 0.5
                    # In present or future schedules, the value doesn't matter
                    # since no one can say for sure whether the person will
                    # follow the schedule or not
                    else:
                        # I use a smaller constant here becuase we dont know
                        # for sure if the person is gonna do it
                        namelist[name] -= 0.1 if namelist[name] > 1 else 0
        weekyear = last_week_weekyear(weekyear)
    return {name:value for name, value in namelist.items()}

def namelist_to_str(namelist:NameList) -> str:
    return "\n".join((f"{name:16} {namelist[name]}" for name in sorted(namelist.keys())))


namelist_all = read_namelist("namelist.txt")
namelist_toilet = read_namelist("namelist_toilet.txt")
