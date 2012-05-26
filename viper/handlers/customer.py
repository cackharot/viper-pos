from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
from pyramid.response import Response

from ..models.Customer import Customer, CustomerContactDetails
from ..services.SecurityService import SecurityService
from ..services.CustomerService import CustomerService

from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..forms import CustomerSchema, ContactSchema
from datetime import datetime

from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
customerService = CustomerService()

def includeme(config):
	config.add_handler('customers','customers/{action}', CustomerController)
	config.add_handler('editcustomer', '/customers/manage/{cid}',handler=CustomerController,action='manage')
	config.add_handler('customers_index','/customers',handler=CustomerController,action='index')
	config.add_handler('deletecustomer', '/customers/delete/{cid}',handler=CustomerController,action='delete')
	config.add_route('addcustomer', '/customers/manage')
	config.add_route('savecustomer', '/customers/manage')
	config.add_route('searchcustomer', '/customers/search')
	pass

class CustomerController(object):
	"""
		Customer Management Controller/View
	"""
	def __init__(self, request):
		self.request = request
		self.TenantId = self.request.user.TenantId
		self.UserId = self.request.user.Id
		
	@action(renderer='templates/customers/index.jinja2')
	def index(self):
		pageNo = self.request.params.get('pageNo',0)
		pageSize = self.request.params.get('pageSize', 50)
		searchValue = self.request.params.get('searchValue', None)
		searchField = self.request.params.get('searchField', 'name')
		
		lstCustomers = customerService.SearchCustomers(self.TenantId,\
				pageNo,pageSize,searchField,searchValue)
		
		return dict(model=lstCustomers)
		
	@action(renderer='json')
	def search(self):
		try:
			searchValue = self.request.params.get('search')
			searchField = self.request.params.get('field','name')
			result = customerService.SearchCustomers(self.TenantId,0,10,searchField,searchValue)
			if result:
				lst = [dict(id=x.Id,name=x.Contacts[0].FirstName,mobile=x.Contacts[0].Mobile) for x in result]
				return dict(mylist=lst)
			return dict(error='Not found!')
		except Exception, e:
			return dict(error=str(e))
	
	@action(renderer='templates/customers/manage.jinja2')
	def manage(self):
		errors = None
		
		if self.request.method == 'POST':
			cid = self.request.params.get('cid',None)
		else:
			cid = self.request.matchdict.get('cid',None)

		try:
			if cid:
				model = customerService.GetCustomer(cid,self.TenantId)
			
				if not model:
					return HTTPFound(location='/customers/index')
				
				form = Form(self.request,schema=CustomerSchema,obj=model)
				cntform = Form(self.request,schema=ContactSchema,obj=model.Contacts[0])
				
				if form.validate() and cntform.validate():
					form.bind(model)
					cntform.bind(model.Contacts[0])
					
					model.UpdatedBy = self.UserId
					model.Status = True
					
					if customerService.SaveCustomer(model):
						return HTTPFound(location='/customers/index')
					else:
						errors='Unable to add customer details!'
			else:
				model = Customer()
				form = Form(self.request,schema=CustomerSchema,defaults={})
				cntform = Form(self.request,schema=ContactSchema,defaults={})
				
				if form.validate() and cntform.validate():
					model = form.bind(Customer())
					contact = cntform.bind(CustomerContactDetails())
					
					model.Contacts.append(contact)
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True
					log.info('adding new customer')
					if customerService.AddCustomer(model):
						return HTTPFound(location='/customers/index')
					else:
						errors='Unable to save customer details!'
		except Exception,e:
			log.debug(str(e))
			errors = str(e)
		
		return dict(model=model,renderer=vFormRenderer(form),cfr=vFormRenderer(cntform),errors=errors)
		
	@action()	
	def delete(self):
		cid = self.request.matchdict.get('cid',None)
		val = customerService.DeleteCustomer(cid,self.TenantId)
		return HTTPFound(location='/customers/index')
	pass
