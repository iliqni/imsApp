# imsApp
Inventory and Order managemnt in Python/Django done for Galileia 2020 Ltd.

This app was made for the needs of my wife's advertising agency as a learning project.
You are free to use it if you want but no support will be given.

Follow these instructions to run it locally.

For Linux

Run terminal in the app folder and execute the following commands:

pip install virtualenv

virtualenv env

source env/bin/activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

For Windows pretty much the same..

pip install virtualenv

virtualenv env

cd env/Scripts

activate

cd ../..

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
