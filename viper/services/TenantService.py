import json
import uuid
import random
from datetime import datetime, date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc, func, cast, Date

from ..models import DBSession
from ..models.User import User
from ..models.Tenant import Tenant
from ..models.UserRoles import Role, UserRoles, RolePrivileges
from ..library.ViperLog import log

class TenantService(object):
	"""
		Tenant service class
	"""

	def GetTenantDetails(self, tenantId):
		if tenantId:
			return DBSession.query(Tenant).get(tenantId)
		return None

	def GetTenantDetailsByName(self, name):
		if name:
			return DBSession.query(Tenant).filter(Tenant.Name == name, Tenant.Status == True).first()
		return None

	def GetActiveTenants(self):
		return DBSession.query(Tenant).filter(Tenant.Status == True).all()

	def GetInActiveTenants(self):
		return DBSession.query(Tenant).filter(Tenant.Status == False).all()

	def DeleteTenant(self, tenantId):
		DBSession.query(Tenant).get(tenantId).delete()
		return True

	def CheckTenantNameExists(self,tenantId, name):
		if name:
			query = DBSession.query(Tenant.Id).filter(Tenant.Name == name)
			if tenantId:
				query = query.filter(Tenant.Id!=tenantId)
			if query.count() > 0:
				return True
		return False

	def ProvisionTenant(self, tenant):
		DBSession.autoflush = False
		if self.CheckTenantNameExists(None,tenant.Name):
			raise Exception('Tenant Name already exists! Please use different name.')
		DBSession.add(tenant)
		DBSession.commit()
		if tenant.AdminUser and not tenant.AdminUser.TenantId:
			tenant.AdminUser.TenantId = tenant.Id
		DBSession.flush()
		return True

	def SaveTenant(self, tenant):
		if tenant and tenant.Id and len(tenant.Name) > 0:
			DBSession.autoflush = False
			if self.CheckTenantNameExists(tenant.Id,tenant.Name):
				raise Exception('Tenant Name already exists! Please use different name.')
			DBSession.add(tenant)
			DBSession.flush()
			return True
		return False
		
