import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date

from ..models import DBSession
from ..models.Product import Product
from ..models.Customer import Customer
from ..models.Order import Order
from ..models.LineItem import LineItem
from ..models.OrderPayment import OrderPayment
from ..library.ViperLog import log

from ..services.SecurityService import SecurityService
from ..services.CustomerService import CustomerService

customerService = CustomerService()
DefaultCustomerId = uuid.UUID('1dba743b516242108265dc0c12513b6c')

class OrderService(object):
	"""
		Order service class
	"""
	
	def GetOrderById(self, orderid,tenantId):
		"""
			Fetchs the orders details by order id
			Returns Order Object if found else None
		"""
		if orderid and tenantId:
			order = DBSession.query(Order).filter(Order.Id==orderid, Order.TenantId==tenantId, Order.Status==True).first()
			if order:
				if order.CustomerId:
					cus = customerService.GetCustomer(order.CustomerId,tenantId)
					if cus:
						order.CustomerName = cus.Contacts[0].FirstName
				#fetch the line items here
				order.LineItems = DBSession.query(LineItem).filter(LineItem.OrderId==order.Id).all()
				#fetch the payment details
				order.Payments = DBSession.query(OrderPayment).filter(OrderPayment.OrderId==order.Id, OrderPayment.Status==True).all()
				return order
		return None
	
	def NewOrder(self,tenantId,userId):
		"""
			Creates new order in db and returns it
		"""
		if not tenantId or not userId:
			return None
		o = Order()
		o.Id = uuid.uuid4()
		o.TenantId = tenantId
		o.CustomerId = DefaultCustomerId
		o.CustomerName = 'Default'
		o.OrderNo = self.GenerateOrderNo(tenantId) #generate unique order no
		o.OrderDate = datetime.utcnow()
		o.IpAddress = None
		o.CreatedBy = userId
		o.CreatedOn = o.OrderDate = datetime.utcnow()
		o.Status = True
		DBSession.add(o) #add to db
		return o
	
	def SaveOrder(self, order,tenantId,userId):
		"""
			Saves the order details in db
		"""
		if order:
			if order["orderid"]:
				orderid = order["orderid"]
				o = self.GetOrderById(orderid,tenantId)
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
						DBSession.query(LineItem).filter(LineItem.OrderId==orderid).delete()
						self.SaveOrderLineItems(o.Id,lineitems)
					else:
						DBSession.query(LineItem).filter(LineItem.OrderId==orderid).delete()
						
					payments = order["payments"]
					if payments:
						DBSession.query(OrderPayment).filter(OrderPayment.OrderId==orderid).delete()
						self.SaveOrderPayments(o.Id,payments,userId)
					else:
						DBSession.query(OrderPayment).filter(OrderPayment.OrderId==orderid).delete()
		pass
	
	def SaveOrderLineItems(self,orderid,lineitems):
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
	
	def SaveOrderPayments(self,orderid,payments,userId):
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
			DBSession.query(Order).filter(Order.OrderId==orderid,Order.TenantId==tenantId).delete()
		pass
		
	def UpdateOrderPayment(self, orderid, orderpayment,userId):
		"""
			Saves the order payment details in db
		"""
		if orderpayment:
			if orderpayment.Id:
				o = DBSession.query(OrderPayment).get(orderpayment.Id)
				if o:
					o.UpdatedBy = userId
					o.UpdatedOn = datetime.utcnow()
			else:
				orderpayment.OrderId = orderid
				orderpayment.CreatedBy = userId
				orderpayment.CreatedOn = datetime.utcnow()
				DBSession.add(orderpayment)
					
		pass
		
	def DeleteOrderPayment(self, orderpaymentid):
		"""
			Deletes the order payment details from db
		"""
		if orderpaymentid:
			o = DBSession.query(OrderPayment).get(orderpaymentid)
			if o:
				DBSession.delete(o)			
		pass
	
	def SearchOrders(self,searchParam):
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
		if searchParam:
			query = DBSession.query(Order)
			
			if not searchParam.TenantId:
				return None
			
			query = query.filter(Order.TenantId==searchParam.TenantId)
			query = query.filter(Order.Status==True)
			
			if searchParam.UserId:
				query = query.filter(Order.CreatedBy==searchParam.UserId, \
										   Order.UpdatedBy==searchParam.UserId)
			if searchParam.OrderNo:
				query = query.filter(Order.OrderNo==searchParam.OrderNo)
			if searchParam.CustomerId:
				query = query.filter(Order.CustomerId==searchParam.CustomerId)
			if searchParam.IpAddress:
				query = query.filter(Order.IpAddress==searchParam.IpAddress)
				
			if searchParam.FromOrderDate and not searchParam.ToOrderDate:
				query = query.filter(cast(Order.OrderDate,Date) > searchParam.FromOrderDate)
			if not searchParam.FromOrderDate and searchParam.ToOrderDate:
				query = query.filter(cast(Order.OrderDate,Date) < searchParam.ToOrderDate)
			if searchParam.FromOrderDate and searchParam.ToOrderDate:
				query = query.filter(cast(Order.OrderDate,Date) > searchParam.FromOrderDate, \
										cast(Order.OrderDate,Date) <= searchParam.ToOrderDate)
										
			if searchParam.MinAmount and not searchParam.MaxAmount:
				query = query.filter(Order.OrderAmount >= searchParam.MinAmount)
			if not searchParam.MinAmount and searchParam.MaxAmount:
				query = query.filter(Order.OrderAmount <= searchParam.MaxAmount)
			if searchParam.MinAmount and searchParam.MaxAmount:
				query = query.filter(Order.OrderAmount >= searchParam.MinAmount, \
										Order.OrderAmount <= searchParam.MaxAmount)
			
			if not searchParam.PageNo:
				searchParam.PageNo = 0
			
			if not searchParam.PageSize and searchParam.PageSize <=0:
				searchParam.PageSize = 50
				
			query = query.order_by(desc(Order.OrderDate))
			query = query.limit(searchParam.PageSize).offset(searchParam.PageNo)
			orders = query.all()
			
			if orders:
				for order in orders:
					if order:
						order.CustomerName = None
						#fetch the line items here
						order.LineItems = DBSession.query(LineItem).filter(LineItem.OrderId==order.Id).all()
						if order.LineItems:
							order.OrderAmount = sum([x.Amount for x in order.LineItems])
						#fetch the payment details
						order.Payments = DBSession.query(OrderPayment).filter(OrderPayment.OrderId==order.Id, OrderPayment.Status==True).all()
						if order.Payments:
							order.PaidAmount = sum([x.PaidAmount for x in order.Payments])
			
			return orders
		return None
		
	def GenerateOrderNo(self,tenantId):
		import sys
		#return random.randint(0, sys.maxint)
		tmp = DBSession.query(func.max(Order.OrderNo)).filter(Order.TenantId==tenantId).scalar()
		if tmp != None: return int(tmp)+1 
		else: return 1
		
	pass

