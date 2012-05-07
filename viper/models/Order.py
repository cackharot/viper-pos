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
from ..library.helpers import jsonHandler

class Order(Base):
	__tablename__ = 'Orders'
	Id = id_column()
	TenantId = Column(UUID(), nullable=False,index=True)
	OrderNo = Column(Integer,index=True)
	CustomerId = Column(String(50), nullable=True)
	OrderAmount = Column(Float,default=0)
	PaidAmount = Column(Float,default=0) 
	OrderDate = Column(DateTime)
	ShipDate = Column(DateTime, nullable=True)
	IpAddress = Column(String(30), nullable=True)
	CreatedBy = Column(String(50))
	CreatedOn = Column(DateTime)
	UpdatedBy = Column(String(50), nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status = Column(Boolean, default=True)		
	
	def __init__(self):
		self.Id = self.TenantId = self.CustomerId = None
		self.CustomerName = None
		self.OrderNo = 0
		self.OrderAmount = self.PaidAmount = 0.0
		d = datetime.utcnow()
		self.OrderDate = d
		self.ShipDate = None
		self.IpAddress = '0.0.0.0'
		self.LineItems = None
		self.Payments = None
		pass
		
	def toJSON(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		if hasattr(self,'CustomerName'): serialized['CustomerName']=self.CustomerName 
		else: serialized['CustomerName']=None
		import json
		return json.dumps(serialized,default=jsonHandler)

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name)) for column_name in self.__table__.c.keys())
		if hasattr(self,'CustomerName'): serialized['CustomerName']=self.CustomerName 
		else: serialized['CustomerName']=None
		return serialized
        
	def __repr__(self):
		return u"Order(%s, %s)" % (self.Id, self.OrderNo)
	pass

class OrderSearchParam(object):
	def __init__(self):
		self.TenantId = None
		self.OrderId = None
		self.OrderNo = None
		self.CustomerId = None
		self.CustomerName = None
		self.FromOrderDate = None
		self.ToOrderDate = None
		self.UserId = None
		self.PageNo = None
		self.PageSize = None
		self.IpAddress = None
		self.MinAmount = None
		self.MaxAmount = None
	pass
