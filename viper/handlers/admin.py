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
        tenantForm = None
        contactForm = None
        adminUserForm = None
        userContactForm = None
        try:
            tenantService = TenantService()
            tenant = tenantService.GetTenantDetails(self.TenantId)
    
            if len(tenant.AdminUser.Contacts) <= 0:
                tenant.AdminUser.Contacts.append(UserContactDetails())
    
            tenantForm = Form(self.request, schema=TenantSchema, obj=tenant)
            adminUserForm = Form(self.request, schema=UserSchema, obj=tenant.AdminUser)
            contactForm = vForm(request=self.request, prefix='tenantcontact-', schema=ContactSchema, obj=tenant.Contacts[0])
            userContactForm = vForm(request=self.request, prefix='usercontact-', schema=ContactSchema, obj=tenant.AdminUser.Contacts[0])
    
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
        except Exception,e:
            log.info(e)
            errors = e.message
            
        return dict(model=tenant, tfr=vFormRenderer(tenantForm),
                    ufr=vFormRenderer(adminUserForm),
                    cfr=vFormRenderer(contactForm),
                    ucfr=vFormRenderer(userContactForm), errors=errors)
    
    @action(renderer='templates/admin/settings.jinja2')
    def settings(self):
        return dict()
    
    @action(renderer='templates/admin/templates.jinja2')
    def templates(self):
        return dict()
    
    @action(renderer='templates/admin/modules.jinja2')
    def modules(self):
        return dict()