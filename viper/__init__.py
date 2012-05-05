from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from models import DBSession
from viper.views import customers,stock,sales

def main(global_config, **settings):
    """ 
    	This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.include(sales.includeme)
    config.include(stock.includeme)
    config.include(customers.includeme)
    config.scan()
    return config.make_wsgi_app()
