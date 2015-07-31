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
# hashids
from hashids import Hashids
hashids = Hashids()

from stark.models.schema import ProductSchema, AffiliateInfoSchema
from stark.models.product import Product
from stark.models.affiliate import Affiliate
from stark.models.customer import Customer

import re
from lannister.utils.routes import AppURL, api_version


class AffiliateHandler(CacheJSONHandler):

	def refresh_cache(self, productId=None):
		# refresh cache
		product_url = "%s/products/%s" % (api_version, productId)
		cache_refresh(self, [AppURL["products"], product_url, AppURL["affiliates"]])


	@gen.coroutine
	@auth()
	@cache()
	def get(self, id=None):
		try:
			logger.debug('get affiliates info')
			logger.debug(self.request.arguments)

			self.db.begin()
			criteria = self.db.query(Affiliate).distinct(Affiliate.id).group_by(Affiliate.id)

			# filtering
			if id == None:
				# customer
				customer_filter = False
				if 'customer' in self.request.arguments:
					customer_filter = True
					customer_id = self.get_argument('customer')
					logger.debug('customer criteria: %s' % customer_id)
					criteria = criteria.filter(Affiliate.customer_id == customer_id)

				# product
				product_filter = False
				if 'product' in self.request.arguments:
					product_filter = True
					product_id = self.get_argument('product')
					logger.debug('product criteria: %s' % product_id)
					criteria = criteria.filter(Affiliate.product_id == product_id)

				if customer_filter and product_filter:
					# fetch one
					affiliate = criteria.one()
					serializer = AffiliateInfoSchema()
					self.response['affiliate'] = serializer.dump(affiliate).data

				else:
					affiliates = criteria.all()
					serializer = AffiliateInfoSchema(many= True)
					self.response['affiliates'] = serializer.dump(affiliates).data

			else:
				# fetch one
				criteria = self.db.query(Affiliate).filter(Affiliate.id == id)
				affiliate = criteria.one()
				serializer = AffiliateInfoSchema()
				self.response['affiliate'] = serializer.dump(affiliate).data

			self.db.commit()
			logger.debug(self.response)
			self.write_json()

		except Exception as error:
			self.db.rollback()
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch data');

	@gen.coroutine
	@auth()
	def post(self, id):
		try:
			self.db.begin()
			logger.debug('join products affiliate %s' % id)
			
			# extract body
			customer_id = self.request.data['customer_id']
			logger.debug('customer %s' % customer_id)

			# get customer
			criteria = self.db.query(Customer).filter(Customer.id == customer_id)
			customer = criteria.one()

			criteria = self.db.query(Product).filter(Product.id == id)
			product = criteria.one()

			# create new affiliate
			affiliate = Affiliate(product=product, customer=customer)
			# create new product page with hashid
			newid = hashids.encode(product.id)
			affiliate.product_page = "%s/%s" % (AFFILIATE_URL, newid)
			affiliate.headline = product.headline
			product.affiliates.append(affiliate)

			# save product
			self.db.commit()

			# return response
			serializer = ProductSchema()
			self.response['product'] = serializer.dump(product).data
			self.response['message'] = 'Join affiliate success'
			self.response['success'] = True

			# refresh cache
			self.refresh_cache(productId=id)

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to join affiliate')


	@gen.coroutine
	@auth()
	def delete(self, id):
		try:
			self.db.begin()
			logger.debug('remove products affiliate %s' % id)
			
			# extract body
			customer_id = self.request.data['customer_id']
			logger.debug('customer %s' % customer_id)

			# get affiliate
			criteria = self.db.query(Affiliate)
			criteria = criteria.filter(Affiliate.product_id == id)
			criteria = criteria.filter(Affiliate.customer_id == customer_id)
			affiliate = criteria.one()

			# remove affiliate
			self.db.delete(affiliate)

			# commit
			self.db.commit()

			# get updated product
			self.db.begin()

			criteria = self.db.query(Product).filter(Product.id == id)
			product = criteria.one()

			self.db.commit()

			# return response
			serializer = ProductSchema()
			self.response['product'] = serializer.dump(product).data
			self.response['message'] = 'Remove affiliate success'
			self.response['success'] = True

			# refresh cache
			self.refresh_cache(productId=id)

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to remove affiliate')