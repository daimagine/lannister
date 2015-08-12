import urllib
import simplejson as json
from urllib2 import Request, urlopen, URLError, HTTPError
from lannister.utils.logs import logger
from lannister import settings


def verify_captcha(captcha):
    try:
        captchaURL = "https://www.google.com/recaptcha/api/siteverify"
        secret = settings.CAPTCHA_SECRET_KEY

        data = urllib.urlencode({
        	'secret': secret,
        	'response': captcha
        })

        request = Request(captchaURL, data)
        response = urlopen(request)
        api_response = json.loads(response.read())

        logger.debug('captcha response')
        logger.debug(api_response)
        return api_response['success']

    except HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    except URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    
    return false