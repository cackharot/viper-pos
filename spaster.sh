#!/bin/sh
../bin/paster serve --daemon --pid-file=paster_5000.pid production.ini http_port=5000
../bin/paster serve --daemon --pid-file=paster_5001.pid production.ini http_port=5001
