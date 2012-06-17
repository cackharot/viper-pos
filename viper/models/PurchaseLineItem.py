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

class PurchaseLineItem(Base):
	"""
		Purchased line items details entity
	"""
	__tablename__ 	 = 'PurchaseLineItems'
	Id 				 = id_column()
	PurchaseId 		 = Column(UUID(), ForeignKey('Purchases.Id'), nullable=False)
	ProductId 		 = Column(UUID(), nullable=True)
	Barcode 		 = Column(String(20), nullable=False)
	Name 			 = Column(Unicode(50), nullable=False)
	MRP 			 = Column(Float, nullable=False, default=0.0)
	Tax 			 = Column(Float, nullable=False, default=0.0)
	Discount		 = Column(Float, nullable=False, default=0.0)
	BuyPrice 		 = Column(Float, nullable=False, default=0.0)
	Quantity 		 = Column(Float, nullable=False, default=0.0)

	def __init__(self):
		self.Id = self.PurchaseId = self.ProductId = None
		self.Name = self.Barcode = ''
		self.MRP = self.BuyPrice = 0.0
		self.Discount = 0.0
		self.Quantity = 0.0
		self.Status = True
		pass

	@property
	def BuyAmount(self):
		return round(self.BuyPrice * self.Quantity)

	@property
	def Amount(self):
		return round(self.MRP * self.Quantity)

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

