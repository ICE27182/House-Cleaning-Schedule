

from .type_aliases import NameList, PathLike, WeekYear
from .date_utils import week_difference, last_week_weekyear, is_past
from .type_utils import weekyear_to_date
# from .type_aliases import Name, PathLike, Self, RecordGet, TYPE_CHECKING
# from .type_utils import weekyear_to_date
# from .date_utils import is_past, week_difference, get_today_weekyear
# if TYPE_CHECKING:
#     from .database import Record

import re

DEFAULT_OFFSET = 16.0
DEFAULT_PENALTY = 1.0

def read_namelist(path:PathLike) -> NameList:
    namelist = {}
    with open(path, "r") as file:
        file = file.read()
        names = re.split(r"\s+", file)
        for name in names:
            if name.startswith("#"): continue
            namelist[name] = DEFAULT_OFFSET
    return namelist

def updated_namelist(namelist:NameList, record, up_to_weekyear:WeekYear, threshold:int=3) -> NameList:
    from .database import RecordGet, Record
    namelist = {name:DEFAULT_OFFSET for name in namelist.keys()}
    record:Record
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
                        # Some rather random constants here
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
        # print(weekyear)
        # print_namelist(namelist)
        # print('')
        weekyear = last_week_weekyear(weekyear)
    return {name:value for name, value in namelist.items()}
# {name:ceil(value) for name, value in namelist_all.items() if name in names_to_choose_from}
# {name:ceil(value) for name, value in names_to_choose_from.items()}

def namelist_to_str(namelist:NameList) -> str:
    return "\n".join((f"{name:16} {namelist[name]}" for name in sorted(namelist.keys())))


namelist_all = read_namelist("namelist.txt")
namelist_toilet = read_namelist("namelist_toilet.txt")

# class NameList:
#     DEFAULT_OFFSET = 16
#     def __init__(self, path:PathLike = None) -> None:
#         """
#         Only create an instance, `self.namelist` will be empty
#         """
#         self.path = path
#         self.namelist:dict[Name:int] = {}

    # @classmethod
    # def from_record(cls, record:Record, path:PathLike = None, 
    #                 threshold:int = 20) -> Self:
    #     """
    #     Initialize NameList with a `Record` object

    #     Everyon in record will be added to the returned `namelist`

    #     Discard past records that exceeds `threshold`
    #     """
    #     namelist = NameList(path)
    #     for weekyear, recordget in record.data.items():
    #         recordget:RecordGet
    #         if (
    #             not is_past(weekyear) or 
    #             week_difference(date.today(), weekyear_to_date(weekyear)) > threshold
    #         ):
    #             continue
    #         for task_info in recordget.values():
    #             names_states:dict[Name:bool] = task_info[0]
    #             for name, state in names_states.items():
    #                 if name in namelist.namelist.keys():
    #                     # If True, do nothing; If False, add 1
    #                     namelist.namelist[name] += not state
    #                 else:
    #                     namelist.namelist[name] = NameList.DEFAULT_OFFSET
    #     return namelist
    
    # def __str__(self) -> str:
    #     out = [f"self.path = {self.path}"]
    #     for name, value in self.namelist.items():
    #         out.append(f"{name:16}: \t{value}")
    #     return "\n".join(out)
    
    # def __sub__(self, namelist2:set[str]|Self) -> Self:
    #     if (
    #         isinstance(namelist2, set) and 
    #         (len(namelist2) == 0 or isinstance(namelist2[0], str))
    #     ):
    #         out = NameList()
    #         out.namelist = {
    #             name:value for name, value in self.namelist.items()
    #             if name in (self.namelist.keys() - namelist2)
    #         }
    #         return out
    #     elif isinstance(namelist2, NameList):
    #         out = NameList()
    #         out.namelist = {
    #             name:value for name, value in self.namelist.items()
    #             if (
    #                 name in (self.namelist.keys() - namelist2.namelist.keys())
    #                 and
    #                 self.namelist[name] == namelist2.namelist[name]
    #             )
    #         }
    #         return out
    #     else:
    #         return NotImplemented
    
    # def read_names(self, path:PathLike = None, record = None, threshold:int = 20) -> bool:
    #     """
    #     Return `True` if successfully read the names, 
    #     `self.namelist` will be set to {`Name`: `NameList.DEFAULT_OFFSET`},
    #     and `self.path` will be set to path

    #     Return `False` if failed to read the names, nothing will change

    #     names starting with # will be ignored 
    #         (e.g. #ICE27182 will be ignored, 
    #          but for # ICE27182, ICE27182 will not be ignored)

    #     Return `False` if reading fails, nothing will happen

    #     If `record` is provided, only names inside both the file at `path` 
    #     and the `record` will be added to the final `namelist`

    #     The file should be in form of \s*,\s*(\w*\s*)*
    #     """
    #     if path is None:
    #         path = self.path
    #     try:
    #         with open(path, "r") as file:
    #             file = file.read()
    #             names = re.split(r"(\s*,?\s+|\s+,?\s*)", file)
    #             for name in names:
    #                 if name.startswith("#"): continue
    #                 self.namelist[name] = NameList.DEFAULT_OFFSET
    #     except Exception as e:
    #         print(e)
    #         return False
        
    #     if record is not None:
    #         names_not_in_record = self.namelist.keys()
    #         for weekyear, recordget in record.data.items():
    #             recordget:RecordGet
    #             if (
    #                 not is_past(weekyear) or 
    #                 week_difference(date.today(), weekyear_to_date(weekyear)) > threshold
    #             ):
    #                 continue
    #             for task_info in recordget.values():
    #                 names_states:dict[Name:bool] = task_info[0]
    #                 for name, state in names_states.items():
    #                     if name in self.namelist.keys():
    #                         # If True, do nothing; If False, add 1
    #                         self.namelist[name] += not state
    #                         names_not_in_record -= {name}
    #         for name in names_not_in_record:
    #             del self.namelist[name]
    #     # atomic transaction ACID ;P
    #     self.path = path
    #     return True
        



    # def read_json(self, path:PathLike = None) -> bool:
    #     """
    #     Return `True` if reading succeeds
    #     `self.path` will be updated to `path`

    #     Return `False` if reading fails, nothing will (should) change
    #     """
    #     if path is None:
    #         path = self.path
        
    #     try:
    #         with open(path, "rb") as file:
    #             self.namelist = json.load(file)
    #         self.path = path
    #         return True
    #     except Exception as e:
    #         print(f"{e} (path: {path})")
    #         return False
    
    # def write_json(self, path:PathLike = None) -> bool:
    #     """
    #     Return `True` if writing succeeds
    #     `self.path` will be updated to `path`

    #     Return `False` if reading fails, nothing will (should) change
    #     """
    #     if path is None:
    #         path = self.path
    #     try:
    #         with open(path, "wb") as file:
    #             json.dump(self.namelist, file)
    #         self.path = path
    #         return True
    #     except Exception as e:
    #         print(f"{e} (path: {path})")
    #         return False

