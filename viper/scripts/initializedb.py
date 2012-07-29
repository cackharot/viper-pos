import os
import sys
import transaction
from datetime import datetime
import random
import uuid

from sqlalchemy import engine_from_config, func

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
    TenantSetting,
    PrintTemplate,
    UserRoles,
    Base,
    )

from ..models.Purchase import Purchase
from ..models.PurchaseLineItem import PurchaseLineItem
from ..models.PurchasePayment import PurchasePayment

from ..library.helpers import EncryptPassword

TestTenantId = uuid.UUID('4f362af5865741bca8c60166c46a4431')
TestUserId = uuid.UUID('895f05cf7fd345a288d013fac7d567f1')
DefaultCustomerId = uuid.UUID('1dba743b516242108265dc0c12513b6c')
DefaultSupplierId = uuid.UUID('4b893117e6aa47b1a062cf6d471917a2')

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
			uc.UserId = TestUserId
			uc.FirstName = u'admin'
			uc.LastName = u'Company'
			uc.Mobile = '12323453'
			uc.Phone = '123435'
			uc.Address = 'Address'
			uc.City = 'City'
			uc.Country = 'Country'
			uc.Zipcode = '1233455'

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
			
		supplier = DBSession.query(Supplier.Supplier).get(DefaultSupplierId)
		if not supplier:
			supplier = Supplier.Supplier()
			supplier.Id = DefaultSupplierId
			supplier.TenantId = TestTenantId
			supplier.Name = 'Default'
			supplier.Description = 'Default Supplier'
			supplier.Address = 'Address'
			supplier.CreatedOn = datetime.utcnow()
			supplier.CreatedBy = u'admin'
			supplier.Status = True

			c = Supplier.SupplierContactDetails()
			c.SupplierId = DefaultSupplierId
			c.FirstName = u'Default'
			c.LastName = u'Supplier'
			c.Email = u'defaultsupplier@company.com'
			c.Mobile = u'987654321'
			c.Address = u'Address'
			c.City = u'Pondy'
			c.Country = u'India'
			c.Zipcode = '605001'

			supplier.Contacts.append(c)
			DBSession.add(supplier)

        ptmpl = DBSession.query(func.count(PrintTemplate.PrintTemplate.Id)).filter(PrintTemplate.PrintTemplate.Name==u'Sales Print Template').scalar()
        print('Template count: %s' % ptmpl)
        if ptmpl == 0:
            tpl = PrintTemplate.PrintTemplate()
            tpl.Id = uuid.uuid4()
            tpl.Name = u'Sales Print Template'
            tpl.TenantId = TestTenantId
            tpl.Status = 1
            tpl.Content = u"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>Order #<%=order.get('OrderNo') %></title>
<style>
/*@page {
            margin:0px;
            padding:0px;
            width:100%;
        }*/
@font-face {
    font-family: 'RupeeForadianRegular';
    src: url('/static/font/rupee_foradian-webfont.eot');
    src: url('/static/font/rupee_foradian-webfont.eot?#iefix')
        format('embedded-opentype'),
        url('/static/font/rupee_foradian-webfont.woff') format('woff'),
        url('/static/font/rupee_foradian-webfont.ttf') format('truetype'),
        url('/static/font/rupee_foradian-webfont.svg#RupeeForadianRegular')
        format('svg');
    font-weight: normal;
    font-style: normal;
}

.currency {
    font-family: "RupeeForadianRegular", 'rupi foradian';
}

.big {
    font-size: 16px;
}

body {
    font-size: 13px;
    margin: 0px auto;
    padding: 0px;
    color: #000;
    font-family: "Arial", Verdana;
}

h1,h2,h3,h4,h5,h6 {
    padding: 0px;
    margin: 0px;
}

h4 {
    font-size: 1.6em;
}

table {
    background-color: transparent;
    border-collapse: collapse;
    border-spacing: 0;
    width: 99.9%;
}

table tbody+tbody {
    border-top: 2px solid #dddddd;
}

.heading {
    text-align: center;
}

#pDebug,#pDebugToolbarHandle {
    display: none !important;
}

@media print {
    #pDebug,#pDebugToolbarHandle {
        display: none !important;
    }
}
</style>
</head>
<body>
    <div>
<% 
var paidAmt = Math.round(order.GetPaidAmount()).toFixed(2); 
var totalAmt = Math.round(order.GetTotalAmount()).toFixed(2); 
var balanceAmt = Math.round(order.GetBalanceAmount()).toFixed(2); 
var savingsAmt = Math.round(order.GetSavingsAmount()).toFixed(2);
%>
        <div class="heading">
            <h3>Sree Durga Home Needs Super Market</h3>
            <h5>#25, M.G.Road, Pondy-3. Ph: 2337517</h5>
            <h5>TIN: 34110014710</h5>
            <h5><%= ((balanceAmt > 0) ? 'Credit' : 'Cash') %> Bill</h5>
        </div>
        <table style="float: left;width:auto;">
            <tbody>
                <tr>
                    <td width="50px">Bill No#</td>
                    <td><b><%=order.get('OrderNo') %></b></td>
                </tr>
                <tr>
                    <td width="50px">Customer:</td>
                    <td><%=order.get('Customer').get('Contact').get('FirstName') || '' %></td>
                </tr>
            </tbody>
        </table>
        <table style="float: right;width:auto;">
            <tbody>
                <tr>
                    <td align="right" width="50px">Date:</td>
                    <td><%=$.format.date(ToLocalDate(order.get('OrderDate')),
                        'dd-MM-yyyy') %></td>
                </tr>
                <tr>
                    <td align="right" width="50px">Time:</td>
                    <td><%=$.format.date(ToLocalDate(order.get('OrderDate')),'hh:mm a') %></td>
                </tr>
            </tbody>
        </table>
        <div style="clear:both;"></div>
        <table>
            <thead>
                <tr
                    style="border-bottom: 1px solid black; border-top: 1px solid black;">
                    <th style="text-align: left;">Name</th>
                    <th style="text-align: right; width: 40px;">MRP</th>
                    <th style="text-align: right; width: 40px;">Price</th>
                    <th style="text-align: right; width: 25px;">Qty</th>
                    <th style="text-align: right; width: 40px;">Total</th>
                </tr>
            </thead>
            <tbody>
                <% order.get('LineItems').each(function(item) { %>
                <tr>
                    <td style="text-align: left; overflow: auto;"><%=
                        item.get('Name') %></td>
                    <td style="text-align: right;"><%= item.get('MRP').toFixed(2) %></td>
                    <td style="text-align: right;"><%= item.get('SellPrice').toFixed(2) %></td>
                    <td style="text-align: right;"><%= item.get('Quantity') %></td>
                    <td style="text-align: right;"><%=
                        item.get('Amount').toFixed(2) %></td>
                </tr>
                <% }); %>
                <tr style="border-top: 1px solid black;">
                    <td colspan="2" style="text-align: left;">Items/Qty:
                        <%= order.GetTotalItems() %>/<%=order.GetTotalQuantity() %></td>
                    <td colspan="2" style="text-align: right;"><h4>Total:</h4></td>
                    <td style="text-align: right;"><h4>
                            <span class="currency">`</span><%=totalAmt%>
                        </h4></td>
                </tr>
                <tr>
                    <td style="text-align: left;">Savings: <b><span
                            class="currency">`</span><%=savingsAmt%></b></td>
                    <td></td>
                    <td colspan="2" style="text-align: right;">Paid:</td>
                    <td style="text-align: right;"><span class="currency">`</span><%=paidAmt%></td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td colspan="2" style="text-align: right;"><%=(balanceAmt>0)?'Balance':'Change'%> :
                    </td>
                    <td style="text-align: right;"><span class="currency">`</span><%=balanceAmt%></td>
                </tr>
                <tr>
                    <td colspan="5" style="text-align: center;"><b><i>Thank    You! Visit Again!</i></b></td>
                </tr>
                <tr>
                    <td colspan="5" style="text-align: center;">Please AVOID CARRY BAGS!</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>"""
            print(u'Adding template to session...')
            DBSession.add(tpl)
            DBSession.flush()
            print(u'Flushed template to session...')
            transaction.manager.commit()
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
