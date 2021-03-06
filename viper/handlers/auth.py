from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.url import route_url
from pyramid_handlers import action
from pyramid.view import view_config
#from pyramid.response import Response
from pyramid.security import Allow, Everyone

from ..services.SecurityService import SecurityService

import logging
log = logging.getLogger(__name__)

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'everybody'),
                (Allow, 'basic', 'entry'),
                (Allow, 'secured', ('entry', 'topsecret'))
              ]
    def __init__(self, request):
        pass

class Auth(object):
    """
        User Authentication handler
    """
    def __init__(self, request):
        self.request = request

    @view_config(renderer='templates/login/login.jinja2', context='pyramid.exceptions.Forbidden')
    @action(renderer='templates/login/login.jinja2')
    def login(self):
        #log.info('login called')
        #log.info(self.request.params)
        if 'companycode' in self.request.params:
            companycode = self.request.params['companycode']
            username = self.request.params['username']
            password = self.request.params['password']

            securityService = SecurityService()
            userid = securityService.ValidateUser(companycode, username, password)

            #log.debug('userid: %s' % userid)
            if userid is not None:
                headers = remember(self.request, userid)
                home = route_url('home', self.request)
                return HTTPFound(location=home, headers=headers)
            message = 'Please check your company code, username and password'
            return dict(message=message, companycode=companycode, username=username, password=password)
        else:
            return {'companycode':'', 'username':'', 'password':'', 'message':''}

    def logout(self):
        headers = forget(self.request)
        loginpage = route_url('login', self.request)
        return HTTPFound(location=loginpage, headers=headers)
