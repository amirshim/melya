import google.appengine.ext.db as db
from utils import getGitBlobHash
from google.appengine.api import memcache
import datamodel, logging, re
from inmemconfig import InAppMemConfig
_memcache = memcache.Client()

jvDollarEscapeRe = re.compile(r'(\$\$jv:([^\$]+)\$\$)')

def getJsFileString(fn, tag):
    # TODO: cache?
    latestVersion = datamodel.DB_FileVersion.getMostRecent(fn, tag, keys_only=True)
    if not latestVersion:
        logging.error('File not found: %s %s' % (fn, tag))
        return ''
    theHash = latestVersion.parent().name()
    theVersion = latestVersion.name()
    theHashCacheKey = 'hashFileCache%s' % theHash
    theDataEnt = _memcache.get(theHashCacheKey)
    if not theDataEnt:
        prnt = latestVersion.parent()
        theDataEnt = db.get(prnt)
        if theDataEnt:
            theDataEnt = theDataEnt.data
            _memcache.set(theHashCacheKey, theDataEnt)

    if not theDataEnt:
        logging.info('File not found2: %s %s' % (fn, tag))
        return ''

    def func(matchobj):
        tt = matchobj.group(2)
        if tt == 'fn': return str(fn)
        elif tt == 'ver': return str(theVersion)
        elif tt == 'maxver': return str(InAppMemConfig.Current().fileVersion)
        elif tt == 'tag': return tag
        elif tt.startswith('inc:'):
            xx = tt[4:]
            if xx.startswith('curver:'): # something like $$jv:curver:a:js/myfile.js$$
                xx = xx.split(':')
                return str(getCurCacheVer(xx[2], xx[1]))
            return getJsFileString(xx, tag)
        else:
            return '$$UNKNOWN JV ESCAPE$$'
    restext = jvDollarEscapeRe.sub(func, theDataEnt)
    return restext

def forceCacheRebuild(filename, tag):
    """
    This should be called on saving of files (on tag 'z')
    """
    return getCurCacheVer(filename, tag, forceRebuild = True)


def getCurCacheVer(filename, tag, forceRebuild = False):
    """
    tag is from the DB_FileVersion.tags field. right now it's 'z' or 'a'
    """
    fv = InAppMemConfig.Current().fileVersion
    buildkey = '%s:%s:' % (filename,tag) # the front... no version...
    fvmckey = 'fcv:%s:%s' % (fv, buildkey) # file cache version
    res = _memcache.get(fvmckey) # res is a curcachever
    if not forceRebuild and res: return res # fast track.

    fb = datamodel.DB_FileBuild.get_by_key_name(buildkey)
    if not forceRebuild and fb:
        if fb.fileVerCheckTime == fv: # simply evicted from memcache
            _memcache.set(fvmckey, fb.cacheVerNum)
            return fb.cacheVerNum

        data = getJsFileString(filename, tag)
        hashVal = getGitBlobHash(data)
        if fb.hashVal == hashVal:
            # nothing changed... update fileVerCheckTime to current version
            fb.fileVerCheckTime = fv
            _memcache.set(fvmckey, fb.cacheVerNum)
            db.put_async(fb) # don't care when we do it since it is idempotent
            return fb.cacheVerNum

        # it changed... fall through to update it.
    else:
        data = getJsFileString(filename, tag)
        hashVal = getGitBlobHash(data)

    theKey = '%s:%s:%s' % (filename, tag, fv)
    memck = 'datagen' + theKey

    # create a new build with the current specific version
    fb = datamodel.DB_FileBuild(key_name = theKey, hashVal=hashVal, cacheVerNum=fv, fileVerCheckTime=fv, data=data)
    # update the non-version one to point to the most current one.
    fb2 = datamodel.DB_FileBuild(key_name = buildkey, hashVal=hashVal, cacheVerNum=fv, fileVerCheckTime=fv)
    db.put([fb,fb2])

    _memcache.set(fvmckey, fv) # fast track for this function...
    _memcache.set(memck, data) # fast track for getCurCacheBlob
    return fv

def getCurCacheBlob(filename, tag, cacheVerNum, tryLowerNum=True):
    theKey = '%s:%s:%s' % (filename, tag, cacheVerNum)
    memck = 'datagen' + theKey
    res = _memcache.get(memck)
    if res: return res
    fb = datamodel.DB_FileBuild.get_by_key_name(theKey)
    if not fb:
        if tryLowerNum:
            cacheVerNum = getCurCacheVer(filename, tag)
            return getCurCacheBlob(filename, tag, cacheVerNum, False)
        logging.error('Version not found %s %s %s' % (filename, tag, cacheVerNum))
        return '' # TODO: something smarter? exception?
    _memcache.set(memck, fb.data)
    return fb.data

def getRawFileData(filename, tag):
    # TODO: add caching
    latestVersion = datamodel.DB_FileVersion.getMostRecent(filename, tag, keys_only=True)
    prnt = latestVersion.parent()
    theDataEnt = db.get(prnt)
    if theDataEnt: return theDataEnt.data
    return '' # TODO: exception?


    