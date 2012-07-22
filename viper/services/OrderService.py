#import json
import uuid
#import random
from datetime import datetime
import dateutil.parser

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc, func, cast, Date, or_

from ..models import DBSession
from ..models.Product import Product
from ..models.Customer import Customer, CustomerContactDetails
from ..models.Order import Order
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment
from ..library.ViperLog import log

from ..services.SecurityService import SecurityService
from ..services.CustomerService import CustomerService

customerService = CustomerService()
#DefaultCustomerId = uuid.UUID('1dba743b516242108265dc0c12513b6c')

class OrderService(object):
	"""
		Order service class
	"""

	def GetOrderById(self, orderid, tenantId):
		"""
			Fetchs the orders details by order id
			Returns Order Object if found else None
		"""
		if orderid and tenantId:
			order = DBSession.query(Order).filter(Order.Id == orderid, Order.TenantId == tenantId, Order.Status == True).first()
			if order:
				if order.CustomerId:
					cus = customerService.GetCustomer(order.CustomerId, tenantId)
					if cus:
						order.Customer = cus
						order.CustomerName = cus.Contacts[0].FirstName
						order.CustomerNo   = cus.CustomerNo
				#fetch the line items here
				order.LineItems = DBSession.query(LineItem).filter(LineItem.OrderId == order.Id).all()
				#fetch the payment details
				order.Payments = DBSession.query(OrderPayment).filter(OrderPayment.OrderId == order.Id, OrderPayment.Status == True).all()
				return order
		return None

	def NewOrder(self, tenantId, userId):
		"""
			Creates new order in db and returns it
		"""
		if not tenantId or not userId:
			return None

		defaultCustomer = customerService.GetDefaultCustomer(tenantId)

		o = Order()
		o.Id = uuid.uuid4()
		o.TenantId = tenantId
		o.Customer = defaultCustomer
		if defaultCustomer and defaultCustomer.Id and defaultCustomer.Contacts:
			o.CustomerId = defaultCustomer.Id
			o.CustomerNo = defaultCustomer.CustomerNo
			o.CustomerName = defaultCustomer.Contacts[0].FirstName
		o.OrderNo = self.GenerateOrderNo(tenantId) #generate unique order no
		o.OrderDate = datetime.utcnow()
		o.IpAddress = None
		o.CreatedBy = userId
		o.CreatedOn = datetime.utcnow()
		o.Status = True
		DBSession.add(o) #add to db
		return o

	def SaveOrder(self, order, tenantId, userId):
		"""
			Saves the order details in db
		"""
		if order:
			if order["Id"]:
				orderid = order["Id"]
				o = self.GetOrderById(orderid, tenantId)
				if o:
					#o.TenantId = tenantId
					o.CustomerId = order["CustomerId"]
					o.OrderAmount = order["OrderAmount"]
					o.PaidAmount = order["PaidAmount"]
					o.IpAddress = order['IpAddress']
					if order['DueDate'] and len(order['DueDate']) > 0:
						o.DueDate = dateutil.parser.parse(order['DueDate'])
					if order['OrderDate'] and len(order['OrderDate']) > 0:
						o.OrderDate = dateutil.parser.parse(order['OrderDate'])
					o.UpdatedBy = userId
					o.UpdatedOn = datetime.utcnow()

					lineitems = order["LineItems"]
					if lineitems:
						DBSession.query(LineItem).filter(LineItem.OrderId == orderid).delete()
						self.SaveOrderLineItems(o.Id, lineitems)
					else:
						DBSession.query(LineItem).filter(LineItem.OrderId == orderid).delete()

					payments = order["Payments"]
					if payments:
						DBSession.query(OrderPayment).filter(OrderPayment.OrderId == orderid).delete()
						self.SaveOrderPayments(o.Id, payments, userId)
					else:
						DBSession.query(OrderPayment).filter(OrderPayment.OrderId == orderid).delete()
		pass

	def SaveOrderLineItems(self, orderid, lineitems):
		if orderid and lineitems:
			for x in lineitems:
				item = LineItem()
				item.OrderId = orderid
				if x.has_key('ProductId'):
					item.ProductId = x['ProductId']
				item.Name = x["Name"]
				item.Barcode = x["Barcode"]
				item.MRP = x["MRP"]
				item.Discount = x["Discount"]
				item.SellPrice = x["SellPrice"]
				item.Quantity = x["Quantity"]
				DBSession.add(item)

		pass

	def SaveOrderPayments(self, orderid, payments, userId):
		"""
			Saves the order payment details in db
		"""
		if orderid and payments:
			for x in payments:
				item = OrderPayment()
				item.OrderId = orderid
				item.PaidAmount = x["PaidAmount"]
				item.PaymentType = x["PaymentType"]
				if x['PaymentDate'] and len(x['PaymentDate']) > 0:
					item.PaymentDate = dateutil.parser.parse(x['PaymentDate'])
				else:
					item.PaymentDate = datetime.utcnow()
				item.CreatedBy = userId
				item.CreatedOn = datetime.utcnow()
				DBSession.add(item)
		pass

	def DeleteOrder(self, tenantId, orderids):
		"""
			Deletes the order details from db
		"""
		if tenantId and orderids:
			orders = DBSession.query(Order).filter(Order.Id.in_(orderids), Order.TenantId == tenantId).all()
			for o in orders:
				DBSession.delete(o)
		pass

	def UpdateOrderPayment(self, orderid, paymentid, details, userId):
		"""
			Adds or Saves the order payment details in db
		"""
		if orderid and details and userId:
			if paymentid:
				payment = DBSession.query(OrderPayment).get(paymentid)
			else:
				payment = OrderPayment()
				payment.OrderId = orderid
				payment.CreatedBy  = userId
				payment.CreatedOn  = datetime.utcnow()
			
			if payment and payment.OrderId:
				if payment.Id:
					payment.UpdatedBy  = userId
					payment.UpdatedOn  = datetime.utcnow()
					
				payment.PaidAmount = details['paidAmount']
				payment.PaymentType= details['paymentType']
				payment.PaymentDate= dateutil.parser.parse(details['paymentDate'].strip())
				payment.Status     = True
				DBSession.add(payment)

	def DeleteOrderPayment(self, orderpaymentid):
		"""
			Deletes the order payment details from db
		"""
		if orderpaymentid:
			DBSession.query(OrderPayment).filter(OrderPayment.Id==orderpaymentid).delete()

	def SearchOrders(self, searchParam):
		"""
			Searchs the order from the given parameters
			Searchable Params:
				TenantId (mandatory)
				UserId
				IpAddress
				OrderNo
				CustomerId
				CustomerName
				FromOrderDate
				ToOrderDate
				MinAmount
				MaxAmount
				PageNo (default=0)
				PageSize (default=50)
		"""
		if not searchParam or not searchParam.TenantId:
			return None

		osq = DBSession.query(LineItem.OrderId, func.count(LineItem.OrderId).label('ItemCount'), \
							func.ROUND(func.sum(LineItem.Quantity * LineItem.SellPrice),2).label('OrderAmount'))
		osq = osq.join(Order, Order.Id == LineItem.OrderId).group_by(LineItem.OrderId).subquery()
		

		psq = DBSession.query(OrderPayment.OrderId, func.ROUND(func.sum(OrderPayment.PaidAmount),2).label('PaidAmount'))
		psq = psq.join(Order, Order.Id == OrderPayment.OrderId).group_by(OrderPayment.OrderId).subquery()
		
		query = DBSession.query(Order.Id, Order.OrderNo, Order.OrderDate, Order.CustomerId, Order.TenantId, Order.CreatedBy, \
							 Order.CreatedOn, Order.UpdatedBy, Order.UpdatedOn, Order.Status, Order.IpAddress, Order.DueDate,\
							 Customer.CustomerNo, CustomerContactDetails.FirstName.label('CustomerName'), osq.c.ItemCount,\
							 func.ifnull(osq.c.OrderAmount,0).label('OrderAmount'), func.ifnull(psq.c.PaidAmount,0).label('PaidAmount'))
		query = query.outerjoin(osq, osq.c.OrderId == Order.Id).outerjoin(psq, psq.c.OrderId == Order.Id)
		query = query.outerjoin(Customer, Customer.Id == Order.CustomerId)
		query = query.outerjoin(CustomerContactDetails, Customer.Id == CustomerContactDetails.CustomerId)
		
		if searchParam.NotEmpty:
			query = query.filter(osq.c.ItemCount > 0)

		query = query.filter(Order.TenantId == searchParam.TenantId)
		query = query.filter(Order.Status == True)

		query = self.formQueryFromParam(query, osq, psq, searchParam)

		if not searchParam.PageNo:
			searchParam.PageNo = 0
		if not searchParam.PageSize and searchParam.PageSize <= 0:
			searchParam.PageSize = 50

		query = query.order_by(desc(Order.OrderDate))
		orders = query.limit(searchParam.PageSize).offset(searchParam.PageNo).all()
		
		if not searchParam.LoadStats:
			return orders
		
		tquery = DBSession.query(func.count(Order.Id).label('ItemsCount'), \
								func.ifnull(func.sum(osq.c.OrderAmount),0).label('TotalAmount'),\
								func.ifnull(func.sum(func.IF(psq.c.PaidAmount>=osq.c.OrderAmount,osq.c.OrderAmount,psq.c.PaidAmount)),0).label('TotalPaidAmount'))
		tquery = tquery.outerjoin(osq, osq.c.OrderId == Order.Id).outerjoin(psq, psq.c.OrderId == Order.Id)
		
		if searchParam.CustomerName:
			tquery = tquery.outerjoin(Customer, Customer.Id == Order.CustomerId)
			tquery = tquery.outerjoin(CustomerContactDetails, Customer.Id == CustomerContactDetails.CustomerId)
		
		tquery = self.formQueryFromParam(tquery, osq, psq, searchParam)

		return orders, tquery.first()
	
	def formQueryFromParam(self,query,osq,psq, searchParam):
		if searchParam.Credit:
			query = query.filter(osq.c.OrderAmount > psq.c.PaidAmount)
			
		if searchParam.UserId:
			query = query.filter(Order.CreatedBy == searchParam.UserId, \
									   Order.UpdatedBy == searchParam.UserId)
		if searchParam.OrderNo:
			query = query.filter(Order.OrderNo == searchParam.OrderNo)
		if searchParam.CustomerId:
			query = query.filter(Order.CustomerId == searchParam.CustomerId)
		if searchParam.CustomerName:
			query = query.filter(CustomerContactDetails.FirstName.like('%%%s' % searchParam.CustomerName))
		if searchParam.IpAddress:
			query = query.filter(Order.IpAddress == searchParam.IpAddress)


		if searchParam.FromOrderDate and searchParam.ToOrderDate and searchParam.FromOrderDate == searchParam.ToOrderDate: 
			query = query.filter(cast(Order.OrderDate, Date) == searchParam.ToOrderDate)
		elif searchParam.FromOrderDate and not searchParam.ToOrderDate:
			query = query.filter(cast(Order.OrderDate, Date) > searchParam.FromOrderDate)
		elif not searchParam.FromOrderDate and searchParam.ToOrderDate:
			query = query.filter(cast(Order.OrderDate, Date) < searchParam.ToOrderDate)
		elif searchParam.FromOrderDate and searchParam.ToOrderDate:
			query = query.filter(cast(Order.OrderDate, Date) > searchParam.FromOrderDate, \
									cast(Order.OrderDate, Date) <= searchParam.ToOrderDate)
						
		if searchParam.MinAmount and not searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount >= searchParam.MinAmount)
		if not searchParam.MinAmount and searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount <= searchParam.MaxAmount)
		if searchParam.MinAmount and searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount >= searchParam.MinAmount, \
									Order.OrderAmount <= searchParam.MaxAmount)
			
			
		if searchParam.InvoiceStatus == 'opened':
			query = query.filter(or_(osq.c.OrderAmount > psq.c.PaidAmount, osq.c.OrderAmount==0, osq.c.OrderAmount == None))
		elif searchParam.InvoiceStatus == 'closed':
			query = query.filter(osq.c.OrderAmount <= psq.c.PaidAmount, osq.c.OrderAmount!=0)
		elif searchParam.InvoiceStatus == 'overdue':
			query = query.filter(osq.c.OrderAmount > psq.c.PaidAmount, Order.DueDate < func.now())
			
		return query
		
	def GetOrderPayments(self,orderId,tenantId):
		if orderId and tenantId:
			query = DBSession.query(OrderPayment).join(Order,OrderPayment.OrderId==orderId)\
							 .filter(Order.Status==True,Order.TenantId==tenantId)
			payments = query.all()
			return payments						
		return None

	def GenerateOrderNo(self, tenantId):
		tmp = DBSession.query(func.max(Order.OrderNo)).filter(Order.TenantId == tenantId).scalar()
		if tmp != None: return int(tmp) + 1
		else: return 1000

	pass

