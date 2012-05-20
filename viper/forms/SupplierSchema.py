from formencode import Schema, validators, ForEach

from .ContactSchema import ContactSchema

class SupplierSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	Name 		= validators.MinLength(5,strip=True,not_empty=True,messages=dict(empty='Agency name is required!'))
	Address 	= validators.String(strip=True,not_empty=True,messages=dict(empty='Agency Address is required!'))
	Description = validators.String(strip=True,not_empty=True,messages=dict(empty='Agency Description is required!'))
	pass
