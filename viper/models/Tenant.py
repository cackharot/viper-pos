from sqlalchemy import (
	Table, 
	Column, 
	Boolean, 
	DateTime, 
	Integer, 
	Float, 
	String, 
	MetaData, 
	ForeignKey,
	)
from datetime import datetime 	
from . import Base
from ..library.vuid import id_column, UUID

class Tenant(Base):
	__tablename__ = 'TenantDetails'
	Id            = id_column()
	Name          = Column(String(50),index=True)
	Description   = Column(String(255))
	Url           = Column(String(255),index=True)
	Website       = Column(String(255))
	AdminUserId   = Column(UUID(),nullable=True)
	BillingUserId = Column(UUID(),nullable=True)
	CreatedBy = Column(String(50))
	CreatedOn = Column(DateTime)
	UpdatedBy = Column(String(50), nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status    = Column(Boolean, default=True)		
	
	def __init__(self):
		self.Name = None
		self.Password = None
		pass

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized
		
	def __repr__(self):
		return u"User(%s, %s)" % (self.Id, self.Name)
	pass
