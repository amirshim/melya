import webapp2
import melya.handlerhelpers

application = webapp2.WSGIApplication([
    (r'/api/(.*)', melya.handlerhelpers.GeneralApiHandler),
    (r'.*', melya.handlerhelpers.GeneralPageHandler),
])