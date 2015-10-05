#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth
from lannister.utils.caching_query import FromCache, RelationshipCache

from stark.models.schema import TransactionsSalesOverviewSchema
from stark.models.transactions import Transactions
from stark.models.affiliate import Affiliate
from stark.models.customer import Customer

import lannister.common.transactions_state as TransactionState
import lannister.common.transactions_status as TransactionStatus


class AffiliateSalesHandler(CacheJSONHandler):
	@gen.coroutine
	@auth()
	@cache()
	def get(self, affiliator_id):
		""" Get affiliate sales overview """
		try:
			logger.debug('get affiliate sales overview')
			logger.debug(self.request.arguments)

			self.db.begin()
			criteria = self.db.query(Transactions).distinct(Transactions.id).group_by(Transactions.id)

			# filter transactions
			criteria = criteria.filter(Transactions.state == TransactionState.DONE)
			criteria = criteria.filter(Transactions.status == TransactionStatus.SUCCESS)
			criteria = criteria.join(Affiliate).join(Affiliate.customer)
			criteria = criteria.filter(Customer.id == affiliator_id)
			criteria = criteria.order_by(self.db_desc(Transactions.id))

			# get transactions of affiliator
			transactions = criteria.all()

			# calculate
			count = 0
			amount = 0
			total = 0

			for transaction in transactions:
				count = count + 1
				total = total + transaction.amount
				if transaction.affiliator_received != None:
					amount = amount + transaction.affiliator_received

			# pack response
			sales_overview = dict()
			serializer = TransactionsSalesOverviewSchema(many=True)
			sales_overview['transactions'] = serializer.dump(transactions).data
			sales_overview['count'] = count
			sales_overview['amount'] = amount
			sales_overview['total'] = total

			self.response['sales_overview'] = sales_overview

			self.db.commit()
			logger.debug(self.response)
			self.write_json()

		except Exception as error:
			self.db.rollback()
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch affiliate sales overview data')