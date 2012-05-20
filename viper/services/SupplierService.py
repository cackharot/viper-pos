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
	
	def CheckSupplierExists(self,cid,mobile=None,email=None):
		if mobile and email:
			query = DBSession.query(Supplier.Id)
			if cid:
				query = query.filter(Supplier.Id!=cid)
			query = query.filter(or_(Supplier.Contacts.any(SupplierContactDetails.Mobile==mobile),\
					Supplier.Contacts.any(SupplierContactDetails.Email==email)))
			valid = query.scalar()
			if valid:
				return True
		return False
		
	def AddSupplier(self, entity):
		if entity and entity.TenantId and entity.CreatedBy and len(entity.Contacts) > 0:
			cnt = entity.Contacts[0]
			if self.CheckSupplierExists(None,cnt.Mobile, cnt.Email):
				raise Exception('Supplier email or mobile already exists!')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def SaveSupplier(self, entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy and len(entity.Contacts)>0:
			cnt = entity.Contacts[0]
			entity.Contacts[0].CustomerId = entity.Id
			if self.CheckSupplierExists(entity.Id, cnt.Mobile, cnt.Email):
				raise Exception('Supplier email or mobile already exists!')
			entity.UpdatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def DeleteSupplier(self,id,tenantId):
		if id and tenantId:
			return DBSession.query(Supplier).filter(Supplier.Id==id,\
					Supplier.TenantId==tenantId).delete()
		return False
	pass
