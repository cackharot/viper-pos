from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.url import route_url
from pyramid_handlers import action
from pyramid.view import view_config
from pyramid.response import Response
from ..models import User
from ..services.SecurityService import SecurityService
from pyramid.view import forbidden_view_config

import logging
log = logging.getLogger(__name__)

securityService = SecurityService()

from pyramid.security import Allow, Everyone

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'everybody'),
                (Allow, 'basic', 'entry'),
                (Allow, 'secured', ('entry', 'topsecret'))
              ]
    def __init__(self, request):
        pass

#@view_config(renderer='templates/login/login.jinja2',context='pyramid.exceptions.Forbidden')
def forbidden(request):
	return {'companycode':'', 'username':'', 'password':'', 'message':''}

class Auth(object):
	"""
		User Authentication handler
	"""
	def __init__(self, request):
		self.request = request

	@view_config(renderer='templates/login/login.jinja2',context='pyramid.exceptions.Forbidden')
	@action(renderer='templates/login/login.jinja2')
	def login(self):
		log.info('login called')
		log.info(self.request.params)
		if 'submitlogin' in self.request.params:
			companycode = self.request.params['companycode']
			username = self.request.params['username']
			password = self.request.params['password']
			userid = securityService.ValidateUser(companycode,username,password)
			log.debug('userid: %s' % userid)
			if userid is not None:
				headers = remember(self.request, userid)
				home = route_url('home', self.request)
				return HTTPFound(location=home, headers=headers)
			message = 'Please check your company code or username or password'
			return dict(message=message, companycode=companycode, username=username, password=password)
		else:
			return {'companycode':'', 'username':'', 'password':'', 'message':''}

	def logout(self):
		headers = forget(self.request)
		loginpage = route_url('login', self.request)
		return HTTPFound(location=loginpage, headers=headers)
