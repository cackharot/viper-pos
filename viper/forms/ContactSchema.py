from formencode import Schema, validators, compound

class ContactSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	FirstName = validators.MinLength(4, strip=True, not_empty=True, messages=dict(empty='First Name is required!', tooShort='First name should be atleast 4 letters long!'))
	LastName = validators.MinLength(4, strip=True, not_empty=False, messages=dict(tooShort='Last name should be atleast 4 letters long!'))
	Email = validators.Email(strip=True, not_empty=False, messages=dict(empty='Enter a valid email address!'))
	Phone = validators.String(strip=True, not_empty=False, messages=dict(invalid='Enter a valid phone number!'))
	Mobile = validators.Number(strip=True, not_empty=False, messages=dict(empty='Enter a valid mobile number!', invalid='Mobile number should contain only digits!'))
	Address = validators.NotEmpty(strip=True, not_empty=False, messages=dict(empty='Enter a valid address!'))
	City = validators.NotEmpty(strip=True, not_empty=False, messages=dict(empty='Enter a valid City!'))
	Country = validators.NotEmpty(strip=True, not_empty=False, messages=dict(empty='Enter a valid Country!'))
	Zipcode = compound.All(validators.Number(not_empty=False, strip=True, messages=dict(number='Enter a 6 digit zipcode!')), \
					validators.MinLength(6, messages=dict(tooShort='Zipcode should be 6 digits!')))
	pass

class TenantContactSchema(ContactSchema):
	pass

class UserContactSchema(ContactSchema):
	pass

class CustomerContactSchema(ContactSchema):
	pass
