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
from sqlalchemy.orm import relationship

from .Supplier import Supplier
from datetime import datetime
from . import Base
from ..library.vuid import id_column, UUID
from .AuditMixin import AuditMixin

class Product(AuditMixin, Base):
	__tablename__ = 'Products'
	Id 			 = id_column()
	TenantId	 = Column(UUID(), ForeignKey('TenantDetails.Id'), nullable=False, index=True)
	Name 		 = Column(Unicode(50), index=True)
	Barcode 	 = Column(Unicode(20), index=True)
	MRP 		 = Column(Float)
	Discount 	 = Column(Float)
	BuyPrice 	 = Column(Float)
	SellPrice 	 = Column(Float)
	MfgDate 	 = Column(DateTime, nullable=True)
	ExpiryDate	 = Column(DateTime, nullable=True)
	SupplierId	 = Column(UUID(), ForeignKey('Supplier.Id'), nullable=True, index=True)
	CategoryId 	 = Column(Integer, nullable=True)
	TaxCategoryId = Column(Integer, nullable=True)
	Picture 	 = Column(String(255), nullable=True)

	Supplier 	 = relationship("Supplier")

	def __init__(self):
		self.Name = self.Barcode = ''
		self.MRP = self.BuyPrice = self.SellPrice = self.Discount = 0.0
		d = datetime.utcnow().date()
		self.MfgDate = d.strftime('%d-%m-%Y')
		self.ExpiryDate = d.replace(year=d.year + 1).strftime('%d-%m-%Y')
		pass

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

	def __repr__(self):
		return u"Product(%s, %s)" % (self.Id, self.Barcode)
	pass
