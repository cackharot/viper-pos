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

class Product(Base):
	__tablename__ = 'Products'
	Id = id_column()
	TenantId = Column(UUID(), nullable=False)
	Name = Column(String)
	Barcode = Column(String)
	MRP = Column(Float)
	Discount = Column(Float)
	BuyPrice = Column(Float)
	SellPrice = Column(Float)
	MfgDate = Column(DateTime, nullable=True)
	ExpiryDate = Column(DateTime, nullable=True)
	CategoryId = Column(Integer, nullable=True)
	TaxCategoryId = Column(Integer, nullable=True)
	Picture = Column(String, nullable=True)
	CreatedBy = Column(String)
	CreatedOn = Column(DateTime)
	UpdatedBy = Column(String, nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status = Column(Boolean, default=True)
		
	
	def __init__(self):
		self.Name = self.Barcode = ''
		self.MRP = self.BuyPrice = self.SellPrice = self.Discount = 0
		d = datetime.utcnow()
		self.MfgDate = d
		self.ExpiryDate = d.replace(year=d.year+1)
		pass

	def __repr__(self):
		return u"Product(%s, %s)" % (self.Id, self.Barcode)
	pass

