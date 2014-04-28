#! /bin/bash

dropdb uniplanner_dev
createdb uniplanner_dev

./manage.py syncdb