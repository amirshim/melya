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

from handlerutils import RetType, getUserAndIsAdmin, RequireAdmin, RequireAdminRaw

def GetDynamicGenerator(dynCache, prefix, isHead, ver):
    # the decorator
    def DynApiReq(urlName = None, allowGet=False):
        if urlName and not isinstance(urlName, str):
            raise Exception('Decorator used without parentheses. Please add parentheses, i.e. "@JsonReq()"')
        def wwrap(func):
            uu = urlName
            if not uu:
                uu = func.__name__.replace('_', '/')
            if not uu.startswith(prefix): logging.info('Dynamic api %s doesn\'t start with: %s' % (uu, prefix))
            pp = '' if isHead else '%s.' % ver
            uu1 = pp + 'post.' + uu
            if uu1 in dynCache:
                logging.info('Already in dynamic cache: %s' % uu1)
                return
            dynCache[uu1] = func
            if allowGet:
                uu1 = pp + 'get.' + uu
                if uu1 in dynCache:
                    logging.info('Already in dynamic cache: %s' % uu1)
                    return
                dynCache[uu1] = func
            return func
        return wwrap
    return DynApiReq

def getApiCmd(command, isPost, req):
    session = get_current_session()
    isHead = not session or session.get('jvdevver') != '-1'
    dac = InAppMemConfig.Current().dynamicApiCache
    cmdkey = command
    if isPost: cmdkey = 'post.' + cmdkey
    else: cmdkey = 'get.' + cmdkey

    tryFileName = None

    if not isHead:
        # TODO: cache this, so we don't access it every request.
        firstpart = command.split('/', 1)[0]
        tryFileName = 'rest/%s.py' % firstpart
        latestVersion = datamodel.DB_FileVersion.getMostRecent(tryFileName, 'z', keys_only=True)
        if not latestVersion: return None
        cmdkey = latestVersion.name() + "." + cmdkey

    res = dac.get(cmdkey, None)
    if res: return res

    if not tryFileName:
        firstpart = command.split('/', 1)[0]
        tryFileName = 'rest/%s.py' % firstpart

    # TODO: cache this... so we don't hit the DB on fail? (And don't do it, if we did it above)
    latestVersion = datamodel.DB_FileVersion.getMostRecent(tryFileName, 'a' if isHead else 'z', keys_only=True)
    if not latestVersion: return None
    theDataEnt = db.get(latestVersion.parent())
    if not theDataEnt: return None
    code = unicode(theDataEnt.data, 'utf8') # for now, consider all string to be utf8
    theVersion = int(latestVersion.name())
    # TODO: try-catch block...
    cc = compile(code, '<string>', 'exec')
    dd = {}
    exec cc in globals(), dd
    if 'init' not in dd: return None

    from handlerhelpers import RetType
    dd.get('init')(ApiFileVer=theVersion, ApiReq=GetDynamicGenerator(dac, firstpart, isHead, theVersion)) #, RetType=RetType)

    res = dac.get(cmdkey, None)
    return res

