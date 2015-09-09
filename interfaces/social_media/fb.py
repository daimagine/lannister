import facebook
import json
import urllib2
import urllib
from lannister.utils.logs import logger
from lannister.utils.strings import StringUtils
from lannister import settings
from lannister.interfaces.social_media.exceptions import SocmedException, SocmedPostException

class FacebookInterface(object):
	@staticmethod
	def post(fb_account, headline, product_page, product):
		try:
			logger.debug('FacebookInterface: post to facebook %s' % fb_account.social_name)

			# build graph api
			ACCESS_TOKEN = fb_account.token
			graph = facebook.GraphAPI(access_token=ACCESS_TOKEN)

			# set headline
			logger.debug('FacebookInterface: headline: %s' % headline)
			message = "%s %s" % (headline, product_page)

			# post
			attachment =  {
				'name': product.name,
				'link': product_page,
				'description': product.description,
				'picture': product.image
			}
			graph.put_wall_post(message=message, attachment=attachment)

		except Exception, error:
			logger.exception(error);
			raise SocmedException('Failed to post to facebook', error)

	@staticmethod
	def get_redirect_url(customer, social_media, callback_url):
		try:
			# build facebook redirect
			CLIENT_ID = social_media.consumer_key
			redirect_url = "https://www.facebook.com/dialog/oauth?"\
				"client_id=%s"\
				"&response_type=code"\
				"&scope=email,user_about_me,user_status,"\
				"user_friends,user_posts,"\
				"publish_actions,manage_pages,status_update"\
				"&redirect_uri=%s" % (CLIENT_ID, callback_url)

			response = dict()
			response['redirect_url'] = redirect_url

			return response

		except Exception, error:
			logger.exception(error);
			raise SocmedException('Failed to get facebook redirect URL', error)

	@staticmethod
	def verify(social_media, verifier, callback_url):
		try:
			logger.debug('FacebookInterface: confirming user and get access_token')

			# build facebook redirect
			'''
			GET	https://graph.facebook.com/v2.3/oauth/access_token?
				client_id={app-id}
				&redirect_uri={redirect-uri}
				&client_secret={app-secret}
				&code={code-parameter}
			'''
			CLIENT_ID = social_media.consumer_key
			CLIENT_SECRET = social_media.consumer_secret
			
			verify_param = {
				'client_id' : CLIENT_ID,
				'client_secret' : CLIENT_SECRET,
				'redirect_uri' : callback_url,
				'code' : verifier
			}
			verify_query = urllib.urlencode(verify_param)
			verify_url = "https://graph.facebook.com/v2.3/oauth/access_token?%s" % verify_query

			# confirming user and get access token
			logger.debug('FacebookInterface: access_token %s' % verifier)
			logger.debug('FacebookInterface: callback_url %s' % callback_url)
			logger.debug('FacebookInterface: verify_url %s' % verify_url)

			# hit the road
			data = json.load(urllib2.urlopen(verify_url))
			logger.debug('FacebookInterface: verify result %s' % data)

			# extract access_token
			access_token = data['access_token']

			# get account info
			graph = facebook.GraphAPI(access_token=access_token)
			user = graph.get_object('me')
			logger.debug('FacebookInterface: facebook account %s', user)

			# get profile picture
			pictures = graph.get_object('me/picture')
			logger.debug('FacebookInterface: profile pictures %s', pictures['url'])

			response = dict()
			response['access_token'] = data['access_token']
			response['social_id'] = user['id']
			response['social_name'] = user['name']
			response['image'] = pictures['url']

			return response

		except Exception, error:
			logger.exception(error);
			raise SocmedException('Failed to get verify facebook account', error)
