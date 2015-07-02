# json handler
from lannister.common.handler import JSONHandler
# settings
from lannister import settings


# define api version
api_version = '/api/' + settings.API_VERSION

# Add URL handler on this dict
AppURL = dict()
AppURL["session_create"] = "%s/sessions/create" % api_version,
AppURL["products"] = "%s/products" % api_version
AppURL["product"] = "%s/product/([0-9]+)" % api_version