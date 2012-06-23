import json
from datetime import datetime, date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc, func, cast, Date

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

	def GetInvoiceTotals(self, tenantId):
		"""
			Calculates invoice totals, amounts, due, etc.,
		"""
		if tenantId:
			osq = DBSession.query(LineItem.OrderId, func.sum(LineItem.Quantity * LineItem.SellPrice).label('OrderAmount'))
			osq = osq.join(Order, Order.Id == LineItem.OrderId).group_by(LineItem.OrderId).subquery()
	
			psq = DBSession.query(OrderPayment.OrderId, func.sum(OrderPayment.PaidAmount).label('PaidAmount'))
			psq = psq.join(Order, Order.Id == OrderPayment.OrderId).group_by(OrderPayment.OrderId).subquery()
	
			query = DBSession.query(func.count(Order.Id).label('Count'), \
								 func.ifnull(func.sum(osq.c.OrderAmount),0).label('TotalAmount'), \
								 func.ifnull(func.sum(func.IF(psq.c.PaidAmount>=osq.c.OrderAmount,osq.c.OrderAmount,psq.c.PaidAmount)),0).label('PaidAmount'))
			query = query.outerjoin(osq, osq.c.OrderId == Order.Id).outerjoin(psq, psq.c.OrderId == Order.Id)
			
			query = query.filter(Order.TenantId == tenantId, Order.Status == True)
			
			totals = query.first()
			
			if totals:
				oq = query.filter(osq.c.OrderAmount > psq.c.PaidAmount, Order.DueDate<func.now()).subquery()
				totals.Overdues = DBSession.query(oq.c.Count,\
												(oq.c.TotalAmount-oq.c.PaidAmount).label('OverdueAmount')).first() 
			
			return totals
		return None
	
	def GetPurchaseTotals(self, tenantId):
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
			
			totals = query.first()
			
			if totals:
				oq = query.filter(a.c.PurchaseAmount > b.c.PaidAmount, Purchase.DueDate < func.now()).subquery()
				totals.Overdues = DBSession.query(oq.c.Count,\
												(oq.c.TotalAmount-oq.c.PaidAmount).label('OverdueAmount')).first() 
			
			return totals
		return None
	
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
