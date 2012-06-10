from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
from pyramid.response import Response

from ..models import DBSession
from ..models.User import User
from ..models.Tenant import Tenant
from ..models.Product import Product
from ..models.Purchase import Purchase, PurchaseSearchParam
from ..models.PurchaseLineItem import PurchaseLineItem
from ..models.PurchasePayment import PurchasePayment

from ..services.SecurityService import SecurityService
from ..services.TenantService import TenantService
from ..services.StockService import StockService
from ..services.SupplierService import SupplierService

from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..forms import ProductSchema, PurchaseSchema, PurchaseLineItemSchema
from datetime import datetime

from ..forms.vForm import vForm
from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

securityService = SecurityService()
tenantService = TenantService()
stockService = StockService()

def includeme(config):
	config.add_handler('stock','stock/{action}', StockController)
	config.add_handler('stock_index','/stock',handler=StockController,action='index')
	config.add_handler('editproduct', '/stock/manangeproduct/{pid}',handler=StockController,action='manageproduct')
	config.add_handler('editpurchase', '/stock/manangepurchase/{pid}',handler=StockController,action='managepurchase')
	config.add_handler('deleteproduct', '/stock/deleteproduct/{pid}',handler=StockController,action='deleteProduct')
	config.add_handler('deletepurchase', '/stock/deletepurchase/{pid}',handler=StockController,action='deletePurchase')
	config.add_handler('markreturnproduct', '/stock/markreturnproduct/{pid}',handler=StockController,action='markReturnProduct')

	config.add_route('products', '/stock/products')
	config.add_route('products_xhr', '/stock/products_xhr')
	config.add_route('purchases', '/stock/purchases')
	config.add_route('purchases_xhr', '/stock/purchases_xhr')
	config.add_route('addproduct', '/stock/manageproduct')
	config.add_route('addpurchase', '/stock/managepurchase')
	config.add_route('saveproduct', '/stock/manageproduct')
	config.add_route('savepurchase', '/stock/managepurchase')
	pass

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
		barcode = self.request.params.get('barcode',None)
		if barcode:
			items = stockService.GetProductsByBarcode(self.TenantId,barcode)
			if items and len(items) > 0:
				return [x.toDict() for x in items]
		return dict(status=False,message='No items found for the barcode "%s"!' % barcode)
		
	@action(renderer='templates/stock/products/index.jinja2')
	def products(self):
		return self.getproducts()
		
	@action(renderer='templates/stock/products/partialItemList.jinja2',xhr=True)
	def products_xhr(self):
		return self.getproducts()
	
	@action(renderer='json',xhr=True)
	def updateproduct_xhr(self):
		id = self.request.params.get('id',None)
		if id:
			entity = stockService.GetProduct(id,self.TenantId)
			if entity:
				barcode = self.request.params.get('Barcode',None)
				if barcode:
					entity.Barcode = barcode
					
				name = self.request.params.get('Name',None)
				if name:
					entity.Name = name
					
				mrp = self.request.params.get('MRP',None)
				if mrp:
					entity.MRP = float(mrp)
					
				sellPrice = self.request.params.get('SellPrice',None)
				if sellPrice:
					entity.SellPrice = float(sellPrice)
					
				discount = self.request.params.get('Discount',None)
				if discount:
					entity.Discount = float(discount)
				
				entity.UpdatedBy = self.UserId
				stockService.SaveProduct(entity)
				
				return dict(status=True)
				
		return dict(status=False)
	
	def getproducts(self):
		pageNo = self.request.params.get('pageNo',0)
		pageSize = self.request.params.get('pageSize',20)
		searchValue = self.request.params.get('searchValue',None)
		searchField = self.request.params.get('searchField',None)
		
		lstProducts = stockService.GetProducts(self.TenantId,\
				pageNo,pageSize,searchField,searchValue)
		
		return dict(model=lstProducts)
	
	@action(renderer='templates/stock/products/manage.jinja2')
	def manageproduct(self):
		errors = None
		model = None
		if self.request.method == 'GET':
			pid = self.request.matchdict.get('pid',None)
		else:
			pid = self.request.params.get('pid',None)
		try:
			if pid:
				model = stockService.GetProduct(pid,self.TenantId)
			
				if not model:
					return HTTPFound(location='/stock/products')
			
				pForm = Form(self.request,schema=ProductSchema,obj=model)

				if pForm.validate():
					pForm.bind(model)
					model.UpdatedBy = self.UserId
					if stockService.SaveProduct(model):
						return HTTPFound(location='/stock/products')
					else:
						errors='Unable to add product details!'
			else:
				model = Product()
				pForm = Form(self.request,schema=ProductSchema,defaults=model.toDict())
			
				if pForm.validate():
					model = pForm.bind(Product())
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True
					if stockService.AddProduct(model):
						return HTTPFound(location='/stock/products')
					else:
						errors='Unable to save product details!'
		except Exception, e:
			errors = str(e)
			log.debug(e)
			
		return dict(model=model,renderer=vFormRenderer(pForm),errors=errors)
		
	@action()	
	def deleteProduct(self):
		pid = self.request.matchdict.get('pid',None)
		val = stockService.DeleteProduct(pid,self.TenantId)
		return HTTPFound(location='/stock/products')
		
	@action(renderer='json')
	def markReturnProduct(self):
		pid = self.request.matchdict.get('pid',None)
		status = self.request.params.get('status',u'false')
		if pid:
			model = stockService.GetProduct(pid,self.TenantId)
			if model:
				model.Status = status == 'true'
				stockService.SaveProduct(model)
				return dict(status=True)
		return dict(status=False)
		
	@action()	
	def deletePurchase(self):
		pid = self.request.matchdict.get('pid',None)
		val = stockService.DeletePurchase(pid,self.TenantId)
		return HTTPFound(location='/stock/purchases')
		
	@action(renderer='templates/stock/purchase/index.jinja2')
	def purchases(self):
		lstSuppliers = self.GetSuppliers()
		lst = self.getPurchaseList()
		return dict(model=lst,suppliers=lstSuppliers)
		
	@action(renderer='templates/stock/purchase/partialPurchaseList.jinja2',xhr=True)
	def purchases_xhr(self):
		lst = self.getPurchaseList()
		return dict(model=lst)
	
	def getPurchaseList(self):
		param = PurchaseSearchParam()
		param.TenantId = self.TenantId
		param.PurchaseNo = self.request.params.get('billNo',None)
		param.SupplierId = self.request.params.get('supplierId',None)
		param.PageSize = self.request.params.get('pageSize',20)
		param.PageNo = self.request.params.get('pageNo',0)

		bdate = self.request.params.get('billDate',None)
		if bdate and len(bdate) > 0:
			param.PurchaseDate = datetime.strptime(bdate.strip(),'%d-%m-%Y')

		lstPurchases = stockService.SearchPurchases(param)
		return lstPurchases
		
	def GetSuppliers(self):
		lstSuppliers = SupplierService().GetSuppliers(self.TenantId)
		if lstSuppliers:
			lstSuppliers = [[str(x.Id),x.Name] for x in lstSuppliers]
		return lstSuppliers
		
	@action(renderer='json')
	def deletepurchaselineitem(self):
		purchaseId = self.request.params.get('purchaseId',None)
		lineItemId = self.request.params.get('lineItemId',None)
		
		if purchaseId and lineItemId:
			if stockService.DeletePurchaseLineItem(purchaseId,lineItemId,self.TenantId):
				return dict(status=True,message='Line Item deleted successfully!')
		
		return dict(status=False,message="Invalid Data!")
		
	@action(renderer='json')
	def addpurchaselineitem(self):
		purchaseId = self.request.params.get('pid',None)
		supplierId = self.request.params.get('SupplierId',None)
		if purchaseId and supplierId:
			model = None
			productId = self.request.params.get('ProductId',None)
			quantity  = float(self.request.params.get('Quantity', 0.0))
			taxAmount = float(self.request.params.get('TaxAmount',0.0))
			
			try:
				if productId:
					model = stockService.GetProduct(productId,self.TenantId)
				if not model:
					model = Product()
			
				pForm = Form(self.request,schema=ProductSchema,obj=model)
			
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
					litem.ProductId  = model.Id
					litem.Name 		 = model.Name
					litem.Barcode 	 = model.Barcode
					litem.MRP 		 = model.MRP
					litem.Tax 		 = taxAmount
					litem.BuyPrice 	 = model.BuyPrice
					litem.Discount 	 = model.Discount
					litem.Quantity 	 = quantity
				
					result = stockService.AddPurchaseLineItem(litem,self.TenantId)
					if result:
						return dict(status=True,id=litem.Id,message="Item added successfully!")
					else:
						DBSession.rollback()
				else:
					log.info('pForm validate failed : %s!' % (pForm.all_errors()))
					return dict(status=False,message=pForm.all_errors())
			except Exception,e:
				log.debug(e)
				return dict(status=False,message=e.message)
		return dict(status=False,message="Invalid PurchaseId or SupplierId!")
	
	@action(renderer='templates/stock/purchase/manage.jinja2')
	def managepurchase(self):
		errors = None
		model = None
		form = None
		lstSuppliers = []
		productmodel = Product()
		pForm = Form(self.request,schema=ProductSchema,defaults=productmodel.toDict())
			
		if self.request.method == 'GET':
			pid = self.request.matchdict.get('pid',None)
		else:
			pid = self.request.params.get('pid',None)
		
		lstSuppliers = self.GetSuppliers()
		
		try:
			if pid:
				model = stockService.GetPurchase(pid,self.TenantId)
				
				if not model:
					return HTTPFound(location='/stock/purchases')
				
				form = Form(self.request,schema=PurchaseSchema,obj=model)
				
				if form.validate():
					form.bind(model)
					model.TenantId = self.TenantId
					model.UpdatedBy = self.UserId
					model.Status = True
					if stockService.SavePurchase(model):
						return HTTPFound(location='/stock/purchases')
					else:
						errors='Unable to save purchase details!'
			else:
				model = Purchase()
				form = Form(self.request,schema=PurchaseSchema,defaults=model.toDict())
				
				if form.validate():
					model = form.bind(Purchase())
					model.TenantId = self.TenantId
					model.CreatedBy = self.UserId
					model.Status = True
					if stockService.AddPurchase(model):
						return HTTPFound(location='/stock/purchases')
					else:
						errors='Unable to save purchase details!'
		except Exception,e:
			errors = str(e)
			log.debug(e)
			
		return dict(model=model,suppliers=lstSuppliers,renderer=vFormRenderer(pForm),purchaseRenderer=vFormRenderer(form),errors=errors)

