
from app.database import schedule
from app.database import record
from app.date_utils import str_last_week_year, str_next_week_year

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
if True:
    assert(str_last_week_year("46 2024") == "45 2024")
    assert(str_next_week_year("46 2024") == "47 2024")
    
    week_year = "46 2024"
    assert(str_last_week_year(str_next_week_year(week_year)) == week_year)
    week_year = "1 2024"
    assert(str_last_week_year(str_next_week_year(week_year)) == week_year)
    week_year = "52 2024"
    assert(str_last_week_year(str_next_week_year(week_year)) == week_year)
    week_year = "1 2024"
    assert(str_next_week_year(str_last_week_year(week_year)) == week_year)
    week_year = "52 2024"
    assert(str_next_week_year(str_last_week_year(week_year)) == week_year)

    print("-"*80 + "\n"*2)    
