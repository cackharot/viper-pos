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
		items = stockService.GetProducts(self.TenantId,0,20,searchField='Status',searchValue=False)
		if items and len(items) > 0:
			return dict(status=True,items=[dict(Barcode=x.Barcode,Name=x.Name,MRP=x.MRP,Stock=0.0) for x in items])
		return dict(status=False)
		
	def logout(self):
		headers = forget(self.request)
		loginpage = route_url('login', self.request)
		return HTTPFound(location=loginpage, headers=headers)
