from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.url import route_url
from pyramid.config.settings import asbool
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import unauthenticated_userid
from pyramid.authentication import AuthTktCookieHelper
from pyramid.security import Allow, Everyone, Authenticated
from pyramid.security import authenticated_userid
from zope.interface import implements

from ..models import DBSession
from ..models.User import User
import logging

log = logging.getLogger(__name__)

from pyramid.events import subscriber
from pyramid.events import BeforeRender

@subscriber(BeforeRender)
def add_global(event):
	request, context = event['request'], event['context']
	event['user'] = request.user
	#log.info(event['user'])
	pass


def auth_tween_factory(handler, registry):
    if registry.settings.get('useauth','1') == '1':
        def auth_tween(request):
			userid = None
			#log.debug('request url: %s' % request.url)#route_url('login',request))
			tokens = request.url.split('/')
			skip = False
			for x in ['admin','login','static','_debug_toolbar']:
				if x in tokens:
					skip = True
					break
			if not skip:
				log.info('checking auth')
				userid = authenticated_userid(request)
				if userid is None:
					#raise HTTPForbidden()
					return HTTPFound(location=route_url('login',request))
			response = handler(request)
			return response
        return auth_tween
    return handler


def get_user(request):
    # the below line is just an example, use your own method of
    # accessing a database connection here (this could even be another
    # request property such as request.db, implemented using this same
    # pattern).
    #log.info('called get user.')
    userid = unauthenticated_userid(request)
    if userid is not None:
        return DBSession.query(User).get(userid)
    return None

class SaaSAuthTktAuthenticationPolicy(object):
	implements(IAuthenticationPolicy)
	"""
		Custom AUthentication Ticket policy
	"""
	def __init__(self, settings):
		self.cookie = AuthTktCookieHelper(
            settings.get('auth.secret','v1p3R53cr3t'),
            cookie_name=settings.get('auth.token') or 'auth_tkt',
            secure=asbool(settings.get('auth.secure',False)),
            timeout=int(settings.get('auth.timeout',3600)),
            reissue_time=int(settings.get('auth.reissue_time',360)),
            max_age=int(settings.get('auth.max_age',3600)))
        pass

	def remember(self, request, principal, **kw):
		return self.cookie.remember(request, str(principal),**kw)

	def forget(self, request):
		return self.cookie.forget(request)

	def unauthenticated_userid(self, request):
		import uuid
		result = self.cookie.identify(request)
		if result:
			return uuid.UUID(result['userid'])

	def authenticated_userid(self, request):
		#if request.user:
		#	return request.user.id
		result = self.cookie.identify(request)
		if result:
			return result['userid']

	def effective_principals(self, request):
		principals = [Everyone]
		user = request.user
		if user:
			principals += [Authenticated, 'u:%s' % user.Id]
			principals.extend(('g:%s' % g for g in ['admin','user']))
			log.info(principals)
			#principals.extend(('g:%s' % g.name for g in user.groups))
		return principals
	
	
class UserAuthorizationPolicy(object):
	implements(IAuthorizationPolicy)
	"""
		Custom User authorization policy
	"""
	def permits(self,context,principals,permission):
		return True
		
	def principals_allowed_by_permission(self,context,permission):
		raise NotImplementedError('Method Not Implemented.')
		
	pass
