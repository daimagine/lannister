#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth
# settings
from lannister.settings import AFFILIATE_URL
# social medias
from lannister.interfaces.social_media import constants as SOCIAL_MEDIA
from lannister.interfaces.social_media.exceptions import SocmedPostException
from lannister.interfaces.social_media.base import SocmedInterface

from stark.models.schema import ProductSchema, AffiliateInfoSchema
from stark.models.product import Product
from stark.models.affiliate import Affiliate
from stark.models.customer import Customer
from stark.models.customer_socmed_account import CustomerSocmedAccount

import re
from lannister.utils.routes import AppURL, api_version


class SocmedPostHandler(CacheJSONHandler):

	def refresh_cache(self, productId=None):
		# refresh cache
		product_url = "%s/products/%s" % (api_version, productId)
		cache_refresh(self, [AppURL["products"], product_url, AppURL["affiliates"]])

	@gen.coroutine
	@auth()
	def post(self):
		try:
			self.db.begin()
			logger.debug('post headline to socmeds')
			
			# extract body
			headline = self.request.data['headline']
			socmed_account_ids = self.request.data['socmed_accounts']
			product_page = self.request.data['product_page']
			product_id = self.request.data['product_id']
			affiliate_id = 0
			if 'affiliate_id' in self.request.data:
				affiliate_id = self.request.data['affiliate_id']

			# get socmed accounts data
			criteria = self.db.query(CustomerSocmedAccount)
			criteria = criteria.distinct(CustomerSocmedAccount.id)
			criteria = criteria.group_by(CustomerSocmedAccount.id)

			criteria = criteria.filter(CustomerSocmedAccount.id.in_(socmed_account_ids))
			socmed_accounts = criteria.all()

			if affiliate_id != 0:
				# find and update affiliate headline
				logger.debug('find and update affiliate by affiliate_id %s' % affiliate_id)
				affiliate_criteria = self.db.query(Affiliate).filter(Affiliate.id == affiliate_id)
				affiliate = affiliate_criteria.one()
				affiliate.headline = headline
				# set affiliate response
				serializer = AffiliateInfoSchema()
				self.response['affiliate'] = serializer.dump(affiliate).data

			else :
				# find and update product headline
				logger.debug('find and update product by product_id %s' % product_id)
				product_criteria = self.db.query(Product).filter(Product.id == product_id)
				product = product_criteria.one()
				product.headline = headline
				# set product response
				serializer = ProductSchema()
				self.response['product'] = serializer.dump(product).data

			# save product or affiliate headline
			self.db.commit()

			# having all required infos, post to social medias
			for socmed in socmed_accounts:
				logger.debug('post to socmed account %s' % socmed.social_name)
				if socmed.social_media.id == SOCIAL_MEDIA.TWITTER:
					SocmedInterface.post(socmed, headline, product_page)

			# return response
			self.response['message'] = 'Post to social media success'
			self.response['success'] = True

			# refresh cache
			self.refresh_cache(productId=product_id)

			logger.debug(self.response)
			self.write_json()

		except SocmedPostException, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error=error.message)

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to post to social media')