#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth

from stark.models.schema import ProductSchema
from stark.models.product import Product
from stark.models.affiliate import Affiliate
from stark.models.customer import Customer
from stark.models.images import ProductImage
from lannister.utils.caching_query import FromCache, RelationshipCache

from lannister.utils.routes import AppURL, api_version


class ProductAffiliateInfoHandler(CacheJSONHandler):

	def refresh_cache(self, productId=None):
		# refresh cache
		product_url = "%s/products/%s" % (api_version, productId)
		cache_refresh(self, [AppURL["products"], product_url, AppURL["affiliates"]])

	@gen.coroutine
	@auth()
	def put(self, id):
		try:
			self.db.begin()
			logger.debug('post products %s' % id)
			
			# extract body
			productParam = self.request.data['product']
			logger.debug(productParam)

			criteria = self.db.query(Product).filter(Product.id == id)
			product = criteria.one()

			# extract param
			is_affiliate_ready = productParam['is_affiliate_ready']
			affiliate_fee_type = productParam['affiliate_fee_type']
			affiliate_fee = productParam['affiliate_fee']
			affiliate_percentage = productParam['affiliate_percentage']

			# validate affiliate fee thru product client formula


			# update affiliate
			product.is_affiliate_ready = is_affiliate_ready
			product.affiliate_fee = affiliate_fee
			product.affiliate_fee_type = affiliate_fee_type
			product.affiliate_percentage = affiliate_percentage

			# save product
			self.db.commit()

			# return response
			serializer = ProductSchema()
			self.response['product'] = serializer.dump(product).data
			self.response['message'] = 'Update product affiliate info success'
			self.response['success'] = True

			# refresh cache
			self.refresh_cache(productId=id)

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to save product')