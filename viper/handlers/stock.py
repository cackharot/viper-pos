from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
#from pyramid.response import Response

from ..models import DBSession
import json
#from ..models.User import User
#from ..models.Tenant import Tenant
from ..models.Product import Product
from ..models.Purchase import Purchase, PurchaseSearchParam
from ..models.PurchaseLineItem import PurchaseLineItem
#from ..models.PurchasePayment import PurchasePayment

from ..services.SecurityService import SecurityService
from ..services.TenantService import TenantService
from ..services.StockService import StockService
from ..services.SupplierService import SupplierService

from pyramid_simpleform import Form

from ..forms import ProductSchema, PurchaseSchema, PurchaseLineItemSchema
from datetime import datetime

from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
tenantService = TenantService()
stockService = StockService()

def includeme(config):
	config.add_handler('stock', 'stock/{action}', StockController)
	config.add_handler('stock_index', '/stock', handler=StockController, action='index')
	config.add_handler('addproduct', '/stock/products/manage', handler=StockController, action='manageproduct')
	config.add_handler('saveproduct', '/stock/products/manage', handler=StockController, action='manageproduct',request_method='POST')
	config.add_handler('editproduct', '/stock/products/manage/{pid}', handler=StockController, action='manageproduct')
	config.add_handler('deleteproduct', '/stock/products/delete/{pid}', handler=StockController, action='deleteProduct')
	config.add_handler('markreturnproduct', '/stock/products/return/{pid}', handler=StockController, action='markReturnProduct')
	
	config.add_handler('addpurchase', '/stock/purchases/manage', handler=StockController, action='managepurchase')
	config.add_handler('savepurchase', '/stock/purchases/manage', handler=StockController, action='managepurchase',request_method='POST')
	config.add_handler('editpurchase', '/stock/purchases/manage/{pid}', handler=StockController, action='managepurchase')
	config.add_handler('deletepurchase', '/stock/purchases/delete/{pid}', handler=StockController, action='deletePurchase')
	config.add_handler('purchasepayments','/stock/purchases/payments/{purchaseId}', handler=StockController, action='purchasePayments')
		
	config.add_route('products', '/stock/products')
	config.add_route('products_xhr', '/stock/products_xhr')
	config.add_route('purchases', '/stock/purchases')
	config.add_route('purchases_xhr', '/stock/purchases_xhr')
	config.add_route('savepurchasepayments', '/stock/savepurchasepayments', xhr=True)
	
class StockController(object):
	"""
		Stock Management Controller/View
	"""
	def __init__(self, request):
		self.request = request
		self.TenantId = self.request.user.TenantId
		self.UserId = self.request.user.Id

	@action(renderer='templates/stock/index.jinja2')
	def index(self):
		return {}

	@action(renderer='json')
	def getproductsbybarcode(self):
		barcode = self.request.params.get('barcode', None)
		if barcode:
			items = stockService.GetProductsByBarcode(self.TenantId, barcode)
			if items and len(items) > 0:
				return [x.toDict() for x in items]
		return dict(status=False, message='No items found for the barcode "%s"!' % barcode)

	@action(renderer='templates/stock/products/index.jinja2')
	def products(self):
		return self.getproducts()

	@action(renderer='templates/stock/products/partialItemList.jinja2', xhr=True)
	def products_xhr(self):
		return self.getproducts()

	@action(renderer='json', xhr=True)
	def updateproduct_xhr(self):
		productId = self.request.params.get('productId', None)
		if productId:
			entity = stockService.GetProduct(productId, self.TenantId)
			if entity:
				barcode = self.request.params.get('Barcode', None)
				if barcode:
					entity.Barcode = barcode

				name = self.request.params.get('Name', None)
				if name:
					entity.Name = name

				mrp = self.request.params.get('MRP', None)
				if mrp:
					entity.MRP = float(mrp)

				sellPrice = self.request.params.get('SellPrice', None)
				if sellPrice:
					entity.SellPrice = float(sellPrice)

				discount = self.request.params.get('Discount', None)
				if discount:
					entity.Discount = float(discount)

				entity.UpdatedBy = self.UserId
				stockService.SaveProduct(entity)

				return dict(status=True)

		return dict(status=False)

	def getproducts(self):
		pageNo = self.request.params.get('pageNo', 0)
		pageSize = self.request.params.get('pageSize', 20)
		searchValue = self.request.params.get('searchValue', None)
		searchField = self.request.params.get('searchField', None)

		lstProducts = stockService.GetProducts(self.TenantId, \
				pageNo, pageSize, searchField, searchValue)

		return dict(model=lstProducts,searchValue=searchValue,searchField=searchField)

	@action(renderer='templates/stock/products/manage.jinja2')
	def manageproduct(self):
		errors = None
		model = None
		if self.request.method == 'GET':
			pid = self.request.matchdict.get('pid', None)
		else:
			pid = self.request.params.get('pid', None)
		try:
			if pid:
				model = stockService.GetProduct(pid, self.TenantId)

				if not model:
					return HTTPFound(location=self.request.route_url('products'))

				pForm = Form(self.request, schema=ProductSchema, obj=model)

				if pForm.validate():
					pForm.bind(model)
					model.UpdatedBy = self.UserId
					if stockService.SaveProduct(model):
						return HTTPFound(location=self.request.route_url('products'))
					else:
						errors = 'Unable to add product details!'
			else:
				model = Product()
				pForm = Form(self.request, schema=ProductSchema, defaults=model.toDict())

				if pForm.validate():
					model = pForm.bind(Product())
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True
					if stockService.AddProduct(model):
						return HTTPFound(location=self.request.route_url('products'))
					else:
						errors = 'Unable to save product details!'
		except Exception, e:
			errors = str(e)
			log.debug(e)

		return dict(model=model, renderer=vFormRenderer(pForm), errors=errors)

	@action()
	def deleteProduct(self):
		pid = self.request.matchdict.get('pid', None)
		stockService.DeleteProduct(pid, self.TenantId)
		return HTTPFound(location=self.request.route_url('products'))

	@action(renderer='json')
	def markReturnProduct(self):
		pid = self.request.matchdict.get('pid', None)
		status = self.request.params.get('status', u'false')
		if pid:
			model = stockService.GetProduct(pid, self.TenantId)
			if model:
				model.Status = status == 'true'
				stockService.SaveProduct(model)
				if self.request.is_xhr: return dict(status=True)
				return HTTPFound(location=self.request.route_url('products'))
		if self.request.is_xhr:	return dict(status=False)
		return HTTPFound(location=self.request.route_url('products'))

	@action()
	def deletePurchase(self):
		pid = self.request.matchdict.get('pid', None)
		stockService.DeletePurchase(pid, self.TenantId)
		return HTTPFound(location=self.request.route_url('purchases'))

	@action(renderer='templates/stock/purchase/index.jinja2')
	def purchases(self):
		lstSuppliers = self.GetSuppliers()
		data = self.getPurchaseList()
		data['suppliers']=lstSuppliers
		return data

	@action(renderer='templates/stock/purchase/partialPurchaseList.jinja2', xhr=True)
	def purchases_xhr(self):
		return self.getPurchaseList()

	def getPurchaseList(self):
		param = PurchaseSearchParam()
		param.TenantId = self.TenantId
		param.PurchaseNo = self.request.params.get('billNo', None)
		param.SupplierId = self.request.params.get('supplierId', None)
		param.PageSize = self.request.params.get('pageSize', 20)
		param.PageNo = self.request.params.get('pageNo', 0)

		bdate = self.request.params.get('billDate', None)
		if bdate and len(bdate) > 0:
			param.PurchaseDate = datetime.strptime(bdate.strip(), '%d-%m-%Y')
		
		lstPurchases, stat = stockService.SearchPurchases(param)
		totalPurchases = stat.ItemsCount
		totalAmount = stat.TotalAmount
		totalDueAmount = stat.TotalAmount - stat.TotalPaidAmount        
		return dict(model=lstPurchases,totalPurchases=totalPurchases,totalAmount=totalAmount,totalDueAmount=totalDueAmount)

	def GetSuppliers(self):
		lstSuppliers = SupplierService().GetSuppliers(self.TenantId)
		if lstSuppliers:
			lstSuppliers = [[str(x.Id), x.Name] for x in lstSuppliers]
		return lstSuppliers
	
	@action(renderer='json',xhr=True)
	def purchasePayments(self):
		purchaseId = self.request.matchdict['purchaseId']
		if purchaseId:
			stockService = StockService()
			payments = stockService.GetPurchasePayments(purchaseId, self.TenantId)
			if payments:
				return dict(payments=[x.toDict() for x in payments])
		return dict(payments=None)
	
	@action(renderer='json')
	def savepurchasepayments(self):
		data = json.loads(self.request.body)
		#log.info(data)
		if data and data['purchaseId']:
			purchaseId = data['purchaseId']
			stockService = StockService()
			purchase = stockService.GetPurchase(purchaseId, self.TenantId)
			if purchase:
				for item in data['payments']:
					if item['remove'] == '1':
						stockService.DeletePurchasePayment(item['paymentId'])
					else:    
						stockService.UpdatePurchasePayment(purchaseId, item['paymentId'], item, self.UserId)
				return dict(status=True, message='Payment details saved successfully!')
		return dict(status=False, message='Error while saving payment details!')

	@action(renderer='json')
	def deletepurchaselineitem(self):
		purchaseId = self.request.params.get('purchaseId', None)
		lineItemId = self.request.params.get('lineItemId', None)

		if purchaseId and lineItemId:
			if stockService.DeletePurchaseLineItem(purchaseId, lineItemId, self.TenantId):
				return dict(status=True, message='Line Item deleted successfully!')

		return dict(status=False, message="Invalid Data!")

	@action(renderer='json')
	def addpurchaselineitem(self):
		purchaseId = self.request.params.get('pid', None)
		supplierId = self.request.params.get('SupplierId', None)
		if purchaseId and supplierId:
			model = None
			productId = self.request.params.get('ProductId', None)
			quantity = float(self.request.params.get('Quantity', 0.0))
			taxAmount = float(self.request.params.get('TaxAmount', 0.0))

			try:
				if productId:
					model = stockService.GetProduct(productId, self.TenantId)
				if not model:
					model = Product()

				pForm = Form(self.request, schema=ProductSchema, obj=model)

				if pForm.validate():
					pForm.bind(model)
					model.SupplierId = supplierId
					model.TenantId = self.TenantId
					model.Status = True

					if model.Id:
						model.UpdatedBy = self.UserId
						stockService.SaveProduct(model)
					else:
						model.CreatedBy = self.UserId
						stockService.AddProduct(model)

					litem 			 = PurchaseLineItem()
					litem.PurchaseId = purchaseId
					litem.ProductId = model.Id
					litem.Name 		 = model.Name
					litem.Barcode 	 = model.Barcode
					litem.MRP 		 = model.MRP
					litem.Tax 		 = taxAmount
					litem.BuyPrice 	 = model.BuyPrice
					litem.Discount 	 = model.Discount
					litem.Quantity 	 = quantity

					result = stockService.AddPurchaseLineItem(litem, self.TenantId)
					if result:
						return dict(status=True, id=litem.Id, message="Item added successfully!")
					else:
						DBSession.rollback()
				else:
					log.info('pForm validate failed : %s!' % (pForm.all_errors()))
					return dict(status=False, message=pForm.all_errors())
			except Exception, e:
				log.debug(e)
				return dict(status=False, message=e.message)
		return dict(status=False, message="Invalid PurchaseId or SupplierId!")

	@action(renderer='templates/stock/purchase/manage.jinja2')
	def managepurchase(self):
		errors = None
		model = None
		form = None
		productmodel = Product()
		pForm = Form(self.request, schema=ProductSchema, defaults=productmodel.toDict())

		log.info(self.request.method)

		if self.request.method == 'GET':
			pid = self.request.matchdict.get('pid', None)
		else:
			pid = self.request.params.get('pid', None)

		lstSuppliers = self.GetSuppliers()

		try:
			if pid:
				model = stockService.GetPurchase(pid, self.TenantId)

				if not model:
					return HTTPFound(location='/stock/purchases')

				form = Form(self.request, schema=PurchaseSchema, obj=model)

				if form.validate():
					form.bind(model)
					model.TenantId = self.TenantId
					model.UpdatedBy = self.UserId
					model.Status = True
					if stockService.SavePurchase(model):
							return HTTPFound(location=self.request.route_url('purchases'))					
					else:
						errors = 'Unable to save purchase details!'
			else:
				model = Purchase()
				form = Form(self.request, schema=PurchaseSchema, defaults=model.toDict())

				if form.validate():
					model = form.bind(Purchase())
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True
					if stockService.AddPurchase(model):
						return HTTPFound(location=self.request.route_url('editpurchase',pid=model.Id))
					else:
						errors = 'Unable to save purchase details!'
		except Exception, e:
			errors = str(e)
			log.debug(e)

		return dict(model=model, suppliers=lstSuppliers, renderer=vFormRenderer(pForm), purchaseRenderer=vFormRenderer(form), errors=errors)

