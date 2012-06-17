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

class LineItem(Base):
	__tablename__ = 'LineItems'
	Id = id_column()
	OrderId = Column(UUID(), nullable=False)
	ProductId = Column(UUID(), nullable=True)
	Barcode = Column(String(20), nullable=False)
	Name = Column(Unicode(50), nullable=False)
	MRP = Column(Float, default=0.0)
	Discount = Column(Float, default=0.0)
	SellPrice = Column(Float, default=0.0)
	Quantity = Column(Float, default=0.0)

	def __init__(self):
		self.Id = self.OrderId = self.ProductId = None
		self.Name = self.Barcode = ''
		self.MRP = self.Discount = self.SellPrice = 0.0
		self.Quantity = 0.0
		pass

	@property
	def Amount(self):
		return round(self.SellPrice * self.Quantity)

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

	def __repr__(self):
		return u"LineItem(%s, %s)" % (self.Id, self.Name)
	pass

