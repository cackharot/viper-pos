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

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
    	p = Product.Product()
    	p.TenantId = TestTenantId
    	p.Barcode = '1234%s' % getRand()
    	p.Name = 'Test Item %s' % getRand()
    	p.MRP = 10.0
    	p.BuyPrice = 9.00
    	p.SellPrice = 9.50
    	p.Discount = 0.0
    	p.CreatedBy = TestUserId
    	p.CreatedOn = datetime.datetime.utcnow()
    	p.Status = 1
    	
    	c = Customer.Customer()
    	c.TenantId = TestTenantId
    	c.SSN = getRand()
    	c.FirstName = 'Customer%s' % getRand()
    	c.Email = c.FirstName + '@test.com'
    	c.Mobile = '9876543210'
    	c.Phone = '654321'
    	c.Country = 'India'
    	c.City = 'TN'
    	c.CreatedBy = TestUserId
    	c.CreatedOn = datetime.datetime.utcnow()
    	c.Status = 1
    	
    	DBSession.add(p)
    	DBSession.add(c)
    print('Done.')
    pass
