from sqlalchemy import (
	Table,
	Column,
	Boolean,
	DateTime,
	Integer,
	Float,
	String,
	Unicode,
	MetaData,
	ForeignKey,
	)
from sqlalchemy.orm import relationship

from . import Base

import uuid
from ..library.vuid import id_column, UUID
from .AuditMixin import AuditMixin

class Customer(AuditMixin, Base):
	__tablename__ = 'Customers'
	Id = id_column()
	TenantId = Column(UUID(), ForeignKey('TenantDetails.Id'), nullable=False, index=True)
	CustomerNo = Column(String(20), index=True)

	Contacts = relationship('CustomerContactDetails', cascade="all, delete, delete-orphan")

	def __init__(self):
		self.CustomerNo = None
		pass

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		if self.Contacts and len(self.Contacts) > 0:
			serialized['Contact'] = self.Contacts[0].toDict()
			
		return serialized

	def __repr__(self):
		return u"Customer(%s, %s)" % (self.Id, self.CustomerNo)
	pass

from .ContactDetailsMixin import ContactDetailsMixin
class CustomerContactDetails(ContactDetailsMixin, Base):
	__tablename__ = 'CustomerContactDetails'
	CustomerId = Column(UUID(), ForeignKey('Customers.Id'), nullable=False)

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

	def __repr__(self):
		return u"CustomerContact(%s)" % (str(self.toDict()))
	pass
