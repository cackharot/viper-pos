from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
#from pyramid.response import Response

from ..models.User import User, UserContactDetails
from ..models.Tenant import Tenant, TenantContactDetails

from ..services.SecurityService import SecurityService
from ..services.UserService import UserService
from ..services.TenantService import TenantService

from ..forms import TenantSchema, UserSchema, ContactSchema, TenantContactSchema, UserContactSchema
from ..library.helpers import EncryptPassword

from datetime import datetime

from pyramid_simpleform import Form
from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
userService = UserService()

def includeme(config):
    config.add_handler('adminhandler', 'admin/{action}', AdminController)
    config.add_route('admin','/admin/index')
    config.add_route('settings','/admin/settings')
    config.add_route('templatesettings','/admin/templates')
    
class AdminController(object):
    """
        Admin Management Controller
    """
    def __init__(self, request):
        self.request = request
        self.TenantId = self.request.user.TenantId
        self.UserId = self.request.user.Id

    @action(renderer='templates/admin/index.jinja2')
    def index(self):
        tenant = None
        errors = None
        success = None
        tenantForm = None
        contactForm = None
        try:
            tenantService = TenantService()
            tenant = tenantService.GetTenantDetails(self.TenantId)
    
            tenantForm = Form(self.request, schema=TenantSchema, obj=tenant)
            contactForm = vForm(request=self.request, prefix='tenantcontact-', schema=ContactSchema, obj=tenant.Contacts[0])
    
            valid = tenantForm.validate()
            valid = contactForm.validate() and valid
            if valid:
                tenantForm.bind(tenant)
                contactForm.bind(tenant.Contacts[0])
    
                tenant.UpdatedBy = self.UserId
                tenant.UpdatedOn = datetime.utcnow()
    
                if tenantService.SaveTenant(tenant):
                    success = "Company details saved successfully!"
                else:
                    errors = "Error while saving Company details. Please try later." 
        except Exception,e:
            log.info(e)
            errors = e.message
            
        return dict(model=tenant, tfr=vFormRenderer(tenantForm), cfr=vFormRenderer(contactForm), errors=errors, success=success)
    
    @action(renderer='templates/admin/settings.jinja2')
    def settings(self):
        return dict()
    
    @action(renderer='templates/admin/templates.jinja2')
    def templates(self):
        return dict()
    
    @action(renderer='templates/admin/modules.jinja2')
    def modules(self):
        return dict()