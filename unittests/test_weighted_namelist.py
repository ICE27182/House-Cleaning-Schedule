

import unittest
from unittest import skip
from message import *

from random import choices

from app import WeightedNameList


NAMELIST = [
    "Minecraft",
    "Death Stranding",
    "Cyberpunk 2077",
    # [
        "Grand Theft Auto V", 
        "Red Dead Redemption 2",
    # ],
    "The Elder Scrolls V: Skyrim",
    "Microsoft Flight Simulator 2020",
    "Kerbal Space Program",
    # [
        "Assassin's Creed II", 
        "Assassin's Creed: Brotherhood", 
        "Assassin's Creed: Revelations",
    # ],
    # [
        "Assassin's Creed III", 
        "Assassin's Creed III: Liberation",
    # ],
    # [
        "The Witcher 2: Assassins of Kings", 
        "The Witcher 3: Wild Hunt",
    # ],
    "Arma 3",
    "Besiege",
    "Tomb Raider",
    "Shadow Tactics",
    "Assetto Corsa",
    "Forza Horizon 4",
    "Cities Skylines",
]

def _flatten(namelist) -> list[str]:
    out = []
    for elem in namelist:
        if isinstance(elem, str):
            out.append(elem)
        else:
            out.extend(elem)
    return out

FLATTENED_NAMELIST = set(_flatten(NAMELIST))


class T_WeightedNameList(unittest.TestCase):
    @skip("Grouping is not supported")
    def test_from_namelist_with_grouping(self):
        expected = ("WeightedNameList:\n"
                    "\tMinecraft (16.000)\n"
                    "\tDeath Stranding (16.000)\n"
                    "\tCyberpunk 2077 (16.000)\n"
                    "\tGrand Theft Auto V (16.000) in group with Red Dead Redemption 2\n"
                    "\tRed Dead Redemption 2 (16.000) in group with Grand Theft Auto V\n"
                    "\tThe Elder Scrolls V: Skyrim (16.000)\n"
                    "\tMicrosoft Flight Simulator 2020 (16.000)\n"
                    "\tKerbal Space Program (16.000)\n"
                    "\tAssassin's Creed II (16.000) in group with Assassin's Creed: Brotherhood, Assassin's Creed: Revelations\n"
                    "\tAssassin's Creed: Brotherhood (16.000) in group with Assassin's Creed II, Assassin's Creed: Revelations\n"
                    "\tAssassin's Creed: Revelations (16.000) in group with Assassin's Creed II, Assassin's Creed: Brotherhood\n"
                    "\tAssassin's Creed III (16.000) in group with Assassin's Creed III: Liberation\n"
                    "\tAssassin's Creed III: Liberation (16.000) in group with Assassin's Creed III\n"
                    "\tThe Witcher 2: Assassins of Kings (16.000) in group with The Witcher 3: Wild Hunt\n"
                    "\tThe Witcher 3: Wild Hunt (16.000) in group with The Witcher 2: Assassins of Kings\n"
                    "\tArma 3 (16.000)\n"
                    "\tBesiege (16.000)\n"
                    "\tTomb Raider (16.000)\n"
                    "\tShadow Tactics (16.000)\n"
                    "\tAssetto Corsa (16.000)\n"
                    "\tForza Horizon 4 (16.000)\n"
                    "\tCities Skylines (16.000)")
        # green(str(WeightedNameList.from_namelist(NAMELIST)).replace("\n", "27182\n"))
        self.assertEqual(
            str(WeightedNameList.from_namelist(NAMELIST)), 
            expected,
        )

    def test_from_namelist_without_grouping(self):
        expected = ("WeightedNameList:\n"
                    "\tMinecraft (16.000)\n"
                    "\tDeath Stranding (16.000)\n"
                    "\tCyberpunk 2077 (16.000)\n"
                    "\tGrand Theft Auto V (16.000)\n"
                    "\tRed Dead Redemption 2 (16.000)\n"
                    "\tThe Elder Scrolls V: Skyrim (16.000)\n"
                    "\tMicrosoft Flight Simulator 2020 (16.000)\n"
                    "\tKerbal Space Program (16.000)\n"
                    "\tAssassin's Creed II (16.000)\n"
                    "\tAssassin's Creed: Brotherhood (16.000)\n"
                    "\tAssassin's Creed: Revelations (16.000)\n"
                    "\tAssassin's Creed III (16.000)\n"
                    "\tAssassin's Creed III: Liberation (16.000)\n"
                    "\tThe Witcher 2: Assassins of Kings (16.000)\n"
                    "\tThe Witcher 3: Wild Hunt (16.000)\n"
                    "\tArma 3 (16.000)\n"
                    "\tBesiege (16.000)\n"
                    "\tTomb Raider (16.000)\n"
                    "\tShadow Tactics (16.000)\n"
                    "\tAssetto Corsa (16.000)\n"
                    "\tForza Horizon 4 (16.000)\n"
                    "\tCities Skylines (16.000)")
        # green(str(WeightedNameList.from_namelist(NAMELIST)).replace("\n", "27182\n"))
        self.assertEqual(
            str(WeightedNameList.from_namelist(NAMELIST)), 
            expected,
        )

    def test_pick_num(self):
        weighted_namelist = WeightedNameList.from_namelist(
            NAMELIST, 
            WeightedNameList.DISCARD,
        )
        for _ in range(1000):
            self.assertEqual(1, len(weighted_namelist.pick(1)))
            self.assertEqual(2, len(weighted_namelist.pick(2)))
            self.assertEqual(4, len(weighted_namelist.pick(4)))
            self.assertEqual(8, len(weighted_namelist.pick(8)))
    
    def test_pick_one_name(self):
        weighted_namelist = WeightedNameList.from_namelist(
            NAMELIST,
            WeightedNameList.DISCARD
        )
        for name in choices(tuple(FLATTENED_NAMELIST), k=2000):
            p = weighted_namelist[name]
            p.weight = 16
            for _ in range(100):
                self.assertEqual(
                    weighted_namelist.pick(k=1),
                    {name}
                )
            p.weight = WeightedNameList.DISCARD
    @skip("Grouping is not supported")
    def test_pick_two_names_naive_with_groups(self):
        N = 10_000
        M = 100
        frequncies:list[float] = [0] * N
        skipped = 0

        weighted_namelist = WeightedNameList.from_namelist(
            NAMELIST,
            WeightedNameList.DISCARD
        )

        for i in range(N):
            names = choices(tuple(FLATTENED_NAMELIST), k=2)
            p1 = weighted_namelist[names[0]]
            p2 = weighted_namelist[names[1]]
            if p1.name == p2.name or p1.group != p2.group: 
                skipped += 1
                continue
            p1.weight = 16
            p2.weight = 16
            names = set(names)
            frequncy = [None] * M
            for j in range(M):
                picked = list(weighted_namelist.pick(k=2))
                self.assertTrue(
                    set(picked) == names
                )
                frequncy[j] = picked[0] == p1.name
                self.assertEqual(
                    len(weighted_namelist[picked[0]].group),
                    len(weighted_namelist[picked[1]].group),
                )
            p1.weight = WeightedNameList.DISCARD
            p2.weight = WeightedNameList.DISCARD

            frequncies[i] = sum(frequncy) / M
        self.assertAlmostEqual(sum(frequncies) / (N-skipped), 0.5, delta=0.01)
    
    def test_pick_two_names_naive_without_grouping(self):
        N = 5_000
        M = 50
        frequncies:list[float] = [0] * N
        skipped = 0

        weighted_namelist = WeightedNameList.from_namelist(
            NAMELIST,
            WeightedNameList.DISCARD
        )

        for i in range(N):
            names = choices(tuple(FLATTENED_NAMELIST), k=2)
            p1 = weighted_namelist[names[0]]
            p2 = weighted_namelist[names[1]]
            if p1.name == p2.name: 
                skipped += 1
                continue
            p1.weight = 16
            p2.weight = 16
            names = set(names)
            frequncy = [None] * M
            for j in range(M):
                picked = weighted_namelist.pick(k=2)
                self.assertTrue(
                    picked == names
                )
                frequncy[j] = tuple(picked)[0] == p1.name
            p1.weight = WeightedNameList.DISCARD
            p2.weight = WeightedNameList.DISCARD

            frequncies[i] = sum(frequncy) / M
        self.assertAlmostEqual(sum(frequncies) / (N-skipped), 0.5, delta=0.01)


    def test_pick_two_names_more_realistic_without_grouping(self):
        N = 15_000
        weighted_namelist = WeightedNameList.from_namelist(
            NAMELIST,
            16
        )
        for i in range(N):
            picked = list(weighted_namelist.pick(2))
            self.assertNotEqual(
                picked[0],
                picked[1]
            )
            self.assertTrue(
                (
                    1 == len(weighted_namelist[picked[1]].group)
                    == len(weighted_namelist[picked[0]].group) 
                    or
                    weighted_namelist[picked[0]].group 
                    == weighted_namelist[picked[1]].group
                ),
                f"\n{i}\n{picked}"
                + f"\n{weighted_namelist[picked[0]].group}"
                + f"\n{weighted_namelist[picked[1]].group}"
            )

    @skip("Test code not implemented yet")
    def test_pick_three_names(self):
        raise NotImplementedError
