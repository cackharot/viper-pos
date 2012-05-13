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

import logging
log = logging.getLogger(__name__)

class SecurityService(object):
	"""
		Security service class
	"""
	
	def ValidateUser(self,tenantcode,username,password):
		if tenantcode and username and password:
			tenantService = TenantService()
			t = tenantService.GetTenantDetailsByName(tenantcode)
			if t:
				userService = UserService()
				user = userService.GetUserDetailsByName(username,t.Id)
				if user:
					givenhashpass = EncryptPassword(password)
					if user.Password == givenhashpass:
						return user.Id
		return None
	
	def GetUserRoles(self,userId):
		if name:
			result = DBSession.query(UserRoles).filter(UserRoles.UserId==userId).all()
			if result:
				return [x.RoleId for x in result]
		return None
	
	pass

