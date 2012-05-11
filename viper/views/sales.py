from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import json
import uuid
from datetime import datetime 

from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models.Product import Product
from ..models.Customer import Customer
from ..models.Order import Order, OrderSearchParam
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment
from ..library.ViperLog import log
from ..library.UserIdentity import UserIdentity
from ..library.helpers import jsonHandler

from ..services.OrderService import OrderService

orderServiceProxy = OrderService()

def includeme(config):
	config.add_route('sales', '/sales')
	config.add_route('listorders','/sales/listorders')
	config.add_route('neworder', '/sales/neworder', xhr=True)
	config.add_route('saveorder', '/sales/saveorder/{orderid}',xhr=True)
	config.add_route('savelineitems','/sales/savelineitems',xhr=True)
	config.add_route('deleteorder', '/sales/deleteorder/{orderid}',xhr=True)
	config.add_route('getorder', '/sales/getorder/{orderid}',xhr=True)
	config.add_route('todayorders', '/sales/todayorders',xhr=True)
	config.add_route('addlineitem', '/sales/addlineitem',xhr=True)
	config.add_route('deletelineitem', '/sales/deletelineitem/{id}',xhr=True)
	config.add_route('updatelineitem', '/sales/updatelineitem',xhr=True)
	config.add_route('searchitems','/sales/searchitem',xhr=True)
	pass

@view_config(route_name='sales', renderer='sales/index.jinja2')
def salesPage(request):
	d = datetime.utcnow()
	return { 'date': d.date(), 'time': d.time() }

@view_config(route_name='listorders', renderer="sales/orderlist.jinja2")
def listOrders(request):
	searchParam = OrderSearchParam()
	model = orderServiceProxy.SearchOrders(searchParam)
	return {'model':model}


@view_config(route_name='todayorders', renderer="json")
def getTodayOrders(request):
	searchParam = OrderSearchParam()
	d = datetime.utcnow().date()
	searchParam.FromOrderDate = d.replace(day=d.day-1)
	searchParam.ToOrderDate = d
	model = orderServiceProxy.SearchOrders(searchParam)

	if model:
		items = [x.toDict() for x in model]
		result = json.dumps(items,default=jsonHandler)
		return result
	return None
	
@view_config(route_name='getorder', renderer="json", accept="application/json")
def getOrder(request):
	orderid = request.matchdict['orderid']
	if orderid:
		model = orderServiceProxy.GetOrderById(orderid)
		if model:
			lineItems = None
			payments = None
			if model.LineItems and len(model.LineItems) > 0:
				lineItems = [x.toDict() for x in model.LineItems]
			if model.Payments and len(model.Payments) > 0:
				payments = [x.toDict() for x in model.Payments]
			result = json.dumps({"order":model.toDict(),"lineitems":lineItems,"payments":payments},default=jsonHandler)
			return result
	return None
	    
@view_config(route_name='neworder', renderer="json", accept="application/json")
def newOrder(request):
	model = orderServiceProxy.NewOrder()
	return model.toJSON()
	
@view_config(route_name='saveorder', renderer="json")
def saveOrder(request):
	order = json.loads(request.body)
	log.info(order)
	if order:
		orderServiceProxy.SaveOrder(order)
		return {'status':'success','message':'Order Saved Successfully!'}
	return {'status':'error','message':'Invalid data!'}

@view_config(route_name='savelineitems', renderer="json")
def saveOrderlineitems(request):
	orderid = request.matchdict['orderid']
	lineitems = request.body
	if orderid and lineitems:
		orderServiceProxy.SaveOrderLineItems(lineitems)
		return {'status':'success','message':'LineItems Saved Successfully!'}
	return {'status':'error','message':'Invalid data!'}

@view_config(route_name='deleteorder', renderer="json", accept="application/json")
def deleteOrder(request):
	return {'status':'success','message':'Order Deleted Successfully!'}
	
@view_config(route_name='addlineitem', renderer="json", accept="application/json")
def addLineItem(request):
	return json.dumps({'status':'success','message':'Line Item added successfully!'})
	
@view_config(route_name='updatelineitem', renderer="json", accept="application/json")
def updateLineItem(request):
	return json.dumps({'status':'success','message':'Line Item updated successfully!'})	
	
@view_config(route_name='deletelineitem', renderer="json", accept="application/json")
def deleteLineItem(request):
	return json.dumps({'status':'success','message':'Line Item deleted successfully!'})
	
@view_config(route_name='searchitems', renderer="json")	
def searchItem(request):
	barcode = request.params.get('barcode')
	name = request.params.get('name')
	if barcode or name:
		query = DBSession.query(Product)
		if barcode:
			query = query.filter(Product.Barcode==barcode)
		elif name:
			query = query.filter(Product.Name.like('%%%s%%' % name)).order_by(Product.Name)
		items = query.limit(10).offset(0).all()
		if items and len(items) > 0:
			result = [x.toDict() for x in items]
			return json.dumps(result,default=jsonHandler)
	return None
