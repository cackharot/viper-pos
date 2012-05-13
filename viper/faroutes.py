from viper import models, faforms
import logging

log = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings.get('viper.fa_config', {})

    # Example to add a specific model
    config.formalchemy_admin("/admin_product", models=models.Product, 
							forms=faforms,**settings)
    config.formalchemy_admin("/admin_customer", models=models.Customer, 
							forms=faforms,**settings)

    log.info('viper.faroutes loaded')
