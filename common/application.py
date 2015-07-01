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
from lannister.utils.routes import AppURL
# resource handlers
from lannister.handlers.products import ProductHandler
from lannister.handlers.sessions import SessionHandler


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
        self.db = scoped_session(sessionmaker(bind=db_engine, autocommit=True))

        # Match url to preffered Handlers
        AppHandlers = [
            (r"/", HomeHandler),
            (r"%s" % AppURL["session_create"], SessionHandler),
            (r"%s" % AppURL["products"], ProductHandler)
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


class HomeHandler(JSONHandler):

    def get(self):
        logger.info('Hello from Jualio')
        self.response['title'] = "Juali API Service"
        self.write()