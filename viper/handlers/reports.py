from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid_handlers import action
from pyramid.view import view_config
from pyramid.response import Response

from ..models import User
from ..models import Product
from ..services.SecurityService import SecurityService
from ..services.StockService import StockService

import logging
log = logging.getLogger(__name__)

securityService = SecurityService()
stockService = StockService()

def includeme(config):
	config.add_handler('reports','reports/{action}', ReportController)
	pass

class ReportController(object):
	"""
		User Authentication handler
	"""
	def __init__(self, request):
		self.request = request
		self.UserId = request.user.Id
		self.TenantId = request.user.TenantId

	@action(renderer='json')
	def getreturnproducts(self):
		ids, total = stockService.GetReturnableProductIds(self.TenantId,0,20)
		if ids and len(ids) > 0:
			items, total = stockService.GetProductStock(self.TenantId,1000,[x.Id for x in ids])
			log.info(items)
			log.info(total)
			if items and len(items) > 0:
				return dict(status=True,total=total,items=[dict(SupplierName=x.SupplierName,Barcode=x.Barcode,Name=x.Name,MRP=x.MRP,Stock=x.Stock) for x in items])
		return dict(status=False)
		
	@action(renderer='json')
	def lowstocks(self):
		minStock = self.request.params.get('minStock',1000)
		items, total = stockService.GetProductStock(self.TenantId,minStock)
		if items and len(items) > 0:
			return dict(status=True,total=total,items=[dict(SupplierName=x.SupplierName,Barcode=x.Barcode,Name=x.Name,MRP=x.MRP,Stock=x.Stock) for x in items])
		return dict(status=False)
		
	@action(renderer='json')
	def creditpurchases(self):
		pageNo     = self.request.params.get('pageNo',0)
		pageSize   = self.request.params.get('pageSize',10)
		supplierId = self.request.params.get('supplierId',None)
		items, total = stockService.SearchPurchases(self.TenantId,pageNo,pageSize,'Credit',None)
		if items and len(items) > 0:
			return dict(status=True,total=total,
								items=[dict(PurchaseNo=x.PurchaseNo,
								SupplierName=x.SupplierName,
								PurchaseDate=x.PurchaseDate,
								PurchaseAmount=round(x.PurchaseAmount),
								PaidAmount=round(x.PaidAmount)) for x in items])
		return dict(status=False)
		
