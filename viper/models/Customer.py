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
from . import Base

import uuid
from ..library.vuid import id_column, UUID

class Customer(Base):
	__tablename__ = 'Customers'
	Id = id_column()
	TenantId = Column(UUID(), nullable=False)
	SSN = Column(String, nullable=False)
	FirstName = Column(String)
	LastName = Column(String, nullable=True)
	Email = Column(String, nullable=True)
	Phone = Column(String, nullable=True)
	Mobile = Column(String, nullable=True)
	Address = Column(String, nullable=True)
	Address2 = Column(String, nullable=True)
	City = Column(String, nullable=True)
	Country = Column(String, nullable=True)
	Zipcode = Column(String, nullable=True)
	Picture = Column(String, nullable=True)
	CreatedBy = Column(String)
	CreatedOn = Column(DateTime)
	UpdatedBy = Column(String, nullable=True)
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
		return u"Customer(%s, %s, %s)" % (self.Id, self.SSN, self.FirstName)
	pass

