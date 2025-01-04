
from app.database import schedule, record
from app.date_utils import last_week_weekyear, next_week_weekyear

# Schedule.add_task, Schedule[week_year]
if False:
    print("46: ", schedule["46 2024"], end="\n\n")
    print("47: ", schedule["47 2024"], end="\n\n")
    print("48: ", schedule["48 2024"], end="\n\n")
    print("49: ", schedule["49 2024"], end="\n\n")
    print("50: ", schedule["50 2024"], end="\n\n")
    print("51: ", schedule["51 2024"], end="\n\n")
    print("52: ", schedule["52 2024"], end="\n\n")

    print("-"*80 + "\n"*2)

# Record
if False:
    record.strip_data()
    print("46: ", record["46 2024"], end="\n\n")
    print("47: ", record["47 2024"], end="\n\n")
    print("48: ", record["48 2024"], end="\n\n")
    print("49: ", record["49 2024"], end="\n\n")
    print("50: ", record["50 2024"], end="\n\n")
    print("51: ", record["51 2024"], end="\n\n")
    print("52: ", record["52 2024"], end="\n\n")
    
    print("-"*80 + "\n"*2)

# last/next week_year
if False:
    assert(last_week_weekyear("46 2024") == "45 2024")
    assert(next_week_weekyear("46 2024") == "47 2024")
    
    week_year = "46 2024"
    assert(last_week_weekyear(next_week_weekyear(week_year)) == week_year)
    week_year = "1 2024"
    assert(last_week_weekyear(next_week_weekyear(week_year)) == week_year)
    week_year = "52 2024"
    assert(last_week_weekyear(next_week_weekyear(week_year)) == week_year)
    week_year = "1 2024"
    assert(next_week_weekyear(last_week_weekyear(week_year)) == week_year)
    week_year = "52 2024"
    assert(next_week_weekyear(last_week_weekyear(week_year)) == week_year)

    print("-"*80 + "\n"*2)    


if False:
    from datetime import date
    from app.date_utils import week_difference
    date2 = date(2024, 8, 5)
    for d in range(365):
        print( 
            f"{
                ", ".join(map(str, tuple(date.isocalendar(date2 + timedelta(d)))))
            } -- " +
            f"{str(date2 + timedelta(d))} -- " +
            f"{week_difference(date.today(), date2 + timedelta(d))}" 
        )

if False:
    from app.date_utils import last_week_weekyear, last_week_weekyear_DEPRECATED
    for n in range(2, 53):
        weekyear = f"{n} 2024"
        assert(
            f"{n - 1} 2024" ==
            last_week_weekyear_DEPRECATED(weekyear) ==
            last_week_weekyear(weekyear)
        )

TO = 6
schedules = "\n".join((record.str_weekyear(f"{n} 2025") for n in range(1, TO + 1)))
print(schedules)

from app.database import namelist_all, updated_namelist
namelist_all = updated_namelist(namelist_all, record, f"{TO} 2025", 999)
nl = ["Justin", "Sam", "Davide", "Saša", "Nil", "Hamna", "Hannah", "Isabelle", "Korina", "Evelin", "Adarsh", "Gregor", "Swastika", "Ismail", "Pati", "Jehanzeb", "Dongfang", "Marton"]
nl_t = {"Marton", "Dongfang", "Isabelle", "Sam", "Evelin", "Pati",}
for name in sorted(nl):
    if name in nl_t:
        print("\033[38;2;196;196;63m", end = '')
    print(
        f"{name:16} {schedules.count(name):4} {round(namelist_all[name])}",
        end='\033[0m\n'
    )