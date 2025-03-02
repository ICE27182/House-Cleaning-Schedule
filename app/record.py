

from .weekyear import WeekYear
from .chore import Chore
from .weighted_namelist import WeightedNameList, Namelist

from typing import Self
from collections.abc import Iterable, Iterator
from os import PathLike
from dataclasses import dataclass
import json

@dataclass
class Record(Iterable):
    @dataclass
    class RecordEntry:
        chore_name: str
        when: str
        people: dict[str, bool]

        @classmethod
        def generate(cls, 
                     weighted_namelist:WeightedNameList, 
                     chore:Chore) -> Self:
            return cls(
                chore.name,
                chore.how_often.which_day(),
                {
                    name:False 
                    for name in weighted_namelist.pick(chore.num_of_people)
                }
            )
        
        @classmethod
        def from_json_dict(cls, record_entry: dict) -> Self:
            return cls(
                chore_name = record_entry["chore_name"],
                when = record_entry["when"],
                people = record_entry["people"],
            )
        
        def to_json(self) -> dict:
            return {
                "chore_name": self.chore_name,
                "when": self.when,
                "people": self.people,
            }
    
    type RecordAtWeekYear = dict[str: RecordEntry]
    type RecordData = dict[WeekYear: RecordAtWeekYear]
    data: RecordData
    gen_range = range(-10, 6)
    
    def __iter__(self) -> Iterator:
        raise NotImplementedError

    @classmethod
    def load_from_json_format(cls, json_dict:dict) -> Self:
        """
        Construct a `Record` object from a dictionary in json format
        """
        raise NotImplementedError
    
    @classmethod
    def load_from_json_file(cls, path:PathLike) -> Self:
        """
        Construct a `Record` object from the json file at `path`.
        """
        with open(path, "r") as json_file:
            return Record.load_from_json_format(json_file.read())
    
    def to_json(self) -> dict:
        """
        Serialize itself to a dict in json format, which can be used to
        reconstruct a `Record` object later with `Record.load_from_json_file`.
        """
        raise NotImplementedError
    
    def save_to_json(self, path:PathLike) -> None:
        """
        Serialize itself and save to the file at `path`, which can be used to
        reconstruct a `Record` object later with 
        `Record.load_from_json_format`.
        """
        with open(path, "w") as json_file:
            json.dump(self.to_json(), json_file)

    def generate(
            self, 
            chores: Iterable[Chore], 
            weekyear: WeekYear, 
            current_weekyear: WeekYear,
        ) -> RecordAtWeekYear:
        """
        Generate a new RecordAtWeekYear
        """
        raise NotImplementedError
        # Generate WeightNamelist
        # Loop through chores and generate RecordEntry
    
    def __getitem__(self, weekyear:WeekYear) -> RecordAtWeekYear:
        """
        Get a `RecordAtWeekYear` object at given `weekyear`.
        Raise a `KeyError` if record at `weekyear` does not exist.`
        """
        raise NotImplementedError
    
    def stripe(self, threshold:int|range = range(-52, 7)) -> Self:
        raise NotImplementedError

    def weighted_namelist(self, namelist:Namelist) -> WeightedNameList:
        """
        Generate a weighted namelist based on past record.
        The weight strategy is defined within the method.
        """
        raise NotImplementedError
    
    def negate_state(self, 
                     weekyear: WeekYear, 
                     chore: Chore|str,
                     name: str) -> None:
        """
        Set the boolean value at given path to its opposite.
        """
        raise NotImplementedError
    
    def add_new_chores(self, 
                       chores: Iterable[Chore], 
                       from_weekyear: WeekYear|None = None) -> None:
        """
        Add a series of chores to the record from the given `weekyear` to 
        `weekyear + self.gen_range.stop - 1`
        """
        raise NotImplementedError
