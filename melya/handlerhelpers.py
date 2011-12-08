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

import dynamicapi

# this should be moved into config store...
html_unit_url = None # set this to something like 'http://hu.myapplicationnamegoeshere.appspot.com/hu?url=%s'

jvDollarEscapeRe = re.compile(r'(\$\$jv:([^\$]+)\$\$)')
_memcache = memcache.Client()
_webFuncs = {}
_webFuncsGet = {}

# the decorator 
def ApiReq(urlName = None, allowGet=False):
    if urlName and not isinstance(urlName, str):
        raise Exception('Decorator used without parentheses. Please add parentheses, i.e. "@JsonReq()"')
    def wwrap(func):
        uu = urlName
        if not uu:
            uu = func.__name__.replace('_', '/')
        if uu in _webFuncs:
            raise Exception('Duplicate Request Type', uu)
        _webFuncs[uu] = func
        if allowGet: _webFuncsGet[uu] = func
        return func
    return wwrap


# these are the built in APIs - don't remove
import melya.fileapi
import melya.adminapi
import melya.githubapi


def SetCachingHeadersForResponse(response, max_age = 600):
    response.headers['Expires'] = email.Utils.formatdate(time.time() + max_age, usegmt=True)
    response.headers['Cache-Control'] = 'public, max-age=%d' % max_age

class ZipHandler(webapp2.RequestHandler):
  """Request handler serving static files from zipfiles. - copied from zipserve"""
  zipfile_cache = {}
  def ServeFromZipFile(self, zipfilename, name):
    """Helper for the GET request handler.

    This serves the contents of file 'name' from zipfile
    'zipfilename', logging a message and returning a 404 response if
    either the zipfile cannot be opened or the named file cannot be
    read from it.

    Args:
      zipfilename: The name of the zipfile.
      name: The name within the zipfile.
    """

    zipfile_object = self.zipfile_cache.get(zipfilename)
    if zipfile_object is None:
      try:
        zipfile_object = zipfile.ZipFile(zipfilename)
      except (IOError, RuntimeError, zipfile.BadZipfile), err:


        logging.error('Can\'t open zipfile %s: %s', zipfilename, err)
        zipfile_object = ''
      self.zipfile_cache[zipfilename] = zipfile_object
    if zipfile_object == '':
      self.error(404)
      self.response.out.write('Not found')
      return
    try:
      data = zipfile_object.read(name)
    except (KeyError, RuntimeError), err:
      self.error(404)
      self.response.out.write('Not found')
      return
    content_type, encoding = mimetypes.guess_type(name)
    if content_type:
      self.response.headers['Content-Type'] = content_type
    self.SetCachingHeaders()
    self.response.out.write(data)

  MAX_AGE = 600
  PUBLIC = True

  def SetCachingHeaders(self):
    SetCachingHeadersForResponse(self.response, self.MAX_AGE)


class GeneralApiHandler(ZipHandler): #webapp2.RequestHandler):
    def post(self, command):
        return self.get(command, isPost=True)

    def get(self, command, isPost=False):
        InAppMemConfig.UpdateIfNeeded()
        if command.startswith('z/'): return self.zipsrv(command)
        if command.startswith('d/'): return self.dynsrv(command)

        if isPost and command in _webFuncs:
            cmd = _webFuncs[command]
        elif command in _webFuncsGet:
            cmd = _webFuncsGet[command]
        else:
            cmd = None

        if not cmd:
            cmd = dynamicapi.getApiCmd(command, isPost, self.request)

        if cmd:
            res = cmd(self.request)
            if not res:
                logging.error('Must return one of the functions from RetType')
                return self.response.set_status(500)
            if not isinstance(res, tuple):
                return res(self)
            return res[0](self, *res[1:])

        return self.response.set_status(404)

    def dynsrv(self, command):
        spl = command.split('/', 2) # ['d', 'a1234', 'js/myfile.js']
        if len(spl) != 3 or len(spl[1]) == 0 or len(spl[2]) == 0: return self.response.set_status(404)
        tag = spl[1][0]
        cacheVerNum = spl[1][1:]
        fileName = spl[2]

        if not cacheVerNum: cacheVerNum = getCurCacheVer(fileName, tag)
        res = getCurCacheBlob(fileName, tag, cacheVerNum)

        content_type, encoding = mimetypes.guess_type(fileName)
        if content_type:
            self.response.headers['Content-Type'] = content_type

        #if fileName.endswith('.js'):
        #    self.response.headers['Content-Type'] = 'text/javascript'
        #elif fileName.endswith('.css'):
        #    self.response.headers['Content-Type'] = 'text/css'

        if tag == 'a': self.SetCachingHeaders()
        return self.response.out.write(res)

    def zipsrv(self, command):
        _, prefix, name = command.split('/', 2) # ['z', 'a1234', 'js/myfile.js']
        file = os.path.join(os.path.dirname(__file__), 'zips/'+ prefix + '.zip')
        self.ServeFromZipFile(file , name)

class GeneralPageHandler(webapp2.RequestHandler):
    def get(self):
        InAppMemConfig.UpdateIfNeeded()
        session = get_current_session()

        curHost = self.request.host
        curDomain = self.resolveDomain(curHost)
        if not curDomain:
            # TODO: remove
            self.response.out.write('Domain not found: %s' % curHost)
            return


        curDomainName = curDomain.name
        curPath = self.request.path
        curPage = None
        for p in InAppMemConfig.Current().pages:
            if (not p.domainName or p.domainName == curDomainName) and p._compiledRegex.match(curPath):
                curPage = p
                break

        if not curPage:
            # TODO: remove
            self.response.out.write('Page not found: %s' % curPath)
            return

        if html_unit_url and self.request.get('_escaped_fragment_', None) != None or self.request.get('nojs', None) == '1':
            return self.serveSEOContent(curDomain, curPage)

        isHead = not session or session.get('jvdevver') != '-1'

        curTag = 'a' if isHead else 'z'

        if 'jinja' in curPage._parsedFlagList:
            res = renderWithJinja(curPage.fileName, isHead=isHead, curPage=curPage, curDomain=curDomain, config=InAppMemConfig.Current(), curTag=curTag, webreq=self.request)
        elif 'melya' in curPage._parsedFlagList: # Melya's js parsing...
            res = getCurCacheBlob(curPage.fileName, curTag, InAppMemConfig.Current().fileVersion)
        else:
            res = getRawFileData(curPage.fileName, curTag)

        if isHead and 'cache' in curPage._parsedFlagList:
            SetCachingHeadersForResponse(self.response)

        content_type, encoding = mimetypes.guess_type(curPage.fileName)
        if content_type:
            self.response.headers['Content-Type'] = content_type


        return self.response.out.write(res)

    def serveSEOContent(self, curDomain, curPage):
        url = self.request.path_url
        cutoff = url.find('://')
        if cutoff >= 0:
            url = url[cutoff+3:]
        url = html_unit_url % url

        from google.appengine.api import urlfetch
        result = urlfetch.fetch(url, deadline=60)
        if result.status_code == 200:
          self.response.out.write(result.content)


    @classmethod
    def resolveDomain(cls, curHost):
        for d in InAppMemConfig.Current().domains:
            if d._compiledRegex.match(curHost): return d
        return None
