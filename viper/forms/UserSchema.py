from formencode import Schema, validators

class UserSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	UserName  = validators.MinLength(4, not_empty=True,messages=dict(empty='Username is required!'))
	#Password  = validators.MinLength(4, not_empty=False,messages=dict(empty='Enter valid Password!'))
	pass
