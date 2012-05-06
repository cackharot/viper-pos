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
	Unicode
	)
from . import Base

import uuid
from ..library.vuid import id_column, UUID

class Customer(Base):
	__tablename__ = 'Customers'
	Id = id_column()
	TenantId = Column(UUID(), nullable=False,index=True)
	FirstName = Column(Unicode(50),index=True)
	LastName = Column(Unicode(50), nullable=True)
	Email = Column(String(255), nullable=True,index=True)
	Phone = Column(String(20), nullable=True)
	Mobile = Column(String(15), nullable=True)
	Address = Column(Unicode(250), nullable=True)
	Address2 = Column(Unicode(255), nullable=True)
	City = Column(Unicode(80), nullable=True)
	Country = Column(Unicode(80), nullable=True)
	Zipcode = Column(String(10), nullable=True)
	Picture = Column(String(255), nullable=True)
	CreatedBy = Column(String(50))
	CreatedOn = Column(DateTime)
	UpdatedBy = Column(String(50), nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status = Column(Boolean, default=True)
	
	
	def __init__(self):
		self.FirstName = ''
		self.LastName = ''
		self.Email = ''
		self.Phone = ''
		self.Mobile = ''
		self.Address = ''
		self.City = ''
		self.Country = ''
		pass

	def __repr__(self):
		return u"Customer(%s, %s)" % (self.Id, self.FirstName)
	pass

