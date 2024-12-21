
from app.database import schedule
from app.database import record
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
