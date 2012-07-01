from sqlalchemy import (
    Column,
    Boolean,
    Unicode,
    ForeignKey,
    )

from . import Base
from ..library.vuid import id_column, UUID

class TenantSetting(Base):
    '''
    Tenant Setting class
    '''
    __tablename__   = 'TenantSetting'
    Id              = id_column()
    TenantId        = Column(UUID(), ForeignKey('TenantDetails.Id'), nullable=False)
    AttributeName   = Column(Unicode(50), index=True, nullable=False)
    AttributeValue  = Column(Unicode(50), nullable=True)
    Status          = Column(Boolean, default=True)

    def __init__(self):
        pass

    def toDict(self):
        serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
        return serialized

    def __repr__(self):
        return u"TenantSetting(%s, %s)" % (self.Id, self.TenantId)
    pass