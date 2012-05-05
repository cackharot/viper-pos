#!/bin/sh
rm -f uwsgi.log
../bin/uwsgi --ini-paste-logged development.ini
