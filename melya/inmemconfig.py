# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.
import datetime, logging, datamodel, re
from google.appengine.api import memcache

# in memory config

_memcache = memcache.Client() # THREAD SAFE?


# so we don't hit the same memcache location on every req.
_checkMemcacheFreq = datetime.timedelta(seconds=1) # how often to check memcache for change.


class InAppMemConfig(object):
    _nextCheckTime = datetime.datetime.min
    _processCfgVer = -1 # invalid version
    _memcachekey = 'processCfgVer'
    _currentConfig = None
    _lastDomainUpdate = datetime.datetime.min
    _domainsCache = []
    _lastPageUpdate = datetime.datetime.min
    _pagesCache = []

    def __init__(self):
        self.configInitTime = datetime.datetime.now()
        self.configVersion = InAppMemConfig._processCfgVer
        self.fileVersion = datamodel.DB_JV_AtomicCounter.GetMostRecentlyReturnedCounterValue('fver') # read from cache?
        #logging.info('init inappmemconfig: %s %s %s' % (self.configInitTime, self.configVersion, self.fileVersion))

        self.domains = self.UpdateDomains()
        self.pages = self.UpdatePages()

    @classmethod
    def UpdateDomains(cls):
        res = datamodel.DB_Domains.all().order('-dateUpdated').get()
        if not res or res.dateUpdated == cls._lastDomainUpdate: return cls._domainsCache
        domains = datamodel.DB_Domains.all().order('order').fetch(1000)
        for x in domains: x._compiledRegex = re.compile(x.regex) # compile them for faster access
        cls._domainsCache = domains # assign here to be threadsafe - kind of
        cls._lastDomainUpdate = res.dateUpdated
        return cls._domainsCache

    @classmethod
    def UpdatePages(cls):
        res = datamodel.DB_Pages.all().order('-dateUpdated').get()
        if not res or res.dateUpdated == cls._lastPageUpdate: return cls._pagesCache
        pages = datamodel.DB_Pages.all().order('order').fetch(1000)
        for x in pages:
            x._compiledRegex = re.compile(x.regex) # compile them for faster access
            x._parsedFlagList = frozenset(x.flags.split(',')) if x.flags else frozenset()
        cls._pagesCache = pages # assign here to be threadsafe - kind of
        cls._lastPageUpdate = res.dateUpdated
        return cls._pagesCache


    @classmethod
    def Current(cls):
        if cls._currentConfig:
            return cls._currentConfig
        return cls.UpdateIfNeeded()

    @classmethod
    def UpdateIfNeeded(cls):
        # we check to see if enough time passed so if we have high load, we're not hitting the same memcache
        #  entry on every page.
        curTime = datetime.datetime.now()
        if curTime <= cls._nextCheckTime: return cls._currentConfig
        cls._nextCheckTime = curTime + _checkMemcacheFreq
        pcd = _memcache.get(cls._memcachekey)
        if pcd and pcd == cls._processCfgVer:
            # if it didn't change in memcache, just return it.
            return cls._currentConfig
        pcd  = datamodel.DB_JV_AtomicCounter.GetMostRecentlyReturnedCounterValue('processCfgVer')
        if pcd != cls._processCfgVer:
            cls._processCfgVer = pcd
            # create a new one.
            cls._currentConfig = InAppMemConfig()

        _memcache.set(cls._memcachekey, pcd)

        return cls._currentConfig

    @classmethod
    def ForceVersionIncrement(cls):
        pcd  = datamodel.DB_JV_AtomicCounter.GetNextCounter('processCfgVer')
        _memcache.set(cls._memcachekey, pcd)
        return pcd




