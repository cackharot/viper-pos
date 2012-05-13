from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import pyramid
import uuid
from datetime import datetime 

from sqlalchemy.exc import DBAPIError

from viper.models import (
    DBSession,
    )
from ..models.Product import Product
from ..library.ViperLog import log

def includeme(config):
	config.add_route('stock', '/stock')
	config.add_route('products', '/stock/products')
	config.add_route('addproduct', '/stock/product/add')
	config.add_route('editproduct', '/stock/product/edit/{pid}')
	config.add_route('saveproduct', '/stock/product/save')
	config.add_route('deleteproduct', '/stock/product/delete/{pid}')
	pass

@view_config(route_name='stock', renderer='stock/index.jinja2')
def stockPage(request):
    return {}
    
@view_config(route_name='products', renderer='stock/products/index.jinja2')
def productListPage(request):
	try:
		pageNo = request.params.get('pageNo',0)
		pageSize = request.params.get('pageSize', 50)
		searchValue = request.params.get('searchValue', None)
		
		query = DBSession.query(Product)
		
		if searchValue is not None and searchValue != '':
			query = query.filter_by(Name=searchValue)
		
		lstItems = query.offset(pageNo).limit(pageSize).all()
	except DBAPIError:
		return Response(conn_err_msg, content_type='text/plain', status_int=500)
	return {'model':lstItems}
	
@view_config(route_name='addproduct', renderer='stock/products/manage.jinja2')
def addProduct(request):
	model = Product()
	return {'model':model}

@view_config(route_name='editproduct', renderer='stock/products/manage.jinja2')
def editProduct(request):
	pid = request.matchdict['pid']
	if pid == None or pid == '':
		return HTTPFound(location = request.route_url('products'))
	else:
		model = DBSession.query(Product).get(pid)
	return {'model':model}

@view_config(route_name='saveproduct', renderer='stock/products/manage.jinja2', request_method='POST')	
def saveProduct(request):
	pid = request.params.get('Id')
	log.info('Product Id: ' + pid)
	if pid == None or pid == '':
		p = Product()
	else:
		p = DBSession.query(Product).get(uuid.UUID(pid))
		
	p.TenantId = request.user.TenantId
	p.CreatedBy = request.user.Id
	p.UpdatedBy = request.user.Id
	p.Barcode = request.params.get('Barcode', None)
	p.Name = request.params.get('Name', None)
	p.MRP = request.params.get('MRP', 0.0)
	p.BuyPrice = request.params.get('BuyPrice', 0.0)
	p.SellPrice = request.params.get('SellPrice', 0.0)
	p.Discount = request.params.get('Discount', 0.0)
	
	tmp = request.params.get('MfgDate',None)
	if not tmp and tmp != '':
		p.MfgDate = datetime.strptime(tmp,'%d-%m-%Y')
	
	tmp = request.params.get('ExpiryDate',None)
	if not tmp and tmp != '':
		p.ExpiryDate = datetime.strptime(tmp,'%d-%m-%Y')
	
	if p.Name !=None and p.Barcode != None and p.MRP > 0.0 \
		and p.BuyPrice < p.MRP and p.SellPrice > p.BuyPrice:
		DBSession.add(p)
	return HTTPFound(location = request.route_url('products'))

@view_config(route_name='deleteproduct')	
def deleteProduct(request):
	pid = request.matchdict['pid']
	if pid != None or pid == '':
		model = DBSession.query(Product).get(pid)
		if model != None:
			DBSession.delete(model)
	return HTTPFound(location = request.route_url('products'))
      
conn_err_msg = """
Error In fetching Products.
"""
