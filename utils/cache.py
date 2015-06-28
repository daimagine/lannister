# coding: utf-8
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import hashlib
    sha1 = hashlib.sha1
except ImportError:
    import sha
    sha1 = sha.new
import functools
 
from lannister.utils.logs import logger
 
def cache(expires=7200, cache_enabled=True):
    def _func(func):
        @functools.wraps(func)
        def wrapper(handler, *args, **kwargs):
            handler.expires = expires
            handler.cache_enabled = cache_enabled
            return func(handler, *args, **kwargs)
        return wrapper
    return _func
 
class CacheMixin(object):
 
    @property
    def cache(self):
        return self.application.cache
 
    def prepare(self):
        super(CacheMixin, self).prepare()
        will_cache = True
        if hasattr(self, "cache_enabled"):
            will_cache = self.cache_enabled
        logger.debug('prepare: cache_enabled is %s', will_cache)

        key = self._generate_key(self.request)
        if self.cache.exists(self._prefix(key)) and will_cache:
            logger.debug('return cache from redis %s' % key)
            rv = pickle.loads(self.cache.get(self._prefix(key)))
            self.write_cache(rv)
            self.finish()
 
    def _generate_key(self, request):
        key = pickle.dumps((request.path, request.arguments))
        return sha1(key).hexdigest()
 
    def _prefix(self, key):
        return "Cache:%s" % key
 
    def write_cache(self, chunk):
        logger.debug('write cache')
        super(CacheMixin, self).write(chunk)
 
    def write(self, chunk):
        will_cache = True
        if hasattr(self, "cache_enabled"):
            will_cache = self.cache_enabled
        logger.debug('write: cache_enabled is %s', will_cache)

        if self.get_status() == 200 and will_cache:
            pickled = pickle.dumps(chunk)
            key = self._generate_key(self.request)
            logger.debug('write cache to redis %s' % key)
            if hasattr(self, "expires"):
                self.cache.set(self._prefix(key), pickled, self.expires)
            else:
                self.cache.set(self._prefix(key), pickled)
        super(CacheMixin, self).write(chunk)
 
 
class CacheBackend(object):
    """
    The base Cache Backend class
    """
 
    def get(self, key):
        raise NotImplementedError
 
    def set(self, key, value, timeout):
        raise NotImplementedError
 
    def delitem(self, key):
        raise NotImplementedError
 
    def exists(self, key):
        raise NotImplementedError
 
 
class RedisCacheBackend(CacheBackend):
 
    def __init__(self, redis_connection, **options):
        self.options = dict(timeout=86400)
        self.options.update(options)
        self.redis = redis_connection
 
    def get(self, key):
        if self.exists(key):
            return self.redis.get(key)
 
        return None
 
    def set(self, key, value, timeout=None):
        self.redis.set(key, value)
        if timeout:
            self.redis.expire(key, timeout)
        else:
            self.redis.expire(key, self.options["timeout"])
 
    def delitem(self, key):
        self.redis.delete(key)
 
    def exists(self, key):
        return bool(self.redis.exists(key))