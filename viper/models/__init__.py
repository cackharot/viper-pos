from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
    
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


from .ContactDetailsMixin import ContactDetailsMixin

#from .Tenant import Tenant
#from .User import User
#from .Order import Order
#from .LineItem import LineItem
#from .Product import Product
#from .Customer import Customer
#from .OrderPayment import OrderPayment
#from .UserRoles import UserRoles, Role, RolePrivileges
