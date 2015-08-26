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
AppURL["affiliate_product"] = "%s/affiliate_product/([A-Za-z0-9]+)" % api_version
AppURL["products"] = "%s/products" % api_version
AppURL["search_affiliates"] = "%s/affiliates/search" % api_version
AppURL["affiliate"] = "%s/affiliates/([0-9]+)" % api_version
AppURL["affiliates"] = "%s/affiliates" % api_version
AppURL["customer_socmed"] = "%s/socmed_accounts/([0-9]+)" % api_version
AppURL["customer_socmeds"] = "%s/socmed_accounts" % api_version
AppURL["socmed_posts"] = "%s/socmed_posts" % api_version
AppURL["twitter_redirect_url"] = "%s/socmeds/twitter/actions/redirect_url" % api_version
AppURL["twitter_verify_account"] = "%s/socmeds/twitter/actions/verify" % api_version
AppURL["users"] = "%s/users/([0-9]+)" % api_version
AppURL["affiliate_sales"] = "%s/affiliate_sales/([0-9]+)" % api_version
AppURL["product_affiliate_info"] = "%s/product_affiliate_info/([0-9]+)" % api_version