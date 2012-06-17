from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
from pyramid.response import Response

from ..models import DBSession
from ..models.User import User
from ..models.Tenant import Tenant
from ..models.Product import Product
from ..models.Purchase import Purchase, PurchaseSearchParam
from ..models.PurchaseLineItem import PurchaseLineItem
from ..models.PurchasePayment import PurchasePayment

from ..services.SecurityService import SecurityService
from ..services.TenantService import TenantService
from ..services.StockService import StockService
from ..services.SupplierService import SupplierService

from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..forms import ProductSchema, PurchaseSchema, PurchaseLineItemSchema
from datetime import datetime

from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

def includeme(config):
	config.add_handler('invoice', 'invoice/{action}', InvoiceController)

	#config.add_route('invoice','/invoice/index')
	config.add_handler('searchinvoices', '/invocie/search/{searchField}/{searchValue}', InvoiceController, action='search')
	pass

class InvoiceController(object):
	"""
		Invoice Controller/View
	"""
	def __init__(self, request):
		self.request = request
		self.TenantId = self.request.user.TenantId
		self.UserId = self.request.user.Id

	@action(renderer='templates/invoice/index.jinja2')
	def index(self):
		return {}

	@action(renderer='templates/invoice/index.jinja2')
	def search(self):
		return {}

