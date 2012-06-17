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

from datetime import datetime
from . import Base
from ..library.vuid import id_column, UUID
from .AuditMixin import AuditMixin

class User(AuditMixin, Base):
	__tablename__ = 'UserDetails'
	Id = id_column()
	TenantId = Column(UUID(), nullable=True)
	UserName = Column(Unicode(50), nullable=False, index=True)
	Password = Column(Unicode(50), nullable=False)

	Contacts = relationship("UserContactDetails", cascade="all, delete, delete-orphan")

	def __init__(self):
		self.Name = None
		self.Password = None
		pass

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

	def __repr__(self):
		return u"User(%s, %s)" % (self.Id, self.UserName)
	pass

from .ContactDetailsMixin import ContactDetailsMixin
class UserContactDetails(ContactDetailsMixin, Base):
	__tablename__ = 'UserContactDetails'
	UserId = Column(UUID(), ForeignKey('UserDetails.Id'), nullable=False)

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized
	pass
