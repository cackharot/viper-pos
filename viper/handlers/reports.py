from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid_handlers import action
from pyramid.view import view_config
from pyramid.response import Response

from ..models.Order import OrderSearchParam
from ..models.Purchase import PurchaseSearchParam

from ..services.SecurityService import SecurityService
from ..services.StockService import StockService
from ..services.SupplierService import SupplierService
from ..services.OrderService import OrderService
from ..services.ReportService import ReportService

from collections import namedtuple

import logging
log = logging.getLogger(__name__)

def includeme(config):
	config.add_handler('reportshandler', 'reports/{action}', ReportController)
	
	config.add_route('reports','/reports/index')
	pass

class SearchParam(object):
	TenantId 		= None
	FromDate		= None
	ToDate			= None
	Status			= None
	CustomerId		= None
	CustomerName	= None
	SupplierId		= None
	SupplierName	= None
	MinAmount		= None
	MaxAmount		= None
	QuickDates		= None
	IpAddress		= None
	PurchaseNo		= None
	InvoiceNo		= None
	PurchaseAmount	= None
	PurchaseDate	= None
	InvoiceDate		= None
	Credit			= False
	InvoiceStatus   = None
	
	def __init__(self):
		pass

class ReportController(object):
	"""
		Basic Report Handler
	"""
	def __init__(self, request):
		self.request = request
		self.UserId = request.user.Id
		self.TenantId = request.user.TenantId
	
	def getDateFmt(self,value):
		from ..library.filters import todatetime
		return todatetime(value)
		
	@action(renderer='/reports/index.jinja2')
	def index(self):
		service = ReportService()
		invoiceTotals  = service.GetInvoiceTotals(self.TenantId)
		purchaseTotals = service.GetPurchaseTotals(self.TenantId)
		totals = service.GetTotals(self.TenantId)
		return dict(status=True,invoice=invoiceTotals,purchase=purchaseTotals,totals=totals)
	
	@action(renderer='/reports/invoices.jinja2')
	def invoices(self):
		param = SearchParam()
		param.FromDate = self.getDateFmt(self.request.params.get('fromDate',None))
		param.ToDate = self.getDateFmt(self.request.params.get('toDate',None))
		param.Status = self.request.params.get('status',None)
		param.CustomerName = self.request.params.get('customerName',None)
		param.QuickDates = self.request.params.get('search_quick_dates',None)
		
		service = ReportService()
		invoiceTotals  = service.GetInvoiceTotals(self.TenantId, param)
		
		if self.request.is_xhr:
			self.request.override_renderer = '/reports/partialInvoices.jinja2'
		
		return dict(invoice=invoiceTotals)
	
	@action(renderer='/reports/purchases.jinja2')
	def purchases(self):
		param = SearchParam()
		param.FromDate = self.getDateFmt(self.request.params.get('fromDate',None))
		param.ToDate = self.getDateFmt(self.request.params.get('toDate',None))
		param.Status = self.request.params.get('status',None)
		param.SupplierId = self.request.params.get('supplierId',None)
		param.QuickDates = self.request.params.get('search_quick_dates',None)
		
		service = ReportService()
		purchaseTotals  = service.GetPurchaseTotals(self.TenantId, param)
		
		lstSuppliers = None
		if self.request.is_xhr:
			self.request.override_renderer = '/reports/partialPurchases.jinja2'
		else:
			lstSuppliers = self.GetSuppliers()
		return dict(purchase=purchaseTotals,suppliers=lstSuppliers)
	
	def products(self):
		return HTTPFound(location='/reports/index')

	def customers(self):
		return HTTPFound(location='/reports/index')
	
	def suppliers(self):
		return HTTPFound(location='/reports/index')
	
	def GetSuppliers(self):
		lstSuppliers = SupplierService().GetSuppliers(self.TenantId)
		if lstSuppliers:
			lstSuppliers = [[str(x.Id), x.Name] for x in lstSuppliers]
		return lstSuppliers

	@action(renderer='json')
	def getreturnproducts(self):
		stockService = StockService()
		ids, total = stockService.GetReturnableProductIds(self.TenantId, 0, 20)
		if ids and len(ids) > 0:
			items, total = stockService.GetProductStock(self.TenantId, 1000, [x.Id for x in ids])
			if items and len(items) > 0:
				return dict(status=True, total=total, items=[dict(SupplierName=x.SupplierName, Barcode=x.Barcode, Name=x.Name, MRP=x.MRP, Stock=x.Stock) for x in items])
		return dict(status=False)

	@action(renderer='json')
	def lowstocks(self):
		minStock = self.request.params.get('minStock', 1000)
		stockService = StockService()
		items, total = stockService.GetProductStock(self.TenantId, minStock)
		if items and len(items) > 0:
			return dict(status=True, total=total, items=[dict(SupplierName=x.SupplierName, Barcode=x.Barcode, Name=x.Name, MRP=x.MRP, Stock=x.Stock) for x in items])
		return dict(status=False)

	@action(renderer='json')
	def creditpurchases(self):
		param = PurchaseSearchParam()
		param.TenantId = self.TenantId
		param.PageNo = self.request.params.get('pageNo', 0)
		param.PageSize = self.request.params.get('pageSize', 10)
		param.SupplierId = self.request.params.get('supplierId', None)
		param.Credit 	 = True

		stockService = StockService()
		items, stat = stockService.SearchPurchases(param)
		if items and len(items) > 0:
			return dict(status=True, total=stat.ItemsCount,
								items=[dict(PurchaseNo=x.PurchaseNo,
								SupplierName=x.SupplierName,
								PurchaseDate=x.PurchaseDate,
								PurchaseAmount=x.PurchaseAmount,
								PaidAmount=x.PaidAmount) for x in items])
		return dict(status=False)

	@action(renderer='json')
	def creditorders(self):
		param = OrderSearchParam()
		param.TenantId = self.TenantId
		param.CustomerId = self.request.params.get('customerId', None)
		param.PageNo = self.request.params.get('pageNo', 0)
		param.PageSize = self.request.params.get('pageSize', 10)
		param.Credit = True

		service = OrderService()
		items, stat = service.SearchOrders(param)

		if items and len(items) > 0:
			return dict(status=True, total=stat.ItemsCount,
								items=[dict(OrderNo=x.OrderNo,
								CustomerName=x.Customer.Contacts[0].FirstName,
								OrderDate=x.OrderDate,
								OrderAmount=(x.OrderAmount),
								PaidAmount=(x.PaidAmount)) for x in items])
		return dict(status=False)

