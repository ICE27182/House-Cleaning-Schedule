

from .weekyear import WeekYear
from .how_often import HowOften
from .chore import Chore
from .weighted_namelist import WeightedNameList, Namelist

from typing import Self, Any
from collections.abc import Iterable, Iterator, Sequence, Callable
from os import PathLike
from dataclasses import dataclass
from enum import StrEnum, auto
from datetime import date
from random import shuffle
from copy import copy
import json


class RecordTime(StrEnum):
    HISTORY = auto()
    PRESENT = auto()
    FUTURE = auto()



@dataclass
class Record(Sequence):
    @dataclass
    class RecordEntry:
        chore_name: str
        when: str
        people: dict[str, bool]

        @classmethod
        def generate(cls, 
                     weighted_namelist: WeightedNameList, 
                     chore: Chore) -> Self:
            return cls(
                chore.name,
                chore.how_often.which_day(),
                {
                    name: False 
                    for name in weighted_namelist.pick(chore.num_of_people)
                }
            )
        
        @classmethod
        def from_json_dict(cls, record_entry: dict) -> Self:
            return cls(
                chore_name=record_entry["chore_name"],
                when=record_entry["when"],
                people=copy(record_entry["people"]),
            )

        def to_json(self) -> dict:
            return {
                "chore_name": self.chore_name,
                "when": self.when,
                "people": self.people,
            }
    
        def __str__(self) -> str:
            status = "\t".join(
                f"{name:20} [{'X' if status else ' '}]"
                for name, status in self.people.items()
            )
            return f"{self.chore_name:32}\t|\t{self.when:12}\t|\t{status}"

    type RecordAtWeekYear = dict[str: RecordEntry]
    type RecordData = dict[WeekYear: RecordAtWeekYear]
    data: RecordData
    gen_range:range = range(-10, 6)

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, weekyear: WeekYear) -> RecordAtWeekYear:
        """
        Get a `RecordAtWeekYear` object at given `weekyear`.
        Raise a `KeyError` if record at `weekyear` does not exist.`
        """
        return self.data[weekyear]
    
    def __contains__(self, value: Any) -> bool:
        return value in self.data
    
    def slice(self, start: WeekYear, stop: WeekYear) -> Self:
        if not (isinstance(start, WeekYear) and isinstance(stop, WeekYear)):
            raise TypeError(
                "Slice indices must be `WeekYear` objects. Got"
                f" {type(start)} and {type(stop)}."
            )
        data = {}
        while start < stop:
            if start not in self.data:
                start += 1
                continue
            data[start] = {
                chore_name: Record.RecordEntry(
                    chore_name=entry.chore_name,
                    when=entry.when,
                    people=copy(entry.people)
                )
                for chore_name, entry in self.data[start].items()
            }
            start += 1
        return Record(data, self.gen_range)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Record):
            return False
        return self.data == other.data
    
    def __str__(self) -> str:
        self.sort()
        out = []
        for weekyear, record_at_weekyear in self.data.items():
            entries = "\n\t".join(
                str(entry) for entry in record_at_weekyear.values()
            )
            out.append(f"{weekyear}\n\t{entries}")
        return "\n\n".join(out)

    def sort(self) -> None:
        """
        Sort by weekyear and chore names.
        """
        self.data = dict(sorted(self.data.items()))
        for weekyear in self.data.keys():
            self.data[weekyear] = dict(sorted(self.data[weekyear].items()))

    @classmethod
    def load_from_json_format(cls, json_dict: dict) -> Self:
        """
        Construct a `Record` object from a dictionary in json format
        """
        data = {}
        for weekyear, record_at_weekyear in json_dict.items():
            data[WeekYear.from_str(weekyear)] = {
                chore_name: Record.RecordEntry.from_json_dict(record_entry)
                for chore_name, record_entry in record_at_weekyear.items()
            }
        return cls(data)

    @classmethod
    def load_from_json_file(cls, path: PathLike) -> Self:
        """
        Construct a `Record` object from the json file at `path`.
        """
        with open(path, "r") as json_file:
            return Record.load_from_json_format(json_file.read())
    
    @classmethod
    def _load_old_record(cls, 
                         path: PathLike, 
                         renaming: Callable[[str], str] | dict = {}) -> Self:
        """
        Construct a `Record` object from the old json format.
        """
        if isinstance(renaming, dict):
            def mapped_name(original_name):
                return (
                    renaming[original_name] if original_name in renaming
                    else original_name
                )
        else:
            mapped_name = renaming
        
        with open(path, "r") as json_file:
            old = json.load(json_file)
        out = {}
        for weekyear, old_record_at_weekyear in old.items():
            out[weekyear] = {}
            for old_chore_name, old_entry in old_record_at_weekyear.items():
                chore_name = mapped_name(old_chore_name)
                out[weekyear][chore_name] = {
                    "chore_name": chore_name,
                    "when": Record._convert_old_time_repr_to_new(
                        old_entry[1]
                    ),
                    "people": old_entry[0]
                }
        return Record.load_from_json_format(out)
    
    @staticmethod
    def _convert_old_time_repr_to_new(string:str) -> str:
        if " - " in string:
            return "Whole Week"
        day, month, year = map(int, string.split("/"))
        return (
            HowOften.WEEKDAYS[
                date(year, month, day).weekday() + 1
            ].capitalize()
        )

    def to_json(self) -> dict:
        """
        Serialize itself to a dict in json format, which can be used to
        reconstruct a `Record` object later with `Record.load_from_json_file`.
        """
        out = {}
        for weekyear, record_at_weekyear in self.data.items():
            out[str(weekyear)] = {
                chore_name: record_entry.to_json()
                for chore_name, record_entry in record_at_weekyear.items()
            }
        return out
    
    def save_to_json(self, path: PathLike) -> None:
        """
        Serialize itself and save to the file at `path`, which can be used to
        reconstruct a `Record` object later with 
        `Record.load_from_json_format`.
        """
        with open(path, "w") as json_file:
            json.dump(self.to_json(), json_file, indent=4)

    def generate(
            self, 
            chores: Sequence[Chore], 
            weekyear: WeekYear, 
            this_weekyear: WeekYear|None = None,
        ) -> RecordAtWeekYear:
        """
        Generate a new `RecordAtWeekYear` at `weekyear` using `chores`.
        
        This method does not modify `self.data`but instead returns a new 
        `RecrodAtWeek` instance.
        
        `this_week` helps calculate the weights for the random generator.
        It defaults to `weekyear - self.gen_range.stop` if not provided.

        If possible, it avoids having the same person doing more than one
        chore in a week, or doing exactly the same chore they did last week.
        """
        if this_weekyear is None:
            this_weekyear = weekyear - self.gen_range.stop
        out:dict[str, Record.RecordEntry] = {}
        # Generate WeightNamelist
        # Loop through chores and generate RecordEntry
        excluded = set()
        chore_order = list(range(len(chores)))
        shuffle(chore_order)
        for i in chore_order:
            chore = chores[i]
            if chore.how_often.is_this_week(weekyear):
                last_weekyear = this_weekyear - 1
                if (last_weekyear in self 
                    and chore.name in self.data[last_weekyear]):
                    last_week_names = (
                        self.data[last_weekyear][chore.name].people.keys()
                    )
                else:
                    last_week_names = set()
                weighted_namelist = self.weighted_namelist(
                    chore.namelist,
                    this_weekyear
                ).exclude(excluded | last_week_names)
                out[chore.name] = Record.RecordEntry.generate(
                    weighted_namelist,
                    chore,
                )
                excluded |= out[chore.name].people.keys()
        return out
    
    def stripe(self, 
               threshold: range = range(-53, 6), 
               this_week: WeekYear|None = None) -> Self:
        """
        Keep records within the threshold and remove the rest.
        Return a `Record` object containing the removed records.
        """
        striped = {}
        if this_week is None:
            this_week = WeekYear.present_weekyear()
        for weekyear, record_at_weekyear in self.data.items():
            if weekyear - this_week not in threshold:
                striped[weekyear] = record_at_weekyear
        for weekyear in striped:
            del self.data[weekyear]
        return Record(striped)

    def weighted_namelist(
            self, 
            namelist: Namelist, 
            this_weekyear: WeekYear|None = None,
            default_weight: float = 16,
    ) -> WeightedNameList:
        """
        Generate a weighted namelist based on past record.
        The weight strategy is defined within the method.
        """
        if this_weekyear is None:
            this_weekyear = WeekYear.present_weekyear()
        weighted_namelist = WeightedNameList.from_namelist(namelist, 
                                                           default_weight)
        for offset in self.gen_range:
            weekyear = this_weekyear + offset
            if weekyear not in self: 
                continue
            record_time = (
                RecordTime.HISTORY if weekyear < this_weekyear else
                RecordTime.PRESENT if weekyear == this_weekyear else
                RecordTime.FUTURE 
            )
            for record_entry in self.data[weekyear].values():
                for name, has_done in record_entry.people.items():
                    if name in weighted_namelist:
                        new_weight = Record._adjust_weight(
                            weighted_namelist[name].weight, 
                            has_done,
                            record_time
                        )
                        weighted_namelist[name].weight = new_weight
        return weighted_namelist

    @staticmethod
    def _adjust_weight(weight: float, 
                       has_done: bool, 
                       record_time: RecordTime) -> float:
        if record_time == RecordTime.PRESENT:
            record_time = RecordTime.FUTURE

        if record_time == RecordTime.HISTORY:
            if has_done:
                weight -= 0.6 * 3
            else:
                weight += 1.5 * 3
        elif record_time == RecordTime.PRESENT:
            pass
        elif record_time == RecordTime.FUTURE:
            weight -= 0.3 * 3
        else:
            raise ValueError(f"Not supported record time. Got {record_time}.")
        return max(WeightedNameList.DISCARD, weight)
    
    def flip_status(self, 
                   weekyear: WeekYear, 
                   chore: Chore|str,
                   name: str) -> None:
        """
        Set the boolean value at given path to its opposite.
        """
        if isinstance(chore, Chore):
            chore = chore.name
        people = self.data[weekyear][chore].people
        people[name] = not people[name]
    
    def add_new_chores(self,
                       chores: Iterable[Chore],
                       this_weekyear: WeekYear|None = None) -> None:
        """
        Add a series of chores to the record from the given weekyear to 
        `weekyear + self.gen_range.stop - 1`.
        If there are existing records in the range, it will skip that record
        and keep them as is.
        """
        if this_weekyear is None:
            this_weekyear = WeekYear.present_weekyear()

        for offset in range(self.gen_range.stop):
            weekyear = offset + this_weekyear
            if weekyear not in self:
                self.data[weekyear] = {}
            record_at_weekyear = self.generate(chores, 
                                               weekyear, 
                                               this_weekyear)
            for chore_name, entry in record_at_weekyear.items():
                if chore_name not in self.data[weekyear]:
                    self.data[weekyear][chore_name] = entry
    


