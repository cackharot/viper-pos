import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date

from ..models import DBSession
from ..models.Product import Product
from ..library.ViperLog import log
from ..models.Purchase import Purchase
from ..models.PurchaseLineItem import PurchaseLineItem
from ..models.PurchasePayment import PurchasePayment

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
		if product and product.TenantId and product.CreatedBy:
			product.CreatedOn = datetime.utcnow()
			product.Status = True
			DBSession.add(product)
			return True
		return False
		
	def SaveProduct(self,product):
		if product and product.Id and product.TenantId and product.UpdatedBy:
			product.UpdatedOn = datetime.utcnow()
			DBSession.add(product)
			return True
		return False
		
	def DeleteProduct(self,id,tenantId):
		if id and tenantId:
			return DBSession.query(Product).filter(Product.Id==id,\
					Product.TenantId==tenantId).delete()
		return False
		
	def GetPurchase(self,id,tenantId):
		return DBSession.query(Purchase).filter(Purchase.Id==id,Purchase.TenantId==tenantId,Purchase.Status==True).first()
			
	def AddPurchase(self,purchase):
		if purchase and purchase.TenantId and purchase.CreatedBy:
			purchase.CreatedOn = datetime.utcnow()
			purchase.Status = True
			DBSession.add(purchase)
			return True
		return False
		
	def SavePurchase(self,purchase):
		if purchase and purchase.Id and purchase.TenantId and purchase.UpdatedBy:
			purchase.UpdatedOn = datetime.utcnow()
			DBSession.add(purchase)
			return True
		return False
		
	def DeletePurchase(self,id,tenantId):
		if id and tenantId:
			return DBSession.query(Purchase).filter(Purchase.Id==id,\
					Product.TenantId==tenantId).delete()
		return False
		
	def SearchPurchases(self,tenantId,pageNo=0,pageSize=50,searchField=None,searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Purchase).filter(Purchase.TenantId==tenantId,Purchase.Status==True)
		
		if searchValue and searchField:
			if searchField == 'PurchaseNo':
				query = query.filter(Purchase.PurchaseNo==searchValue)
			elif searchField == 'SupplierId':
				query = query.filter(Purchase.SupplierId==searchValue)
			elif searchField == 'Amount':
				query = query.filter(Purchase.PurchaseAmount == searchValue)
			elif searchField == 'Date':
				query = query.filter(Purchase.PurchaseDate == searchValue)
		
		lstItems = query.offset(pageNo).limit(pageSize).all()
		return lstItems
	pass
