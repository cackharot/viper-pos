import memcache
import logging
log = logging.getLogger(__name__)

memcacheServers = ['127.0.0.1:11211']
cacheExpireTime = 0 #30*60 #in seconds [30 minutes]

def initCacheServer():
	log.info('Init Cache Manager with cache servers %s' % (memcacheServers))
	return memcache.Client(memcacheServers,debug=0)

class CacheManager(object):
	cache = initCacheServer()
	
	@staticmethod
	def Add(key,value):
		#log.info('adding %s=%s' % (key,value))
		CacheManager.cache.set(key,value)#,time=cacheExpireTime)
		pass
		
	@staticmethod
	def Get(key):
		value = CacheManager.cache.get(key)
		#log.info('getting %s=%s' % (key,value))
		return value
		
	@staticmethod
	def Remove(key):
		CacheManager.cache.delete(key)
		pass
		
	@staticmethod
	def Clear():
		CacheManager.cache.flush_all()
		pass

	pass
