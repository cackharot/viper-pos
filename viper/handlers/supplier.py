from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
from pyramid.response import Response

from ..models.Supplier import Supplier, SupplierContactDetails
from ..services.SecurityService import SecurityService
from ..services.SupplierService import SupplierService

from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..forms import SupplierSchema, ContactSchema
from datetime import datetime

from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
supplierService = SupplierService()

def includeme(config):
	config.add_handler('suppliers','suppliers/{action}', SupplierController)
	config.add_handler('editsupplier', '/suppliers/manage/{sid}',handler=SupplierController,action='manage')
	config.add_handler('supplier_index','/suppliers',handler=SupplierController,action='index')
	config.add_handler('deletesupplier', '/suppliers/delete/{sid}',handler=SupplierController,action='delete')
	config.add_route('addsupplier', '/suppliers/manage')
	config.add_route('savesupplier', '/suppliers/manage')
	config.add_route('searchsupplier', '/suppliers/search')
	pass

class SupplierController(object):
	"""
		Supplier Management Controller/View
	"""
	def __init__(self, request):
		self.request = request
		self.TenantId = self.request.user.TenantId
		self.UserId = self.request.user.Id
		
	@action(renderer='templates/suppliers/index.jinja2')
	def index(self):
		pageNo = self.request.params.get('pageNo',0)
		pageSize = self.request.params.get('pageSize', 50)
		searchValue = self.request.params.get('searchValue', None)
		searchField = self.request.params.get('searchField', 'name')
		
		lstSuppliers = supplierService.SearchSupplier(self.TenantId,\
				pageNo,pageSize,searchField,searchValue)
		
		return dict(model=lstSuppliers)
		
	@action(renderer='json')
	def search(self):
		try:
			searchValue = self.request.params.get('search')
			searchField = self.request.params.get('field','name')
			result = supplierService.SearchSupplier(self.TenantId,0,10,searchField,searchValue)
			if result:
				lst = [dict(id=x.Id,name=x.Name,contactname=x.Contacts[0].FirstName,mobile=x.Contacts[0].Mobile) for x in result]
				return dict(mylist=lst)
			return dict(error='Not found!')
		except Exception, e:
			return dict(error=str(e))
	
	@action(renderer='templates/suppliers/manage.jinja2')
	def manage(self):
		errors = None
		
		if self.request.method == 'POST':
			sid = self.request.params.get('sid',None)
		else:
			sid = self.request.matchdict.get('sid',None)

		try:
			if sid: #edit
				model = supplierService.GetSupplier(sid,self.TenantId)
			
				if not model:
					return HTTPFound(location='/suppliers/index')
				
				form = Form(self.request,schema=SupplierSchema,obj=model)
				cntform = vForm(prefix='suppliercontact-',request=self.request,schema=ContactSchema,obj=model.Contacts[0])
				
				valid = form.validate() 
				valid = cntform.validate() and valid
				
				if valid:
					form.bind(model)
					cntform.bind(model.Contacts[0])
					
					model.UpdatedBy = self.UserId
					model.Status = True
					
					if supplierService.SaveSupplier(model):
						return HTTPFound(location='/suppliers/index')
					else:
						errors='Unable to add suppliers details!'
			else: #add
				model = Supplier()
				form = Form(self.request,schema=SupplierSchema,defaults={})
				cntform = vForm(prefix='suppliercontact-',request=self.request,schema=ContactSchema,defaults={})
				
				valid = form.validate() 
				valid = cntform.validate() and valid
				
				if valid:
					model = form.bind(Supplier())
					contact = cntform.bind(SupplierContactDetails())
					
					model.Contacts.append(contact)
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True

					if supplierService.AddSupplier(model):
						return HTTPFound(location='/suppliers/index')
					else:
						errors='Unable to save suppliers details!'
		except Exception,e:
			errors = str(e)
		
		return dict(model=model,renderer=vFormRenderer(form),cfr=vFormRenderer(cntform),errors=errors)
		
	@action()	
	def delete(self):
		sid = self.request.matchdict.get('sid',None)
		val = supplierService.DeleteSupplier(sid,self.TenantId)
		return HTTPFound(location='/suppliers/index')
	pass

