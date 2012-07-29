import json
from datetime import datetime, date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc, func, cast, Date, or_

from ..models import DBSession
from ..models.Product import Product
from ..models.Supplier import Supplier
from ..models.Customer import Customer, CustomerContactDetails
from ..models.Order import Order
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment
from ..models.Purchase import Purchase, PurchaseSearchParam
from ..models.PurchaseLineItem import PurchaseLineItem
from ..models.PurchasePayment import PurchasePayment
from ..library.ViperLog import log

from ..services.SecurityService import SecurityService
from ..services.CustomerService import CustomerService

customerService = CustomerService()

class ReportService(object):
	"""
		Reporting service class
	"""

	def GetInvoiceTotals(self, tenantId, param=None):
		"""
			Calculates invoice totals, amounts, due, etc.,
		"""
		if tenantId:
			query = DBSession.query(func.count(Order.Id).label('Count'), \
								 func.ifnull(func.sum(Order.OrderAmount),0).label('TotalAmount'), \
								 func.ifnull(func.sum(func.IF(Order.PaidAmount>=Order.OrderAmount,Order.OrderAmount,Order.PaidAmount)),0).label('PaidAmount'))
			
			query = query.filter(Order.TenantId == tenantId, Order.Status == True)
			
			if param:
				query = self.applySearchParam(query,param)
			
			totals = query.first()
			
			if totals:
				oq = query.filter((Order.OrderAmount - Order.PaidAmount) > 0.5, Order.DueDate<func.now()).subquery()
				totals.Overdues = DBSession.query(oq.c.Count,\
												(oq.c.TotalAmount-oq.c.PaidAmount).label('OverdueAmount')).first() 
			
			return totals
		return None
	
	def applySearchParam(self, query, searchParam):
		if searchParam.CustomerId:
			query = query.filter(Order.CustomerId == searchParam.CustomerId)
		if searchParam.CustomerName:
			query = query.filter(CustomerContactDetails.FirstName.like('%%%s' % searchParam.CustomerName))
		if searchParam.IpAddress:
			query = query.filter(Order.IpAddress == searchParam.IpAddress)

		if searchParam.FromDate and not searchParam.ToDate:
			query = query.filter(cast(Order.OrderDate, Date) >= searchParam.FromDate)
		if not searchParam.FromDate and searchParam.ToDate:
			query = query.filter(cast(Order.OrderDate, Date) <= searchParam.ToDate)
		if searchParam.FromDate and searchParam.ToDate:
			query = query.filter(cast(Order.OrderDate, Date) >= searchParam.FromDate, \
									cast(Order.OrderDate, Date) <= searchParam.ToDate)

		if searchParam.MinAmount and not searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount >= searchParam.MinAmount)
		if not searchParam.MinAmount and searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount <= searchParam.MaxAmount)
		if searchParam.MinAmount and searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount >= searchParam.MinAmount, \
									Order.OrderAmount <= searchParam.MaxAmount)			
			
		if searchParam.InvoiceStatus == 'opened':
			query = query.filter(or_((Order.OrderAmount - Order.PaidAmount) > 0.5, Order.OrderAmount==0))
		elif searchParam.InvoiceStatus == 'closed':
			query = query.filter(Order.OrderAmount != 0, (Order.PaidAmount - Order.OrderAmount) > 0.001)
		elif searchParam.InvoiceStatus == 'overdue':
			query = query.filter((Order.OrderAmount - Order.PaidAmount) > 0.5, Order.DueDate < func.now())
		return query
	
	def GetPurchaseTotals(self, tenantId, param=None):
		"""
			Calculates invoice totals, amounts, due, etc.,
		"""
		if tenantId:
			a = DBSession.query(PurchaseLineItem.PurchaseId, \
						func.sum(PurchaseLineItem.BuyPrice * PurchaseLineItem.Quantity).label('PurchaseAmount'))
			a = a.join(Purchase,Purchase.Id==PurchaseLineItem.PurchaseId).group_by(PurchaseLineItem.PurchaseId).subquery()
			
			b = DBSession.query(PurchasePayment.PurchaseId, func.sum(PurchasePayment.PaidAmount).label('PaidAmount'))
			b = b.join(Purchase,Purchase.Id==PurchasePayment.PurchaseId).group_by(PurchasePayment.PurchaseId).subquery()
	
			query = DBSession.query(func.count(Purchase.Id).label('Count'),\
						func.ifnull(func.sum(a.c.PurchaseAmount), 0).label('TotalAmount'), \
						func.ifnull(func.sum(func.IF(b.c.PaidAmount>=a.c.PurchaseAmount,a.c.PurchaseAmount,b.c.PaidAmount)),0).label('PaidAmount'))
			query = query.outerjoin(a,a.c.PurchaseId==Purchase.Id).outerjoin(b,b.c.PurchaseId==Purchase.Id)
			
			query = query.filter(Purchase.TenantId == tenantId, Purchase.Status == True)
			
			if param:
				query = self.applyPurchaseSearchParam(query,a,b,param)
			
			totals = query.first()
			
			if totals:
				oq = query.filter(a.c.PurchaseAmount > b.c.PaidAmount, Purchase.DueDate < func.now()).subquery()
				totals.Overdues = DBSession.query(oq.c.Count,\
												(oq.c.TotalAmount-oq.c.PaidAmount).label('OverdueAmount')).first() 
			
			return totals
		return None
	
	def applyPurchaseSearchParam(self,query,a,b,param):
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
			
		if param.FromDate and not param.ToDate:
			query = query.filter(cast(Purchase.PurchaseDate, Date) >= param.FromDate)
		if not param.FromDate and param.ToDate:
			query = query.filter(cast(Purchase.PurchaseDate, Date) <= param.ToDate)
		if param.FromDate and param.ToDate:
			query = query.filter(cast(Purchase.PurchaseDate, Date) >= param.FromDate, \
									cast(Purchase.PurchaseDate, Date) <= param.ToDate)
			
		if param.Status == 'opened':
			query = query.filter(or_(a.c.PurchaseAmount > b.c.PaidAmount, a.c.PurchaseAmount==0, \
									b.c.PaidAmount == None, a.c.PurchaseAmount == None))
		elif param.Status == 'closed':
			query = query.filter(a.c.PurchaseAmount <= b.c.PaidAmount, a.c.PurchaseAmount!=0)
		elif param.Status == 'overdue':
			query = query.filter(a.c.PurchaseAmount > b.c.PaidAmount, Purchase.DueDate < func.now())

		return query
	
	def GetTotals(self,tenantId):
		if not tenantId:
			return None
		
		invociequery  = DBSession.query(Order.Id).filter(Order.TenantId==tenantId).subquery()
		purchasequery = DBSession.query(Purchase.Id).filter(Purchase.TenantId==tenantId).subquery()
		itemquery  	  = DBSession.query(Product.Id).filter(Product.TenantId==tenantId).subquery()
		customerquery = DBSession.query(Customer.Id).filter(Customer.TenantId==tenantId).subquery()
		supplierquery = DBSession.query(Supplier.Id).filter(Supplier.TenantId==tenantId).subquery()
		
		totals = DBSession.query(invociequery.count().label('Invoices'),\
								purchasequery.count().label('Purchases'),\
								itemquery.count().label('Products'),\
								customerquery.count().label('Customers'),\
								supplierquery.count().label('Suppliers')).first()
		
		return totals
