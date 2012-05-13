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

class Product(Base):
	__tablename__ = 'Products'
	Id = id_column()
	TenantId = Column(UUID(), ForeignKey('TenantDetails.Id'), nullable=False,index=True)
	Name = Column(Unicode(50),index=True)
	Barcode = Column(String(20),index=True)
	MRP = Column(Float)
	Discount = Column(Float)
	BuyPrice = Column(Float)
	SellPrice = Column(Float)
	MfgDate = Column(DateTime, nullable=True)
	ExpiryDate = Column(DateTime, nullable=True)
	CategoryId = Column(Integer, nullable=True)
	TaxCategoryId = Column(Integer, nullable=True)
	Picture = Column(String(255), nullable=True)
	CreatedBy = Column(String(50))
	CreatedOn = Column(DateTime)
	UpdatedBy = Column(String(50), nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status = Column(Boolean, default=True)
		
	
	def __init__(self):
		self.Name = self.Barcode = ''
		self.MRP = self.BuyPrice = self.SellPrice = self.Discount = 0
		d = datetime.utcnow()
		self.MfgDate = d
		self.ExpiryDate = d.replace(year=d.year+1)
		pass
	
	def toJSON(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		import json
		from ..library.helpers import jsonHandler
		return json.dumps(serialized,default=jsonHandler)

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized
		
	def __repr__(self):
		return u"Product(%s, %s)" % (self.Id, self.Barcode)
	pass
