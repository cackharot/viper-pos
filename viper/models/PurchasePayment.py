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

class PurchasePayment(AuditMixin, Base):
	__tablename__ 	 = 'PurchasePayments'
	Id 				 = id_column()
	PurchaseId 		 = Column(UUID(), ForeignKey('Purchases.Id'), nullable=False)
	PaymentDate		 = Column(DateTime, nullable=True)
	PaymentType		 = Column(Unicode(10) , default=u'Cash')
	PaidAmount  	 = Column(Float, default=0.0)

	def __init__(self):
		self.Id = self.PurchaseId = None
		self.PaidAmount = 0.0
		self.PaymentType = u'Cash'
		d = datetime.utcnow()
		self.PaymentDate = d
		self.CreatedOn = d
		self.Status = True
		pass

	def toDict(self):
		serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
		return serialized

