

from message import *
import unittest

from app import Chore

import json

NAMELIST = [
    "Minecraft",
    "Death Stranding",
    "Cyberpunk 2077",
        "Grand Theft Auto V", 
        "Red Dead Redemption 2",
    "The Elder Scrolls V: Skyrim",
    "Microsoft Flight Simulator 2020",
    "Kerbal Space Program",
        "Assassin's Creed II", 
        "Assassin's Creed: Brotherhood", 
        "Assassin's Creed: Revelations",

        "Assassin's Creed III",
        "Assassin's Creed III: Liberation",

        "The Witcher 2: Assassins of Kings", 
        "The Witcher 3: Wild Hunt",
    "Arma 3",
    "Besiege",
    "Tomb Raider",
    "Shadow Tactics",
    "Assetto Corsa",
    "Forza Horizon 4",
    "Cities Skylines",
]

CHORES = [
            {
                "name": "Kitchen Cleaning",
                "namelist": NAMELIST,
                "num_of_people": 2,
                "how_often": "Once per week",
            },
            {
                "name": "House Vacuuming",
                "namelist": "unittests/namelist.json",
                "num_of_people": 2,
                "how_often": "Once per week",
            },
            {
                "name": "Basement Cleaning",
                "namelist": NAMELIST,
                "num_of_people": 1,
                "how_often": "Once per week",
            },
            {
                "name": "Glass Garbage",
                "namelist": NAMELIST,
                "num_of_people": 1,
                "how_often":  "Once per 2 week with offset 1",
            },
            {
                "name": "Carboard Garbage",
                "namelist": NAMELIST,
                "num_of_people": 1,
                "how_often": "Weeks on Sunday in 2025: 2 6 10 14 19 24 28 32 36 41 45 49",
            },
            {
                "name": "Organic Garbage",
                "namelist": "unittests/namelist.json",
                "num_of_people": 1,
                "how_often": "Once per 2 weeks on Sunday with offset 0"
            },
            {
                "name": "Plastic Garbage",
                "namelist": NAMELIST,
                "num_of_people": 1,
                "how_often": "Once per 2 weeks on Sunday with offset 1"
            },
            {
                "name": "Toilet&Bathroom Cleaning North",
                "namelist": NAMELIST,
                "num_of_people": 1,
                "how_often": "Once per week"
            },
            {
                "name": "Toilet&Bathroom Cleaning South",
                "namelist": NAMELIST,
                "num_of_people": 1,
                "how_often": "Once per week"
            },
        ]

class T_Chore(unittest.TestCase):
    @unittest.skip("No assertions inside")
    def test_from_json_dict(self):
        for chore in CHORES:
            chore = Chore.from_json_dict(chore)
            yellow(chore, end = "\n" + "-"*80 + "\n")
            blue(repr(chore), end = "\n" + "-"*80 + "\n\n\n")
    @unittest.skip("No assertions inside")
    def test_load_chores_from_json(self):
        for chore in Chore.load_chores_from_json("unittests/chores.json"):
            yellow(chore, end = "\n" + "-"*80 + "\n")
            blue(repr(chore), end = "\n" + "-"*80 + "\n\n\n")
    
    def test_all(self):
        for chore_file, chore_json_dict in zip(
            Chore.load_chores_from_json("unittests/chores.json"), 
            CHORES,
        ):
            chore_file:Chore
            chore_code:Chore = Chore.from_json_dict(chore_json_dict)
            self.assertEqual(str(chore_file),str(chore_code))
            self.assertEqual(repr(chore_file),repr(chore_code))
            # More conversions
            self.assertEqual(chore_file.to_json(), chore_code.to_json())
            self.assertEqual(
                str(Chore.from_json_dict(chore_file.to_json())),
                str(Chore.from_json_dict(chore_code.to_json())),
            )
            self.assertEqual(
                str(Chore.from_json_dict(chore_file.to_json())),
                str(chore_file),
            )
