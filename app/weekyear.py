
from datetime import date, timedelta
from collections.abc import Sequence
from typing import Self


class WeekYear(Sequence):
    def __init__(self, week:int, year:int):
        if year < 1 or year > 9999:
            raise ValueError(
                "`year` should be larger than 0 and smaller than 9999. "
                + f"Got {year}."
            )
        elif week < 0 or week > WeekYear.week_num_in_year(year):
            raise ValueError(
                "`week` should be larger than 0 and smaller than "
                + f"{WeekYear.week_num_in_year(year)} in the given year {year}. "
                + f"Got {week}."
            )
        self.week = week
        self.year = year
    
    @classmethod
    def from_date(cls, date_obejct:date) -> Self:
        if not isinstance(date_obejct, date):
            raise TypeError(
                "`date_object` must be of type `date`. "
                + f"Got {type(date_object)}"
            )
        return cls(date_obejct.isocalendar().week, date_obejct.isocalendar().year)
    
    @classmethod
    def from_str(cls, string:str) -> Self:
        if not isinstance(string, str):
            raise TypeError(
                "`date_object` must be of type `str`. "
                + f"Got {type(string)}"
            )
        weekyear = string.split(" ")
        if len(weekyear) != 2:
            raise ValueError(f"Unsupported format. Got {string}")
        return cls(int(weekyear[0]), int(weekyear[1]))
    
    @classmethod
    def present_weekyear(cls) -> Self:
        return cls.from_date(date.today())
    
    def week_count_from_1_1_1(self) -> int:
        return self - date(1, 1, 1)

    def __str__(self) -> str:
        return f"{self.week} {self.year}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(week={self.week}, year={self.year})"
    
    def __iter__(self):
        return iter(tuple(self.week, self.year))

    def __getitem__(self, index):
        if index == 0 or index == -2: return self.week
        elif index == 1 or index == -1: return self.year
        else: return IndexError("Index out of range")
    
    def __len__(self) -> int:
        return 2
    
    def __eq__(self, other:Self) -> Self:
        if not isinstance(other, WeekYear):
            raise TypeError(
                "Comparison not supported between instances of "
                f"{type(self)} and {type(other)}."
            )
        return self.week == other.week and self.year == other.year
    
    def __hash__(self):
        return hash((self.week, self.year))
    
    def __lt__(self, other:Self) -> Self:
        if not isinstance(other, WeekYear):
            raise TypeError(
                "Comparison not supported between instances of "
                f"{type(self)} and {type(other)}."
            )
        return other - self > 0
    
    def __sub__(self, subtractor:Self|int|date) -> int|Self:
        if isinstance(subtractor, date):
            subtractor = WeekYear.from_date(subtractor)

        if isinstance(subtractor, WeekYear):
            return (
                date.fromisocalendar(self.year, self.week, 1)
                - date.fromisocalendar(subtractor.year, subtractor.week, 1)
            ).days // 7
        elif isinstance(subtractor, int):
            return WeekYear.from_date(
                date.fromisocalendar(self.year, self.week, 1)
                - timedelta(subtractor * 7)
            )
        else:
            raise TypeError(
                "Unsupported operand type(s) for "
                + f"{type(self)} - {type(subtractor)}."
            )
        
    def __rsub__(self, subtractor:Self|date) -> int:
        if not isinstance(subtractor, (WeekYear, date)):
            raise TypeError(
                "Unsupported operand type(s) for "
                + f"{type(subtractor)} - {type(self)}."
            )
        return -(self - subtractor)
        
    def __add__(self, week_difference: int|timedelta) -> Self:
        if isinstance(week_difference, int):
            return self - -week_difference
        elif isinstance(week_difference, timedelta):
            return self - -week_difference.days//7
        else:
            raise TypeError(
                f"{self.__class__.__name__} can only be added to an integer "
                + "or a datetime.timedelta object. "
                + f"Got {type(week_difference)}."
            )
    
    def __radd__(self, week_difference: int|timedelta) -> Self:
        return self + week_difference
    
    def week_num_in_year(year_info:int|Self|date) -> int:
        """
        return the number of weeks, 
        which can be either 52 or 53 depending on which year it is.
        """
        if isinstance(year_info, int):
            december28th = date(year_info, 12, 28)
        elif isinstance(year_info, WeekYear) or isinstance(year_info, date):
            december28th = date(year_info.year, 12, 28)
        else:
            raise TypeError(
                "This method only takes `int`, `WeekYear` or `date` object. "
                + f"Got {type(year_info)}"
                )
        # 12/28 is guaranteed to be in the last week of the given year
        return december28th.isocalendar().week
