import app.database
from app.database import Schedule, schedule
from app.database import Record, record

# Schedule.add_task, Schedule[week_year]
if True:
    print("46: ", schedule["46 2024"], end="\n\n")
    print("47: ", schedule["47 2024"], end="\n\n")
    print("48: ", schedule["48 2024"], end="\n\n")
    print("49: ", schedule["49 2024"], end="\n\n")
    print("50: ", schedule["50 2024"], end="\n\n")
    print("51: ", schedule["51 2024"], end="\n\n")
    print("52: ", schedule["52 2024"], end="\n\n")

    print("-"*80 + "\n"*2)

# Record
if True:
    record.strip_data()
    print("46: ", record["46 2024"], end="\n\n")
    print("47: ", record["47 2024"], end="\n\n")
    print("48: ", record["48 2024"], end="\n\n")
    print("49: ", record["49 2024"], end="\n\n")
    print("50: ", record["50 2024"], end="\n\n")
    print("51: ", record["51 2024"], end="\n\n")
    print("52: ", record["52 2024"], end="\n\n")
    record.write()
    print("-"*80 + "\n"*2)
