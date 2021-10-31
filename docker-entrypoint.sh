#!/bin/bash

python3 manage.py migrate --run-syncdb
python3 manage.py filldb --test 5
#python3 manage.py createfixtures
#python3 manage.py cleanuptasks
bash import-data.sh

/usr/bin/supervisord -c "/etc/supervisor/conf.d/supervisord.conf"
