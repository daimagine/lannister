# tornado
import tornado.web
import functools
import simplejson as json
from datetime import datetime
# cache
from lannister.utils.cache import CacheMixin
# logging
from lannister.utils.logs import logger
# schema
from stark.models.customer import Customer


def auth(required=False):
    def _func(func):
        @functools.wraps(func)
        def wrapper(handler, *args, **kwargs):
            auth_required = required
            logger.debug('BaseHandler: auth_required is %s', auth_required)
            if auth_required:
                try:
                    client_token = handler.request.headers['Authorization']
                    # find customer by client_token and valid time criteria
                    handler.db.begin()
                    criteria = handler.db.query(Customer)
                    logger.debug('find customer by client_token: %s' % client_token)
                    criteria = criteria.filter(Customer.client_token == client_token)
                    criteria = criteria.filter(Customer.client_token_valid_time > datetime.utcnow())
                    # find or fail customer
                    customer = criteria.one()
                    handler.db.commit()
                except Exception, err:
                    handler.db.rollback()
                    logger.exception(err)
                    message = 'Authentication Failed'
                    self.send_error(400, message=message)

            return func(handler, *args, **kwargs)
        return wrapper
    return _func


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class JSONHandler(BaseHandler):
    ''' RequestHandler for JSON request and response '''

    def prepare(self):
        logger.debug(self.request)
        logger.debug(self.request.body)
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                self.request.data = json_data
                logger.debug('request body json data:')
                logger.debug(json_data)
            except ValueError, e:
                logger.exception(e)
                message = 'Unsupported Media Type'
                self.send_error(415, message=message)  # Bad Request

        # listen for db changes

        # Set up response dictionary
        self.response = dict()
        self.set_default_header()

    def set_default_header(self):
        logger.debug('set default header to application/vnd.api+json')
        self.set_header('Content-Type', 'application/vnd.api+json')

    def write_error(self, status_code, **kwargs):
        logger.debug('write error with status code %s' % status_code)
        response = dict()
        if 'error' not in kwargs:
            if status_code == 405:
                response['error'] = 'Invalid HTTP method'
            else:
                response['error'] = 'Unknown error'
        else:
            response['error'] = kwargs['error']

        self.response = response
        self.set_status(status_code)
        
        logger.debug(self.response)
        self.write(self.response)

    def write_json(self):
        logger.debug('write_json')
        output = json.dumps(self.response)
        # logger.debug(output)
        self.write(output)


class CacheJSONHandler(CacheMixin, JSONHandler):
    def prepare(self):
        super(CacheJSONHandler, self).prepare()