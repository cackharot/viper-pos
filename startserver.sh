#!/bin/sh
rm -f uwsgi.log
../bin/uwsgi --ini-paste production.ini
