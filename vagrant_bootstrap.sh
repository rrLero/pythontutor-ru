#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y python3 python-virtualenv
cd /vagrant
virtualenv -p python3 venv
source venv/bin/activate
which python3
which pip
pip install -r requirements.txt

# export PYTHONPATH=/vagrant/
python3 manage.py syncdb
python3 manage.py migrate tutorial
python3 manage.py runserver 0.0.0.0:8000
