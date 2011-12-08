# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

import email.Utils, mimetypes, time, re, inspect
import webapp2,json,logging,os, zipfile
from google.appengine.api import users,memcache
import google.appengine.ext.db as db
import datamodel
from inmemconfig import InAppMemConfig
from jintemps import renderWithJinja
from filegen import getCurCacheBlob, getCurCacheVer, getRawFileData
from gaesessions import get_current_session
from functools import wraps


class RetType:
    """
    This was going to be a simple enum, but decided I could simply make it the funcions...
    """
    @classmethod
    def JSONSUCCESS(cls, self, json_obj = None):
        if json_obj:
            json_obj['success'] = True
            return self.response.out.write(json.dumps(json_obj, check_circular=False, separators=(',',':')))
        else:
            return self.response.out.write('{"success":true}')

    @classmethod
    def JSONFAIL(cls, self, json_obj = None):
        if json_obj:
            json_obj['success'] = False
            return self.response.out.write(json.dumps(json_obj, check_circular=False, separators=(',',':')))
        else:
            return self.response.out.write('{"success":false}')

    @classmethod
    def REDIRECT(cls, self, redir = None):
        if not redir:
            return self.redirect('/')
        else:
            return self.redirect(str(redir))

    @classmethod
    def RAW(cls, self, data = None):
        return self.response.out.write(data)

    @classmethod
    def NOTFOUND(cls, self):
        return self.response.set_status(404)

    @classmethod
    def HEADERSANDRAW(cls, self, headers=None, data=None, ):
        if headers:
            for x,y in headers.items():
                self.response.headers[x] = y
        self.response.out.write(data)

def getUserAndIsAdmin(req):
    """
    return (User, isAdmin bool)
    """
    guser = users.get_current_user()
    if not guser: return None, False
    usergkey = 'g'+str(guser.user_id())
    res = datamodel.DB_UserLoginAssoc.get_by_key_name(usergkey)
    if not res: return None, False
    muser = datamodel.DB_User.get_by_id(res.uid)
    return muser, users.is_current_user_admin()

def GenerateRequireAdminLoginDelegate(failReturnValue):
    def RequireAdminFunc(func):
        expectsUser = 'user' in inspect.getargspec(func)[0]
        @wraps(func)
        def wrapped(req):
            user, isAdmin = getUserAndIsAdmin(req)
            if not isAdmin: return failReturnValue
            if expectsUser:
                return func(req, user=user)
            return func(req)
        return wrapped
    return RequireAdminFunc

RequireAdmin = GenerateRequireAdminLoginDelegate((RetType.JSONFAIL, {'needlogin':True}))
RequireAdminRaw = GenerateRequireAdminLoginDelegate((RetType.RAW, 'Requires admin login'))

  