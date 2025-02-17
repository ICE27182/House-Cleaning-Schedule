
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
    def present_weekyear(cls) -> Self:
        return cls.from_date(date.today())
    
    @classmethod
    def nth_week_in_month(cls, n:int, month:int, year:int) -> Self:
        """
        Return a `WeekYear` object representing the n-th week 
        of the given month in the given year
        """
        week_num_in_month = (
            date(
                year if month != 12 else year + 1, 
                month + 1 if month != 12 else 1, 
                7
            ) 
            - WeekYear.from_date(date(year, month, 7))
        )
        if not isinstance(n, int):
            raise TypeError(f"`n` must be an integer. Got {type(n)}.")
        elif not isinstance(month, int):
            raise TypeError(f"`n` must be an integer. Got {type(month)}.")
        elif not isinstance(year, int):
            raise TypeError(f"`n` must be an integer. Got {type(year)}.")
        elif n not in range(1, week_num_in_month + 1):
            raise TypeError(
                f"`n` must between 1 and {week_num_in_month} "
                + f"with {month=}, {year=}. Got {n}."
            )
        elif month not in range(1, 12 + 1):
            raise ValueError(
                f"`month` must be between 1 and 12. Got {month}."
            )
        elif year not in (1, 9999 + 1):
            raise ValueError(
                f"`year` must be between 1 and 9999. Got {year}."
            )
        first_week_in_month = cls.from_date(date(year, month, 7))
        result = first_week_in_month + n
        return result
    
    def __str__(self) -> str:
        return f"{self.week} {self.year}"
    
    def __iter__(self):
        return iter(tuple(self.week, self.year))

    def __getitem__(self, index):
        if index == 0 or index == -2: return self.week
        elif index == 1 or index == -1: return self.year
        else: return IndexError("Index out of range")
    
    def __len__(self) -> int:
        return 2
    
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

    def nth_week_in_its_month(self) -> int:
        pass
        



        

if __name__ == "__main__":
    # Check the first week of a month
    if False:
        for year in range(1, 2024):
            for month in range(1, 12 + 1):
                date7 = date(year, month, 7)
                assert(date.fromisocalendar(year, date7.isocalendar().week, 7).month)
        year = 2024
        for month in range(1, 12 + 1):
                date7 = date(year, month, 7)
                print(date.fromisocalendar(year, date7.isocalendar().week, 7).isocalendar())
    # Check the number of week in a month
    if False:
        for year in range(1, 2025 + 1):
            for month in range(1, 12):
                diff = WeekYear.from_date(date(year, month + 1, 7)) - date(year, month, 7)
                if diff != 4:
                    print(f"{year:4} - {month:2}: {diff}")
        year = 2024              
        for month in range(1, 12 + 1):      
            print(
                month, 
                date(
                    year if month != 12 else year + 1, 
                    month + 1 if month != 12 else 1, 
                    7
                ) 
                - WeekYear.from_date(date(year, month, 7))
            )
    expected = (" 1 5"
                " 2 4"
                " 3 4"
                " 4 5"
                " 5 4"
                " 6 4"
                " 7 5"
                " 8 4"
                " 9 5"
                "10 4"
                "11 4"
                "12 5"
    )
    actual = ""
    year = 2024              
    for month in range(1, 12 + 1):      
        actual += (
            f"{month:2} " 
            + str(
                date(
                    year if month != 12 else year + 1, 
                    month + 1 if month != 12 else 1, 
                    7
                ) 
                - WeekYear.from_date(date(year, month, 7))
            )
        )
    assert(actual == expected)

    assert(date.today() - WeekYear.present_weekyear() == 0)
    assert(WeekYear.present_weekyear() - 55 - WeekYear.from_date(date.today()) == -55)

    print("\033[92mAll Assertions past\033[0m")