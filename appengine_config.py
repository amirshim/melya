from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
    #from google.appengine.ext.appstats import recording
    #app = recording.appstats_wsgi_middleware(app)
    app = SessionMiddleware(app,
        cookie_key='Generate your own key using os.urandom(64) offline\x04c\x9d(\x88\xcc\xf3!\xdd\x14\x13\x19\xa2\xec'
    )
    return app

