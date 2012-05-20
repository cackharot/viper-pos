import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date

from ..models import DBSession
from ..models.Product import Product
from ..library.ViperLog import log

class StockService(object):
	"""
		Stock management service
	"""
	def GetProduct(self,id,tenantId):
		return DBSession.query(Product).filter(Product.Id==id,Product.TenantId==tenantId,Product.Status==True).first()
		
	def GetProducts(self,tenantId,pageNo=0,pageSize=50,searchField='Name',searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Product).filter(Product.TenantId==tenantId,Product.Status==True)
		
		if searchValue and searchValue != '':
			if searchField and searchField == 'Name':
				query = query.filter(Product.Name.like('%%%s%%' % searchValue))
		
		lstItems = query.offset(pageNo).limit(pageSize).all()
		return lstItems
		
	def AddProduct(self,product):
		if product and product.TenantId:
			product.CreatedOn = datetime.utcnow()
			DBSession.add(product)
			return True
		return False
		
	def SaveProduct(self,product):
		if product and product.Id and product.TenantId:
			product.UpdatedOn = datetime.utcnow()
			DBSession.add(product)
			return True
		return False
		
	def DeleteProduct(self,id,tenantId):
		if id and tenantId:
			return DBSession.query(Product).filter(Product.Id==id,\
					Product.TenantId==tenantId).delete()
		return False
	pass
