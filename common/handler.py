# tornado
import tornado.web
import json
# cache
from lannister.utils.cache import CacheMixin
# logging
from lannister.utils.logs import logger


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

        # Set up response dictionary
        self.respose = dict()
        self.set_default_header()

    def set_default_header(self):
        logger.debug('set default header to application/vnd.api+json')
        self.set_header('Content-Type', 'application/vnd.api+json')

    def write_error(self, status_code, **kwargs):
        logger.debug('write error with status code %s' % status_code)
        response = dict()
        if 'message' not in kwargs:
            if status_code == 405:
                response['message'] = 'Invalid HTTP method'
            else:
                response['message'] = 'Unknwon error'
        else:
            response['message'] = kwargs['message']

        self.response = response
        self.set_status(status_code)
        
        logger.debug(self.response)
        self.write(self.response)

    def write_json(self):
        logger.debug('write_json')
        output = json.dumps(self.response)
        logger.debug(output)
        self.write(output)


class CacheJSONHandler(CacheMixin, JSONHandler):
    def prepare(self):
        super(CacheJSONHandler, self).prepare()