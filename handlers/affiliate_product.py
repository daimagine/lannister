#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth

from stark.models.schema import AffiliateSchema
from stark.models.product import Product
from stark.models.affiliate import Affiliate
from stark.models.customer import Customer
from stark.models.images import ProductImage
from lannister.utils.caching_query import FromCache, RelationshipCache


class AffiliateProductHandler(CacheJSONHandler):
	@gen.coroutine
	@auth()
	@cache()
	def get(self, token):
		try:
			logger.debug('get affiliate products with token %s' % token)
			self.db.begin()

			# get affiliate info
			criteria = self.db.query(Affiliate).distinct(Affiliate.id).group_by(Affiliate.id)

			# lazy load entities
			criteria = criteria.join(Product).join(ProductImage)
			
			# fetch one
			criteria = criteria.filter(Affiliate.token == token)
			affiliate = criteria.one()
			serializer = AffiliateSchema()
			self.response['affiliate'] = serializer.dump(affiliate).data

			self.db.commit()
			logger.debug(self.response)
			self.write_json()

		except Exception as error:
			self.db.rollback()
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch data')