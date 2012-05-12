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

class TenantService(object):
	"""
		Tenant service class
	"""
	
	def GetTenantDetails(self,tenantId):
		if not tenantId:
			return DBSession.query(Tenant).get(tenantId)
		return None
	
	def GetTenantDetailsByName(self,name):
		if not name:
			return DBSession.query(Tenant).filter(Tenant.Name==name).one()
		return None
	
	pass

