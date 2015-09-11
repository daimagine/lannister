# tornado
import tornado.web
# cache
from utils.cache import RedisCacheBackend
import redis
# settings
from lannister import settings
# logging
from lannister.utils.logs import logger
# sql alchemy
from sqlalchemy import create_engine, sql
from sqlalchemy.orm import scoped_session, sessionmaker

# routes
from lannister.utils.app_handlers import AppHandlers


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
        self.sql = sql

        super(Application, self).__init__(AppHandlers, **tornado_settings)