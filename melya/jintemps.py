import webapp2
from jinja2 import Environment, Template, BaseLoader, TemplateNotFound
import google.appengine.ext.db as db
from google.appengine.api import memcache
import datamodel
from datetime import datetime
from inmemconfig import InAppMemConfig
from filegen import getCurCacheVer # for Jinja Globals Environment

_memcache = memcache.Client()

class JVJinjaLoader(BaseLoader):
    def __init__(self, isHead):
        self.isHead = isHead

    def get_source(self, environment, template):
        fn = template
        latestVersion = datamodel.DB_FileVersion.getMostRecent(fn, 'a' if self.isHead else 'z', keys_only=True)
        if not latestVersion: raise TemplateNotFound(template)
        prnt = latestVersion.parent()
        #theVersion = latestVersion.name()
        theDataEnt = db.get(prnt)
        if not theDataEnt: raise TemplateNotFound(template)
        curTime = InAppMemConfig.Current().configInitTime
        data = unicode(theDataEnt.data, 'utf8') # for now, consider all string to be utf8
        return data, fn, lambda: InAppMemConfig.Current().configInitTime == curTime # False means reload -- TODO: for now...

def createJinjaEnv(isHead):
    res = Environment(loader=JVJinjaLoader(isHead), autoescape=True, auto_reload=True)
    res.globals['getCurCacheVer'] = getCurCacheVer
    return res

jinjaEnvHead = createJinjaEnv(True)
jinjaEnv = createJinjaEnv(False)

def renderWithJinja(template, isHead=True, **kwds):
    if isHead:
        template = jinjaEnvHead.get_template(template)
    else:
        template = jinjaEnv.get_template(template)
    return template.render(**kwds)
