from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import pyramid
from datetime import datetime 
import json
from sqlalchemy.exc import DBAPIError
from sqlalchemy import func

from viper.models import (
    DBSession,
    )
from viper.models.Customer import Customer
from ..library.UserIdentity import UserIdentity
from ..library.helpers import jsonHandler

def includeme(config):
	config.add_route('customers', '/customers')
	config.add_route('addcustomer', '/customers/add')
	config.add_route('editcustomer', '/customers/edit/{cid}')
	config.add_route('savecustomer', '/customers/save')
	config.add_route('deletecustomer', '/customers/delete/{cid}')
	config.add_route('searchcustomer', '/customers/search')
	pass

@view_config(route_name='searchcustomer', renderer='json')
def searchCustomer(request):
	try:
		searchValue = request.params.get('search')
		field = request.params.get('field','name')
		result = None		
		query = DBSession.query(Customer)
		
		if searchValue is not None and searchValue != '':
			searchValue = '%%%s%%' % searchValue
			if field == 'name':
				query = query.filter(Customer.FirstName.like(searchValue))
			elif field == 'mobile':
				query = query.filter(Customer.Mobile.like(searchValue))
			elif field == 'customerno':
				query = query.filter(Customer.Mobile.like(searchValue))
			lstItems = query.offset(0).limit(10).all()
			if lstItems:
				result = json.dumps([dict(name=x.FirstName,id=x.Id,mobile=x.Mobile) for x in lstItems],default=jsonHandler)
	except DBAPIError:
		return {'status':'error','message':'Error while searching for customers!'}
	return {'mylist':result}

@view_config(route_name='customers', renderer='customers/index.jinja2')
def customerList(request):
	try:
		pageNo = request.params.get('pageNo',0)
		pageSize = request.params.get('pageSize', 50)
		searchValue = request.params.get('searchValue', None)
		
		query = DBSession.query(Customer)
		
		if searchValue is not None and searchValue != '':
			query = query.filter(Customer.FirstName==searchValue)
		
		lstItems = query.offset(pageNo).limit(pageSize).all()
	except DBAPIError:
		return Response(conn_err_msg, content_type='text/plain', status_int=500)
	return {'model':lstItems}


@view_config(route_name='addcustomer', renderer='customers/manage.jinja2')
def addCustomer(request):
	model = Customer()
	return {'model':model}
		
@view_config(route_name='editcustomer', renderer='customers/manage.jinja2')
def editCustomer(request):
	cid = request.matchdict['cid']
	if cid == None or cid == '':
		return HTTPFound(location = request.route_url('customers'))
	else:
		model = DBSession.query(Customer).get(cid)
	return {'model':model}

@view_config(route_name='savecustomer', renderer='customers/manage.jinja2', request_method='POST')	
def saveCustomer(request):
	cid = request.params.get('Id')
	if cid == None or cid == '':
		c = Customer()
	else:
		c = DBSession.query(Customer).get(cid)
	
	if c.SSN == None or c.SSN <= 0:
		c.SSN = int(DBSession.execute('SELECT MAX(SSN) FROM Customers').scalar()) + 1	
	c.TenantId = UserIdentity.TenantId
	c.FirstName = request.params.get('FirstName', None)
	c.LastName = request.params.get('LastName', None)
	c.Email = request.params.get('Email', None)
	c.Phone = request.params.get('Phone', None)
	c.Mobile = request.params.get('Mobile', None)
	c.Address = request.params.get('Address', None)
	c.City = request.params.get('City', None)
	
	if c.FirstName !=None and len(c.FirstName) > 4:
		DBSession.add(c)
	return HTTPFound(location = request.route_url('customers'))

@view_config(route_name='deletecustomer')	
def deleteCustomer(request):
	cid = request.matchdict['cid']
	if cid != None or cid == '':
		model = DBSession.query(Customer).get(cid)
		if model != None:
			DBSession.delete(model)
	return HTTPFound(location = request.route_url('customers'))
      
conn_err_msg = """
Error in fetching customers.
"""
