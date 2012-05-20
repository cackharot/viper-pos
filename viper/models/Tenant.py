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
from .User import User
import formalchemy

class Tenant(AuditMixin, Base):
	__label__	  = 'Tenant Details'
	__tablename__ = 'TenantDetails'
	Id            = id_column()
	Name          = Column(Unicode(50),index=True)
	Description   = Column(Unicode(255))
	Url           = Column(Unicode(255),index=True)
	Website       = Column(Unicode(255))
	AdminUserId   = Column(UUID(),ForeignKey('UserDetails.Id',use_alter=True,name='fk_tenant_user_id'),nullable=False)
	
	AdminUser	  = relationship("User",single_parent=True,primaryjoin=AdminUserId==User.Id, cascade="all, delete, delete-orphan")
	Contacts 	  = relationship("TenantContactDetails", cascade="all, delete, delete-orphan")

	def __init__(self):
		pass

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized
		
	def __repr__(self):
		return u"Tenant(%s, %s)" % (self.Id, self.Name)
	pass
	
from .ContactDetailsMixin import ContactDetailsMixin	
class TenantContactDetails(ContactDetailsMixin, Base):
	__tablename__ = 'TenantContactDetails'
	TenantId  = Column(UUID(), ForeignKey('TenantDetails.Id'), nullable=False)
	
	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized
	pass	
