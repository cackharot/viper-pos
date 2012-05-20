from formencode import Schema, validators, ForEach

from .ContactSchema import ContactSchema

class CustomerSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	#Contacts = ForEach(ContactSchema())
	pass
