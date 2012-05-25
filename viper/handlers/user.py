from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
from pyramid.response import Response

from ..models.User import User, UserContactDetails
from ..services.SecurityService import SecurityService
from ..services.UserService import UserService

from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..forms import UserSchema, ContactSchema
from datetime import datetime

from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
userService = UserService()

def includeme(config):
	config.add_handler('users','users/{action}', UserController)
	config.add_handler('edituser', '/users/manage/{uid}',handler=UserController,action='manage')
	config.add_handler('user_index','/users',handler=UserController,action='index')
	config.add_handler('deleteuser', '/users/delete/{uid}',handler=UserController,action='delete')
	config.add_route('adduser', '/users/manage')
	config.add_route('saveuser', '/users/manage')
	config.add_route('searchuser', '/users/search')
	pass

class UserController(object):
	"""
		User Management Controller/View
	"""
	def __init__(self, request):
		self.request = request
		self.TenantId = self.request.user.TenantId
		self.UserId = self.request.user.Id
		
	@action(renderer='templates/users/index.jinja2')
	def index(self):
		pageNo = self.request.params.get('pageNo',0)
		pageSize = self.request.params.get('pageSize', 50)
		searchValue = self.request.params.get('searchValue', None)
		searchField = self.request.params.get('searchField', 'username')
		
		lstUsers = userService.SearchUser(self.TenantId,\
				pageNo,pageSize,searchField,searchValue)
		
		return dict(model=lstUsers)
		
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
	
	@action(renderer='templates/users/manage.jinja2')
	def manage(self):
		errors = None
		
		if self.request.method == 'POST':
			uid = self.request.params.get('uid',None)
		else:
			uid = self.request.matchdict.get('uid',None)

		try:
			if uid: #edit
				model = userService.GetUserDetails(uid,self.TenantId)
			
				if not model:
					return HTTPFound(location='/users/index')
				
				form = Form(self.request,schema=UserSchema,obj=model)
				cntform = vForm(prefix='usercontact-',request=self.request,schema=ContactSchema,obj=model.Contacts[0])
				
				valid = form.validate() 
				valid = cntform.validate() and valid
				
				if valid:
					form.bind(model)
					cntform.bind(model.Contacts[0])
					
					model.UpdatedBy = self.UserId
					model.Status = True
					
					if userService.SaveUser(model):
						return HTTPFound(location='/users/index')
					else:
						errors='Unable to add users details!'
			else: #add
				model = User()
				form = Form(self.request,schema=UserSchema,defaults={})
				cntform = vForm(prefix='usercontact-',request=self.request,schema=ContactSchema,defaults={})
				
				valid = form.validate() 
				valid = cntform.validate() and valid
				
				if valid:
					model = form.bind(User())
					contact = cntform.bind(UserContactDetails())
					
					model.Contacts.append(contact)
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True

					if userService.AddUser(model):
						return HTTPFound(location='/users/index')
					else:
						errors='Unable to save users details!'
		except Exception,e:
			errors = str(e)
		
		return dict(model=model,renderer=vFormRenderer(form),cfr=vFormRenderer(cntform),errors=errors)
		
	@action()	
	def delete(self):
		uid = self.request.matchdict.get('uid',None)
		val = userService.DeleteUser(uid,self.TenantId)
		return HTTPFound(location='/users/index')
	pass

