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

class Supplier(AuditMixin, Base):
	__tablename__ = 'Supplier'
	Id = id_column()
	TenantId = Column(UUID(), ForeignKey('TenantDetails.Id'), nullable=False, index=True)
	Name 		 = Column(Unicode(20), nullable=False, index=True)
	Description = Column(Unicode(255), nullable=False, index=True)
	Address 	 = Column(Unicode(255), nullable=False, index=True)

	Contacts = relationship('SupplierContactDetails', cascade="all, delete, delete-orphan")

	def __init__(self):
		self.CustomerNo = None
		pass

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

	def __repr__(self):
		return u"Supplier(%s, %s)" % (self.Id, self.Name)
	pass

from .ContactDetailsMixin import ContactDetailsMixin
class SupplierContactDetails(ContactDetailsMixin, Base):
	__tablename__ = 'SupplierContactDetails'
	SupplierId = Column(UUID(), ForeignKey('Supplier.Id'), nullable=False)

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

	def __repr__(self):
		return u"SupplierContact(%s)" % (str(self.toDict()))
	pass
