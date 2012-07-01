from datetime import datetime
import uuid
from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc, cast, Date, func, or_
#from sqlalchemy.sql.operators.Operators import in_

from ..models import DBSession
from ..models.Product import Product
#from ..models.Order import Order
from ..models.LineItem import LineItem
from ..models.Supplier import Supplier

from ..models.Purchase import Purchase, PurchaseSearchParam
from ..models.PurchaseLineItem import PurchaseLineItem
from ..models.PurchasePayment import PurchasePayment

from .OrderCacheService import OrderCacheService

class StockService(object):
	"""
		Stock management service
	"""
	def GetProduct(self, productId, tenantId):
		if productId and tenantId:
			entity = OrderCacheService.GetProduct(productId)
			if entity and entity.TenantId == tenantId:
				if not entity in DBSession:
					DBSession.add(entity)
				return entity
			else:
				entity = DBSession.query(Product).filter(Product.Id == productId, Product.TenantId == tenantId).first()
				OrderCacheService.AddProduct(entity)
			return entity
		return None

	def GetProductsByBarcode(self, tenantId, barcode):
		if tenantId and barcode:
			items = OrderCacheService.GetProductsByBarcode(tenantId, barcode)
			if items and len(items) > 0:
				return items
			else:
				items = self.GetProducts(tenantId, 0, 10, 'Barcode', barcode)
				if items and len(items) > 0:
					for i in items:
						OrderCacheService.AddProduct(i)
					return items
		return None

	def GetProducts(self, tenantId, pageNo=0, pageSize=50, searchField=None, searchValue=None):
		if not tenantId:
			return None
		query = DBSession.query(Product).filter(Product.TenantId == tenantId)

		if searchField:
			if searchField == 'Name' and searchValue:
				query = query.filter(Product.Name.like('%%%s%%' % searchValue)).order_by(Product.Name)
			elif searchField == 'Barcode' and searchValue:
				query = query.filter(Product.Barcode == searchValue)
			elif searchField == 'Status':
				query = query.filter(Product.Status == searchValue)
			elif searchField == 'SuppierName' and searchValue:
				query = query.join(Supplier).filter(Supplier.Name == searchValue)

		lstItems = query.order_by(desc(Product.UpdatedOn), desc(Product.CreatedOn)).offset(pageNo).limit(pageSize).all()
		return lstItems

	def GetReturnableProductIds(self, tenantId, pageNo=0, pageSize=50):
		if not tenantId:
			return None
		query = DBSession.query(Product.Id).filter(Product.TenantId == tenantId, Product.Status == False)
		#query = query.order_by(desc(Product.UpdatedOn),desc(Product.CreatedOn))
		lstItems = query.offset(pageNo).limit(pageSize).all()
		return lstItems, query.count()

	def GetProductStock(self, tenantId, minStock=1000, productIds=None):
		if not tenantId:
			return None

		lsb = DBSession.query(LineItem.ProductId, func.sum(LineItem.Quantity).label('Sold')).group_by(LineItem.ProductId).subquery()
		plsb = DBSession.query(PurchaseLineItem.ProductId, func.sum(PurchaseLineItem.Quantity).label('Bought')).group_by(PurchaseLineItem.ProductId).subquery()

		smt = DBSession.query(Product.SupplierId, Supplier.Name.label('SupplierName'), Product.Id, Product.Name, Product.Barcode, Product.MRP, (func.ifnull(plsb.c.Bought, 0) - func.ifnull(lsb.c.Sold, 0)).label('Stock'))
		smt = smt.join(Supplier)
		smt = smt.outerjoin(lsb, lsb.c.ProductId == Product.Id)
		smt = smt.outerjoin(plsb, plsb.c.ProductId == Product.Id)
		smt = smt.group_by(Product.Id)

		if productIds and len(productIds) > 0:
			smt = smt.filter(Product.Id.in_(productIds))

		smt = smt.filter(Product.TenantId == tenantId).subquery()

		query = DBSession.query(smt)
		query = query.filter(smt.c.Stock <= minStock).order_by(smt.c.Stock)

		lstItems = query.offset(0).limit(20).all()
		return lstItems, query.count()

	def AddProduct(self, entity):
		if entity and entity.TenantId and entity.CreatedBy:
			if entity.MfgDate and isinstance(entity.MfgDate, unicode):
				entity.MfgDate = datetime.strptime(entity.MfgDate, '%d-%m-%Y')
			if entity.ExpiryDate and isinstance(entity.ExpiryDate, unicode):
				entity.ExpiryDate = datetime.strptime(entity.ExpiryDate, '%d-%m-%Y')
			if entity.CategoryId !='' and isinstance(entity.CategoryId,unicode):
				entity.CategoryId = uuid.UUID(entity.CategoryId)
			elif entity.CategoryId == '':
				entity.CategoryId = None
			if entity.TaxCategoryId != '' and isinstance(entity.TaxCategoryId,unicode):
				entity.TaxCategoryId = uuid.UUID(entity.TaxCategoryId)
			if entity.SupplierId != '' and isinstance(entity.SupplierId,unicode):
				entity.SupplierId = uuid.UUID(entity.SupplierId)
			elif entity.SupplierId == '':
				entity.SupplierId = None
				
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			DBSession.flush()
			OrderCacheService.AddProduct(entity)
			return True
		return False

	def SaveProduct(self, entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy:
			if entity.MfgDate and isinstance(entity.MfgDate, unicode):
				entity.MfgDate = datetime.strptime(entity.MfgDate, '%d-%m-%Y')
			if entity.ExpiryDate and isinstance(entity.ExpiryDate, unicode):
				entity.ExpiryDate = datetime.strptime(entity.ExpiryDate, '%d-%m-%Y')
			if entity.CategoryId !='' and isinstance(entity.CategoryId,unicode):
				entity.CategoryId = uuid.UUID(entity.CategoryId)
			elif entity.CategoryId == '':
				entity.CategoryId = None
			if entity.TaxCategoryId != '' and isinstance(entity.TaxCategoryId,unicode):
				entity.TaxCategoryId = uuid.UUID(entity.TaxCategoryId)
			if entity.SupplierId != '' and isinstance(entity.SupplierId,unicode):
				entity.SupplierId = uuid.UUID(entity.SupplierId)
			elif entity.SupplierId == '':
				entity.SupplierId = None
					
			entity.UpdatedOn = datetime.utcnow()
			if not entity in DBSession:
				DBSession.add(entity)
			DBSession.flush()
			OrderCacheService.AddProduct(entity)
			return True
		return False

	def DeleteProduct(self, productIds, tenantId):
		if productIds and tenantId:
			entities = DBSession.query(Product).filter(Product.Id.in_(productIds), \
												Product.TenantId == tenantId).all()					
			if entities:
				for entity in entities:
					OrderCacheService.RemoveProduct(entity.Id)
					DBSession.delete(entity)
		return False

	def GetPurchase(self, purchaseId, tenantId):
		query = DBSession.query(Purchase)
		query = query.filter(Purchase.Id == purchaseId, Purchase.TenantId == tenantId, Purchase.Status == True)
		entity = query.one()
		return entity

	def CheckDuplicatePurchase(self, purchaseId, tenantId, no):
		query = DBSession.query(Purchase.Id).filter(Purchase.TenantId == tenantId)
		if purchaseId:
			query = query.filter(Purchase.Id != purchaseId)
		found = query.filter(Purchase.PurchaseNo == no).count()
		if found > 0:
			return True
		return False

	def AddPurchase(self, entity):
		if entity and entity.TenantId and entity.CreatedBy:
			DBSession.autoflush = False
			if self.CheckDuplicatePurchase(None, entity.TenantId, entity.PurchaseNo):
				raise Exception('Duplicate Purchase entry!')
			if entity.PurchaseDate and isinstance(entity.PurchaseDate, unicode):
				entity.PurchaseDate = datetime.strptime(entity.PurchaseDate, '%d-%m-%Y')
			if entity.DueDate and isinstance(entity.DueDate, unicode):
				entity.DueDate = datetime.strptime(entity.DueDate, '%d-%m-%Y')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			DBSession.flush()
			return True
		return False

	def SavePurchase(self, entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy:
			DBSession.autoflush = False
			if self.CheckDuplicatePurchase(entity.Id, entity.TenantId, entity.PurchaseNo):
				DBSession.expire(entity)
				raise Exception('Duplicate Purchase entry!')
			if entity.PurchaseDate and isinstance(entity.PurchaseDate, unicode):
				entity.PurchaseDate = datetime.strptime(entity.PurchaseDate, '%d-%m-%Y')
			if entity.DueDate and isinstance(entity.DueDate, unicode):
				entity.DueDate = datetime.strptime(entity.DueDate, '%d-%m-%Y')
			entity.UpdatedOn = datetime.utcnow()
			if not entity in DBSession:
				DBSession.add(entity)
			return True
		return False

	def DeletePurchase(self, purchaseids, tenantId):
		if purchaseids and tenantId:
			entities = DBSession.query(Purchase).filter(Purchase.Id.in_(purchaseids), \
														Purchase.TenantId == tenantId).all()
			if entities:
				for entity in entities:
					DBSession.delete(entity)
		return False

	def SearchPurchases(self, param):
		if not (param and param.TenantId):
			return None

		a = DBSession.query(PurchaseLineItem.PurchaseId, func.count(PurchaseLineItem.PurchaseId).label('ItemCount'),\
						func.ROUND(func.sum(PurchaseLineItem.BuyPrice * PurchaseLineItem.Quantity),2).label('PurchaseAmount'))
		a = a.join(Purchase,Purchase.Id==PurchaseLineItem.PurchaseId).group_by(PurchaseLineItem.PurchaseId).subquery()
		
		b = DBSession.query(PurchasePayment.PurchaseId, func.ROUND(func.sum(PurchasePayment.PaidAmount),2).label('PaidAmount'))
		b = b.join(Purchase,Purchase.Id==PurchasePayment.PurchaseId).group_by(PurchasePayment.PurchaseId).subquery()

		query = DBSession.query(Purchase.Id, Purchase.PurchaseNo, Purchase.PurchaseDate, \
					Purchase.DueDate, \
					Supplier.Name.label('SupplierName'), \
					a.c.ItemCount, \
					func.ifnull(a.c.PurchaseAmount, 0).label('PurchaseAmount'), \
					func.ifnull(b.c.PaidAmount, 0).label('PaidAmount'))
		query = query.join(Supplier).outerjoin(a,a.c.PurchaseId==Purchase.Id).outerjoin(b,b.c.PurchaseId==Purchase.Id).group_by(Purchase.Id)

		query = self.formQueryFromParam(query, a, b, param)
		query = query.order_by(desc(Purchase.PurchaseDate),a.c.PurchaseAmount)

		lstItems = query.offset(param.PageNo).limit(param.PageSize).all()
		
		if not param.LoadStats:
			return lstItems
		
		tquery = DBSession.query(func.count(Purchase.Id).label('ItemsCount'), \
								func.ifnull(func.sum(a.c.PurchaseAmount),0).label('TotalAmount'),\
								func.ifnull(func.sum(func.IF(b.c.PaidAmount>=a.c.PurchaseAmount,a.c.PurchaseAmount,b.c.PaidAmount)),0).label('TotalPaidAmount'))
		tquery = tquery.join(Supplier)\
					.outerjoin(a,a.c.PurchaseId==Purchase.Id)\
					.outerjoin(b,b.c.PurchaseId==Purchase.Id)
		
		tquery = self.formQueryFromParam(tquery, a, b, param)

		return lstItems, tquery.first()
	
	def formQueryFromParam(self,query,a,b,param):
		if param.PurchaseNo:
			query = query.filter(Purchase.PurchaseNo == param.PurchaseNo)
			
		if param.SupplierId and len(param.SupplierId) > 0:
			query = query.filter(Purchase.SupplierId == param.SupplierId)
		elif param.SupplierName:
			query = query.join(Supplier).filter(Supplier.Name.like('%%%s%%' % param.SupplierName))
			
		if param.PurchaseAmount:
			query = query.filter(Purchase.PurchaseAmount == param.PurchaseAmount)
		if param.PurchaseDate:
			query = query.filter(Purchase.PurchaseDate == param.PurchaseDate)
		
		if param.Credit:
			query = query.filter(a.c.PurchaseAmount > b.c.PaidAmount)
			
		if param.FromPurchaseDate and not param.ToPurchaseDate:
			query = query.filter(cast(Purchase.PurchaseDate, Date) >= param.FromPurchaseDate)
		if not param.FromPurchaseDate and param.ToPurchaseDate:
			query = query.filter(cast(Purchase.PurchaseDate, Date) <= param.ToPurchaseDate)
		if param.FromPurchaseDate and param.ToPurchaseDate:
			query = query.filter(cast(Purchase.PurchaseDate, Date) >= param.FromPurchaseDate, \
									cast(Purchase.PurchaseDate, Date) <= param.ToPurchaseDate)
			
		if param.PurchaseStatus == 'opened':
			query = query.filter(or_(a.c.PurchaseAmount > b.c.PaidAmount, a.c.PurchaseAmount==0, \
									b.c.PaidAmount == None, a.c.PurchaseAmount == None))
		elif param.PurchaseStatus == 'closed':
			query = query.filter(a.c.PurchaseAmount <= b.c.PaidAmount, a.c.PurchaseAmount!=0)
		elif param.PurchaseStatus == 'overdue':
			query = query.filter(a.c.PurchaseAmount > b.c.PaidAmount, Purchase.DueDate < func.now())

		query = query.filter(Purchase.TenantId == param.TenantId, Purchase.Status == True)
		return query
	
	def AddPurchaseLineItem(self, entity, tenantId):
		if tenantId and entity and entity.PurchaseId:
			DBSession.autoflush = False
			purchase = self.GetPurchase(entity.PurchaseId, tenantId)
			if purchase:
				purchase.LineItems.append(entity)
				DBSession.flush()
				return True
		return False
	
	def GetPurchasePayments(self, purchaseId, tenantId):
		if purchaseId and tenantId:
			payments = DBSession.query(PurchasePayment).filter(PurchasePayment.PurchaseId==purchaseId).all()
			return payments
		return None
	
	def DeletePurchasePayment(self,paymentId):
		if paymentId:
			DBSession.query(PurchasePayment).filter(PurchasePayment.Id==paymentId).delete()
			return False
		return True
	
	def UpdatePurchasePayment(self,purchaseId,paymentId,details,userId):
		if purchaseId and details and userId:
			if paymentId:
				payment = DBSession.query(PurchasePayment).get(paymentId)
			else:
				payment = PurchasePayment()
				payment.PurchaseId = purchaseId
				payment.CreatedBy  = userId
				payment.CreatedOn  = datetime.utcnow()
				
			if payment:
				if payment.Id:
					payment.UpdatedBy = userId
					payment.UpdatedOn = datetime.utcnow()
				
				payment.PaidAmount = details['paidAmount']
				payment.PaymentType= details['paymentType']
				payment.PaymentDate= datetime.strptime(details['paymentDate'].strip(),'%d-%m-%Y')
				payment.Status     = True
				DBSession.add(payment)
			return True
		return False

	def DeletePurchaseLineItem(self, purchaseId, lineItemId, tenantId):
		if tenantId and purchaseId and lineItemId:
			query = DBSession.query(PurchaseLineItem)#.join(Purchase)
			#query = query.filter(Purchase.Id==purchaseId,Purchase.TenantId==tenantId)
			query = query.filter(PurchaseLineItem.Id == lineItemId)
			return query.delete()
		return False
	pass
