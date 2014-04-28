#! /bin/bash

clear
echo "Starting script."

./manage.py dumpdata sessions > sessions.json

dropdb uniplanner_dev
createdb uniplanner_dev

./manage.py syncdb
./manage.py loaddata fb_user.json
./manage.py loaddata fb_testusers.json
./manage.py loaddata fb_testusers_incourses.json

./manage.py loaddata sessions.json

