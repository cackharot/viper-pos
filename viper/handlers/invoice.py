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

def includeme(config):
    config.add_handler('invoice', 'invoice/{action}', InvoiceController)
    config.add_handler('invoicepayments','/invoice/payments/{invoiceid}', InvoiceController, action='payments')
    
    config.add_handler('addinvoice','/invoice/new', InvoiceController, action='newInvoice')
    config.add_handler('deleteinvoice','/invoice/delete/{invoiceid}', InvoiceController, action='delete')
    config.add_handler('editinvoice','/invoice/edit/{invoiceid}', InvoiceController, action='edit')
    config.add_handler('searchinvoices', '/invoice/index/{searchField}/{searchValue}', InvoiceController, action='index')
    
    config.add_route('invoices','/invoice/index')
    config.add_route('searchinvoices_xhr','/invoice/index',xhr=True)

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
        searchParam = OrderSearchParam()
        searchParam.TenantId = self.request.user.TenantId
        orderService = OrderService()
        model = orderService.SearchOrders(searchParam)
        return dict(model=model)

    @action(renderer='templates/invoice/payments.jinja2')
    def payments(self):
        return dict(status=True)
    
    @action()
    def delete(self):
        return HTTPFound(location=self.request.route_url('invoices'))
