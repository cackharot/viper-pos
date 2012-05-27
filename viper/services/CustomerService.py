import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date
from sqlalchemy import or_

from ..models import DBSession
from ..models.Customer import Customer, CustomerContactDetails
from ..library.ViperLog import log

class CustomerService(object):
	"""
		Customer management service
	"""
	def GetCustomer(self,id,tenantId):
		entity = DBSession.query(Customer).filter(Customer.Id==id,Customer.TenantId==tenantId,Customer.Status==True).one()
		return entity
		
	def SearchCustomers(self,tenantId,pageNo=0,pageSize=50,searchField='name',searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Customer).filter(Customer.TenantId==tenantId,Customer.Status==True)\
							.join(CustomerContactDetails)
		
		if searchValue and searchValue != '':
			searchValue = '%%%s%%' % searchValue
			if searchField == 'name':
				query = query.filter(CustomerContactDetails.FirstName.like(searchValue))
			elif searchField == 'mobile':
				query = query.filter(CustomerContactDetails.Mobile.like(searchValue))
			elif searchField == 'customerno':
				query = query.filter(CustomerContactDetails.Mobile.like(searchValue))
		
		lstCustomers = query.offset(pageNo).limit(pageSize).all()
		return lstCustomers
	
	def CheckCustomerExists(self,cid,tenantId,customerNo,mobile=None,email=None):
		if mobile and email and customerNo:
			query = DBSession.query(Customer.Id).filter(Customer.TenantId==tenantId)
			if cid:
				query = query.filter(Customer.Id!=cid)
			query = query.filter(or_(Customer.CustomerNo==customerNo,Customer.Contacts.any(CustomerContactDetails.Mobile==mobile),\
					Customer.Contacts.any(CustomerContactDetails.Email==email)))
			valid = query.scalar()
			if valid:
				return True
		return False
		
	def AddCustomer(self, entity):
		if entity and entity.TenantId and entity.CreatedBy and len(entity.Contacts) > 0:
			DBSession.autoflush = False
			cnt = entity.Contacts[0]
			if self.CheckCustomerExists(None,entity.TenantId,entity.CustomerNo,cnt.Mobile, cnt.Email):
				raise Exception('Customer Number or email or mobile already exists!')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def SaveCustomer(self, entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy and len(entity.Contacts)>0:
			DBSession.autoflush = False
			cnt = entity.Contacts[0]
			entity.Contacts[0].CustomerId = entity.Id
			if self.CheckCustomerExists(entity.Id, entity.TenantId, entity.CustomerNo, cnt.Mobile, cnt.Email):
				DBSession.expire(entity)
				raise Exception('Customer Number or email or mobile already exists!')
			entity.UpdatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def DeleteCustomer(self,id,tenantId):
		if id and tenantId:
			return DBSession.query(Customer).filter(Customer.Id==id,\
					Customer.TenantId==tenantId).delete()
		return False
	pass
