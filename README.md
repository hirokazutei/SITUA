# SITUA

## What is SITUA

SITUA stands for Structural Integrity Tracking Using Accelerometers. In essense, it is a website that helps anyone track the predominant period of a building. The change of the predominant period of a building are often good indicators of structural change, therefore, knowing the shifts in predominant frequency can tell us about the building's current SITUAtion.

## What is being tracked?

To track predominant period of the building, one would need two accelerometers, one situated at the basement, or ground level, and another at the top level of the building. When an earthquake occures, the accelerometer at the bottom measure the acceleration experienced at the ground level, and the accelerometer on top measures the acceleration experienced on the top. With data from both, the predominant period of the building can be derived.

## What is predominant period?

Things tends to like to shake in a certain way. If you get a plastic ruler and shake it back and forth, you will realize that it will wriggle at a certain pattern, that is the predominant period. The stiffer something is, the shorter the period. In otherwords, if the period begomes longer, the building may have become less stiff, which could indicate that something is damaged.

## Set-Up For Running Your Own Server Locally
### Database Set-Up
1. Update brew and install postgresql
~~~
$ brew update
$ brew install postgresql@9.5
~~~
2. Add postgresql to PATH
~~~
$ vim ~/.bashrc
write: export PATH="/usr/local/opt/postgresql@9.5/bin:$PATH"
$ Source ~/.bashrc
$ exec $SHELL -1
~~~
3. Create the databases
~~~
$ brew services start postgresql@9.5
-- psql
CREATE DATABASE UofT;
~~~

### Django Set-Up
Prerequisite:
* Python 3.6
* git

1. Clone the repository and move to the directory
~~~
$ git clone git@github.com:hirokazutei/SITUA.git
$ cd SITUA
~~~
2. Create a virtual environment and activate it
~~~
$ python3 -m venv venv
$ . venv/bin/activate
~~~
3. Make migrations and migrate
~~~
python manage.py makemigrations
python manage.py migrate
~~~
4. Create superuser to access database
~~~
python manage.py createsuperuser
~~~
5. Run the server
~~~
python manage.py runserver
~~~
6. The app is now available locally [HERE: http://127.0.0.1:8000/tracker/](http://127.0.0.1:8000/tracker/)
7. The admin page can be accessed [HERE: http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
