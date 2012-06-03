from ..library import CacheManager
import uuid

import logging
log = logging.getLogger(__name__)

_OrderCacheKey = 'order:'
_ProductCacheKey = 'product:'
	
class OrderCacheService(object):
	"""
		Order, Product Cache service manager
	"""
	@staticmethod
	def AddProduct(entity):
		if entity and entity.Id:
			items = CacheManager.Get(_ProductCacheKey)
			if items:
				items[str(entity.Id)] = entity
				CacheManager.Add(_ProductCacheKey,items)
			else:
				v = dict()
				v[str(entity.Id)] = entity
				CacheManager.Add(_ProductCacheKey, v)
				log.debug('Init product cache area!')
			return True
		return False
	
	@staticmethod
	def GetProduct(id):
		if isinstance(id,uuid.UUID):
			id = str(id)
		if id:
			items = CacheManager.Get(_ProductCacheKey)
			if items and items.has_key(id):
				return items[id]
		return None
	
	@staticmethod
	def GetProductsByBarcode(tenantId,barcode):
		items = CacheManager.Get(_ProductCacheKey)
		if items and len(items) > 0:
			res = [v for k,v in items.items() if v.TenantId==tenantId and v.Barcode==barcode]
			return res
		return None
	
	@staticmethod
	def RemoveProduct(id):
		if isinstance(id,uuid.UUID):
			id = str(id)
		if id:
			items = CacheManager.Get(_ProductCacheKey)
			if items and items.has_key(id):
				del items[id]
				CacheManager.Add(_ProductCacheKey,items)
				return True
		return False
	pass
