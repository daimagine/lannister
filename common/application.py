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

# resource handlers
from lannister.handlers.products import ProductHandler
from lannister.handlers.sessions import SessionHandler


class Application(tornado.web.Application):
    def __init__(self):
        api_version = '/api/' + settings.DEFAULT_API
        handlers = [
            (r"/", HomeHandler),
            (r"%s/sessions/create" % api_version, SessionHandler),
            (r"%s/products" % api_version, ProductHandler)
        ]

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
        self.db = scoped_session(sessionmaker(bind=db_engine))

        super(Application, self).__init__(handlers, **tornado_settings)


class HomeHandler(JSONHandler):

    def get(self):
        logger.info('Hello from Jualio')
        self.response['title'] = "Juali API Service"
        self.write()
