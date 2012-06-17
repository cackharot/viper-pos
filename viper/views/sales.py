#from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import json
from datetime import datetime

from ..models.Product import Product
from ..models.Customer import Customer
from ..models.Order import Order, OrderSearchParam
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment
from ..library.ViperLog import log

from ..services.OrderService import OrderService
from ..services.StockService import StockService

stockService = StockService()
orderServiceProxy = OrderService()

def includeme(config):
    config.add_route('sales', '/sales')
    config.add_route('neworder', '/sales/neworder', xhr=True)
    config.add_route('saveorder', '/sales/saveorder/{orderid}', xhr=True)
    config.add_route('savelineitems', '/sales/savelineitems', xhr=True)
    config.add_route('deleteorder', '/sales/deleteorder/{orderid}')
    config.add_route('getorder', '/sales/getorder/{orderid}', xhr=True)
    config.add_route('todayorders', '/sales/todayorders', xhr=True)
    config.add_route('addlineitem', '/sales/addlineitem', xhr=True)
    config.add_route('deletelineitem', '/sales/deletelineitem/{id}', xhr=True)
    config.add_route('updatelineitem', '/sales/updatelineitem', xhr=True)
    config.add_route('searchitems', '/sales/searchitem', xhr=True)

@view_config(route_name='sales', renderer='sales/index.jinja2')
def salesPage(request):
    d = datetime.utcnow()
    return { 'date': d.date(), 'time': d.time() }

@view_config(route_name='todayorders', renderer="json")
def getTodayOrders(request):
    searchParam = OrderSearchParam()
    d = datetime.utcnow().date()
    searchParam.FromOrderDate = d.replace(day=d.day - 1)
    searchParam.ToOrderDate = d
    searchParam.TenantId = request.user.TenantId
    entities = orderServiceProxy.SearchOrders(searchParam)

    if entities:
        items = [dict(OrderNo=x.OrderNo, Id=x.Id,
                                CustomerId=x.CustomerId,
                                CustomerName=x.CustomerName,
                                OrderDate=x.OrderDate,
                                OrderAmount=(x.OrderAmount),
                                PaidAmount=(x.PaidAmount)) for x in entities]
        return items
    return None

@view_config(route_name='getorder', renderer="json", accept="application/json")
def getOrder(request):
    orderid = request.matchdict['orderid']
    if orderid:
        model = orderServiceProxy.GetOrderById(orderid, request.user.TenantId)
        if model:
            lineItems = None
            payments = None
            if model.LineItems and len(model.LineItems) > 0:
                lineItems = [x.toDict() for x in model.LineItems]
            if model.Payments and len(model.Payments) > 0:
                payments = [x.toDict() for x in model.Payments]
            result = {"order":model.toDict(), "lineitems":lineItems, "payments":payments}
            return result
    return None

@view_config(route_name='neworder', renderer="json", accept="application/json")
def newOrder(request):
    model = orderServiceProxy.NewOrder(request.user.TenantId, request.user.Id)
    return model.toDict()

@view_config(route_name='saveorder', renderer="json")
def saveOrder(request):
    order = json.loads(request.body)
    #log.info(order)
    if order:
        order['ipaddress'] = request.remote_addr
        orderServiceProxy.SaveOrder(order, request.user.TenantId, request.user.Id)
        return {'status':'success', 'message':'Order Saved Successfully!'}
    return {'status':'error', 'message':'Invalid data!'}

@view_config(route_name='savelineitems', renderer="json")
def saveOrderlineitems(request):
    orderid = request.matchdict['orderid']
    lineitems = request.body
    if orderid and lineitems:
        orderServiceProxy.SaveOrderLineItems(orderid, lineitems)
        return {'status':'success', 'message':'LineItems Saved Successfully!'}
    return {'status':'error', 'message':'Invalid data!'}

@view_config(route_name='deleteorder', renderer="json", accept="application/json")
def deleteOrder(request):
    tenantId = request.user.TenantId
    orderid = request.matchdict['orderid']
    if orderid:
        orderServiceProxy.DeleteOrder(tenantId, orderid)
    #return {'status':'success','message':'Order Deleted Successfully!'}
    return HTTPFound(location='/sales/listorders')

@view_config(route_name='searchitems', renderer="json")
def searchItem(request):
    tenantId = request.user.TenantId
    barcode = request.params.get('barcode')
    name = request.params.get('name')
    if barcode or name:
        if barcode:
            items = stockService.GetProductsByBarcode(tenantId, barcode)
        elif name:
            items = stockService.GetProducts(tenantId, 0, 10, 'Name', name)
        if items and len(items) > 0:
            result = [x.toDict() for x in items]
            return result
    return None
