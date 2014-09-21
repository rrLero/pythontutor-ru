#!/bin/bash

set -x

cd /vagrant/

sudo pkill -f "manage.py"

sudo pip3 install -v --log venv/install.log -r requirements.txt

cat vagrant_conf/db_admin_credentials.txt | python3 manage.py syncdb
python3 manage.py migrate tutorial
python3 manage.py collectstatic --noinput

python3 manage.py runserver 0.0.0.0:8042
