from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
#from pyramid.response import Response

from ..models.User import User, UserContactDetails
from ..models.Tenant import Tenant, TenantContactDetails

from ..services.SecurityService import SecurityService
from ..services.UserService import UserService
from ..services.TenantService import TenantService
from ..services.SettingService import SettingService
from ..services.ServiceExceptions import SettingException, TenantException

from ..forms import TenantSchema, UserSchema, ContactSchema, TenantContactSchema, UserContactSchema
from ..library.helpers import EncryptPassword

from datetime import datetime

from pyramid_simpleform import Form
from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log
from viper.models.PrintTemplate import PrintTemplate

securityService = SecurityService()
userService = UserService()

def includeme(config):
    config.add_handler('adminhandler', 'admin/{action}', AdminController)
    config.add_route('admin','/admin/index')
    config.add_route('settings','/admin/settings')
    config.add_route('addnewtemplate','/admin/managetemplates')
    config.add_route('tags','/admin/tags')
    
    config.add_route('templatesettings','/admin/templates')
    config.add_handler('managetemplates', '/admin/managetemplates/{tid}', handler=AdminController, action='managetemplates')
    config.add_handler('deletetemplates', '/admin/deletetemplates/{tid}', handler=AdminController, action='deletetemplates')
    
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
    
    @action(renderer='templates/admin/tags.jinja2')
    def tags(self):
        return dict()
    
    @action(renderer='templates/admin/templates.jinja2')
    def templates(self):
        service = SettingService()
        model = service.GetPrintTemplates(self.TenantId)
        return dict(model=model)
    
    @action()
    def deletetemplates(self):
        templateIds = self.request.matchdict.get('tid',None)
        if templateIds:
            service = SettingService()
            for templateId in templateIds.split(','):
                service.DeletePrintTemplate(self.TenantId, templateId)
        return HTTPFound(location=self.request.route_url('templatesettings'))
    
    @action(renderer='templates/admin/managetemplates.jinja2')
    def managetemplates(self):
        templateId = self.request.matchdict.get('tid',None)
        errors = None
        service = SettingService()
        try:
            if templateId:
                template = service.GetPrintTemplateById(templateId, self.TenantId)
            else:
                template = PrintTemplate()
                
            if self.request.method == 'POST':
                template.TenantId = self.TenantId
                template.Name = self.request.params.get('Name',None)
                if template.Name:
                    template.Name = template.Name.strip()
                template.Content = self.request.params.get('Content',None)
                if template.Content:
                    template.Content = template.Content.strip()
                template.Status = self.request.params.get('Status',True)
                if template.Status == 'True':
                    template.Status = True
                else:
                    template.Status = False
                service.SavePrintTemplate(template)
                
                return HTTPFound(location=self.request.route_url('templatesettings'))
        except SettingException,e:
            log.error(e)
            errors = e.message
            
        return dict(model=template,errors=errors)
    
    @action(renderer='templates/admin/modules.jinja2')
    def modules(self):
        return dict()