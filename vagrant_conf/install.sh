#!/bin/bash

sudo apt-get update -y
sudo apt-get install vim python-virtualenv python3-dev python3-setuptools -y

sudo easy_install3 pip

# Create sandbox for evaldontevil interpreter.
sudo adduser pythontutor-sandbox --gecos "" --disabled-password
sudo mkdir /srv
sudo virtualenv -p python3 /srv/evaldontevil-python

. /vagrant/vagrant_conf/run.sh
