

from __future__ import annotations
from typing import Self
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from random import uniform, shuffle, choice

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
    namelist:dict[str, WeightedPerson]
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
            
    def __pick(self, k:int) -> set[str]:
        """
        Return a set of randomly picked names.

        It will try to make sure people in the same group are more likely
        to be picked together. However, this also means if someone in a group
        has a high weight, other people from the same group are also more 
        likely to be picked.

        **FIXME:**
        
            It may leads to an infinite loop if for example, we need to 
            generate 2 names out of this namelist [[m, n], o].

            Suppose we first pick o. Then it will only have [m, n] to pick
            from; however, they are not valid because of the group size is
            larger than the space left in `result`.

            NOTE
                -- edited 
                This bug can also be triggered if the sum of weights of people
                who are not in a group can never exceed the threshold, while
                people in the group have weights such that that can exceed it
                e.g. [[(m, 5), (n, 0)], p: 0, q: 0] k = 2, result = {p}
            This bug may only be triggered if we have too few people as shown
            in the example above.
        
        """
        if k > len(self):
            raise ValueError("Too many people to pick.")
        population:tuple[str] = tuple(p.name for p in self)
        weights:list[float] = list(p.weight for p in self)
        order = list(range(len(self)))
        pick_from_group = False
        # Set is necessary. For example:
        #   Given this namelist: [[m, n], o], {m:DISCARD, n:16, o:16}
        #   and we need to pick 2 persons
        #
        #   Suppose we first pick n, then we will pick from [m, n].
        #   However, since we have already picked n, the weights for both m
        #   and n will be DISCARD, which means it is possible to have two n
        #   picked in the result if we use a list.
        #
        #   Thanks to the while loop right below and the fact that result is
        #   a set, even though n is picked again, it doesn't count, and the
        #   method will keep looping until m is picked.
        result = set()
        MAXIUM_LOOPS = 10_000
        loop_counter = 0
        while len(result) < k and loop_counter < MAXIUM_LOOPS:
            loop_counter += 1
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
                    result |= {population[i]}
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
        if loop_counter >= MAXIUM_LOOPS:
            while len(result) < k:
                result |= {choice(self.namelist.keys())}
        return result
    
    def pick(self, k:int) -> set[str]:
        if k > len(self):
            raise ValueError("Too many people to pick.")
        elif not all(len(weighted_person.group) == 1 
                     for weighted_person in self):
            raise ValueError(
                "Groups are not supported by this pick method."
                + f"Got {self}."
            )
        result = set()
        population:tuple[str] = tuple(p.name for p in self)
        weights:list[float] = list(p.weight for p in self)
        # Without this shuffle, if all weights are 0, then the first
        # person in the dictionary will always be picked.
        order = list(range(len(self)))
        # Here I used a while loop instead of a for loop because it is
        # possible that the same name is picked in two iterations if all
        # the weights are 0.
        # It will not lead to an infinite loop because k is guaranteed to be
        # smaller than or equal to the total number of names.
        while len(result) < k:
            shuffle(order)
            total_weight = sum(weights)
            threshold = uniform(0, total_weight)
            cumulative = 0
            for i in order:
                cumulative += weights[i]
                if cumulative >= threshold:
                    result |= {population[i]}
                    weights[i] = WeightedNameList.DISCARD
                    break
        return result
    
    def exclude(self, namelist:Iterable[str]) -> Self:
        """
        Set all weights of all names in the namelist to 
        `WeightedNameList.DISCARD`.
        Return self to allow chaining.
        """
        for name in namelist:
            if name in self:
                self[name].weight = WeightedNameList.DISCARD
        return self
