#!/bin/bash

sudo apt-get update -y
sudo apt-get install vim python3-dev python3-setuptools -y

sudo easy_install3 pip

. /vagrant/vagrant_conf/run.sh
