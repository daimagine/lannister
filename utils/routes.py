# json handler
from lannister.common.handler import JSONHandler
# settings
from lannister import settings


# define api version
api_version = '/api/' + settings.API_VERSION

# Add URL handler on this dict
AppURL = dict()
AppURL["session_create"] = "%s/sessions/create" % api_version
AppURL["auth_token"] = "%s/sessions/auth_token" % api_version
AppURL["product"] = "%s/products/([0-9]+)" % api_version
AppURL["products"] = "%s/products" % api_version
AppURL["search_affiliates"] = "%s/affiliates/search" % api_version
AppURL["affiliates"] = "%s/affiliates/([0-9]+)" % api_version