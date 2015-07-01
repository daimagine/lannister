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
 
from lannister.utils.logs import logger
 
def cache(expires=7200, cache_enabled=True, refresh_cache=[]):
    def _func(func):
        @functools.wraps(func)
        def wrapper(handler, *args, **kwargs):
            handler.expires = expires
            handler.cache_enabled = cache_enabled
            handler.refresh_cache = refresh_cache
            return func(handler, *args, **kwargs)
        return wrapper
    return _func
 
class CacheMixin(object):
 
    @property
    def cache(self):
        return self.application.cache

    @property
    def redis(self):
        return self.application.redis
 
    def prepare(self):
        super(CacheMixin, self).prepare()

        will_cache = True
        if hasattr(self, "cache_enabled"):
            will_cache = self.cache_enabled
        logger.debug('prepare: cache_enabled is %s', will_cache)

        try:
            logger.debug('get cache from redis')
            key = self._generate_key(self.request)
            if self.cache.exists(self._prefix(key)) and will_cache:
                logger.debug('return cache from redis %s' % key)
                rv = pickle.loads(self.cache.get(self._prefix(key)))
                self.write_cache(rv)
                self.finish()
        except Exception, err:
            logger.debug('redis cache fetch failed %s', err.message)
 
    def _generate_key(self, request):
        key = sha1(pickle.dumps(request.arguments)).hexdigest()
        prefix = sha1(request.path).hexdigest()
        return "%s:%s" % (prefix, key)
 
    def _prefix(self, key):
        prefixed = "cache:%s" % key
        return prefixed
 
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

    def cache_refresh(session, refresh_prefixes):
        """
        Refresh the functions cache data in a new thread. Starts refreshing only
        after the session was committed so all database data is available.
        """
        assert isinstance(session, Session), \
            "Need a session, not a sessionmaker or scoped_session"

        @event.listens_for(session, "after_commit")
        def do_refresh(session):
            """
            TODO: create auto commit listener for auto flush
            flush by entity single or multiple key 
            get the key from from auto_flush annotation
            ex: product:1 (single), products (multiple)
            """
            return
 
 
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
 
    def exists(self, key):
        return bool(self.redis.exists(key))