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

class AuditMixin(object):
	CreatedBy = Column(String(50), nullable=False,default=func.now())
	CreatedOn = Column(DateTime, nullable=False)
	UpdatedBy = Column(String(50), nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status    = Column(Boolean, nullable=False, default=True)
	pass
