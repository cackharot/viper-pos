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
from datetime import datetime
from . import Base
from ..library.vuid import id_column, UUID
from .AuditMixin import AuditMixin
from sqlalchemy.orm import relationship

from .PurchaseLineItem import PurchaseLineItem
from .PurchasePayment import PurchasePayment

class Purchase(AuditMixin,Base):
	__tablename__	= 'Purchases'
	Id 				= id_column()
	TenantId 		= Column(UUID(),ForeignKey('TenantDetails.Id'), nullable=False,index=True)
	PurchaseNo 		= Column(Integer,index=True)
	SupplierId 		= Column(UUID(),ForeignKey('Supplier.Id'), nullable=False)
	PurchaseAmount 	= Column(Float,default=0)
	PaidAmount 		= Column(Float,default=0) 
	PurchaseDate 	= Column(DateTime,nullable=False)
	
	Supplier		= relationship("Supplier")
	LineItems		= relationship("PurchaseLineItem", cascade="all, delete, delete-orphan")
	Payments		= relationship("PurchasePayment", cascade="all, delete, delete-orphan")
	
	def __init__(self):
		self.Id = self.TenantId = self.SupplierId = None
		self.SupplierName = None
		self.PurchaseNo = None
		self.PurchaseAmount = self.PaidAmount = 0.0
		d = datetime.utcnow()
		self.PurchaseDate = d.strftime('%d-%m-%Y')
		self.CreatedOn = d
		self.LineItems = []
		self.Payments = []
		self.Status = True
		pass
	
	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name)) for column_name in self.__table__.c.keys())
		if hasattr(self,'SupplierName'): serialized['SupplierName']=self.SupplierName 
		else: serialized['SupplierName']=None
		return serialized
	
	def __repr__(self):
		return u"Purchase(%s, %s)" % (self.Id, self.PurchaseNo)

class PurchaseSearchParam(object):
	def __init__(self):
		self.TenantId = None
		self.PurchaseId = None
		self.PurchaseNo = None
		self.SupplierId = None
		self.SupplierName = None
		self.FromPurchaseDate = None
		self.ToPurchaseDate = None
		self.UserId = None
		self.PageNo = None
		self.PageSize = None
		self.MinAmount = None
		self.MaxAmount = None
	pass
