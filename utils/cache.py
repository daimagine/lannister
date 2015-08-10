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
import base64
from sqlalchemy import event
from sqlalchemy.orm import Session
 
from lannister.utils.logs import logger
 
def cache(expires=7200, cache_enabled=True):
    def _func(func):
        @functools.wraps(func)
        def wrapper(handler, *args, **kwargs):
            logger.debug('cache annotation')
            handler.expires = expires
            handler.cache_enabled = cache_enabled
            try:
                logger.debug('cache: cache_enabled is %s', cache_enabled)
                key = handler._generate_key(handler.request)
                if handler.cache.exists(key) and cache_enabled:
                    logger.debug('return cache from redis %s' % key)
                    rv = pickle.loads(handler.cache.get(key))
                    handler.write_cache(rv)
                    handler.finish()
                else:
                    return func(handler, *args, **kwargs)
            except Exception, err:
                logger.exception(err)
                logger.debug('prepare failed %s', err.message)
                return func(handler, *args, **kwargs)
        return wrapper
    return _func


def generatePrefixKey(prefix):
    logger.debug('generate key for prefix %s' % prefix)
    def _prefix(key):
        prefixed = "cache:%s" % key
        return prefixed
    return _prefix(sha1(prefix).hexdigest())


def cache_refresh(handler, refresh_prefixes=[]):
    """
    Refresh cache with preffered prefix keys
    """
    try:
        prefixes = set(refresh_prefixes)
        for prefix in prefixes:
            key = generatePrefixKey(prefix)
            logger.debug('refresh cache with prefix key: %s' % key)
            handler.application.cache.delprefix(key)
    except Exception, err:
        logger.exception(err)
        logger.debug('refresh cache with prefix key [%s] failed: %s', (key, err.message))


class CacheMixin(object):
 
    @property
    def cache(self):
        return self.application.cache

    @property
    def redis(self):
        return self.application.redis
 
    def prepare(self):
        super(CacheMixin, self).prepare()
 
    def _generate_key(self, request):
        key = sha1(pickle.dumps(request.arguments)).hexdigest()
        prefix = generatePrefixKey(request.path)
        return "%s:%s" % (prefix, key)
 
    def write_cache(self, chunk):
        logger.debug('write cache')
        super(CacheMixin, self).write(chunk)
 
    def write(self, chunk):
        if hasattr(self, "cache_enabled"):
            logger.debug('write: cache_enabled is %s', self.cache_enabled)

            if self.get_status() == 200 and self.cache_enabled:
                pickled = pickle.dumps(chunk)
                key = self._generate_key(self.request)
                logger.debug('write cache to redis %s' % key)
                if hasattr(self, "expires"):
                    self.cache.set(key, pickled, self.expires)
                else:
                    self.cache.set(key, pickled)
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
            decoded = base64.b64decode(self.redis.get(key))
            return decoded
 
        return None
 
    def set(self, key, value, timeout=None):
        encoded = base64.b64encode(value.encode('utf-8'))
        self.redis.set(key, encoded)
        if timeout:
            self.redis.expire(key, timeout)
        else:
            self.redis.expire(key, self.options["timeout"])
 
    def delitem(self, key):
        self.redis.delete(key)

    def delprefix(self, prefix):
        prefixed = prefix + "*"
        keys = self.redis.keys(prefixed)
        for key in keys:
            logger.debug('remove cache %s' % key)
            self.redis.delete(key)
 
    def exists(self, key):
        return bool(self.redis.exists(key))