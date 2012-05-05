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
from ..models.Order import Order
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment
from ..library.ViperLog import log
from ..library.UserIdentity import UserIdentity

from ..services.OrderService import OrderService

orderServiceProxy = OrderService()

def includeme(config):
	config.add_route('sales', '/sales')
	config.add_route('neworder', '/sales/neworder')
	config.add_route('saveorder', '/sales/saveorder')
	config.add_route('deleteorder', '/sales/deleteorder/{orderid}')
	config.add_route('getorder', '/sales/getorder/{orderid}')
	config.add_route('todayorders', '/sales/todayorders')
	config.add_route('addlineitem', '/sales/addlineitem')
	config.add_route('deletelineitem', '/sales/deletelineitem/{id}')
	config.add_route('updatelineitem', '/sales/updatelineitem')
	pass

@view_config(route_name='sales', renderer='sales/index.jinja2')
def salesPage(request):
	d = datetime.utcnow()
	return { 'date': d.date(), 'time': d.time() }

@view_config(route_name='todayorders')
def getTodayOrders(request):
	searchParam = object()
	searchParam.FromOrderDate = datetime.utcnow()
	model = orderServiceProxy.SearchOrders(searchParam)
	return json.dumps({'model':model})
	
@view_config(route_name='getorder')
def getOrder(request):
	orderid = request.params.get(orderid)
	model = orderServiceProxy.GetOrderById(orderid)
	return json.dumps({'model':model})
	    
@view_config(route_name='neworder')
def newOrder(request):
	model = orderServiceProxy.NewOrder()
	return json.dumps({'model':model})
	
@view_config(route_name='saveorder')
def saveOrder(request):
	return json.dumps({'status':'success','message':'Order Saved Successfully!'})

@view_config(route_name='deleteorder')
def deleteOrder(request):
	return json.dumps({'status':'success','message':'Order Deleted Successfully!'})
	
@view_config(route_name='addlineitem')
def addLineItem(request):
	return json.dumps({'status':'success','message':'Line Item added successfully!'})
	
@view_config(route_name='updatelineitem')
def updateLineItem(request):
	return json.dumps({'status':'success','message':'Line Item updated successfully!'})	
	
@view_config(route_name='deletelineitem')
def deleteLineItem(request):
	return json.dumps({'status':'success','message':'Line Item deleted successfully!'})
