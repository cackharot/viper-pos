from sqlalchemy import (
	Column,
	Boolean,
	DateTime,
	String,
	)

from sqlalchemy import func

class AuditMixin(object):
	CreatedBy = Column(String(50), nullable=False)
	CreatedOn = Column(DateTime, nullable=False, default=func.now())
	UpdatedBy = Column(String(50), nullable=True)
	UpdatedOn = Column(DateTime, nullable=True)
	Status    = Column(Boolean, nullable=False, default=True)
	pass
