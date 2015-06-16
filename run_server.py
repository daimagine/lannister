#!/usr/bin/env python
# tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web
# logging
from lannister.utils.logs import logger
# application
from lannister.common.application import Application
from lannister.common.safe_httpserver import SafeHTTPServer

# cmd line options
tornado.options.define('port', type=int, default=8080, 
    help='server port number (default: 8080)')
tornado.options.define('debug', type=bool, default=False, 
    help='run in debug mode with autoreload (default: false)')

def main():
    logger.debug('Initiate tornado server')
    tornado.options.parse_command_line()
    options = tornado.options.options
    application = Application()
    ioloop = tornado.ioloop.IOLoop.instance()

    http_server = SafeHTTPServer(application)
    http_server.listen(options.port)
    logger.info('started on port: %d', options.port)
    ioloop.start()


if __name__ == '__main__':
    main()
