# logging
from lannister.utils.logs import logger
# json handler
from lannister.common.handler import JSONHandler
# routes
from lannister.utils.routes import AppURL
# resource handlers
from lannister.handlers.products import ProductHandler
from lannister.handlers.affiliate_product import AffiliateProductHandler
from lannister.handlers.sessions import SessionHandler
from lannister.handlers.tokens import AuthTokenHandler
from lannister.handlers.search_affiliates import SearchAffiliatesHandler
from lannister.handlers.affiliates import AffiliateHandler
from lannister.handlers.customer_socmeds import CustomerSocmedHandler
from lannister.handlers.socmed_posts import SocmedPostHandler
from lannister.handlers.twitter.add_accounts import AddTwitterAccountHandler
from lannister.handlers.users import UserHandler


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
    (r"%s" % AppURL["affiliate_product"], AffiliateProductHandler),
    (r"%s" % AppURL["affiliate"], AffiliateHandler),
    (r"%s" % AppURL["affiliates"], AffiliateHandler),
    (r"%s" % AppURL["customer_socmeds"], CustomerSocmedHandler),
    (r"%s" % AppURL["socmed_posts"], SocmedPostHandler),
    (r"%s" % AppURL["twitter_redirect_url"], AddTwitterAccountHandler),
    (r"%s" % AppURL["twitter_verify_account"], AddTwitterAccountHandler),
    (r"%s" % AppURL["users"], UserHandler),
]        