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

class Order(Base):
	__tablename__ = 'Orders'
	Id = id_column()
	TenantId = Column(UUID(), nullable=False)
	OrderNo = Column(Integer)
	CustomerId = Column(String, nullable=True)
	OrderAmount = Column(Float,default=0)
	PaidAmount = Column(Float,default=0) 
	OrderDate = Column(DateTime)
	ShipDate = Column(DateTime, nullable=True)
	IpAddress = Column(String, nullable=True)
	CreatedBy = Column(String)
	CreatedOn = Column(DateTime)
	UpdatedBy = Column(String, nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status = Column(Boolean, default=True)		
	
	def __init__(self):
		self.Id = self.TenantId = self.CustomerId = None
		self.OrderNo = 0
		self.OrderAmount = self.PaidAmount = 0.0
		d = datetime.utcnow()
		self.OrderDate = d
		self.ShipDate = None
		self.IpAddress = '0.0.0.0'
		self.LineItems = None
		self.Payments = None
		pass

	def __repr__(self):
		return u"Order(%s, %s)" % (self.Id, self.OrderNo)
	pass

