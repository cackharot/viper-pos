from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action

from ..models.Product import Product
from ..models.Customer import Customer
from ..models.Order import Order, OrderSearchParam
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment

from ..services.SecurityService import SecurityService
from ..services.OrderService import OrderService
from ..services.StockService import StockService
from ..services.SupplierService import SupplierService

from pyramid_simpleform import Form

from datetime import datetime

from ..forms.vFormRenderer import vFormRenderer
from ..library.ViperLog import log

import json

def includeme(config):
    config.add_handler('invoice', 'invoice/{action}', InvoiceController)
    config.add_handler('invoicepayments', '/invoice/payments/{invoiceid}', InvoiceController, action='payments')

    config.add_handler('addinvoice', '/invoice/new', InvoiceController, action='newInvoice')
    config.add_handler('deleteinvoice', '/invoice/delete/{invoiceid}', InvoiceController, action='delete')
    config.add_handler('editinvoice', '/invoice/edit/{invoiceid}', InvoiceController, action='edit')
    
    config.add_route('searchinvoices', '/invoice/index')
    config.add_route('invoices', '/invoice/index')
    config.add_route('searchinvoices_xhr', '/invoice/searchinvoices_xhr', xhr=True)
    config.add_route('saveinvoicepayments', '/invoice/savepayments', xhr=True)

class InvoiceController(object):
    """
        Invoice Controller/View
    """
    def __init__(self, request):
        self.request = request
        self.TenantId = self.request.user.TenantId
        self.UserId = self.request.user.Id

    @action(renderer='templates/invoice/index.jinja2')
    def index(self):
        invoices = self.getInvoices()
        return invoices
    
    @action(renderer='templates/invoice/partialInvoiceList.jinja2', xhr=True)
    def searchinvoices_xhr(self):
        invoices = self.getInvoices()
        return invoices
    
    def getDateFmt(self,value):
        from ..library.filters import todatetime
        return todatetime(value)
    
    def getInvoices(self):
        searchParam = OrderSearchParam()
        searchParam.TenantId = self.request.user.TenantId
        searchParam.CustomerName = self.request.params.get('customerName', None)
        searchParam.CustomerId = self.request.params.get('customerId', None)
        searchParam.OrderNo = self.request.params.get('invoiceNo',None)
        searchParam.FromOrderDate = self.getDateFmt(self.request.params.get('fromDate',None))
        searchParam.ToOrderDate = self.getDateFmt(self.request.params.get('toDate',None))
        searchParam.InvoiceStatus = self.request.params.get('invoicestatus',None)
        
        searchParam.PageSize = self.request.params.get('pageSize',None)
        searchParam.PageNo = self.request.params.get('pageNo',None)

        orderService = OrderService()
        invoices, stat  = orderService.SearchOrders(searchParam)
        totalInvoices = stat.ItemsCount
        totalAmount = stat.TotalAmount
        totalDueAmount = stat.TotalAmount - stat.TotalPaidAmount        
        return dict(model=invoices,totalInvoices=totalInvoices,totalAmount=totalAmount,totalDueAmount=totalDueAmount)


    #@action(renderer='templates/invoice/payments.jinja2',xhr=True)
    @action(renderer='json', xhr=True)
    def payments(self):
        orderId = self.request.matchdict['invoiceid']
        if orderId:
            orderService = OrderService()
            payments = orderService.GetOrderPayments(orderId, self.TenantId)
            if payments:
                return dict(payments=[x.toDict() for x in payments])
        return dict(payments=None)

    @action(renderer='json')
    def savepayments(self):
        data = json.loads(self.request.body)
        #log.info(data)
        if data and data['invoiceId']:
            orderid = data['invoiceId']
            orderService = OrderService()
            order = orderService.GetOrderById(orderid, self.TenantId)
            if order:
                for item in data['payments']:
                    if item['remove'] == '1':
                        orderService.DeleteOrderPayment(item['paymentId'])
                    else:    
                        orderService.UpdateOrderPayment(orderid, item['paymentId'], item, self.UserId)

                return dict(status=True, message='Payment details saved successfully!')
        return dict(status=False, message='Error while saving payment details!')

    @action()
    def delete(self):
        return HTTPFound(location=self.request.route_url('invoices'))
