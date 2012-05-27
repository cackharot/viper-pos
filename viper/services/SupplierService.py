import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date
from sqlalchemy import or_

from ..models import DBSession
from ..models.Supplier import Supplier, SupplierContactDetails
from ..library.ViperLog import log

class SupplierService(object):
	"""
		Supplier management service
	"""
	def GetSupplier(self,id,tenantId):
		return DBSession.query(Supplier).filter(Supplier.Id==id,Supplier.TenantId==tenantId,Supplier.Status==True).first()
	
	def GetSuppliers(self,tenantId):
		query = DBSession.query(Supplier.Id,Supplier.Name).filter(Supplier.TenantId==tenantId,Supplier.Status==True)
		return query.all()
		
	def SearchSupplier(self,tenantId,pageNo=0,pageSize=50,searchField='name',searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Supplier).filter(Supplier.TenantId==tenantId,Supplier.Status==True)\
							.join(SupplierContactDetails)
		
		if searchValue and searchValue != '':
			searchValue = '%%%s%%' % searchValue
			if searchField == 'name':
				query = query.filter(SupplierContactDetails.FirstName.like(searchValue))
			elif searchField == 'mobile':
				query = query.filter(SupplierContactDetails.Mobile.like(searchValue))
			elif searchField == 'customerno':
				query = query.filter(SupplierContactDetails.Mobile.like(searchValue))
		
		lstSuppliers = query.offset(pageNo).limit(pageSize).all()
		return lstSuppliers
	
	def CheckSupplierExists(self,cid,tenantId,name=None):
		if name:
			query = DBSession.query(Supplier.Id).filter(Supplier.TenantId==tenantId)
			if cid:
				query = query.filter(Supplier.Id != cid)
			query = query.filter(Supplier.Name==name)
			valid = query.count()
			if valid:
				return True
		return False
		
	def AddSupplier(self, entity):
		if entity and entity.TenantId and entity.CreatedBy and len(entity.Contacts) > 0:
			DBSession.autoflush = False
			cnt = entity.Contacts[0]
			if self.CheckSupplierExists(None,entity.TenantId,entity.Name):
				raise Exception('Supplier name already exists!')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def SaveSupplier(self, entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy and len(entity.Contacts)>0:
			DBSession.autoflush = False
			cnt = entity.Contacts[0]
			entity.Contacts[0].CustomerId = entity.Id
			if self.CheckSupplierExists(entity.Id,entity.TenantId,entity.Name):
				DBSession.expire(entity)
				raise Exception('Supplier name already exists!')
			entity.UpdatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def DeleteSupplier(self,id,tenantId):
		if id and tenantId:
			DBSession.query(SupplierContactDetails).filter(SupplierContactDetails.SupplierId==id).delete()
			return DBSession.query(Supplier).filter(Supplier.Id==id,\
					Supplier.TenantId==tenantId).delete()
		return False
	pass
