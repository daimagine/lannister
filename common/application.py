# tornado
import tornado.web
# cache
from utils.cache import RedisCacheBackend
import redis
# settings
from lannister import settings
# logging
from lannister.utils.logs import logger
# json handler
from lannister.common.handler import JSONHandler
# sql alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# dogpiles
from dogpile.cache.region import make_region
from lannister.utils.caching_query import query_callable
from hashlib import md5

# routes
from lannister.utils.routes import AppHandlers


class Application(tornado.web.Application):
    def __init__(self):

        tornado_settings = dict(
            xsrf_cookies=False,
            debug=True,
        )

        self.redis = redis.Redis()
        self.cache = RedisCacheBackend(self.redis)

        # sqla
        db_user = settings.DATABASE.get('USER', 'postgres')
        db_pass = settings.DATABASE.get('PASSWORD', '')
        db_server = settings.DATABASE.get('HOST', 'localhost')
        db_port = settings.DATABASE.get('PORT', '5432')
        db_name = settings.DATABASE.get('NAME', '')
        dsn = "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
            db_user,
            db_pass,
            db_server,
            db_port,
            db_name
        )

        db_engine = create_engine(dsn, echo=True)
        #self.db = scoped_session(sessionmaker(bind=db_engine, autocommit=True))

        # dogpile cache regions.  A home base for cache configurations.
        regions = {}

        # configure the "default" cache region.
        regions['default'] = make_region(
                    # string-encoded keys
                    key_mangler=md5_key_mangler
                ).configure(
                    'dogpile.cache.redis',
                    arguments = {
                        'host': 'localhost',
                        'port': 6379,
                        'db': 0,
                        'redis_expiration_time': 60*60*2,   # 2 hours
                        'distributed_lock': True
                        }
                )

        # scoped_session.  Apply our custom CachingQuery class to it,
        # using a callable that will associate the dictionary
        # of regions with the Query.
        self.db = scoped_session(
                        sessionmaker(
                            bind=db_engine, 
                            autocommit=True,
                            query_cls=query_callable(regions)
                        )
                    )

        # optional; call invalidate() on the region
        # once created so that all data is fresh when
        # the app is restarted.  Good for development,
        # on a production system needs to be used carefully
        # regions['default'].invalidate()

        # Match url to preffered Handlers
        AppHandlers = [
            (r"/", HomeHandler),
            (r"%s" % URL["session_create"], SessionHandler),
            (r"%s" % URL["products"], ProductHandler)
        ]
        
        super(Application, self).__init__(AppHandlers, **tornado_settings)


def md5_key_mangler(key):
    """Receive cache keys as long concatenated strings;
    distill them into an md5 hash.

    """
    key = md5(key.encode('ascii')).hexdigest()
    logger.debug('App: md5_key_mangler ')
    logger.debug(key)
    return key