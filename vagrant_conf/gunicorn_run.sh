#!/bin/bash
 
NAME="pythontutor"                                  # Name of the application
DJANGODIR=/vagrant/             # Django project directory
SOCKET=127.0.0.1:9000
# SOCKFILE=/webapps/hello_django/run/gunicorn.sock  # we will communicte using this unix socket
USER=root                                        # the user to run as
GROUP=root                                     # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=$NAME.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=$NAME.wsgi                     # WSGI module name
 
echo "Starting $NAME as `whoami`"
 
# Activate the virtual environment
cd $DJANGODIR
source $DJANGODIR/venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
 
cat vagrant_conf/db_admin_credentials.txt | python3 manage.py syncdb
python3 manage.py migrate tutorial
python3 manage.py collectstatic --noinput

# Create the run directory if it doesn't exist
# RUNDIR=$(dirname $SOCKFILE)
# test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --bind 0.0.0.0:9000
#  --bind=unix:$SOCKFILE
