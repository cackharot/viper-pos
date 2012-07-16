from pyramid.httpexceptions import HTTPFound
from pyramid_handlers import action
from pyramid.view import view_defaults

from ..models.Product import Product
from ..models.Customer import Customer, CustomerContactDetails
from ..models.Order import Order
from ..models.Order import OrderSearchParam
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment

from ..services.SecurityService import SecurityService
from ..services.OrderService import OrderService
from ..services.CustomerService import CustomerService
from ..services.StockService import StockService
from ..services.SupplierService import SupplierService
from ..services.SettingService import SettingService, SettingException

from ..library.ViperLog import log
import json
import uuid
from datetime import datetime


def includeme(config):
    config.add_handler('invoicecreate', 'invoice/rest',      InvoiceController, action='create', request_method='POST')    
    config.add_handler('invoicefetch',  'invoice/rest/{id}', InvoiceController, action='fetch',  request_method='GET')
    config.add_handler('invoiceupdate', 'invoice/rest/{id}', InvoiceController, action='update', request_method='PUT')
    config.add_handler('invoicedelete', 'invoice/rest/{id}', InvoiceController, action='delete', request_method='DELETE')
    
    config.add_handler('invoicehandler', 'invoice/{action}', InvoiceController)
    config.add_handler('invoicepayments', '/invoice/payments/{invoiceid}', InvoiceController, action='payments')

    config.add_handler('addinvoice', '/invoice/manage', InvoiceController, action='manage')
    config.add_handler('deleteinvoice', '/invoice/delete/{invoiceid}', InvoiceController, action='delete')
    config.add_handler('editinvoice', '/invoice/manage/{invoiceid}', InvoiceController, action='manage')
       
    config.add_route('saveinvoice', '/invoice/manage')
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
        
    @action(renderer='json')    
    def fetch(self):
        invoiceid = self.request.matchdict.get('id',None)
        if invoiceid:
            service = OrderService()
            model = service.GetOrderById(invoiceid, self.TenantId)
            if model:
                return model.toDict()
        return dict()
    
    @action(renderer='json')
    def create(self):
        orderService = OrderService()
        #model = orderService.NewOrder(self.TenantId, self.UserId)
        customerService = CustomerService()
        defaultCustomer = customerService.GetDefaultCustomer(self.TenantId)

        model = Order()
        model.Id = uuid.uuid4()
        model.TenantId = self.TenantId
        model.Customer = defaultCustomer
        model.OrderNo = orderService.GenerateOrderNo(self.TenantId) #generate unique order no
        model.OrderDate = model.CreatedOn = datetime.utcnow()
        model.IpAddress = None
        model.CreatedBy = self.UserId
        model.Status = True
        
        model.LineItems = []
        model.Payments = []
        
        return model.toDict()
    
    @action(renderer='json')
    def update(self):
        order = json.loads(self.request.body)
        log.info(order)
        if order:
            order['ipaddress'] = self.request.remote_addr
            #service = OrderService()
            #service.SaveOrder(order, self.TenantId, self.UserId)
            return {'status':'success', 'message':'Invoice Saved Successfully!'}
        return {'status':'error', 'message':'Invalid data!'}
    
    @action(renderer='json')
    def delete(self):
        return dict()    

    @action(renderer='templates/invoice/index.jinja2')
    def index(self):
        invoices = self.getInvoices()
        return invoices
    
    @action(renderer='templates/invoice/partialInvoiceList.jinja2', xhr=True)
    def searchinvoices_xhr(self):
        invoices = self.getInvoices()
        return invoices
    
    @action(renderer='templates/invoice/manage.jinja2')
    def manage(self):
        invoiceid = self.request.matchdict.get('invoiceid',None)
        model = None
        if invoiceid:
            service = OrderService()
            model = service.GetOrderById(invoiceid, self.TenantId)
        else:
            model = Order()
            model.Customer = Customer()
            model.Customer.Contacts.append(CustomerContactDetails())
            
        templates = SettingService().GetPrintTemplates(self.TenantId)

        return dict(model=model,templates=templates)
    
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
        
        pageNo = int(self.request.params.get('page', 1))
        pageSize = int(self.request.params.get('pagesize', 10))
        
        searchParam.PageNo = (pageNo-1)*pageSize
        searchParam.PageSize = pageSize

        orderService = OrderService()
        invoices, stat  = orderService.SearchOrders(searchParam)
        totalInvoices = stat.ItemsCount
        totalAmount = stat.TotalAmount
        totalDueAmount = stat.TotalAmount - stat.TotalPaidAmount        
        return dict(model=invoices,totalInvoices=totalInvoices, \
                    pageno=pageNo,pagesize=pageSize,\
                    customerName=searchParam.CustomerName,customerId=searchParam.CustomerId,\
                    fromDate=searchParam.FromOrderDate,toDate=searchParam.ToOrderDate, \
                    totalAmount=totalAmount,totalDueAmount=totalDueAmount)


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
        ids = self.request.matchdict['invoiceid']
        if ids:
            orderids = ids.split(',')
            orderService = OrderService()
            orderService.DeleteOrder(self.TenantId, orderids)
        return HTTPFound(location=self.request.route_url('invoices'))
