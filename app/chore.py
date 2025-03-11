

from .how_often import HowOften, OncePerNWeek, SpecificWeeks

import json
from os import PathLike
from collections.abc import Iterable
from typing import Self, Any


def _load_namelist_json(path:PathLike) -> list[str|list[str]]:
    with open(path, "r") as file:
        namelist = json.load(file)
        _validate_namelist_layout(namelist)
        return namelist
        
def _validate_namelist_layout(namelist:Any) -> None:
    """
    Validate if `namelist` follows `Iterable[str|Iterable[str]]`.
    Raise ValueError if it does not follow the layout.
    """
    try:
        if not isinstance(namelist, list): 
            raise ValueError
        for name in namelist:
            if isinstance(name, list):
                # `name` here is actually a group of people
                if not all(isinstance(n, str) for n in name):
                    raise ValueError
            elif not isinstance(name, str):
                raise ValueError
        return namelist
    except ValueError:
            raise ValueError(
            "Invalid data layout. "
            "Expected Iterable[str|Iterable[str]]. "
            + f"Got {namelist}."
        )

def _str_to_HowOften(string:str) -> OncePerNWeek | SpecificWeeks:
    try:
        return OncePerNWeek.from_str(string)
    except ValueError as e_OncePerNWeek:
        try:
            return SpecificWeeks.from_str(string)
        except ValueError as e_SpecificWeeks:
            raise ValueError(
                f"Failed to recognize string {repr(string)}\n"
                + f"OncePerNWeek: {e_OncePerNWeek}\n"
                + f"SpecificWeeks: {e_SpecificWeeks}"
            )

class Chore:
    def __init__(self, 
                 name: str, 
                 namelist: PathLike|Iterable[str|Iterable[str]], 
                 num_of_people:int,
                 how_often:HowOften) -> None:
        if not isinstance(name, str):
            raise TypeError(f"`name` must be a str. Got {type(name)}")
        self.name = name

        try:
            namelist = _load_namelist_json(namelist)
        except TypeError:
            _validate_namelist_layout(namelist)
        finally:
            self.namelist:Iterable[str|Iterable[str]] = namelist

        if not isinstance(num_of_people, int):
            raise TypeError("`num_person` must be an int. "
                            + f"Got {type(num_of_people)}")
        elif num_of_people < 0:
            raise ValueError("`num_person` must an non-negative integer.")
        self.num_of_people = num_of_people

        if not isinstance(how_often, HowOften):
            raise TypeError("`how_often` must be an `HowOften` object. "
                            + f"Got{type(how_often)}")
        self.how_often = how_often
        
    def __str__(self) -> str:
        return (
            f"Chore: {self.name}:\n"
            + f"\tPeople Invovled: {self.namelist}\n"
            + f"\tNumber of person(s) required: {self.num_of_people}\n"
            + f"\tFrequency: {str(self.how_often)}"
        )
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name}, " 
            + f"namelist={self.namelist}), num_of_people={self.namelist}, "
            + f"how_often={repr(self.how_often)})"
        )
    
    @classmethod
    def load_chores_from_json(cls, path:PathLike) -> list[Self]:
        with open(path, "r") as file:
            chores = json.load(file)
        out = [cls.from_json_dict(chore) for chore in chores]
        return out
    
    @classmethod
    def from_json_dict(cls, chore:dict) -> Self:
        return cls(
            name = chore["name"],
            namelist = chore["namelist"],
            num_of_people = chore["num_of_people"],
            how_often = _str_to_HowOften(chore["how_often"])
        )

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "namelist": self.namelist,
            "num_of_people": self.num_of_people,
            "how_often": str(self.how_often),
        }
        
    @staticmethod
    def urlized_chore_name(line:str) -> str:
        return "-".join(line.lower().split())
    
    @staticmethod
    def de_urlize_chore_name(urlized:str) -> str:
        return " ".join(map(lambda word: word.capitalize(), urlized.split("-")))
        
    def match_urlized_chore_name(self, urlized:str) -> bool:
        return self.urlized_chore_name() == urlized
    
    def loosely_match_chore_name(self, other:str) -> bool:
        return (
            self.name.lower().replace(" ", "").replace("-", "")
            == other.lower().replace(" ", "").replace("-", "")
        )
