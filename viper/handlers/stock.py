from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
from pyramid.response import Response

from ..models.User import User
from ..models.Tenant import Tenant
from ..models.Product import Product
from ..services.SecurityService import SecurityService
from ..services.TenantService import TenantService
from ..services.StockService import StockService

from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..forms import ProductSchema
from datetime import datetime

from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
tenantService = TenantService()
stockService = StockService()

def includeme(config):
	config.add_handler('stock','stock/{action}', StockController)
	config.add_handler('stock_index','/stock',handler=StockController,action='index')
	config.add_handler('editproduct', '/stock/manangeproduct/{pid}',handler=StockController,action='manageproduct')
	config.add_handler('deleteproduct', '/stock/deleteproduct/{pid}',handler=StockController,action='deleteProduct')
	config.add_route('products', '/stock/products')
	config.add_route('addproduct', '/stock/manageproduct')
	config.add_route('saveproduct', '/stock/manageproduct')
	pass

class StockController(object):
	"""
		Stock Management Controller/View
	"""
	def __init__(self, request):
		self.request = request
		self.TenantId = self.request.user.TenantId
		self.UserId = self.request.user.Id
		
	@action(renderer='templates/stock/index.jinja2')
	def index(self):
		return {}
		
	@action(renderer='templates/stock/products/index.jinja2')
	def products(self):
		pageNo = self.request.params.get('pageNo',0)
		pageSize = self.request.params.get('pageSize', 50)
		searchValue = self.request.params.get('searchValue', None)
		searchField = self.request.params.get('searchField', 'Name')
		
		lstProducts = stockService.GetProducts(self.TenantId,\
				pageNo,pageSize,searchField,searchValue)
		
		return dict(model=lstProducts)
	
	@action(renderer='templates/stock/products/manage.jinja2')
	def manageproduct(self):
		errors = None
		pid = self.request.matchdict.get('pid',None)
		try:
			if pid:
				model = stockService.GetProduct(pid,self.TenantId)
			
				if not model:
					return HTTPFound(location='/stock/products')
			
				pForm = Form(self.request,schema=ProductSchema,obj=model)

				if pForm.validate():
					pForm.bind(model)
					model.UpdatedBy = self.UserId
					if stockService.SaveProduct(model):
						return HTTPFound(location='/stock/products')
					else:
						errors='Unable to add product details!'
			else:
				model = Product()
				pForm = Form(self.request,schema=ProductSchema,defaults=model.toDict())
			
				if pForm.validate():
					model = pForm.bind(Product())
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True
					if stockService.AddProduct(model):
						return HTTPFound(location='/stock/products')
					else:
						errors='Unable to save product details!'
		except Exception, e:
			errors = str(e)
			
		return dict(model=model,renderer=vFormRenderer(pForm),errors=errors)
		
	@action()	
	def deleteProduct(self,request):
		pid = self.request.matchdict.get('pid',None)
		val = stockService.DeleteProduct(pid,self.TenantId)
		return HTTPFound(location='/stock/products')
	pass

