Provides links and ratings for YKnytt game.

## How to setup

### Postgres
create database knyttlevels; \
create user ykuser with encrypted password '000000'; \
grant all privileges on database knyttlevels to ykuser;

### Python
Create and enter virtualenv if needed \
pip install -r requirements.txt \
python manage.py migrate \
python manage.py createsuperuser

### Run
python manage.py runserver

### Import levels
Generate worlds.csv with yknytt-parser/worlds-parse \
python manage.py importcsv worlds.csv \
(to update old levels: python manage.py importcsv worlds.csv --update)

### Setup and run on Heroku
See https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment \
Install Heroku CLI and add its remote repository \
git push heroku master \
heroku run python manage.py migrate \
heroku run python manage.py createsuperuser

### Import levels on Heroku
git push heroku master \
heroku run python manage.py importcsv worlds.csv
