from datetime import datetime
import json
import uuid

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
