import os
import sys
import transaction
from datetime import datetime
import random
import uuid,sha

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
from ..library.helpers import EncryptPassword
    
TestTenantId = uuid.UUID('4f362af5-8657-41bc-a8c6-0166c46a4431')
TestUserId = uuid.UUID('895f05cf-7fd3-45a2-88d0-13fac7d567f1')

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def getRand():
	return random.randint(1,12098)    

def Fixtures():
	with transaction.manager:
		t = Tenant.Tenant()
		t.Id = TestTenantId
		t.Name = 'Company'
		t.Description = 'Master Tenant'
		t.Url = 'http://company.viperpos.in'
		t.Website = 'http://viperpos.in'
		t.CreatedBy = 'Admin'
		t.CreatedOn = datetime.utcnow()
		t.Status = True
		
		DBSession.add(t)
		DBSession.flush()
				
		u = User.User()
		u.Id = TestUserId
		u.TenantId = t.Id
		u.UserName = 'admin'
		u.Password = EncryptPassword('company')
		u.FirstName= 'admin'
		u.LastName = 'company'
		u.Email    = 'admin@company.com'
		u.Mobile   = '987654321'
		u.Address  = 'Address'
		u.City     = 'Pondy'
		u.Country  = 'India'
		u.Zipcode  = '605003'
		u.CreatedBy = 'Admin'
		u.CreatedOn = datetime.utcnow()
		u.Status = True
		
		DBSession.add(u)
		DBSession.flush()
		
		t.AdminUserId = u.Id
		t.BillingUserId = u.Id
		
		DBSession.flush()
		
		r = UserRoles.Role()
		r.Id   = 'GR$Product_Admin'
		r.Name = 'Product Admin'
		r.Description = 'Product administrator role.'
		
		DBSession.add(r)
		
		ur = UserRoles.UserRoles()
		ur.UserId = u.Id
		ur.RoleId = r.Id
		
		DBSession.add(ur)
		DBSession.flush()
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
