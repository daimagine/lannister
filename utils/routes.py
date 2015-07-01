# json handler
from lannister.common.handler import JSONHandler
# settings
from lannister import settings
# resource handlers
from lannister.handlers.products import ProductHandler
from lannister.handlers.sessions import SessionHandler


class HomeHandler(JSONHandler):

    def get(self):
        logger.info('Hello from Jualio')
        self.response['title'] = "Juali API Service"
        self.write()


# define api version
api_version = '/api/' + settings.API_VERSION

# Add URL handler on this dict
URL = dict()
URL["session_create"] = "%s/sessions/create" % api_version,
URL["products"] = "%s/products" % api_version