from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.url import route_url
from pyramid_handlers import action
from pyramid.view import view_config
from pyramid.response import Response

from ..models.User import User, UserContactDetails
from ..models.Tenant import Tenant, TenantContactDetails
from ..services.SecurityService import SecurityService
from ..services.TenantService import TenantService

from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..forms import TenantSchema, UserSchema, ContactSchema, TenantContactSchema, UserContactSchema
from ..library.helpers import EncryptPassword
from datetime import datetime

from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
tenantService = TenantService()

def includeme(config):
	config.add_handler('tenant','tenant/{action}', TenantController)
	pass

class TenantController(object):
	"""
		Tenant Management Controller/View
	"""
	def __init__(self, request):
		self.request = request
		
	@action(renderer='templates/tenant/index.jinja2')
	def index(self):
		lstTenants = tenantService.GetActiveTenants()
		return dict(model=lstTenants)
		pass
	
	@action(renderer='templates/tenant/manage.jinja2')	
	def manage(self):
		errors = None
		tenantId = self.request.params.get('tenantId',None)
		#log.info('TenantId: %s' % tenantId)
		if tenantId: #edit
			tenant = tenantService.GetTenantDetails(tenantId)
			
			if not tenant:
				return HTTPFound(location='/tenant/index')
			
			if len(tenant.AdminUser.Contacts) <= 0:
				tenant.AdminUser.Contacts.append(UserContactDetails())
				
			tenantForm = Form(self.request,schema=TenantSchema,obj=tenant)
			adminUserForm = Form(self.request,schema=UserSchema,obj=tenant.AdminUser)
			contactForm = vForm(request=self.request,prefix='tenantcontact-',schema=ContactSchema,obj=tenant.Contacts[0])
			userContactForm = vForm(request=self.request,prefix='usercontact-',schema=ContactSchema,obj=tenant.AdminUser.Contacts[0])
			
			valid = tenantForm.validate()
			valid = adminUserForm.validate() and valid
			valid = contactForm.validate() and valid
			valid = userContactForm.validate() and valid
			if valid:
				tenantForm.bind(tenant)
				adminUserForm.bind(tenant.AdminUser)
				contactForm.bind(tenant.Contacts[0])
				userContactForm.bind(tenant.AdminUser.Contacts[0])
				
				tenant.AdminUser.TenantId = tenant.Id
				tenant.UpdatedBy = tenant.AdminUser.UpdatedBy = self.request.user.Id
				tenant.UpdatedOn = tenant.AdminUser.UpdatedOn = datetime.utcnow()
				
				tenantService.SaveTenant(tenant)
				return HTTPFound(location='/tenant/index')

		else: #new
			tenantForm = Form(self.request,schema=TenantSchema,defaults={})
			adminUserForm = Form(self.request,schema=UserSchema,defaults={})
			contactForm = vForm(request=self.request,prefix='tenantcontact-',schema=ContactSchema,defaults={})
			userContactForm = vForm(request=self.request,prefix='usercontact-',schema=ContactSchema,defaults={})
			
			valid = tenantForm.validate()
			valid = adminUserForm.validate() and valid
			valid = contactForm.validate() and valid
			valid = userContactForm.validate() and valid
			if valid:
				tenant = tenantForm.bind(Tenant())
				adminUser = adminUserForm.bind(User())
				contact = contactForm.bind(TenantContactDetails())
				userContact = userContactForm.bind(UserContactDetails())
				
				adminUser.Contacts.append(userContact)
				adminUser.TenantId = tenant.Id
				adminUser.Password = EncryptPassword(tenant.Name)
				adminUser.Status = True
				tenant.CreatedBy = adminUser.CreatedBy = self.request.user.Id
				tenant.CreatedOn = adminUser.CreatedOn = datetime.utcnow()
				tenant.Status = True
				
				tenant.AdminUser = adminUser
				tenant.Contacts.append(contact)
				
				try:
					if tenantService.ProvisionTenant(tenant):
						return HTTPFound(location='/tenant/index')
				except Exception,e:
					errors = e
			else:
				tenant = Tenant()
				tenant.AdminUser = User()
				tenant.Contacts.append(TenantContactDetails())
				tenant.AdminUser.Contacts.append(UserContactDetails())

		return dict(model=tenant,tfr=vFormRenderer(tenantForm),
					ufr=vFormRenderer(adminUserForm),
					cfr=vFormRenderer(contactForm),
					ucfr=vFormRenderer(userContactForm),errors=errors)
		pass
		
	@action()
	def delete(self):
		tenantId = self.request.params.get('tenantId',None)
		if tenantId:
			tenant = tenantService.DeleteTenant(tenantId)
		return HTTPFound(location='tenant/index')
	pass

