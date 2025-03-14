

from .weekyear import WeekYear
from .chore import Chore
from .record import Record

from dataclasses import dataclass
from collections.abc import Iterable
from os import PathLike, getcwd
from os.path import dirname
from shutil import make_archive

@dataclass
class App:
    record: Record
    chores: Iterable[Chore]
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
app = App(
    record=Record.load_from_json_file(record_path),
    chores=Chore.load_chores_from_json(chores_path),
    record_path=record_path,
)
