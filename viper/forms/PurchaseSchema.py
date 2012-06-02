from formencode import Schema, validators, ForEach

class PurchaseSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	PurchaseNo	= validators.Number(strip=True,not_empty=True,messages=dict(empty='Bill No is required!'))
	SupplierId 	= validators.String(strip=True,not_empty=True,messages=dict(empty='Supplier is required!'))
	PurchaseDate= validators.DateValidator(strip=True,not_empty=True,messages=dict(empty='Purchsae date is required!'))
	pass
	
class PurchaseLineItemSchema(Schema):
	filter_extra_fields = True
	allow_extra_fields = True
	PurchaseId= validators.String(strip=True,not_empty=False)
	ProductId = validators.String(strip=True,not_empty=False)
	Name      = validators.String(strip=True,not_empty=True,messages=dict(empty='Name is required!'))
	Barcode   = validators.String(strip=True,not_empty=True,messages=dict(empty='Barcode is required!'))
	MRP       = validators.Number(strip=True,not_empty=True,messages=dict(empty='MRP is required!',invalid='MRP must be a decimal number!'))
	Tax       = validators.Number(strip=True,not_empty=True,messages=dict(empty='Tax is required!',invalid='Tax must be a decimal number!'))
	BuyPrice  = validators.Number(strip=True,not_empty=True,messages=dict(empty='Buy Price is required!',invalid='Buy Price must be a decimal number!'))
	Discount  = validators.Number(strip=True,not_empty=True,if_missing=0.0,messages=dict(invalid='Discount must be a decimal number!'))
	Quantity  = validators.Number(strip=True,not_empty=True,if_missing=0.0,messages=dict(invalid='Quantity must be a decimal number!'))
	pass
