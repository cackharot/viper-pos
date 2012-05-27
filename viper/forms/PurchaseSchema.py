from formencode import Schema, validators, ForEach

class PurchaseSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	PurchaseNo	= validators.Number(strip=True,not_empty=True,messages=dict(empty='Bill No is required!'))
	SupplierId 	= validators.String(strip=True,not_empty=True,messages=dict(empty='Supplier is required!'))
	PurchaseDate= validators.DateValidator(strip=True,not_empty=False)
	pass
