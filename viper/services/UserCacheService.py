from ..library import CacheManager

userCacheKey = 'user:'	
		
class UserCacheService(object):
	
	@staticmethod
	def Add(entity):
		if entity and entity.Id:
			CacheManager.Add(userCacheKey+str(entity.Id),entity)
		pass
	
	@staticmethod
	def Get(id):
		if id:
			return CacheManager.Get(userCacheKey+str(id))
		return None
	
	@staticmethod
	def Remove(id):
		if id:
			CacheManager.Remove(userCacheKey+str(id))
	pass
