
from sys import argv
from app import Record, WeekYear, Chore
from collections.abc import Iterable

from app.chore import _load_namelist_json as load_namelist_json

N = 100

def flatten(namelist) -> list[str]:
        out = []
        for elem in namelist:
            if isinstance(elem, str):
                out.append(elem)
            else:
                out.extend(elem)
        return out

def bar_chart(record: Record, 
                namelist: list[str], 
                this_weekyear: WeekYear,
                record_range: range = range(-53, 53)) -> str:
    out = []
    length = 200 / N if N > 100 else 2
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
    
def chore_distribution(record: Record,
                        chores: Iterable[Chore],
                        this_weekyear: WeekYear,
                        record_range: range) -> str:
    out = []
    data = {
        chore.name: {
            person_name: 0
            for person_name in sorted(
                flatten(chore.namelist)
            )
        }
        for chore in sorted(chores, key=lambda chore:chore.name)
    }
    chores = {chore.name: chore for chore in chores}
    for offset in record_range:
        weekyear = this_weekyear + offset
        if weekyear not in record: continue
        for entry in record[weekyear].values():
            if entry.chore_name in data:
                for person_name in entry.people:
                    if person_name in chores[entry.chore_name].namelist:
                        data[entry.chore_name][person_name] += 1
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
if __name__ == "__main__":
    if len(argv) <= 1:
        N = 12
    else:
        print(argv)
        N = int(argv[1])
    record = Record.load_from_json_file("record.json")
    namelist = load_namelist_json("namelist.json")
    chores = Chore.load_chores_from_json("chores.json")
    print(
        bar_chart(
            record,
            namelist,
            WeekYear.present_weekyear(), 
            range(-N, max(record) - WeekYear.present_weekyear())
        )
    )
    print(
        chore_distribution(
            record, 
            chores,
            WeekYear.present_weekyear(),
            range(-N, max(record) - WeekYear.present_weekyear()),
        )
    )


