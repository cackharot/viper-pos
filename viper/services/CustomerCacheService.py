from ..library import CacheManager

customerCacheKey = 'cus:'	
		
class CustomerCacheService(object):
	
	@staticmethod
	def Add(entity):
		if entity and entity.Id:
			CacheManager.Add(customerCacheKey+str(entity.Id),entity)
		pass
		
	@staticmethod
	def AddDefault(entity):
		if entity and entity.Id and entity.TenantId:
			CacheManager.Add(customerCacheKey+str(entity.TenantId)+':def',entity)
		return
	
	@staticmethod
	def GetDefault(tenantId):
		if tenantId:
			return CacheManager.Get(customerCacheKey+str(tenantId)+':def')
		return None
		
	@staticmethod
	def RemoveDefault(tenantId):
		if tenantId:
			CacheManager.Remove(customerCacheKey+str(tenantId)+':def')
		
	@staticmethod
	def Get(id):
		if id:
			return CacheManager.Get(customerCacheKey+str(id))
		return None
	
	@staticmethod
	def Remove(id):
		if id:
			CacheManager.Remove(customerCacheKey+str(id))
	pass
