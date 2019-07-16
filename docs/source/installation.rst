Installation
============

Preparation
^^^^^^^^^^^
Depending on your specific installation, you'll likely want a virtual environment. Create one for PadLock with this command (where 'python3' is your python3 interpreter and 'padlock' is the name of your virutal environment): virtualenv -p python3 padlock. Next, install all the requirement in the requirements.txt file with the following: pip install -r requirements.txt.


Installation
^^^^^^^^^^^^


Setup
^^^^^
From the PadLock root directory simply run python manage.py runmigrations to create required table entries in your database.
As with any django project, once installed, you'll need to run mgrations and create at least one superuser.
Run the migrate command to run migrations:
python manage.py migrate
Create a superuser with the following commands and follow the prompts:
python manage.py createsuperuser
Run python manage.py runserver to launch the demo server.




