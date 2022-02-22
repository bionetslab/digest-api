#!/bin/bash
sleep 5
python3 manage.py makemigrations
python3 manage.py migrate #--run-syncdb
python3 manage.py setup_digest --check
#python3 manage.py migrate --run-syncdb
#python3 manage.py setup_db --refill
#bash import-data.sh

/usr/bin/supervisord -c "/etc/supervisor/conf.d/supervisord.conf"
