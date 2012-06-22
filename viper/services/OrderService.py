import json
import uuid
import random
from datetime import datetime, date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc, func, cast, Date

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
						order.CustomerName = cus.Contacts[0].FirstName
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

		cus = customerService.GetDefaultCustomer(tenantId)

		o = Order()
		o.Id = uuid.uuid4()
		o.TenantId = tenantId
		if cus and cus.Id and cus.Contacts:
			o.CustomerId = cus.Id
			o.CustomerName = cus.Contacts[0].FirstName
		o.OrderNo = self.GenerateOrderNo(tenantId) #generate unique order no
		o.OrderDate = datetime.utcnow()
		o.IpAddress = None
		o.CreatedBy = userId
		o.CreatedOn = o.OrderDate = datetime.utcnow()
		o.Status = True
		DBSession.add(o) #add to db
		return o

	def SaveOrder(self, order, tenantId, userId):
		"""
			Saves the order details in db
		"""
		if order:
			if order["orderid"]:
				orderid = order["orderid"]
				o = self.GetOrderById(orderid, tenantId)
				if o:
					#o.TenantId = tenantId
					o.CustomerId = order["customerid"]
					o.OrderAmount = order["orderamount"]
					o.PaidAmount = order["paidamount"]
					o.IpAddress = order['ipaddress']
					o.ShipDate = o.OrderDate
					o.UpdatedBy = userId
					o.UpdatedOn = datetime.utcnow()

					lineitems = order["lineItems"]
					if lineitems:
						DBSession.query(LineItem).filter(LineItem.OrderId == orderid).delete()
						self.SaveOrderLineItems(o.Id, lineitems)
					else:
						DBSession.query(LineItem).filter(LineItem.OrderId == orderid).delete()

					payments = order["payments"]
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
				if x.has_key('productid'):
					item.ProductId = x['productid']
				item.Name = x["name"]
				item.Barcode = x["barcode"]
				item.MRP = x["mrp"]
				item.Discount = x["discount"]
				item.SellPrice = x["price"]
				item.Quantity = x["quantity"]
				DBSession.add(item)

		pass

	def SaveOrderPayments(self, orderid, payments, userId):
		"""
			Saves the order payment details in db
		"""
		if orderid and payments:
			for x in payments:
				if x["paidamount"] <= 0:
					continue
				item = OrderPayment()
				item.OrderId = orderid
				item.PaidAmount = x["paidamount"]
				item.PaymentType = x["paymenttype"]
				item.PaymentDate = datetime.utcnow()
				item.CreatedBy = userId
				item.CreatedOn = datetime.utcnow()
				DBSession.add(item)
		pass

	def DeleteOrder(self, tenantId, orderid):
		"""
			Deletes the order details from db
		"""
		if tenantId and orderid:
			DBSession.query(Order).filter(Order.Id == orderid, Order.TenantId == tenantId).delete()
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
				payment.PaymentDate= datetime.strptime(details['paymentDate'].strip(),'%d-%m-%Y')
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
							func.sum(LineItem.Quantity * LineItem.SellPrice).label('OrderAmount'))
		osq = osq.join(Order, Order.Id == LineItem.OrderId).group_by(LineItem.OrderId).subquery()

		psq = DBSession.query(OrderPayment.OrderId, func.sum(OrderPayment.PaidAmount).label('PaidAmount'))
		psq = psq.join(Order, Order.Id == OrderPayment.OrderId).group_by(OrderPayment.OrderId).subquery()

		query = DBSession.query(Order.Id, Order.OrderNo, Order.OrderDate, Order.CustomerId, Order.TenantId, Order.CreatedBy, \
							 Order.CreatedOn, Order.UpdatedBy, Order.UpdatedOn, Order.Status, Order.IpAddress, Order.DueDate,\
							 CustomerContactDetails.FirstName.label('CustomerName'), osq.c.ItemCount,\
							 func.ifnull(osq.c.OrderAmount,0).label('OrderAmount'), func.ifnull(psq.c.PaidAmount,0).label('PaidAmount'))
		query = query.outerjoin(osq, osq.c.OrderId == Order.Id).outerjoin(psq, psq.c.OrderId == Order.Id)
		query = query.outerjoin(Customer, Customer.Id == Order.CustomerId)
		query = query.outerjoin(CustomerContactDetails, Customer.Id == CustomerContactDetails.CustomerId)

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
								func.sum(osq.c.OrderAmount).label('TotalAmount'),\
								func.sum(func.IF(psq.c.PaidAmount>=osq.c.OrderAmount,osq.c.OrderAmount,psq.c.PaidAmount)).label('TotalPaidAmount'))
		tquery = tquery.outerjoin(osq, osq.c.OrderId == Order.Id)\
					   .outerjoin(psq, psq.c.OrderId == Order.Id)
		tquery = tquery.outerjoin(Customer, Customer.Id == Order.CustomerId)
		tquery = tquery.outerjoin(CustomerContactDetails, Customer.Id == CustomerContactDetails.CustomerId)
		
		tquery = self.formQueryFromParam(tquery, osq, psq, searchParam)

		return orders, tquery.first()
	
	def formQueryFromParam(self,query,osq,psq, searchParam):
		if searchParam.Credit or searchParam.InvoiceStatus == 'opened':
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

		if searchParam.FromOrderDate and not searchParam.ToOrderDate:
			query = query.filter(cast(Order.OrderDate, Date) > searchParam.FromOrderDate)
		if not searchParam.FromOrderDate and searchParam.ToOrderDate:
			query = query.filter(cast(Order.OrderDate, Date) < searchParam.ToOrderDate)
		if searchParam.FromOrderDate and searchParam.ToOrderDate:
			query = query.filter(cast(Order.OrderDate, Date) > searchParam.FromOrderDate, \
									cast(Order.OrderDate, Date) <= searchParam.ToOrderDate)

		if searchParam.MinAmount and not searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount >= searchParam.MinAmount)
		if not searchParam.MinAmount and searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount <= searchParam.MaxAmount)
		if searchParam.MinAmount and searchParam.MaxAmount:
			query = query.filter(Order.OrderAmount >= searchParam.MinAmount, \
									Order.OrderAmount <= searchParam.MaxAmount)
			
		if searchParam.InvoiceStatus:
			if searchParam.InvoiceStatus == 'closed':
				query = query.filter(osq.c.OrderAmount <= psq.c.PaidAmount)
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

