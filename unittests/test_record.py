

import unittest
from unittest import skip, TestCase, main
from message import *

from app import Record, WeekYear, Chore
from collections.abc import Iterable
from random import random
from time import sleep

def is_sorted(record:Record) -> bool:
    last_weekyear = WeekYear(1, 1)
    last_chore_name = ""
    for w in record:
        if w < last_weekyear:
            return False
        for l in record[w]:
            if l < last_chore_name:
                return False
        last_weekyear = w
    else:
        return True

def set_has_done(record: Record, 
                 weekyear:WeekYear, 
                 probability: float = 1,
                 probabilities:dict[str, float] = {}) -> None:
    if weekyear not in record:
        return
    has_done = (
        lambda name: random() <= probability
                     if name not in probabilities
                     else random() <= probabilities[name]
    )
    for entry in record[weekyear].values():
        entry.people = {
            name: has_done(name)
            for name in entry.people.keys()
        }


    
JSON_DICT = {
    "12 2024": {
        "Tree Farm": {
            "chore_name": "Tree Farm",
            "when": "Later",
            "people": {
                "Steve": False,
            },
        },
        "Iron Farm": {
            "chore_name": "Iron Farm",
            "when": "Monday",
            "people": {
                "ICE27182": True,
                "ICE271828": True,
            },
        },
        "Wither Skeleton Farm": {
            "chore_name": "Wither Skeleton Farm",
            "when": "Saturday",
            "people": {
                "ICE27182": True,
                "ICE271828": False,
            },
        },
        "Mob Farm": {
            "chore_name": "Mob Farm",
            "when": "Whole Week",
            "people": {
                "ICE27182": True,
            },
        },
    },
    "13 2024": {
        "Tree Farm": {
            "chore_name": "Tree Farm",
            "when": "Later",
            "people": {
                "Steve": False,
            },
        },
        "Iron Farm": {
            "chore_name": "Iron Farm",
            "when": "Monday",
            "people": {
                "Alex": True,
                "ICE271828": False,
            },
        },
        "Wither Skeleton Farm": {
            "chore_name": "Wither Skeleton Farm",
            "when": "Saturday",
            "people": {
                "ICE27182": True,
                "ICE271828": False,
            },
        },
        "Mob Farm": {
            "chore_name": "Mob Farm",
            "when": "Whole Week",
            "people": {
                "ICE27182": True,
            },
        },
    },
    "11 2024": {
        "Tree Farm": {
            "chore_name": "Tree Farm",
            "when": "Later",
            "people": {
                "Steve": False,
            },
        },
        "Iron Farm": {
            "chore_name": "Iron Farm",
            "when": "Monday",
            "people": {
                "Alex": True,
                "ICE271828": False,
            },
        },
        "Mob Farm": {
            "chore_name": "Mob Farm",
            "when": "Whole Week",
            "people": {
                "ICE27182": True,
            },
        },
        "Villager Trading Hall": {
            "chore_name": "Villager Trading Hall",
            "when": "Recently",
            "people": {
                "ICE27182": True,
                "ICE271828": False,
                "icecream": False,
            },
        },
    },
    "10 2024": {
        "Tree Farm": {
            "chore_name": "Tree Farm",
            "when": "Later",
            "people": {
                "Steve": True,
            },
        },
        "Iron Farm": {
            "chore_name": "Iron Farm",
            "when": "Monday",
            "people": {
                "ICE27182": False,
                "ICE271828": True,
            },
        },
        "Wither Skeleton Farm": {
            "chore_name": "Wither Skeleton Farm",
            "when": "Saturday",
            "people": {
                "ICE27182": True,
                "ICE271828": True,
            },
        },
        "Mob Farm": {
            "chore_name": "Mob Farm",
            "when": "Whole Week",
            "people": {
                "ICE27182": True,
            },
        },
    },
}

NAMELIST = [
    'icecream',
    'Steve',
    'Alex',
    [
        'ICE27182',
        'ICE271828',
    ]
]

class T_Record(TestCase):
    def test_load_from_json_file(self):
        self.assertEqual(
            JSON_DICT,
            Record.to_json(Record.load_from_json_format(JSON_DICT))
        )
        self.assertEqual(
            0,
            len(Record({}))
        )

    def test_sort(self):
        record = Record.load_from_json_format(JSON_DICT)
        self.assertFalse(is_sorted(record))
        record.sort()
        self.assertTrue(is_sorted(record))

        record = Record({})
        self.assertTrue(is_sorted(record))
        record.sort()
        self.assertTrue(is_sorted(record))
    @skip("Adjusting weights")
    def test_weighted_namelist(self):
        record = Record.load_from_json_format(JSON_DICT)
        # No record
        for p in record.weighted_namelist(NAMELIST, WeekYear(10, 2025)):
            self.assertEqual(p.weight, 16)
        # All in the history
        expected = (
            "WeightedNameList:\n"
            "\ticecream (17.200)\n"
            "\tSteve (19.000)\n"
            "\tAlex (14.800)\n"
            "\tICE27182 (11.800) in group with ICE271828\n"
            "\tICE271828 (20.200) in group with ICE27182"
        )
        self.assertEqual(
            str(record.weighted_namelist(NAMELIST, WeekYear(15, 2024))),
            expected,
        )
        # All in the discarded history
        for p in record.weighted_namelist(NAMELIST, WeekYear(10, 2025)):
            self.assertEqual(p.weight, 16)
        # All in the future
        expected = (
            "WeightedNameList:\n"
            "\ticecream (15.700)\n"
            "\tSteve (14.800)\n"
            "\tAlex (15.400)\n"
            "\tICE27182 (13.000) in group with ICE271828\n"
            "\tICE271828 (13.600) in group with ICE27182"
        )
        self.assertEqual(
            str(record.weighted_namelist(NAMELIST, WeekYear(9, 2024))),
            expected,
        )
        # All in discarded future
        for p in record.weighted_namelist(NAMELIST, WeekYear(10, 2023)):
            self.assertEqual(p.weight, 16)
        # Compound
        expected = (
            "WeightedNameList:\n"
            "\ticecream (17.200)\n"
            "\tSteve (16.000)\n"
            "\tAlex (15.100)\n"
            "\tICE27182 (13.300) in group with ICE271828\n"
            "\tICE271828 (16.000) in group with ICE27182"
        )
        self.assertEqual(
            str(record.weighted_namelist(NAMELIST, WeekYear(12, 2024))),
            expected,
        )
        
    def test_stripe(self):
        RECORD = Record.load_from_json_format(JSON_DICT)

        record = Record.load_from_json_format(JSON_DICT)
        for weekyear in RECORD:
            stripped = record.stripe(this_week= weekyear)
            self.assertEqual(len(stripped), 0)
            self.assertEqual(record, RECORD,
                f"\n{RED}{stripped}\n{GREEN}{RECORD}"
            )
        
        record = Record.load_from_json_format(JSON_DICT)
        stripped = record.stripe(range(10, 15), WeekYear(12, 2024))
        self.assertEqual(len(record), 0)
        self.assertEqual(stripped, RECORD,
            f"\n{RED}{stripped}\n{GREEN}{RECORD}"
        )

        record = Record.load_from_json_format(JSON_DICT)
        stripped = record.stripe(range(-15, -10), WeekYear(12, 2024))
        self.assertEqual(len(record), 0)
        self.assertEqual(stripped, RECORD)

        record = Record.load_from_json_format(JSON_DICT)
        stripped = record.stripe(this_week=WeekYear(10, 2077))
        self.assertEqual(len(record), 0)
        self.assertEqual(stripped, RECORD)

        record = Record.load_from_json_format(JSON_DICT)
        stripped = record.stripe(this_week=WeekYear(32, 1024))
        self.assertEqual(len(record), 0)
        self.assertEqual(stripped, RECORD)

        record = Record.load_from_json_format(JSON_DICT)
        stripped = record.stripe(threshold=range(-1, 2), this_week=WeekYear(11, 2024))
        self.assertEqual(
            record.data.keys(),
            {WeekYear(12, 2024), WeekYear(11, 2024), WeekYear(10, 2024)},
        )
        self.assertEqual(stripped.data.keys(), {WeekYear(week=13, year=2024)})
  
    def test_add_new_chores(self):
        record = Record({})
        chores = Chore.load_chores_from_json("unittests/chores.json")
        record.add_new_chores(chores, WeekYear(10, 2025))
        expected = (
            "10 2025\n"
            "\tBasement Cleaning               \t|\tWhole week  \t|\tAssassin's Creed III: Liberation [ ]\n"
            "\tCarboard Garbage                \t|\tSunday      \t|\tThe Elder Scrolls V: Skyrim [ ]\n"
            "\tHouse Vacuuming                 \t|\tWhole week  \t|\tDeath Stranding      [ ]\tKerbal Space Program [ ]\n"
            "\tKitchen Cleaning                \t|\tWhole week  \t|\tAssassin's Creed II  [ ]\tAssassin's Creed: Brotherhood [ ]\n"
            "\tOrganic Garbage                 \t|\tSunday      \t|\tShadow Tactics       [ ]\n"
            "\tToilet&Bathroom Cleaning North  \t|\tWhole week  \t|\tThe Witcher 2: Assassins of Kings [ ]\n"
            "\tToilet&Bathroom Cleaning South  \t|\tWhole week  \t|\tMicrosoft Flight Simulator 2020 [ ]\n"
            "\n"
            "11 2025\n"
            "\tBasement Cleaning               \t|\tWhole week  \t|\tAssassin's Creed III: Liberation [ ]\n"
            "\tGlass Garbage                   \t|\tWhole week  \t|\tCyberpunk 2077       [ ]\n"
            "\tHouse Vacuuming                 \t|\tWhole week  \t|\tAssetto Corsa        [ ]\tArma 3               [ ]\n"
            "\tKitchen Cleaning                \t|\tWhole week  \t|\tRed Dead Redemption 2 [ ]\tGrand Theft Auto V   [ ]\n"
            "\tPlastic Garbage                 \t|\tSunday      \t|\tBesiege              [ ]\n"
            "\tToilet&Bathroom Cleaning North  \t|\tWhole week  \t|\tThe Elder Scrolls V: Skyrim [ ]\n"
            "\tToilet&Bathroom Cleaning South  \t|\tWhole week  \t|\tMinecraft            [ ]\n"
            "\n"
            "12 2025\n"
            "\tBasement Cleaning               \t|\tWhole week  \t|\tThe Elder Scrolls V: Skyrim [ ]\n"
            "\tHouse Vacuuming                 \t|\tWhole week  \t|\tForza Horizon 4      [ ]\tBesiege              [ ]\n"
            "\tKitchen Cleaning                \t|\tWhole week  \t|\tGrand Theft Auto V   [ ]\tRed Dead Redemption 2 [ ]\n"
            "\tOrganic Garbage                 \t|\tSunday      \t|\tCyberpunk 2077       [ ]\n"
            "\tToilet&Bathroom Cleaning North  \t|\tWhole week  \t|\tArma 3               [ ]\n"
            "\tToilet&Bathroom Cleaning South  \t|\tWhole week  \t|\tShadow Tactics       [ ]\n"
            "\n"
            "13 2025\n"
            "\tBasement Cleaning               \t|\tWhole week  \t|\tAssassin's Creed: Brotherhood [ ]\n"
            "\tGlass Garbage                   \t|\tWhole week  \t|\tForza Horizon 4      [ ]\n"
            "\tHouse Vacuuming                 \t|\tWhole week  \t|\tAssetto Corsa        [ ]\tCities Skylines      [ ]\n"
            "\tKitchen Cleaning                \t|\tWhole week  \t|\tThe Elder Scrolls V: Skyrim [ ]\tCyberpunk 2077       [ ]\n"
            "\tPlastic Garbage                 \t|\tSunday      \t|\tTomb Raider          [ ]\n"
            "\tToilet&Bathroom Cleaning North  \t|\tWhole week  \t|\tAssassin's Creed II  [ ]\n"
            "\tToilet&Bathroom Cleaning South  \t|\tWhole week  \t|\tMicrosoft Flight Simulator 2020 [ ]\n"
            "\n"
            "14 2025\n"
            "\tBasement Cleaning               \t|\tWhole week  \t|\tThe Witcher 2: Assassins of Kings [ ]\n"
            "\tCarboard Garbage                \t|\tSunday      \t|\tThe Witcher 3: Wild Hunt [ ]\n"
            "\tHouse Vacuuming                 \t|\tWhole week  \t|\tAssassin's Creed: Brotherhood [ ]\tAssassin's Creed: Revelations [ ]\n"
            "\tKitchen Cleaning                \t|\tWhole week  \t|\tAssassin's Creed III: Liberation [ ]\tAssassin's Creed III [ ]\n"
            "\tOrganic Garbage                 \t|\tSunday      \t|\tAssassin's Creed II  [ ]\n"
            "\tToilet&Bathroom Cleaning North  \t|\tWhole week  \t|\tMicrosoft Flight Simulator 2020 [ ]\n"
            "\tToilet&Bathroom Cleaning South  \t|\tWhole week  \t|\tAssetto Corsa        [ ]\n"
            "\n"
            "15 2025\n"
            "\tBasement Cleaning               \t|\tWhole week  \t|\tThe Witcher 2: Assassins of Kings [ ]\n"
            "\tGlass Garbage                   \t|\tWhole week  \t|\tCities Skylines      [ ]\n"
            "\tHouse Vacuuming                 \t|\tWhole week  \t|\tShadow Tactics       [ ]\tBesiege              [ ]\n"
            "\tKitchen Cleaning                \t|\tWhole week  \t|\tArma 3               [ ]\tDeath Stranding      [ ]\n"
            "\tPlastic Garbage                 \t|\tSunday      \t|\tTomb Raider          [ ]\n"
            "\tToilet&Bathroom Cleaning North  \t|\tWhole week  \t|\tRed Dead Redemption 2 [ ]\n"
            "\tToilet&Bathroom Cleaning South  \t|\tWhole week  \t|\tForza Horizon 4      [ ]"
        )
        # yellow(repr(str(record)).replace("\\n", '\\n"\n"'))
        for line1, line2 in zip(expected.split("\n"), str(record).split("\n")):
            try:
                self.assertEqual(line1[:line1.index("|", 1+line1.index("|"))],
                                 line2[:line2.index("|", 1+line2.index("|"))])
            except ValueError:
                self.assertEqual(line1, line2)

    def test_flip_status(self):
        record = Record({})
        chores = Chore.load_chores_from_json("unittests/chores.json")
        record.add_new_chores(chores, WeekYear(10, 2025))
        weekyear = WeekYear(15, 2025)
        people = record[weekyear]["Kitchen Cleaning"].people
        self.assertFalse(all(people.values()))
        self.assertTrue(all(map(lambda x: not x, people.values())))
        record.flip_status(
            weekyear, 
            "Kitchen Cleaning", 
            tuple(people.keys())[0]
        )
        self.assertTrue(people[tuple(people.keys())[0]])
        self.assertFalse(
            all(people.values()), 
            f"\n{RED}{people}\n\n{record}{DEFAULT_COLOR}"
            + f"\n{record[WeekYear(15, 2025)]}\n"
        )
        self.assertFalse(all(map(lambda x: not x, people.values())))
        record.flip_status(
            weekyear, 
            "Kitchen Cleaning", 
            tuple(people.keys())[0]
        )
        self.assertFalse(all(people.values()))
        self.assertTrue(all(map(lambda x: not x, people.values())))

    @skip("No assertion inside")
    def test__load_old_record(self):
        record = Record._load_old_record(
            "Records.json", 
            {"Toilet Cleaning": "Toilet&Bathroom Cleaning North"}
        )
        record.add_new_chores(
            Chore.load_chores_from_json(
                "unittests/chores.json"
            ),
            WeekYear(10, 2025)
        )
        yellow(record)
    
# @skip
class T_Record_Random(TestCase):
    START = WeekYear(1, 2025)
    N = 100

    from app.chore import _load_namelist_json as load_namelist_json

    @staticmethod
    def bar_chart(record: Record, 
                  namelist: list[str], 
                  this_weekyear: WeekYear,
                  record_range: range = range(-53, 53)) -> str:
        out = []
        length = 200 / T_Record_Random.N if T_Record_Random.N > 100 else 2
        record_past = str(record.slice(this_weekyear+record_range.start, this_weekyear).to_json())
        record_future = str(record.slice(this_weekyear, this_weekyear+record_range.stop).to_json())
        for i, name in enumerate(sorted(namelist)):
            red = round(record_past.count(f"'{name}': False") * length)
            green = round(record_past.count(f"'{name}': True") * length)
            yellow = round(record_future.count(f"'{name}': False") * length)
            flush = " " * (100 - red - green - yellow)
            if i&1:
                out.append(f'{name:10}\033[101m{' '*red}\033[102m{' '*green}\033[103m{' '*yellow}\033[0m{flush}')
            else:
                out.append(f'{name:10}\033[41m{' '*red}\033[42m{' '*green}\033[43m{' '*yellow}\033[0m{flush}')
        return "\n".join(out)
    
    @staticmethod
    def chore_distribution(record: Record,
                           chores: Iterable[Chore],
                           this_weekyear: WeekYear,
                           record_range: range) -> str:
        out = []
        data = {
            chore.name: {
                person_name: 0
                for person_name in sorted(
                    T_Record_Random.flatten(chore.namelist)
                )
            }
            for chore in sorted(chores, key=lambda chore:chore.name)
        }
        for offset in record_range:
            weekyear = this_weekyear + offset
            if weekyear not in record: continue
            for chore in record[weekyear].values():
                if chore.chore_name in data:
                    for person_name in chore.people:
                        data[chore.chore_name][person_name] += 1
        for i, (chore_name, names_and_chore_counts) in enumerate(data.items()):
            if 1:
                out.append(f"\033[38;2;156;220;255m")
            else:
                out.append(f"\033[38;2;99;35;0m")
            out.append(
                f"{chore_name:20}\n\t"
            )
            for name, count in names_and_chore_counts.items():
                color_value = count * 400 // (record_range.stop-record_range.start)
                color = (
                    "\033[48;2;" 
                    + ";".join((str(color_value),) * 3) 
                    + "m"
                )
                out.append(f"{color}{name:8}{count:<3}")
            out.append("\033[0m\n\n")
        return "".join(out)




    @staticmethod
    def flatten(namelist) -> list[str]:
        out = []
        for elem in namelist:
            if isinstance(elem, str):
                out.append(elem)
            else:
                out.extend(elem)
        return out
    
    @staticmethod
    def visualize(probability: float, 
                  probabilities: dict[str:float]={}, 
                  gen_only: bool=True,
                  show_record: bool = False) -> None:
        print()
        record = Record({}, range(-12, 4))
        chores = Chore.load_chores_from_json("chores.json")
        namelist = T_Record_Random.flatten(
            T_Record_Random.load_namelist_json("namelist.json")
        )
        vis_range = (record.gen_range if gen_only 
                     else range(-T_Record_Random.N, record.gen_range.stop))
        for offset in range(T_Record_Random.N):
            weekyear = T_Record_Random.START + offset
            record_at_weekyear = record.generate(chores, weekyear)
            record.data[weekyear] = record_at_weekyear
            set_has_done(record, 
                         weekyear - record.gen_range.stop, 
                         probability, 
                         probabilities)
            print(
                T_Record_Random.bar_chart(
                    record=record, 
                    namelist=namelist, 
                    this_weekyear=weekyear-record.gen_range.stop,
                    # record_range=range(-T_Record_Random.N, T_Record_Random.N),
                    record_range=vis_range,
                ),
                end="\n"
            )
            print(
                T_Record_Random.chore_distribution(
                    record, 
                    chores, 
                    weekyear-record.gen_range.stop,
                    # range(-12, 5),
                    vis_range,
                ),
                end=""
            )
            print((len(T_Record_Random.flatten(namelist)) + 3 * len(chores))*"\033[F", end="")
            sleep(0.12)
        print("\n"*((len(T_Record_Random.flatten(namelist)) + 3 * len(chores))))
        print(record.weighted_namelist(namelist, weekyear-record.gen_range.stop))
        if show_record:
            print(record)

    @skip("No assertions inside")
    def test_everyone_follows(self):
        T_Record_Random.visualize(1)
    @skip("No assertions inside")
    def test_everyone_95p_follows(self):
        T_Record_Random.visualize(0.95, gen_only=False, show_record=True)

    @skip("No assertions inside")
    def test_everyone_follows_except_sam(self):
        T_Record_Random.visualize(1, {"Sam":0.6}, )
    @skip("No assertions inside")
    def test_everyone_95p_except_sam(self):
        T_Record_Random.visualize(0.95, {"Sam":0.6}, False, True)
    


