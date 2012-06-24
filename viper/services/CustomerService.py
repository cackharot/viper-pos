import json
import uuid
import random
from datetime import datetime, date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc, func, cast, Date
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, subqueryload

from ..models import DBSession
from ..models.Customer import Customer, CustomerContactDetails
from ..library.ViperLog import log

from .CustomerCacheService import CustomerCacheService

class CustomerService(object):
	"""
		Customer management service
	"""
	def GetCustomer(self, id, tenantId):
		entity = CustomerCacheService.Get(id)
		if entity and entity.TenantId == tenantId:
			return entity
		entity = DBSession.query(Customer).options(joinedload(Customer.Contacts))\
						.filter(Customer.Id == id, Customer.TenantId == tenantId, Customer.Status == True).first()
		CustomerCacheService.Add(entity)
		return entity

	def GetDefaultCustomer(self, tenantId):
		entity = CustomerCacheService.GetDefault(tenantId)
		if entity and entity.TenantId == tenantId:
			return entity
		entity = DBSession.query(Customer).options(joinedload(Customer.Contacts)).filter(Customer.TenantId == tenantId, Customer.CustomerNo == 1, Customer.Status == True).first()
		CustomerCacheService.AddDefault(entity)
		return entity

	def SearchCustomers(self, tenantId, pageNo=0, pageSize=50, searchField='name', searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Customer).options(joinedload(Customer.Contacts))\
							.filter(Customer.TenantId == tenantId, Customer.Status == True)\
							.join(CustomerContactDetails)

		if searchValue and searchValue != '':
			searchValue = '%%%s%%' % searchValue
			if searchField == 'name':
				query = query.filter(CustomerContactDetails.FirstName.like(searchValue))
			elif searchField == 'mobile':
				query = query.filter(CustomerContactDetails.Mobile.like(searchValue))
			elif searchField == 'customerno':
				query = query.filter(Customer.CustomerNo.like(searchValue))

		lstCustomers = query.offset(pageNo).limit(pageSize).all()
		return lstCustomers

	def CheckCustomerExists(self, cid, tenantId, customerNo, mobile=None, email=None):
		if mobile and email and customerNo:
			query = DBSession.query(Customer.Id).filter(Customer.TenantId == tenantId)
			if cid:
				query = query.filter(Customer.Id != cid)
			query = query.filter(or_(Customer.CustomerNo == customerNo, Customer.Contacts.any(CustomerContactDetails.Mobile == mobile), \
					Customer.Contacts.any(CustomerContactDetails.Email == email)))
			valid = query.scalar()
			if valid:
				return True
		return False

	def AddCustomer(self, entity):
		if entity and entity.TenantId and entity.CreatedBy and len(entity.Contacts) > 0:
			DBSession.autoflush = False
			cnt = entity.Contacts[0]
			if self.CheckCustomerExists(None, entity.TenantId, entity.CustomerNo, cnt.Mobile, cnt.Email):
				raise Exception('Customer Number or email or mobile already exists!')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			CustomerCacheService.Add(entity)
			return True
		return False

	def SaveCustomer(self, entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy and len(entity.Contacts) > 0:
			DBSession.autoflush = False
			cnt = entity.Contacts[0]
			cnt.CustomerId = entity.Id
			if self.CheckCustomerExists(entity.Id, entity.TenantId, entity.CustomerNo, cnt.Mobile, cnt.Email):
				DBSession.expire(entity)
				raise Exception('Customer Number or email or mobile already exists!')
			entity.UpdatedOn = datetime.utcnow()
			entity.Status = True
			if not entity in DBSession:
				DBSession.add(entity)
			CustomerCacheService.Add(entity)
			if entity.CustomerNo == 1:
				CustomerCacheService.AddDefault(entity)
			return True
		return False

	def DeleteCustomer(self, ids, tenantId):
		if ids and tenantId:
			entities = DBSession.query(Customer).filter(Customer.Id.in_(ids), \
													Customer.TenantId == tenantId).all()
			if entities:
				for entity in entities:
					CustomerCacheService.Remove(entity.Id)
					DBSession.delete(entity)
		return False
	pass
