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

from . import OrderCacheService

class StockService(object):
	"""
		Stock management service
	"""
	def GetProduct(self,id,tenantId):
		if id and tenantId:
			entity = OrderCacheService.GetProduct(id)
			if entity and entity.TenantId == tenantId:
				if not entity in DBSession:
					DBSession.add(entity)
				return entity
			else:
				entity = DBSession.query(Product).filter(Product.Id==id,Product.TenantId==tenantId,Product.Status==True).first()
				OrderCacheService.AddProduct(entity)
			return entity
		return None
		
	def GetProductsByBarcode(self,tenantId,barcode):
		if tenantId and barcode:
			items = OrderCacheService.GetProductsByBarcode(tenantId,barcode)
			if items and len(items) > 0:
				return items
			else:
				items = self.GetProducts(tenantId,0,10,'Barcode',barcode)
				if items and len(items) > 0:
					for i in items:
						OrderCacheService.AddProduct(i)
					return items
		return None
		
	def GetProducts(self,tenantId,pageNo=0,pageSize=50,searchField='Name',searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Product).filter(Product.TenantId==tenantId,Product.Status==True)
		
		if searchValue and searchField:
			if searchField == 'Name':
				query = query.filter(Product.Name.like('%%%s%%' % searchValue)).order_by(Product.Name)
			elif searchField == 'Barcode':
				query = query.filter(Product.Barcode == searchValue)
		
		lstItems = query.offset(pageNo).limit(pageSize).all()
		return lstItems
		
	def AddProduct(self,entity):
		if entity and entity.TenantId and entity.CreatedBy:
			if entity.MfgDate and isinstance(entity.MfgDate,unicode):
				entity.MfgDate = datetime.strptime(entity.MfgDate,'%d-%m-%Y')
			if entity.ExpiryDate and isinstance(entity.ExpiryDate,unicode):
				entity.ExpiryDate = datetime.strptime(entity.ExpiryDate,'%d-%m-%Y')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			DBSession.flush()
			OrderCacheService.AddProduct(entity)
			return True
		return False
		
	def SaveProduct(self,entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy:
			if entity.MfgDate and isinstance(entity.MfgDate,unicode):
				entity.MfgDate = datetime.strptime(entity.MfgDate,'%d-%m-%Y')
			if entity.ExpiryDate and isinstance(entity.ExpiryDate,unicode):
				entity.ExpiryDate = datetime.strptime(entity.ExpiryDate,'%d-%m-%Y')
			entity.UpdatedOn = datetime.utcnow()
			if not entity in DBSession:
				DBSession.add(entity)
			DBSession.flush()
			OrderCacheService.AddProduct(entity)
			return True
		return False
		
	def DeleteProduct(self,id,tenantId):
		if id and tenantId:
			OrderCacheService.RemoveProduct(id)
			return DBSession.query(Product).filter(Product.Id==id,\
					Product.TenantId==tenantId).delete()
		return False
		
	def GetPurchase(self,id,tenantId):
		entity = DBSession.query(Purchase).filter(Purchase.Id==id,Purchase.TenantId==tenantId,Purchase.Status==True).one()
		return entity
	
	def CheckDuplicatePurchase(self,id,tenantId,no):
		query = DBSession.query(Purchase.Id).filter(Purchase.TenantId==tenantId)
		if id:
			query = query.filter(Purchase.Id != id)
		found = query.filter(Purchase.PurchaseNo==no).count()
		if found > 0:
			return True
		return False
	
	def AddPurchase(self,entity):
		if entity and entity.TenantId and entity.CreatedBy:
			DBSession.autoflush = False
			if self.CheckDuplicatePurchase(None,entity.TenantId,entity.PurchaseNo):
				raise Exception('Duplicate Purchase entry!')
			if entity.PurchaseDate and isinstance(entity.PurchaseDate,unicode):
				entity.PurchaseDate = datetime.strptime(entity.PurchaseDate,'%d-%m-%Y')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def SavePurchase(self,entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy:
			DBSession.autoflush = False
			if self.CheckDuplicatePurchase(entity.Id,entity.TenantId,entity.PurchaseNo):
				DBSession.expire(entity)
				raise Exception('Duplicate Purchase entry!')
			if entity.PurchaseDate and isinstance(entity.PurchaseDate,unicode):
				entity.PurchaseDate = datetime.strptime(entity.PurchaseDate,'%d-%m-%Y')
			entity.UpdatedOn = datetime.utcnow()
			if not entity in DBSession:
				DBSession.add(entity)
			return True
		return False
		
	def DeletePurchase(self,id,tenantId):
		if id and tenantId:
			return DBSession.query(Purchase).filter(Purchase.Id==id,\
					Purchase.TenantId==tenantId).delete()
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
