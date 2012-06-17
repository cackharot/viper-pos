import os
import sys
import transaction
from datetime import datetime
import random
import uuid, sha

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Product,
    Customer,
    Supplier,
    Order,
    LineItem,
    OrderPayment,
    User,
    Tenant,
    UserRoles,
    Base,
    )

from ..models.Purchase import Purchase
from ..models.PurchaseLineItem import PurchaseLineItem
from ..models.PurchasePayment import PurchasePayment

from ..library.helpers import EncryptPassword

TestTenantId = uuid.UUID('4f362af5-8657-41bc-a8c6-0166c46a4431')
TestUserId = uuid.UUID('895f05cf-7fd3-45a2-88d0-13fac7d567f1')
DefaultCustomerId = uuid.UUID('1dba743b516242108265dc0c12513b6c')

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def getRand():
	return random.randint(1, 12098)

def Fixtures():
	with transaction.manager:
		tmp = DBSession.query(Purchase).count()
		print('Purchase Count: %s' % tmp)
		t = DBSession.query(Tenant.Tenant).get(TestTenantId)
		if not t:
			t = Tenant.Tenant()
			t.Id = TestTenantId
			t.Name = u'Company'
			t.Description = u'Master Tenant'
			t.Url = u'http://company.viperpos.in'
			t.Website = u'http://viperpos.in'
			t.CreatedBy = u'Admin'
			t.CreatedOn = datetime.utcnow()
			t.Status = True

			u = User.User()
			u.Id = TestUserId
			u.TenantId = t.Id
			u.UserName = u'admin'
			u.Password = EncryptPassword('company')
			u.CreatedBy = u'Admin'
			u.CreatedOn = datetime.utcnow()
			u.Status = True

			uc = User.UserContactDetails()
			u.UserId = TestUserId
			u.FirstName = u'admin'
			u.LastName = u'Company'
			u.Mobile = '12323453'
			u.Phone = '123435'
			u.Address = 'Address'
			u.City = 'City'
			u.Country = 'Country'
			u.Zipcode = '1233455'

			c = Tenant.TenantContactDetails()
			c.TenantId = t.Id
			c.FirstName = u'admin'
			c.LastName = u'company'
			c.Email = u'admin@company.com'
			c.Mobile = u'987654321'
			c.Address = u'Address'
			c.City = u'Pondy'
			c.Country = u'India'
			c.Zipcode = '605003'

			t.AdminUser = u
			t.Contacts.append(c)

			DBSession.add(t)

		r = DBSession.query(UserRoles.Role).get('GR$Product_Admin')
		if not r:
			r = UserRoles.Role()
			r.TenantId = t.Id
			r.Id = u'GR$Product_Admin'
			r.Name = u'Product Admin'
			r.Description = u'Product administrator role.'

			DBSession.add(r)

		ur = DBSession.query(UserRoles.UserRoles).filter(UserRoles.UserRoles.UserId == TestUserId).all()
		if not ur or len(ur) <= 0:
			ur = UserRoles.UserRoles()
			ur.UserId = u.Id
			ur.RoleId = r.Id

			DBSession.add(ur)

		cus = DBSession.query(Customer.Customer).get(DefaultCustomerId)
		if not cus:
			cus = Customer.Customer()
			cus.Id = DefaultCustomerId
			cus.TenantId = TestTenantId
			cus.CustomerNo = 1
			cus.CreatedOn = datetime.utcnow()
			cus.CreatedBy = u'admin'
			cus.Status = True

			c = Customer.CustomerContactDetails()
			c.CustomerId = DefaultCustomerId
			c.FirstName = u'Default'
			c.LastName = u'default'
			c.Email = u'default@company.com'
			c.Mobile = u'987654321'
			c.Address = u'Address'
			c.City = u'Pondy'
			c.Country = u'India'
			c.Zipcode = '605001'

			cus.Contacts.append(c)
			DBSession.add(cus)
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
