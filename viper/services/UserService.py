import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date

from ..models import DBSession
from ..models.User import User
from ..models.UserRoles import Role, UserRoles, RolePrivileges
from ..library.ViperLog import log

class UserService(object):
	"""
		User service class
	"""
	
	def __init__(self,userId=None,tenantId=None):
		self.TenantId = tenantId
		self.UserId   = userId
		pass
	
	def GetUserDetails(self,userId):
		if not userId:
			return DBSession.query(User).get(userId)
		return None
	
	def GetUserDetailsByName(self,name,tenantId):
		if not name:
			return DBSession.query(User).filter(User.TenantId=tenantId,User.UserName==name).one()
		return None
	
	pass

