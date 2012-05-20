from datetime import datetime
import json
import uuid
from pyramid.events import subscriber
from pyramid.events import NewRequest

from .ViperLog import log

def jsonHandler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj,uuid.UUID):
    	return str(obj)
    else:
        #raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))
        return None

import sha
Salt = '!@#$#@!'
        
def EncryptPassword(password):
	if password:
		return sha.new('%s--%s' % (password,Salt)).hexdigest()
	return None
	
def _TryUpdateModel(request):
	req = request
	def UpdateModel(model,prefix=None):
		if req.method == 'POST':
			#log.info(req.params)
			log.info(model)
			
			for k, v in req.params.items():
				nk = k
				if prefix:
					nk = k.replace(prefix,'')
				if hasattr(model, nk):
					log.info('Updating Attribute: %s=%s' % (nk,v))
					setattr(model,nk,v)
		
			return True
		else:
			return False
		pass
	return UpdateModel

@subscriber(NewRequest)
def new_request(event):
	request = event.request
	#log.info('Attaching "TryUpdateModel" to request object.')
	request.set_property(_TryUpdateModel, 'TryUpdateModel', reify=True)
