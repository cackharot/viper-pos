from ..library import CacheManager
import uuid

import logging
log = logging.getLogger(__name__)

_OrderCacheKey = 'OrderCacheKey'
_ProductCacheKey = '_productcachekey'
	
def initCacheAreas():
	log.info('Init cache keys...')
	CacheManager.Add(_ProductCacheKey, dict())
	CacheManager.Add(_OrderCacheKey, dict())
	return True
		
class OrderCacheService(object):
	_isinitialized = initCacheAreas()
	
	@staticmethod
	def AddProduct(entity):
		if entity and entity.Id:
			items = CacheManager.Get(_ProductCacheKey)
			if items:
				items[str(entity.Id)] = entity
				CacheManager.Add(_ProductCacheKey,items)
			else:
				log.debug('Cache miss. Should not happen!')
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
