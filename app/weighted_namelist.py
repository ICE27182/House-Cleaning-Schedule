

from __future__ import annotations
from typing import Self
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from random import uniform, shuffle

type Namelist = Iterable[str|Iterable[str]]

@dataclass
class WeightedPerson:
    name: str = None
    weight: float = None
    group: WeightedNameList = None

    def __str__(self) -> str:
        if len(self.group) < 2:
            group = False
        else:
            group = ", ".join(
                person.name for person in self.group 
                if person.name != self.name
            )
        return (
            f"{self.name} ({self.weight:.3f})"
            + (
                f" in group with {group}" if group else ""
            )
        )
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={repr(self.name)}, " 
            + f"weight={self.weight}, group={repr(self.group)})"
        )

@dataclass
class WeightedNameList(Sequence):
    namelist:dict[WeightedPerson]
    DISCARD = 0

    def __len__(self) -> int:
        return len(self.namelist)

    def __iter__(self) -> Iterator[WeightedPerson]:
        return self.namelist.values().__iter__()
    
    def __str__(self) -> str:
        if len(self) == 0: return "Empty WeightedNameList"
        return (
            f"WeightedNameList:\n\t"
            + "\n\t".join(
                str(person) for person in self
            )
        )
    
    def __eq__(self, another) -> bool:
        if not isinstance(another, WeightedNameList):
            return False
        return (
            {p.name:p.weight for p in self}
            == {p.name:p.weight for p in another}
        )
    
    def __getitem__(self, name:str) -> WeightedPerson:
        return self.namelist[name]
    
    def __contains__(self, value) -> bool:
        return value in self.namelist

    @classmethod
    def from_namelist(cls, namelist: Namelist, default_weight = 16) -> Self:
        """
        Constrcut WeightedNameList with a Namelist 
        (Iterable[str|Iterable[str]]).
        """
        out = {}
        for name in namelist:
            if isinstance(name, str):
                person = WeightedPerson(
                    name=name, 
                    weight=default_weight, 
                    group=WeightedNameList({})
                )
                person.group.namelist[name] = person
                out[name] = person
            elif isinstance(name, Iterable):
                tmp = WeightedNameList.from_namelist(name, default_weight)
                for person in tmp:
                    person.group = tmp
                out.update(tmp.namelist)
        return WeightedNameList(out)
            
    def pick(self, k:int) -> list[str]:
        """
        Return a list of randomly picked names.
        It will try to make sure people in the same group are more likely
        to be picked together. However, this also means if someone in a group
        has a high weight, other people from the same group are also more 
        likely to be picked.
        """
        population:tuple[str] = tuple(p.name for p in self)
        weights:list[float] = list(p.weight for p in self)
        order = list(range(len(self)))
        pick_from_group = False
        result = []
        while len(result) < k:
            # Without this shuffle, if all weights are 0, then the first
            # person in the dictionary will always be picked.
            shuffle(order)
            total_weight = sum(weights)
            threshold = uniform(0, total_weight)
            cumulative = 0
            for i in order:
                cumulative += weights[i]
                if cumulative >= threshold:
                    group = self[population[i]].group
                    # Check if the size of the group the picked person is in
                    # is valid
                    if (
                        not pick_from_group 
                        and len(group) > k - len(result) 
                        and len(result) != 0
                    ):
                        # The picked person is in a group with invalid size
                        break
                    result.append(population[i])
                    weights[i] = WeightedNameList.DISCARD

                    # Change the population of next person to pick if needed
                    if (not pick_from_group and len(group) > 1):
                        pick_from_group = True
                        group_population = tuple(p.name for p in group)
                        # We cannot use weights store in group because some
                        # weights may have been updated before and the changes
                        # are only stored in `weights`
                        weights:list[float] = [
                            w for i, w in enumerate(weights)
                            if population[i] in group_population
                        ]
                        population = group_population
                        order = list(range(len(group)))
                    # Stop picking from a group if ever
                    elif (pick_from_group and all(p.name in result for p in group)):
                        pick_from_group = False
                        population:tuple[str] = tuple(p.name for p in self)
                        weights:list[float] = [
                            (
                                p.weight if p.name not in result 
                                else WeightedNameList.DISCARD
                            )
                            for p in self
                        ]
                        order = list(range(len(self)))
                    break
        return result
 