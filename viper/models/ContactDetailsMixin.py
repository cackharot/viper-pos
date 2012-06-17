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
from sqlalchemy import func
from ..library.vuid import id_column, UUID

class ContactDetailsMixin(object):
	Id = id_column()
	Type 	 = Column(Unicode(20), nullable=False, index=True) #Primary,secondary,billing , etc.
	FirstName = Column(Unicode(20), nullable=False, index=True)
	LastName = Column(Unicode(20), nullable=True)
	Email = Column(Unicode(255), nullable=True, index=True)
	Phone = Column(String(20), nullable=True)
	Mobile = Column(String(20), nullable=False, index=True)
	Address = Column(Unicode(255), nullable=True)
	City = Column(Unicode(30), nullable=False)
	Country = Column(Unicode(30), nullable=False)
	Zipcode = Column(Unicode(10), nullable=False)
	Picture = Column(String(255), nullable=True)

	def __init__(self):
		self.Type = ''
		self.FirstName = ''
		self.LastName = ''
		self.Email = ''
		self.Phone = ''
		self.Mobile = ''
		self.Address = ''
		self.City = ''
		self.Country = ''
		self.Zipcode = ''
		self.Picture = None
		pass
	pass
