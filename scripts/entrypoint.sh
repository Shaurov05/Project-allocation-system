#! /bin/sh

# if it faces any error during running, it will immediately exit
set -e

# this is to collec all the static files and store them in the static root
# django documentation suggested a proxy support to serve static files because
# proxy servers (Nginx/ Apache) serve static files efficiently
python manage.py collecstatic --noinput

# command that run our application using uwsgi. It start the django project
# running in the wsgi server
uwsgi --socket :8000 --master --enable-threads --module app.wsgi

