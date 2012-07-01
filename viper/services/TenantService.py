from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models.Tenant import Tenant

from .ServiceExceptions import TenantException 

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
	
	def GetAllTenants(self):
		return DBSession.query(Tenant).all()

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
		try:
			DBSession.autoflush = False
			if self.CheckTenantNameExists(None,tenant.Name):
				raise Exception('Tenant Name already exists! Please use different name.')
			DBSession.add(tenant)
			DBSession.commit()
			if tenant.AdminUser and not tenant.AdminUser.TenantId:
				tenant.AdminUser.TenantId = tenant.Id
			DBSession.flush()
			return True
		except DBAPIError, ex:
			raise TenantException(ex,'Error while creating new tenant')

	def SaveTenant(self, tenant):
		if tenant and tenant.Id and len(tenant.Name) > 0:
			try:
				DBSession.autoflush = False
				if self.CheckTenantNameExists(tenant.Id,tenant.Name):
					raise Exception('Tenant Name already exists! Please use different name.')
				DBSession.add(tenant)
				DBSession.flush()
				return True
			except DBAPIError, ex:
				raise TenantException(ex,'Error while saving tenant details')
		return False
		
