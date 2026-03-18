#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
apt-get update && apt-get install -y libgl1
python manage.py collectstatic --noinput
python manage.py migrate
