import json
import uuid
import random
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

DefaultCustomerId = '123'

class OrderService(object):
	"""
		Order service class
	"""
	
	def GetOrderById(self, orderid):
		"""
			Fetchs the orders details by order id
			Returns Order Object if found else None
		"""
		if orderid:
			order = DBSession.query(Order).filter_by(Id=orderid, TenantId=UserIdentity.TenantId,Status=True).first()
			if order:
				order.LineItems = None #fetch the line items here
				order.Payments = None #fetch the payment details
				return order
		return None
	
	def NewOrder(self):
		"""
			Creates new order in db and returns it
		"""
		o = Order()
		o.TenantId = UserIdentity.TenantId
		#o.CustomerId = DefaultCustomerId
		o.OrderNo = self.GenerateOrderNo() #generate unique order no
		o.IpAddress = UserIdentity.IpAddress
		o.CreatedBy = UserIdentity.UserId
		o.CreatedOn = o.OrderDate = datetime.utcnow()
		o.Status = True
		DBSession.add(o) #add to db
		return o
	
	def SaveOrder(self, order):
		"""
			Saves the order details in db
		"""
		if order:
			if order.Id:
				o = self.GetOrderById(order.Id)
				if o:
					o.IpAddress = UserIdentity.IpAddress
					o.UpdatedBy = UserIdentity.UserId
					o.UpdatedOn = datetime.utcnow()
			else:
				order.TenantId = UserIdentity.TenantId
				order.IpAddress = UserIdentity.IpAddress
				order.CreatedBy = UserIdentity.UserId
				order.CreatedOn = datetime.utcnow()
				DBSession.add(order) #saves to db
				
			if order.LineItems and len(order.LineItems):
				for i in order.LineItems:
					DBSession.add(i)
					
			if order.Payments and len(order.Payments):
				for p in order.Payments:
					DBSession.add(p)
		pass
		
	def DeleteOrder(self, order):
		"""
			Deletes the order details from db
		"""
		if order and order.Id:
			o = DBSession.query(Order).filter_by(OrderId=order.Id,TenantId=UserIdentity.TenantId).first()
			if o:
				DBSession.remove(o)
		pass
		
	def SaveOrderPayment(self, orderid, orderpayment):
		"""
			Saves the order payment details in db
		"""
		if orderpayment:
			if orderpayment.Id:
				o = DBSession.query(OrderPayment).get(orderpayment.Id)
				if o:
					o.UpdatedBy = UserIdentity.UserId
					o.UpdatedOn = datetime.utcnow()
			else:
				orderpayment.OrderId = orderid
				orderpayment.CreatedBy = UserIdentity.UserId
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
				DBSession.remove(o)			
		pass
	
	def SearchOrders(self,searchParam):
		"""
			Searchs the order from the given parameters
			Searchable Params:
				TenantId (default=UserIdentity.TenantId)
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
				searchParam.TenantId = UserIdentity.TenantId
			
			query = query.filter_by(TenantId=searchParam.TenantId,Status=True)
			
			if searchParam.UserId:
				query = query.filter_by(CreatedBy=searchParam.UserId, \
										   UpdatedBy=searchParam.UserId)
			if searchParam.OrderNo:
				query = query.filter_by(OrderNo=searchParam.OrderNo)
			if searchParam.CustomerId:
				query = query.filter_by(CustomerId=searchParam.CustomerId)
			if searchParam.IpAddress:
				query = query.filter_by(IpAddress=searchParam.IpAddress)
				
			if searchParam.FromOrderDate and not searchParam.ToOrderDate:
				query = query.filter_by(OrderDate>=searchParam.FromOrderDate)
			if not searchParam.FromOrderDate and searchParam.ToOrderDate:
				query = query.filter_by(OrderDate<=searchParam.ToOrderDate)
			if searchParam.FromOrderDate and searchParam.ToOrderDate:
				query = query.filter_by(OrderDate>=searchParam.FromOrderDate, \
										OrderDate<=searchParam.ToOrderDate)
										
			if searchParam.MinAmount and not searchParam.MaxAmount:
				query = query.filter_by(OrderAmount>=searchParam.MinAmount)
			if not searchParam.MinAmount and searchParam.MaxAmount:
				query = query.filter_by(OrderAmount<=searchParam.MaxAmount)
			if searchParam.MinAmount and searchParam.MaxAmount:
				query = query.filter_by(OrderAmount>=searchParam.MinAmount, \
										OrderAmount<=searchParam.MaxAmount)
			
			if not searchParam.PageNo:
				searchParam.PageNo = 0
			
			if not searchParam.PageSize and searchParam.PageSize <=0:
				searchParam.PageSize = 50
				
			query = query.limit(searchParam.PageSize).offset(searchParam.PageNo)
			return query.all()
		return None
		
	def GenerateOrderNo(self):
		import sys
		return random.randint(0, sys.maxint)
		
	pass

