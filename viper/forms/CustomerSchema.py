from formencode import Schema, validators, ForEach

from .ContactSchema import ContactSchema

class CustomerSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	CustomerNo = validators.Number(strip=True, not_empty=True, messages=dict(empty='Unique Customer Number is required!', invalid='Should be numeric!'))
	pass
