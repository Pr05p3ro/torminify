import tornado.ioloop
import tornado.web
import sys
from tornado import autoreload
from base import Index
from tornado.options import define, options 
from torminify.minify import Minify

class Application(tornado.web.Application):
    
    def __init__(self):
        debug = True
        
        self.minify = Minify(
            config='config/minify/minify.yaml',
            watch='config/minify/watch.yaml',
            web_root='/var/www/torminify/',
            cache_index='cache/minify_cache.yaml',
            debug=debug)

        settings = dict(
            cookie_secret = 'FDfsdvcvbsg4354ggfDrbX365G===4354c%$^@mj',
            debug = debug,
            autoreload = debug,
            minify = self.minify
        )

        handlers = [
            (r"/", Index)
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.define('port', default=8889, help='run on the given port', type=int) 
    tornado.options.parse_command_line(sys.argv)
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
