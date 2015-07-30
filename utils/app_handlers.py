# logging
from lannister.utils.logs import logger
# json handler
from lannister.common.handler import JSONHandler
# routes
from lannister.utils.routes import AppURL
# resource handlers
from lannister.handlers.products import ProductHandler
from lannister.handlers.sessions import SessionHandler
from lannister.handlers.tokens import AuthTokenHandler
from lannister.handlers.search_affiliates import SearchAffiliatesHandler
from lannister.handlers.affiliates import AffiliateHandler
from lannister.handlers.customer_socmeds import CustomerSocmedHandler


class HomeHandler(JSONHandler):

    def get(self):
        logger.info('Hello from Jualio')
        self.response['title'] = "Jualio API Service"
        self.write()


# Match url to preffered Handlers
AppHandlers = [
    (r"/", HomeHandler),
    (r"%s" % AppURL["session_create"], SessionHandler),
    (r"%s" % AppURL["auth_token"], AuthTokenHandler),
    (r"%s" % AppURL["product"], ProductHandler),
    (r"%s" % AppURL["products"], ProductHandler),
    (r"%s" % AppURL["search_affiliates"], SearchAffiliatesHandler),
    (r"%s" % AppURL["affiliate"], AffiliateHandler),
    (r"%s" % AppURL["affiliates"], AffiliateHandler),
    (r"%s" % AppURL["customer_socmeds"], CustomerSocmedHandler),
]        