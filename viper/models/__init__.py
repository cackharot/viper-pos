from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


#from .ContactDetailsMixin import ContactDetailsMixin

#from .Tenant import Tenant, TenantContactDetails
#from .User import User, UserContactDetails
#from .Order import Order
#from .LineItem import LineItem
#from .Product import Product
#from .Customer import Customer, CustomerContactDetails
#from .Supplier import Supplier, SupplierContactDetails
#from .OrderPayment import OrderPayment
#from .UserRoles import UserRoles, Role, RolePrivileges
#from .Purchase import Purchase, PurchaseLineItem, PurchasePayment
