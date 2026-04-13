# House-Cleaning-Schedule
A scheduling website written in html, css and python. 

It can automatically and randomly assign chores to different persons balanced by past records, show the schedules web pages and allow people to update the records by interacting with the webpage. 

It mainly focuses on weekly chores but chores with longer periods are also supported.
However, it is less suitable for chores with much shorter periods such as a daily chore.

# How to run?
Python version: 3.13+ 
Library needed: Flask 3.1.0+
Lower version may also work, but I did not test in lower versions.

In order to run the project, you also need to manually add 
an empty `record.json` (an empty dictionary will suffice) 
and a list of strings stored in `namelist.json`,
which I cannot include due to privacy reasons.

You may also modify the namelists specified in chores.json.

Just for illustration purpose, you can simply use `unittests/namelist.json`.

You may need to change the path used in `chores.json`.

`python3 run.py` or `python run.py` will start the web application. 
You can visit the website by directly typing `localhost` in your web browser.

# How can I modify the code to fit my use?
- Modify `chores.json`. To use other file names and paths, goto `app/app.py`.
- Modify or add `namelist.json`. 
  You can have multiple name lists for different purposes
- Modify `record.json`.
- Modify auto-generated more_info pages at `app/templates/more_info/`. 
  Note that they will only be auto-generated when the correspoding page
  is visited and the html file does not exists.
- Add photos and images.
- Modify the code :D
