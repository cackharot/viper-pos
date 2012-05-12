import os
import sys
import transaction
import datetime
import random
import uuid

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Product,
    Customer,
    Order,
    LineItem,
    OrderPayment,
    User,
    Tenant,
    UserRoles,
    Base,
    )
    
TestTenantId = uuid.UUID('4f362af5-8657-41bc-a8c6-0166c46a4431')
TestUserId = str(uuid.UUID('895f05cf-7fd3-45a2-88d0-13fac7d567f1'))

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def getRand():
	return random.randint(1,12098)    

def Fixtures():
	with transaction.manager:
		pass
	pass

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    Fixtures()
    print('Done.')
    pass
