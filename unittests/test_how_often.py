

import unittest
from app import WeekYear, OncePerNWeek

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
            r"Once per 2 weeks.                                  OncePerNWeek(self.weekday=0, self.n=2, self.offset=0)",
            r"Once per 2 weeks on Monday.                        OncePerNWeek(self.weekday=1, self.n=2, self.offset=0)",
            r"Once per 2 weeks on Monday with offset 1.          OncePerNWeek(self.weekday=1, self.n=2, self.offset=1)",
            r"Once per 2 weeks with offset 1.                    OncePerNWeek(self.weekday=0, self.n=2, self.offset=1)",
            r"Once per 2 weeks on Sunday with offset 1.          OncePerNWeek(self.weekday=7, self.n=2, self.offset=1)",
            r"Once per 2 weeks on Sunday.                        OncePerNWeek(self.weekday=7, self.n=2, self.offset=0)",
            r"Once per 1 week.                                   OncePerNWeek(self.weekday=0, self.n=1, self.offset=0)",
            r"Once per 1 week.                                   OncePerNWeek(self.weekday=0, self.n=1, self.offset=0)",
        )
        for string, expected_string in zip(strings_set_P, expected_strings_set_P):
            once_per_week = OncePerNWeek.from_str(string)
            self.assertEqual(
                f"{str(once_per_week):50} {repr(once_per_week)}",
                expected_string
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


