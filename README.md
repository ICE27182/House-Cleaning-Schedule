# House-Cleaning-Schedule
A scheduling website written in html, css and python. It can automatically assign tasks to different person based on past records, show the schedules in a web page and allow people to update the records by interacting with the webpage. It mainly focuses on weekly tasks but tasks with different periods also possible to add.

# How to run?
Python version: 3.13+ (maybe lower version will also work, but I didn't test them)  
Library needed: flask

Because it is more of a final product than a framework, and I have excluded a few files for privacy reasons, you cannot run it right away.

To be able to run it, you can simply add two files: ```namelist.txt``` and ```namelist_toilet.txt```, in which you need to put a few names inside separated by whitespace.  
Note that names starting with ```#``` will be ignored.

For example:  

```namelist.txt```:  
```
N54 WNS    SovOil  Petrochem
Tsunami-Defense-Systems  SegAtari
#Sycust   Raven-Microcyberetics   
```
(Sycust will be ignored)
```namelist_toilet.txt```:  
```
Arasaka   Militech  
Kang-Tao #Zetatech #Lazarus  Biotechnica 
Night-Corp Mitsubishi-Sugo  Kiroshi-Optics

```
(Zetatech and Lazarus will be ignored)

I have also deleted all images, which should not prevent the website from running.

```python3 run.py``` or ```python run.py``` will start the web application. 
You can visit the website by directly typing ```localhost``` in your web browser.

# How can I modify the code to fit my use?
- Change ```namelist.py``` to read from different files
- Change tasks added in ```database.py``` and 
- Change ```more_info.py``` so it covers the task changes above. Also, remember to update the corresponing ```html```files in ```/app/templates/cleaning_schedules/``` if necessary
- Add images at ```/app/static/images/```.
