# e-doctor
Python Django 4 app e-doctor<br><br>

How to run ?

1. clone repository to local
2. docker compose up -d
3. change in settings.py (Allowed hosts and host in postgresql settings from localhost to db)
4. python manage.py makemigrations in web container
5. python manage.py migrate
   
Website with an appointment booking system, schedule of visits to two offices
