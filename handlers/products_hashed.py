#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth

from stark.models.schema import ProductSchema
from stark.models.product import Product
from stark.models.affiliate import Affiliate
from stark.models.customer import Customer
from stark.models.images import ProductImage
from lannister.utils.caching_query import FromCache, RelationshipCache


class ProductHashHandler(CacheJSONHandler):
	@gen.coroutine
	@auth()
	@cache()
	def get(self, token):
		try:
			logger.debug('get products with token %s' % token)

			self.db.begin()
			criteria = self.db.query(Product).distinct(Product.id).group_by(Product.id)

			# lazy load images
			criteria = criteria.join(ProductImage)
		
			# fetch one
			criteria = self.db.query(Product).filter(Product.token == token)
			product = criteria.one()
			serializer = ProductSchema()
			self.response['product'] = serializer.dump(product).data

			self.db.commit()
			logger.debug(self.response)
			self.write_json()

		except Exception as error:
			self.db.rollback()
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch data')