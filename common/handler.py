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
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                self.request.data = json_data
                logger.debug('request body json data')
                logger.debug(json_data)
            except ValueError, e:
                logger.exception(e)
                message = 'Unsupported Media Type'
                self.send_error(415, message=message)  # Bad Request

        # Set up response dictionary
        self.respose = dict()

    def set_default_header(self):
        self.set_header('Content-Type', 'application/vnd.api+json')

    def write_error(self, status_code, **kwargs):
        logger.exception('write error with status code ' + status_code)
        response = dict()
        if 'message' not in kwargs:
            if status_code == 405:
                response['message'] = 'Invalid HTTP method'
            else:
                response['message'] = 'Unknwon error'
        else:
            response['message'] = kwargs['message']

        self.response = response
        self.write(output)

    def write_json(self):
        output = json.dumps(self.response)
        self.write(output)


class CacheJSONHandler(CacheMixin, JSONHandler):
    def prepare(self):
        super(CacheJSONHandler, self).prepare()
