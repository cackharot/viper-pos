from formencode import Schema, validators

class ProductSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    Name = validators.String(strip=True, not_empty=True, messages=dict(empty='Name is required!'))
    Barcode = validators.String(strip=True, not_empty=True, messages=dict(empty='Barcode is required!'))
    SupplierId = validators.String(not_empty=False, if_missing=None)
    CategoryId = validators.String(strip=True, if_missing=None, not_empty=False, messages=dict(empty='Choose a category!'))
    TaxCategoryId = validators.String(strip=True, not_empty=False,if_missing=None, messages=dict(empty='Choose a Tax category!'))
    MRP = validators.Number(strip=True, not_empty=True, messages=dict(empty='MRP is required!', invalid='MRP must be a decimal number!'))
    SellPrice = validators.Number(strip=True, not_empty=True, messages=dict(empty='Sell Price is required!', invalid='Sell Price must be a decimal number!'))
    BuyPrice = validators.Number(strip=True, not_empty=True, messages=dict(empty='Buy Price is required!', invalid='Buy Price must be a decimal number!'))
    Discount = validators.Number(strip=True, not_empty=True, if_missing=0.0, messages=dict(invalid='Discount must be a decimal number!'))
    Status = validators.Bool(not_empty=False, if_missing=False)
    MfgDate = validators.DateValidator(strip=True, not_empty=False)
    ExpiryDate = validators.DateValidator(strip=True, not_empty=False)
