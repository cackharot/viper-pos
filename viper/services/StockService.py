import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date,distinct
#from sqlalchemy.sql.operators.Operators import in_

from ..models import DBSession
from ..models.Product import Product
from ..models.Order import Order
from ..models.LineItem import LineItem
from ..models.Supplier import Supplier
from ..library.ViperLog import log
from ..models.Purchase import Purchase, PurchaseSearchParam
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
				entity = DBSession.query(Product).filter(Product.Id==id,Product.TenantId==tenantId).first()
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
		
	def GetProducts(self,tenantId,pageNo=0,pageSize=50,searchField=None,searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Product).filter(Product.TenantId==tenantId)

		if searchField:
			if searchField == 'Name' and searchValue:
				query = query.filter(Product.Name.like('%%%s%%' % searchValue)).order_by(Product.Name)
			elif searchField == 'Barcode' and searchValue:
				query = query.filter(Product.Barcode == searchValue)
			elif searchField == 'Status':
				query = query.filter(Product.Status == searchValue)
			elif searchField == 'SuppierName' and searchValue:
				query = query.join(Supplier).filter(Supplier.Name == searchValue)
		
		lstItems = query.order_by(desc(Product.UpdatedOn),desc(Product.CreatedOn)).offset(pageNo).limit(pageSize).all()
		return lstItems
		
	def GetReturnableProductIds(self,tenantId,pageNo=0,pageSize=50):
		if not tenantId:
			return None
		query = DBSession.query(Product.Id).filter(Product.TenantId==tenantId,Product.Status==False)
		#query = query.order_by(desc(Product.UpdatedOn),desc(Product.CreatedOn))
		lstItems = query.offset(pageNo).limit(pageSize).all()
		return lstItems, query.count()
		
	def GetProductStock(self,tenantId,minStock=1000,productIds=None):
		if not tenantId:
			return None

		lsb  = DBSession.query(LineItem.ProductId,func.sum(LineItem.Quantity).label('Sold')).group_by(LineItem.ProductId).subquery()
		plsb = DBSession.query(PurchaseLineItem.ProductId,func.sum(PurchaseLineItem.Quantity).label('Bought')).group_by(PurchaseLineItem.ProductId).subquery()
		
		smt = DBSession.query(Product.SupplierId,Supplier.Name.label('SupplierName'),Product.Id,Product.Name,Product.Barcode,Product.MRP,(func.ifnull(plsb.c.Bought,0)-func.ifnull(lsb.c.Sold,0)).label('Stock'))
		smt = smt.join(Supplier)
		smt = smt.outerjoin(lsb,lsb.c.ProductId==Product.Id)
		smt = smt.outerjoin(plsb,plsb.c.ProductId==Product.Id)
		smt = smt.group_by(Product.Id)

		if productIds and len(productIds) > 0:
			smt = smt.filter(Product.Id.in_(productIds))
		
		smt = smt.filter(Product.TenantId==tenantId).subquery()
		
		query = DBSession.query(smt)
		query = query.filter(smt.c.Stock<=minStock).order_by(smt.c.Stock)
			
		lstItems = query.offset(0).limit(20).all()
		return lstItems, query.count()
		
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
		query = DBSession.query(Purchase)
		query = query.filter(Purchase.Id==id,Purchase.TenantId==tenantId,Purchase.Status==True)
		entity = query.one()
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
		
	def SearchPurchases(self,param):
		if not (param and param.TenantId):
			return None
			
		a = DBSession.query(PurchaseLineItem.PurchaseId,PurchaseLineItem.BuyPrice,PurchaseLineItem.Quantity).subquery()
		b = DBSession.query(PurchasePayment.PurchaseId,PurchasePayment.PaidAmount).subquery()
			
		query = DBSession.query(Purchase.Id,Purchase.PurchaseNo,Purchase.PurchaseDate,\
					Supplier.Name.label('SupplierName'),\
					func.count(a.c.PurchaseId).label('ItemCount'), \
					func.sum(a.c.BuyPrice*a.c.Quantity).label('PurchaseAmount'), \
					func.ifnull(func.sum(b.c.PaidAmount),0).label('PaidAmount'))
		query = query.join(Supplier).join(a).outerjoin(b).group_by(Purchase.Id)
		
		if param.PurchaseNo:
			query = query.filter(Purchase.PurchaseNo==param.PurchaseNo)
		elif param.SupplierId and len(param.SupplierId) > 0:
			query = query.filter(Purchase.SupplierId==param.SupplierId)
		elif param.SupplierName:
			query = query.join(Supplier).filter(Supplier.Name.like('%%%s%%' % param.SupplierName))
		elif param.PurchaseAmount:
			query = query.filter(Purchase.PurchaseAmount == param.PurchaseAmount)
		elif param.PurchaseDate:
			query = query.filter(Purchase.PurchaseDate == param.PurchaseDate)
		elif param.Credit:
			#query = query.filter(func.ifnull(func.sum(a.c.BuyPrice*a.c.Quantity),0) >  func.ifnull(func.sum(b.c.PaidAmount),0))
			smt = query.subquery()
			query = DBSession.query(smt).filter(smt.c.PurchaseAmount>smt.c.PaidAmount)
				
		query = query.filter(Purchase.TenantId==param.TenantId,Purchase.Status==True)
		query = query.order_by(desc(Purchase.PurchaseDate))
		
		lstItems = query.offset(param.PageNo).limit(param.PageSize).all()
		if param.Credit:
			return lstItems, query.count()
		else:
			return lstItems
		
	def AddPurchaseLineItem(self,entity,tenantId):
		if tenantId and entity and entity.PurchaseId:
			DBSession.autoflush = False
			purchase = self.GetPurchase(entity.PurchaseId,tenantId)
			if purchase:
				purchase.LineItems.append(entity)
				DBSession.flush()
				return True
		return False
		
	def DeletePurchaseLineItem(self,purchaseId,lineItemId,tenantId):
		if tenantId and purchaseId and lineItemId:
			query = DBSession.query(PurchaseLineItem)#.join(Purchase)
			#query = query.filter(Purchase.Id==purchaseId,Purchase.TenantId==tenantId)
			query = query.filter(PurchaseLineItem.Id==lineItemId)
			return query.delete()
		return False
	pass
