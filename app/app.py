

from .admins import Admins
from .weekyear import WeekYear
from .chore import Chore
from .record import Record

from dataclasses import dataclass
from collections.abc import Iterable
from os import PathLike, getcwd
from os.path import dirname, exists
from shutil import make_archive, copy

@dataclass(slots=True)
class App:
    record: Record
    chores: Iterable[Chore]
    admins: Admins
    record_path: PathLike = "record.json"
    _weekyear: None|WeekYear = None # For testing & debugging

    def get_weekyear(self) -> WeekYear:
        return (self._weekyear if self._weekyear is not None 
                else WeekYear.present_weekyear())
    
    def write_record(self):
        self.record.save_to_json(self.record_path)
    
    def get_table_for_weekyear(self, weekyear:WeekYear) -> str|None:
        # Read
        if weekyear in self.record:
            return self._get_main_table(weekyear=weekyear)
        # Generate new and recurse once
        elif self._valid_for_record_generation(weekyear):
            record_at_weekyear = self.record.generate(
                chores=self.chores, 
                weekyear=weekyear, 
                this_weekyear=self.get_weekyear(),
            )
            self.record.data[weekyear] = record_at_weekyear
            return self.get_table_for_weekyear(weekyear)
        # Invalid (To many weeks ahead or non-existing history)
        else:
            return None
    
    def get_next_week_button(self, this_weekyear:WeekYear) -> str:
        """
        Return the html element of the link to next week.
        Return empty str if next week is out of valid range.
        """
        weekyear = this_weekyear + 1
        if (weekyear in self.record 
            or self._valid_for_record_generation(weekyear)):
            link = f'"/schedules/weekyear/{weekyear.week}-{weekyear.year}"'
            return f'<a class="next_week_button" href={link}>Next Week</a>'
        else:
            return ""
    
    def get_last_week_button(self, this_weekyear:WeekYear) -> str:
        """
        Return the html element of the link to last week.
        Return the lastest possible week if there is a gap.
        Return empty str if next week is out of valid range.
        """
        weekyear = this_weekyear - 1
        if (weekyear in self.record 
            or self._valid_for_record_generation(weekyear)):
            link = f'"/schedules/weekyear/{weekyear.week}-{weekyear.year}"'
            return f'<a class="last_week_button" href={link}>Last Week</a>'
        else:
            return ""
    
    def get_current_week_button(self) -> str:
        link = f'"{self.get_link_to_this_weekyear()}"'
        return f'<a class="current_week_button" href={link}>Current Week</a>' 
    
    def get_weekyear_title(self, weekyear: WeekYear) -> str:
        week, year = weekyear.week, weekyear.year
        if weekyear == self.get_weekyear():
            title = f"<h1>Week {week} in {year}</h1>"
        else:
            title = f'<h1 class="red">Week {week} in {year}</h1>'
        return title + f"<h3>{weekyear.get_range_in_dates()}</h3>"

    def get_link_to_this_weekyear(self) -> str:
        weekyear = self.get_weekyear()
        return f"/schedules/weekyear/{weekyear.week}-{weekyear.year}"

    def compress_everything(self) -> str:
        current_dir = getcwd()
        parent_dir = dirname(current_dir)
        return make_archive(f"{parent_dir}/archive", "zip", current_dir)

    def ensure_more_info_html_exists(self, urlized_chore_name) -> None:
        if not exists(f"app/templates/more_info/{urlized_chore_name}.html"):
            print(
                "A new template is generated at: "
                + copy(
                    f"app/templates/more_info/.template.html",
                    f"app/templates/more_info/{urlized_chore_name}.html"
                )
            )

    def get_more_info_table(self, chore_name:str) -> str:
        str_buff = ["<table>\n"]
        for offset in self.record.gen_range:
            weekyear = app.get_weekyear() + offset
            if (weekyear in self.record
                and chore_name in self.record[weekyear]):
                str_buff.append(
                    "\t<tr>\n\t\t<td>" if weekyear != app.get_weekyear()
                    else '\t<tr class="more_info_current_week">\n\t\t<td>'
                )
                people = self.record[weekyear][chore_name].people
                for person, status in people.items():
                    color_class = "green" if status else "red"
                    str_buff.append(
                        f'<p class="{color_class}">{person}</p>'
                    )
                str_buff.append(
                    "</td>\n"
                    f"\t\t<td>{weekyear.get_range_in_dates()}</td>\n"
                    "\t</tr>\n"
                    )
        str_buff.append("</table>\n")
        return "".join(str_buff)
            
    def _valid_for_record_generation(self, weekyear:WeekYear) -> str:
        return 0 <= weekyear-self.get_weekyear() < self.record.gen_range.stop
    
    def _get_main_table(self, weekyear:WeekYear) -> str:
        string_buff = ['<table class="main">\n']
        for chore in sorted(self.record[weekyear].values(), 
                            key=lambda entry:entry.chore_name):
            chore:Record.RecordEntry
            string_buff.append('\t<tr>\n')
            # Chore Name
            string_buff.append(f'\t\t<td>{chore.chore_name}</td>\n')
            # All persons
            string_buff.append(f'\t\t<td>\n')
            for person, has_done in chore.people.items():
                color_class = "green" if has_done else "red"
                if weekyear == self.get_weekyear():
                    link = App._get_status_button_link(weekyear, 
                                                    chore.chore_name, 
                                                    person)
                    string_buff.append(
                        f'\t\t\t<p><a class="{color_class}" href="{link}">'
                        + f'{person}</a></p>\n'
                    )
                else:
                    string_buff.append(
                        f'\t\t\t<p class="{color_class}">{person}</p>\n'
                    )

            string_buff.append(f'\t\t</td>\n')
            # When
            string_buff.append(f'\t\t<td>{chore.when}</td>\n')
            # More info
            link = f"/schedules/more-info/{App.urlize(chore.chore_name)}"
            string_buff.append(
                f'\t\t<td><a class="more_info" href="{link}">'
                + 'More Info</a></td>\n'
            )
            string_buff.append('\t</tr>\n')
        string_buff.append("</table>")
        return "".join(string_buff)
    

    def confirm_admin_set(self, weekyear: WeekYear, chore_name: str, 
                          name: str, status: str, past_tense: bool) -> str:
        """
        Return a confirmation string.
        Raise a ValueError if the arguments are invalid.
        """
        if status.lower() == "true":
            status = True
        elif status.lower() == "false":
            status = False
        else:
            raise ValueError("Invalid status. "
                             f"Expected either `True` or `False`. "
                             f"Got `{status}`.")
        if weekyear not in self.record:
            raise ValueError("Invalid week and/or year. "
                             f"Got week {weekyear.week} in {weekyear.year}.")
        if chore_name not in self.record[weekyear]:
            raise ValueError("Invalid chore name with given week and year. "
                             f"Got {chore_name}.")
        if name in self.record[weekyear][chore_name].people:
            new_status = not self.record[weekyear][chore_name].people[name]
        else:
            raise ValueError("Invalid name. "
                                f"'{name}' is not in the record with given "
                                "week, year and chore name.")
        word_set = "set" if past_tense else "set"
        return (f"{word_set} the status of '{name}' in chore '{chore_name}' "
                f"for week {weekyear.week} in {weekyear.year} to {new_status}.")
    
    def execute_admin_set(self, weekyear: WeekYear, chore_name: str, 
                          name: str, status: str) -> None:
        """
        Will run confirm_admin_set first to validate the arguments.
        ValueError will raise if the arguments are invalid.
        """
        self.confirm_admin_set(weekyear, chore_name, name, status, False)
        status = True if status.lower() == "true" else False
        self.record[weekyear][chore_name].people[name] = status


    def confirm_admin_change(self, weekyear: WeekYear, chore_name: str, 
                             from_name: str, to_name: str, past_tense: bool) -> str:
        """
        Return a confirmation string.
        Does not check if the `to_name` is valid or not.
        Raise a ValueError if the arguments are invalid.
        """
        if weekyear not in self.record:
            raise ValueError("Invalid week and/or year. "
                             f"Got week {weekyear.week} in {weekyear.year}.")
        if chore_name not in self.record[weekyear]:
            raise ValueError("Invalid chore name with given week and year. "
                             f"Got {chore_name}.")
        if from_name not in self.record[weekyear][chore_name].people:
            raise ValueError("Invalid name. "
                             f"'{from_name}' is not in the record with given "
                             "week, year and chore name.")
        if from_name == to_name:
            raise ValueError("Invalid names. "
                             f"'{from_name}' and '{to_name}' are the same.")
        word_change = "changed" if past_tense else "change"
        return (f"{word_change} '{from_name}' in chore '{chore_name}' "
                f"for week {weekyear.week} in {weekyear.year} to '{to_name}'.")
    
    def execute_admin_change(self, weekyear: WeekYear, chore_name: str, 
                             from_name: str, to_name: str) -> None:
        """
        Will run confirm_admin_change first to validate the arguments.
        ValueError will raise if the arguments are invalid.
        """
        self.confirm_admin_change(weekyear, chore_name, from_name, to_name, False)
        self.record[weekyear][chore_name].people[to_name] = (
            self.record[weekyear][chore_name].people[from_name]
        )
        del self.record[weekyear][chore_name].people[from_name]
        
    
    # def confirm_admin_command(self, command: str, weekyear: WeekYear,
    #                           chore_name: str, name: str) -> str:
    #     """
    #     Return a confirmation string.
    #     Raise a ValueError if the arguments are invalid.
    #     """
    #     if weekyear not in self.record:
    #         raise ValueError("Invalid week and/or year. "
    #                          f"Got week {weekyear.week} in {weekyear.year}.")
    #     if chore_name not in self.record[weekyear]:
    #         raise ValueError("Invalid chore name with given week and year. "
    #                          f"Got {chore_name}.")
        
    #     if command == "add":
    #         if name in self.record[weekyear][chore_name].people:
    #             raise ValueError("Invalid name. "
    #                              f"'{name}' is already in the record with "
    #                              "given week, year and chore name.")
    #         return (f"add '{name}' in chore '{chore_name}' "
    #                 f"for week {weekyear.week} in {weekyear.year}.")
    #     elif command == "change":
    #         if name in self.record[weekyear][chore_name].people:
    #             new_status = not self.record[weekyear][chore_name].people[name]
    #         else:
    #             raise ValueError("Invalid name. "
    #                              f"'{name}' is not in the record with given "
    #                              "week, year and chore name."
    #                              "Use 'add' command if you want to add a new "
    #                              "person if you want to add a new person.")
    #         return (f"change the status of '{name}' in chore '{chore_name}' "
    #                 f"for week {weekyear.week} in {weekyear.year} to {new_status}.")
    #     elif command == "remove":
    #         if name in self.record[weekyear][chore_name].people:
    #             return (f"remove '{name}' from chore '{chore_name}' "
    #                     f"for week {weekyear.week} in {weekyear.year}.")
    #         else:
    #             raise ValueError("Invalid name. "
    #                              f"'{name}' is not in the record with given "
    #                              "week, year and chore name.")
    #     else:
    #         raise ValueError("Invalid command. "
    #                          "Expected either `add`, `change` or `remove`. "
    #                          f"Got `{command}`.")
    
    # def execute_admin_command(self, command: str, weekyear: WeekYear, 
    #                           chore_name: str, name: str) -> None:
    #     """
    #     Will run confirm_admin_command first to validate the arguments.
    #     ValueError will raise if the arguments are invalid.
    #     """
    #     self.confirm_admin_command(command, weekyear, chore_name, name)
    #     if command == "add":
    #         self.record[weekyear][chore_name][name] = False
    #     elif command == "change":
    #         status = self.record[weekyear][chore_name][name]
    #         self.record[weekyear][chore_name][name] = not status
    #     elif command == "remove":
    #         del self.record[weekyear][chore_name][name]
        

    @staticmethod
    def _get_status_button_link(weekyear: WeekYear,
                                chore_name: str,
                                person: str) -> str:
        return (
            "/schedules/update-record"
            f"/{weekyear.week}-{weekyear.year}"
            f"-{App.urlize(chore_name)}"
            f"--{"-".join(person.split())}"
        )
    
    @staticmethod
    def urlize(line: str) -> str:
        return "-".join(line.lower().split())
    

record_path = "record.json"
chores_path = "chores.json"
passkeys_path = "passkeys.json"
app = App(
    record=Record.load_from_json_file(record_path),
    chores=Chore.load_chores_from_json(chores_path),
    record_path=record_path,
    admins=Admins(passkeys_path),
)
