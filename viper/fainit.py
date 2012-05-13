from viper import models, faforms
import logging
from pyramid.security import Allow, Authenticated, ALL_PERMISSIONS
from pyramid_formalchemy.resources import Models

log = logging.getLogger(__name__)

class ModelsWithACL(Models):
    """A factory to override the default security setting"""
    __acl__ = [
            (Allow, 'admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
            (Allow, 'editor', 'edit'),
            (Allow, 'manager', ('new', 'edit', 'delete')),
        ]

def includeme(config):
    config.include('pyramid_formalchemy')

    try:
        # Add fanstatic tween if available
        config.include('pyramid_fanstatic')
    except ImportError:
        log.warn('You should install pyramid_fanstatic or register a fanstatic'
                 ' middleware by hand')

    try:
        # Adding the jquery libraries if available
        config.include('fa.jquery')
    except ImportError:
        model_view = 'pyramid_formalchemy.views.ModelView'
    else:
        model_view = 'fa.jquery.pyramid.ModelView'

    session_factory = getattr(models, "DBSession", None)
    if session_factory is not None:
        # pyramid_alchemy
        session_factory = 'viper.models.DBSession'
    else:
        # Akhet
        session_factory = 'viper.models.Session'

    # register session and model_view for later use
    settings = {'package': 'viper',
                'view': model_view,
                'session_factory': session_factory,
               }
    config.registry.settings['viper.fa_config'] = settings

    config.formalchemy_admin("/admin", models=models.User, 
    						forms=faforms,factory=ModelsWithACL,**settings)
    
    # Adding the package specific routes
    config.include('viper.faroutes')

    log.info('formalchemy_admin registered at /admin')
