from formencode import Schema, validators
#from formencode import variabledecode

class TenantSchema(Schema):
	#pre_validators = [variabledecode.NestedVariables()]
	filter_extra_fields = True
	allow_extra_fields = True
	ignore_key_missing = True
	Name  = validators.MinLength(4,not_empty=True,messages=dict(empty='Enter a valid Tenant Name!'))
	Description = validators.MinLength(4, not_empty=False)
	Website  = validators.URL(not_empty=True,messages=dict(empty='Enter tenant\'s Website!'))
	Url  = validators.URL(not_empty=True,messages=dict(empty='Enter tenant\'s Url to access this application!'))
	pass
