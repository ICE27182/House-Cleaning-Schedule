

import unittest
from app import WeekYear, OncePerNWeek, SpecificWeeks
from message import *

# @unittest.skip("Testing T_SpecificWeeks")
class T_OncePerNWeek(unittest.TestCase):
    def test_parsing_P(self):
        strings_set_P = (
            "Once per 2 weeks ",
            "OncE pEr 2  week oN MONday.",
            "ONCE   per 2 WEEK on Monday  with offset 1",

            "\nOnce per 2 weeks with offset 1",
            "Once per 2 weeks on Sunday with offset 1\n",
            "Once per 2 weeks on Sunday.",
            "Once per week",
            "Once per 1 week",
        )
        expected_strings_set_P = (
            r"Once per 2 weeks.                                  OncePerNWeek(weekday=0, n=2, offset=0)",
            r"Once per 2 weeks on Monday.                        OncePerNWeek(weekday=1, n=2, offset=0)",
            r"Once per 2 weeks on Monday with offset 1.          OncePerNWeek(weekday=1, n=2, offset=1)",
            r"Once per 2 weeks with offset 1.                    OncePerNWeek(weekday=0, n=2, offset=1)",
            r"Once per 2 weeks on Sunday with offset 1.          OncePerNWeek(weekday=7, n=2, offset=1)",
            r"Once per 2 weeks on Sunday.                        OncePerNWeek(weekday=7, n=2, offset=0)",
            r"Once per 1 week.                                   OncePerNWeek(weekday=0, n=1, offset=0)",
            r"Once per 1 week.                                   OncePerNWeek(weekday=0, n=1, offset=0)",
        )
        for string, expected_string in zip(strings_set_P, expected_strings_set_P):
            once_per_week = OncePerNWeek.from_str(string)
            # green(f'r"{str(once_per_week):50} {repr(once_per_week)}",')
            self.assertEqual(
                f"{str(once_per_week):50} {repr(once_per_week)}",
                expected_string,
            )
            self.assertEqual(
                str(OncePerNWeek.from_str(str(once_per_week))), 
                str(once_per_week),
            )
            self.assertEqual(
                str(eval(repr(once_per_week))), 
                str(once_per_week),
            )

    def test_parsing_F(self):
        strings_set_F = (
            "",
            "gbjnkvfmcdl,s liu o fq ieu rg a",
            "\n\n\nsdfwef\n\neq",

            "0nce per 2 weeks with offset 1",
            "Once per two weeks on Sunday",
            "Once per week on Sunday with offset 1",
            "Once per 2 weeks on Wensday with offset 1",
            "Once every week",
            "The first Sunday of every month ", 
        )
        expected_error_message = (
            r"`description` cannot be recognized. Got ''.",  
            r"`description` cannot be recognized. Got 'gbjnkvfmcdl,s liu o fq ieu rg a'.",
            r"`description` cannot be recognized. Got '\n\n\nsdfwef\n\neq'.",
            r"`description` cannot be recognized. Got '0nce per 2 weeks with offset 1'.",
            r"`description` cannot be recognized. Got 'Once per two weeks on Sunday'.",
            r"`description` cannot be recognized. Got 'Once per week on Sunday with offset 1'.",
            r"tuple.index(x): x not in tuple (Possible Cause: 'wensday'(Original:'Wensday') is not a valid weekday name.)",
            r"`description` cannot be recognized. Got 'Once every week'.",
            r"`description` cannot be recognized. Got 'The first Sunday of every month '.",
        )
        for string, expected_msg in zip(strings_set_F, expected_error_message):
            with self.assertRaises(ValueError) as e:
                once_per_week = OncePerNWeek.from_str(string)
            self.assertEqual(str(e.exception), expected_msg)
    
    def test_is_this_week(self):
        regular = OncePerNWeek.from_str("once per week")
        for i in range(-60, 60):
            self.assertTrue(regular.is_this_week(WeekYear.present_weekyear() + i))

        organic = OncePerNWeek.from_str("ONce per 2 weeks on Monday with offset 0")
        plastic = OncePerNWeek.from_str("once per 2 week on Monday with offset 1")
        for i in range(-60, 60, 2):
            weekyear = WeekYear(1, 2025) + i
            self.assertFalse(organic.is_this_week(weekyear))
            self.assertTrue(plastic.is_this_week(weekyear))
            weekyear += 1
            self.assertTrue(organic.is_this_week(weekyear))
            self.assertFalse(plastic.is_this_week(weekyear))

        self.assertTrue(organic.is_this_week(WeekYear(8, 2025)))
        self.assertTrue(plastic.is_this_week(WeekYear(9, 2025)))
        self.assertFalse(organic.is_this_week(WeekYear(33, 2024)))
        self.assertFalse(plastic.is_this_week(WeekYear(32, 2024)))


class T_SpecificWeeks(unittest.TestCase):
    def test_parsing_P(self):
        strings_set_P = (
            "Weekyears on Monday: 32 2025, 24 2025, 43 2025, 45 2025",
            "weeKyEaRs: 32   2025   24      2025, 43   2025  45    2025,  ",
            "Weeks oN Saturday in 2025: 32     24    43   , 45",

            "\nWeekyears on Tuesday: 32 2025, 24 2025, 43 2025, 45 2025,",
            "\nWeekyears on Tuesday: 32 2025 24 2025 43 2025 45 2025\n",
            "Weekyears on Monday:",
            "Weekyears on Monday: 32 2025",
            "Weekyears on Monday: 32 2025,",

            "\nWeekyears: 32 2025, 24 2025, 43 2025, 45 2025,",
            "\nWeekyears: 32 2025 24 2025 43 2025 45 2025\n",
            "Weekyears :",
            "Weekyears : 32 2025",
            "Weekyears : 32 2025,",


            "\nWeeks oN Saturday in 2025: 32     24    43   , 45",
            "\nWeeks oN Saturday in 2025: 32, 24, 43, 45\n",
            "\nWeeks oN Saturday in 2025: 32, 24, 43, 45\n",
            "Weeks in 2025: 32 24 43 45",
            "Weeks in 2024: 32, 24, 43, 45",
            "Weeks in 2024: 32,",
            "Weeks in 2025: 32",
            "Weeks in 2025: 32 34  ",
            "Weeks in 2025: ",
            "Weeks in 2025: ,",
        )
        expected_strings_set_P = (
            r"Weekyears on Monday: 24 2025, 32 2025, 43 2025, 45 2025.     SpecificWeeks(weekday=1, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears: 24 2025, 32 2025, 43 2025, 45 2025.               SpecificWeeks(weekday=0, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears on Saturday: 24 2025, 32 2025, 43 2025, 45 2025.   SpecificWeeks(weekday=6, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears on Tuesday: 24 2025, 32 2025, 43 2025, 45 2025.    SpecificWeeks(weekday=2, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears on Tuesday: 24 2025, 32 2025, 43 2025, 45 2025.    SpecificWeeks(weekday=2, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears on Monday: .                                       SpecificWeeks(weekday=1, weekyears={})",
            r"Weekyears on Monday: 32 2025.                                SpecificWeeks(weekday=1, weekyears={WeekYear(week=32, year=2025)})",
            r"Weekyears on Monday: 32 2025.                                SpecificWeeks(weekday=1, weekyears={WeekYear(week=32, year=2025)})",
            r"Weekyears: 24 2025, 32 2025, 43 2025, 45 2025.               SpecificWeeks(weekday=0, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears: 24 2025, 32 2025, 43 2025, 45 2025.               SpecificWeeks(weekday=0, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears: .                                                 SpecificWeeks(weekday=0, weekyears={})",
            r"Weekyears: 32 2025.                                          SpecificWeeks(weekday=0, weekyears={WeekYear(week=32, year=2025)})",
            r"Weekyears: 32 2025.                                          SpecificWeeks(weekday=0, weekyears={WeekYear(week=32, year=2025)})",
            r"Weekyears on Saturday: 24 2025, 32 2025, 43 2025, 45 2025.   SpecificWeeks(weekday=6, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears on Saturday: 24 2025, 32 2025, 43 2025, 45 2025.   SpecificWeeks(weekday=6, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears on Saturday: 24 2025, 32 2025, 43 2025, 45 2025.   SpecificWeeks(weekday=6, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears: 24 2025, 32 2025, 43 2025, 45 2025.               SpecificWeeks(weekday=0, weekyears={WeekYear(week=24, year=2025), WeekYear(week=32, year=2025), WeekYear(week=43, year=2025), WeekYear(week=45, year=2025)})",
            r"Weekyears: 24 2024, 32 2024, 43 2024, 45 2024.               SpecificWeeks(weekday=0, weekyears={WeekYear(week=24, year=2024), WeekYear(week=32, year=2024), WeekYear(week=43, year=2024), WeekYear(week=45, year=2024)})",
            r"Weekyears: 32 2024.                                          SpecificWeeks(weekday=0, weekyears={WeekYear(week=32, year=2024)})",
            r"Weekyears: 32 2025.                                          SpecificWeeks(weekday=0, weekyears={WeekYear(week=32, year=2025)})",
            r"Weekyears: 32 2025, 34 2025.                                 SpecificWeeks(weekday=0, weekyears={WeekYear(week=32, year=2025), WeekYear(week=34, year=2025)})",
            r"Weekyears: .                                                 SpecificWeeks(weekday=0, weekyears={})",
        )
        for string, expected_string in zip(strings_set_P, expected_strings_set_P):
            # yellow(string)
            specific_weeks = SpecificWeeks.from_str(string)
            # green(f'r"{str(specific_weeks):60} {repr(specific_weeks)}",')
            self.assertEqual(
                f"{str(specific_weeks):60} {repr(specific_weeks)}",
                expected_string,
            )
            self.assertEqual(
                str(SpecificWeeks.from_str(str(specific_weeks))), 
                str(specific_weeks),
            )
            self.assertEqual(
                str(eval(repr(specific_weeks))), 
                str(specific_weeks),
            )

    def test_parsing_F(self):
        strings_set_F = (
            "",
            "gbjnkvfmcdl,s liu o fq ieu rg a",
            "\n\n\nsdfwef\n\neq",

            "Weekyear on Monday: 32 2025, 24 2025, 43 2025, 45 2025",
            "Weekyear: 3 2   2 0 2 5   24      2025, 43   2025  45    2025,  ",
            "Weeks uN Saturday in 2025: 32     24    43   , 45",

            "\nWe\nekyears on Tuesday: 32 2025, 24 2025, 43 2025, 45 2025,",
            "\nWeekyears on Tuseday: 32 2025 24 2025 43 2025 45 2025\n",
            "Weekyears on weekend:",

            "Weekyears oN Saturday in 2025: 32 2025 24 2025 43 2025 45 2025",
            "\nWeekyear: 32 2025 24 2025 43 2025 45 2025\n",
            "Weakyears :",


            "Weeks in 2025 oN Saturday: 32     24    43   , 45",
            "Weeks in Saturday in 2025: 32, 24, 43, 45\n",
            "Weeks at Saturday in 2025: 32, 24, 43, 45\n",
            "Weeks on Saturday on 2025: 32, 24, 43, 45\n",
        )
        expected_error_message = (
            r"`description` cannot be recognized. Got ''.",
            r"`description` cannot be recognized. Got 'gbjnkvfmcdl,s liu o fq ieu rg a'.",
            r"`description` cannot be recognized. Got '\n\n\nsdfwef\n\neq'.",
            r"`description` cannot be recognized. Got 'Weekyear on Monday: 32 2025, 24 2025, 43 2025, 45 2025'.",
            r"`description` cannot be recognized. Got 'Weekyear: 3 2   2 0 2 5   24      2025, 43   2025  45    2025,  '.",
            r"`description` cannot be recognized. Got 'Weeks uN Saturday in 2025: 32     24    43   , 45'.",
            r"`description` cannot be recognized. Got '\nWe\nekyears on Tuesday: 32 2025, 24 2025, 43 2025, 45 2025,'.",
            r"tuple.index(x): x not in tuple (Possible Cause: 'tuseday'(Original:'Tuseday') is not a valid weekday name.)",
            r"tuple.index(x): x not in tuple (Possible Cause: 'weekend'(Original:'weekend') is not a valid weekday name.)",
            r"`description` cannot be recognized. Got 'Weekyears oN Saturday in 2025: 32 2025 24 2025 43 2025 45 2025'.",
            r"`description` cannot be recognized. Got '\nWeekyear: 32 2025 24 2025 43 2025 45 2025\n'.",
            r"`description` cannot be recognized. Got 'Weakyears :'.",
            r"`description` cannot be recognized. Got 'Weeks in 2025 oN Saturday: 32     24    43   , 45'.",
            r"`description` cannot be recognized. Got 'Weeks in Saturday in 2025: 32, 24, 43, 45\n'.",
            r"`description` cannot be recognized. Got 'Weeks at Saturday in 2025: 32, 24, 43, 45\n'.",
            r"`description` cannot be recognized. Got 'Weeks on Saturday on 2025: 32, 24, 43, 45\n'.",
        )
        for string, expected_msg in zip(strings_set_F, expected_error_message):
            # yellow(string)
            with self.assertRaises(ValueError) as e:
                once_per_week = SpecificWeeks.from_str(string)
            # green(f'r"{e.exception}",')    
            self.assertEqual(str(e.exception), expected_msg)

    def test_is_this_week(self):
        weeks = {3, 7, 11, 15, 20, 25, 29, 33, 37, 42, 46, 50}
        carboard = SpecificWeeks.from_str(
            "Weeks on Monday in 2025: 3 7 11 15 20 25 29 33 37 42 46 50"
        )
        for week in range(1, 53):
            if week in weeks:
                self.assertTrue(carboard.is_this_week(WeekYear(week, 2025)))
            else:
                self.assertFalse(carboard.is_this_week(WeekYear(week, 2025)))

"""
@unittest.skip("Not Implemented")        
class T_NthWeekPerMonth(unittest.TestCase):
    def test_parsing_P(self):
        strings_set_P = (
            "The first Sunday of every month ", 
            "The second week of every month", 
            "tHE fifTh tueSdAy of everY MONth . ",

            "\nThe first Sunday of every month",
            "The second WeeK of every month", 
            "  The second    MonDay of every    month\t",
            
            "The first Sunday of every month",
        )
        expected_strings_set_P = (
            r"The first Sunday of every month.                   NthWeekPerMonth(self.n=1, self.weekday=7)",
            r"The second week of every month.                    NthWeekPerMonth(self.n=2, self.weekday=0)",
            r"The fifth Tuesday of every month.                  NthWeekPerMonth(self.n=5, self.weekday=2)",
            r"The first Sunday of every month.                   NthWeekPerMonth(self.n=1, self.weekday=7)",
            r"The second week of every month.                    NthWeekPerMonth(self.n=2, self.weekday=0)",
            r"The second Monday of every month.                  NthWeekPerMonth(self.n=2, self.weekday=1)",
            r"The first Sunday of every month.                   NthWeekPerMonth(self.n=1, self.weekday=7)",
        )
        for string, expected_string in zip(strings_set_P, expected_strings_set_P):
            once_per_week = NthWeekPerMonth.from_str(string)
            # print(f'r"{str(once_per_week):50} {repr(once_per_week)}",',)
            self.assertEqual(
                f"{str(once_per_week):50} {repr(once_per_week)}",
                expected_string
            )

    def test_parsing_F(self):
        strings_set_F = (
            "", 
            "jbhdknjlmk\nbvrnmd  ef", 
            "\n\faserfdxdth\b\b\basfaer",

            "  The sec0nd    MonDay of every    month\t",
            
            "The first of every month",
            "The Sunday of every month",
            "The second sunday per month",
            
            "The sixth sunday of every month",
            "The frist week of every month",
            "The forth week of every mouth",

        )
        expected_error_message = (
            r"`description` cannot be recognized. Got ''.",
            r"`description` cannot be recognized. Got 'jbhdknjlmk\nbvrnmd  ef'.",
            r"`description` cannot be recognized. Got '\n\x0caserfdxdth\x08\x08\x08asfaer'.",
            r"tuple.index(x): x not in tuple (Possible Cause: 'sec0nd'(Original:'sec0nd') is not a valid ordinal numerals (e.g. first, second).)",
            r"`description` cannot be recognized. Got 'The first of every month'.",
            r"`description` cannot be recognized. Got 'The Sunday of every month'.",
            r"`description` cannot be recognized. Got 'The second sunday per month'.",
            r"tuple.index(x): x not in tuple (Possible Cause: 'sixth'(Original:'sixth') is not a valid ordinal numerals (e.g. first, second).)",
            r"tuple.index(x): x not in tuple (Possible Cause: 'frist'(Original:'frist') is not a valid ordinal numerals (e.g. first, second).)",
            r"`description` cannot be recognized. Got 'The forth week of every mouth'.",
        )
        for string, expected_msg in zip(strings_set_F, expected_error_message):
            with self.assertRaises(ValueError) as e:
                once_per_week = NthWeekPerMonth.from_str(string)
            self.assertEqual(str(e.exception), expected_msg)
            # print(f'r"{e.exception}",')
    
    def test_is_this_week(self):
        carboard_monday_2025 = (
            3, 7, 11, 15, 20, 25, 29, 33, 37, 42, 46, 50,
        )
        carboard = NthWeekPerMonth.from_str("The second Monday of every month")
        for i in range(1, 52 + 1):
            weekyear = WeekYear(i, 2025)
            print(weekyear)
            if i in carboard_monday_2025:
                self.assertTrue(carboard.is_this_week(weekyear))
            else:
                self.assertFalse(carboard.is_this_week(weekyear))

"""
