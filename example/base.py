import tornado.web

class Base(tornado.web.RequestHandler):
    def initialize(self):
        self.minify = self.settings['minify']

class Index(Base):
    def get(self):
        self.write(self.minify.render('index.html', param1=True))
        self.finish()