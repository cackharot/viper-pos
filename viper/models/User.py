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

class User(Base):
	__tablename__ = 'UserDetails'
	Id        = id_column()
	TenantId  = Column(None, ForeignKey('TenantDetails.Id'), nullable=False)
	UserName  = Column(String(50), nullable=False,index=True)
	Password  = Column(String(50), nullable=False)
	FirstName = Column(String(20), nullable=False)
	LastName  = Column(String(20), nullable=True)
	Email     = Column(String(255), nullable=True,index=True)
	Phone     = Column(String(20), nullable=True)
	Mobile    = Column(String(20), nullable=True)
	Address   = Column(String(200), nullable=True)
	Address1  = Column(String(255), nullable=True)
	City      = Column(String(30), nullable=False)
	Country   = Column(String(30), nullable=False)
	Zipcode   = Column(String(10), nullable=False)
	CreatedBy = Column(String(50), nullable=False)
	CreatedOn = Column(DateTime, nullable=False)
	UpdatedBy = Column(String(50), nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status    = Column(Boolean, nullable=False, default=True)
		
	
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
