from sqlalchemy import (
    Column,
    Boolean,
    Unicode,
    Text,
    ForeignKey,
    )

from . import Base
from ..library.vuid import id_column, UUID

class PrintTemplate(Base):
    '''
    Print Template class
    '''
    __tablename__   = 'PrintTemplates'
    Id              = id_column()
    TenantId        = Column(UUID(), ForeignKey('TenantDetails.Id'), nullable=False)
    Name            = Column(Unicode(50), nullable=False)
    Content         = Column(Text, nullable=True)
    #Default          = Column(Boolean, default=False)
    Status          = Column(Boolean, default=True)

    def __init__(self):
        self.TenantId=None
        self.Name=None
        self.Content=None
        self.Status=True

    def toDict(self):
        serialized = dict((column_name, getattr(self, column_name))
                          for column_name in self.__table__.c.keys())
        return serialized

    def __repr__(self):
        return u"PrintTemplate(%s, %s, %s)" % (self.Id, self.TenantId,self.Name)
    pass