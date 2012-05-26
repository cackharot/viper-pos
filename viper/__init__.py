from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from library.security import get_user
from library.security import SaaSAuthTktAuthenticationPolicy
from library.security import UserAuthorizationPolicy
from viper.views import sales
from viper.models import DBSession

def main(global_config, **settings):
    """ 
    	This function returns a Pyramid WSGI application.
    """
     # Configure our authorization policy
    authn_policy = SaaSAuthTktAuthenticationPolicy(settings)
    authz_policy = UserAuthorizationPolicy()
    
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings,
    				    	root_factory='viper.handlers.auth.RootFactory',
    				    	authentication_policy=authn_policy,
    				    	authorization_policy=authz_policy)
    
    config.set_request_property(get_user, 'user', reify=True)
    config.include('pyramid_jinja2')
    config.include("pyramid_handlers")
    
    #config.add_translation_dirs('viper:locale/')
    
    #from viper.handlers.auth import forbidden
    #config.add_forbidden_view(forbidden)
    config.add_tween('viper.library.security.auth_tween_factory')

	#config.add_subscriber("simpleauth.subscribers.create_url_generator",       "pyramid.events.ContextFound")
    
    
    # simpleauth additions
    config.add_handler('login', '/login', 'viper.handlers.auth:Auth', action='login')
    config.add_handler('logout', '/logout', 'viper.handlers.auth:Auth', action='logout')
    
    #tenant contoller
    config.include('viper.handlers.tenant')
    config.include('viper.handlers.user')
    config.include('viper.handlers.stock')
    config.include('viper.handlers.customer')
    config.include('viper.handlers.supplier')
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('home', '/')
    config.include(sales.includeme)
    config.scan()
    return config.make_wsgi_app()

