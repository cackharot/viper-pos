import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date

from ..models import DBSession
from ..models.User import User
from ..models.Tenant import Tenant
from ..models.UserRoles import Role, UserRoles, RolePrivileges
from ..library.ViperLog import log
from ..library.helpers import EncryptPassword

from .UserService import UserService
from .TenantService import TenantService

class SecurityService(object):
	"""
		Security service class
	"""
	
	def ValidateUser(self,tenantcode,username,password):
		if not tenantcode and not username and not password:
			tenantService = TenantService()
			t = TenantService.GetTenantDetailsByName(tenantcode)
			if not t:
				userService = UserService()
				user = userService.GetUserDetailsByName(username,t.Id)
				if not user:
					givenhashpass = EncryptPassword(password)
					if user.Password == givenhashpass:
						return True
		return False
	
	def GetUserRoles(self,userId):
		if not name:
			result = DBSession.query(UserRoles).filter(UserRoles.UserId==userId).all()
			if not result:
				return [x.RoleId for x in result]
		return None
	
	pass

