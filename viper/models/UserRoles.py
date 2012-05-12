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

class Role(Base):
	__tablename__ = "Roles"
	Id          = Column(String(20),  primary_key=True, index=True)
	TenantId    = Column(None, ForeignKey('TenantDetails.Id'),nullable=True)
	Name        = Column(String(50),  nullable=False)
	Description = Column(String(100), nullable=True)
	
	def __int__(self):
		self.Name=None
		self.Description=None
	pass

class RolePrivileges(Base):
	__tablename__ = "RolePrivlieges"
	Id            = id_column()
	RoleId        = Column(String(20), nullable=False)
	PrivilegeId   = Column(String(50), nullable=False)
	pass

class UserRoles(Base):
	__tablename__ = 'UserRoles'
	Id      = id_column()
	UserId  = Column(None,ForeignKey('UserDetails.Id'), nullable=False)
	RoleId   = Column(None,ForeignKey('Roles.Id'), nullable=False)
	pass
