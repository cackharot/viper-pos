from formencode import Schema, validators, ForEach

from .ContactSchema import ContactSchema

class SupplierSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	Name 		= validators.MinLength(6,not_empty=True)
	Address 	= validators.String(not_empty=True)
	Description = validators.PlainText()
	pass
