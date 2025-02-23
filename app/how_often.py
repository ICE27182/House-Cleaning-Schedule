

from .weekyear import WeekYear

import re
from abc import ABC, abstractmethod
from typing import Self, Any

class HowOften(ABC):
    WEEKDAYS: tuple[str] = (
        "week",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    def __init__(self, weekday:int|None = None):
        """
        `weekday` starts from 1, representing Monday
        """
        super().__init__()
        if weekday is not None and not isinstance(weekday, int):
            raise TypeError(
                f"`weekday` must be either an integer or None. " 
                + f"Got {type(weekday)}."
            )
        elif weekday is not None and weekday not in range(0, 7 + 1):
            raise ValueError(
                f"`weekday` must be an integer between 0 and 7. "
                + f"Got {weekday}."
            )
        self.weekday = weekday or 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.weekday=})"    

    @abstractmethod
    def is_this_week(self, weekyear:WeekYear) -> bool:
        pass
    @classmethod
    @abstractmethod
    def from_str(cls, description:str) -> Self:
        pass
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @staticmethod
    def validate_weekday(weekday:Any) -> int:
        """
        Return 0 if weekday evaluates to False, which means it lasts a week.
        Return itself if it is an integer in `range(7 + 1)`
        Return an integer in `range(7 + 1)` if it is valid string 
        representing a day in a week (e.g. monday Friday suNDaY).

        Otherwirse, raise an value error.
        """
        if not weekday:
            return 0
        elif isinstance(weekday, str):
            try:
                return HowOften.WEEKDAYS.index(weekday.strip().lower())
            except ValueError as e:
                raise ValueError(
                    f"{e} (Possible Cause: "
                    + f"{repr(weekday.lower())}(Original:{repr(weekday)}) "
                    + "is not a valid weekday name.)"
                )
        elif isinstance(weekday, int):
            if weekday in range(7 + 1):
                return weekday
            else:
                raise ValueError(
                    f"{weekday} is not a valid weekday, which should be in "
                    + "`range(8)`."
                )
        else:
            raise TypeError(f"Unsupported Type. Got {type(weekday)}.")
        

class OncePerNWeek(HowOften):
    REGEX = re.compile(r"^\s*once\s+per\s+(\d+)\s+weeks?(?:\s+on\s+(\w*))?(?:\s+with\s+offset\s+(\d+))?\s*\.?\s*$", re.IGNORECASE)
    ONCE_PER_WEEK_REGEX = re.compile(r"^\s*once\s+per\s+week\s*$", re.IGNORECASE)
    
    def __init__(self, n:int, weekday:int|None = None, offset:int = 0):
        """
        Happens once every `n` weeks.

        `weekday` can be left as None, which means this chore can be done on
        any day in a week.

        `offset`: e.g. `n = 2`, `offset` should be 0 if it happens in even
        weeks in 2025, or 1 if it happens in odd weeks in 2025.
        """
        super().__init__(weekday)

        if not isinstance(n, int):
            raise TypeError(
                f"`n` must be an integer. Got {type(n)}."
            )
        elif not isinstance(offset, int):
            raise TypeError(
                f"`offset` must be an integer. Got {type(offset)}."
            )
        elif offset < 0:
            raise ValueError(
                f"`offset` must not be negative. Got {offset}."
            )
        self.n = n
        self.offset = offset
    
    @classmethod
    def from_str(cls, description:str) -> Self:
        """
        e.g. 
            "Once per 2 weeks ", 
            "OncE pEr 2  weeks oN MONday.", 
            "ONCE   per 2 WEEK on Monday  with offset 1"
            "Once per week"

        Recognize by regex:
            re.compile(r"^\s*once\s+per\s+(\d+)\s+weeks?(?:\s+on\s+(\w*))?(?:\s+with\s+offset\s+(\d+))?\s*\.?\s*$", re.IGNORECASE)
            or
            re.compile(r"^\s*once\s+per\s+week\s*$", re.IGNORECASE)
        """
        if not isinstance(description, str):
            raise TypeError(
                f"`description` must be a str. Got {type(description)}."
            )
        all = OncePerNWeek.REGEX.findall(description)
        if len(all) == 0:
            # Match once per week
            if (OncePerNWeek.ONCE_PER_WEEK_REGEX.match(description)):
                return cls(1, 0, 0)
            raise ValueError(
                "`description` cannot be recognized. "
                + f"Got {repr(description)}."
            )
        n = int(all[0][0])
        weekday = HowOften.validate_weekday(all[0][1])
        offset = int(offset) if (offset := all[0][2]) else 0
        return cls(n, weekday, offset)
    
    def __str__(self) -> str:
        weekday = (f" on {HowOften.WEEKDAYS[self.weekday].capitalize()}"
               if self.weekday else "")
        offset = f" with offset {self.offset}" if self.offset else ""

        return (
            f"Once per {self.n} week{'s' if self.n > 1 else ''}{weekday}{offset}."
        )
    
    def __repr__(self) -> str:
        return f"{super().__repr__()[:-1]}, {self.n=}, {self.offset=})"

    def is_this_week(self, weekyear:WeekYear) -> bool:
        return weekyear.week_count_from_1_1_1() % self.n == self.offset



class NthWeekPerMonth(HowOften):
    ORDINALS:tuple[str] = (
        "week", 
        "first", 
        "second", 
        "third", 
        "forth", 
        "fifth"
    )
    REGEX = re.compile(r"\s*the\s+(\w+)\s+(\w+)\s+of\s+every\s+month\s*\.?\s*", re.IGNORECASE)
    def __init__(self, n:int, weekday:int|None = None):
        """
        
        Happens every in `n`-th week in every month.

        `weekday` can be left as None, which means this chore can be done on
        any day in a week.
        """
        raise NotImplementedError("Not Implemented")
        super().__init__(n, weekday)
    
    @classmethod
    def from_str(cls, description:str) -> Self:
        """
        e.g. 
            "The first Sunday of every month ", 
            "The second week of every month", 
            "tHE fifTh tueSdAy of everY MONth . "

        Recognize by regex:
            re.compile(r"\s*the\s+(\w+)\s+(\w+)\s+of\s+every\s+month\s*\.?\s*", re.IGNORECASE)
        """
        if not isinstance(description, str):
            raise TypeError(
                f"`description` must be a str. Got {type(description)}."
            )
        all = NthWeekPerMonth.REGEX.findall(description)
        if len(all) == 0:
            raise ValueError(
                f"`description` cannot be recognized. Got {repr(description)}."
            )
        
        try:
            ordinal:str = all[0][0]
            n = NthWeekPerMonth.ORDINALS.index(ordinal.lower())
        except ValueError as e:
            raise ValueError(
                f"{e} (Possible Cause: "
                + f"{repr(ordinal.lower())}(Original:{repr(ordinal)}) "
                + "is not a valid ordinal numerals (e.g. first, second).)"
            )
        weekday = HowOften.validate_weekday(all[0][1])
        return cls(n, weekday)

    def __str__(self) -> str:
        weekday = (HowOften.WEEKDAYS[self.weekday].capitalize()
                   if self.weekday else HowOften.WEEKDAYS[self.weekday])
        return (
            f"The {NthWeekPerMonth.ORDINALS[self.n]} {weekday} "
            + "of every month."
        )
    
    def is_this_week(self, weekyear:WeekYear) -> bool:
        return weekyear.nth_week_in_its_month() == self.n
