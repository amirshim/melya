# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.
import google.appengine.ext.db as db
from google.appengine.api import users
from utils import getGitBlobHash, getAllFromFromQuery,DB_SimpleToDict,chunks
from collections import defaultdict
from gaesessions import get_current_session
import datamodel,datetime,logging, os,json
from filegen import forceCacheRebuild

from handlerhelpers import ApiReq
from handlerutils import RetType, getUserAndIsAdmin, RequireAdmin, RequireAdminRaw

_fileVerKey = 'fver'

def createUserIfNeeded(req):
    guser = users.get_current_user()
    if not guser:
        get_current_session().terminate()
        return False

    usergkey = 'g'+str(guser.user_id())
    res = datamodel.DB_UserLoginAssoc.get_by_key_name(usergkey)
    if not res:
        muser = datamodel.DB_User(name=guser.nickname())
        muser.put()
        res = datamodel.DB_UserLoginAssoc(key_name=usergkey, uid = muser.key().id())
        res.put()
        res2 = datamodel.DB_UserData(parent=muser, key_name='emails')
        res2.emails = [guser.email()]
        res2.put()
    else:
        muser = datamodel.DB_User.get_by_id(res.uid)

    get_current_session()['uid'] = muser.key().id()

    return muser

@ApiReq(allowGet=True)
def admin_login(req):
    muser = createUserIfNeeded(req)
    if not muser: return RetType.RAW,("<a href=\"%s\">Login</a>." % users.create_login_url("/api/admin/login"))
    if muser and users.is_current_user_admin(): return RetType.REDIRECT, '/api/admin/DoAdminStuff'
    return RetType.RAW, 'Logged in'

@ApiReq(allowGet=True)
@RequireAdminRaw
def admin_logout(req):
    return RetType.REDIRECT, users.create_logout_url('/')

@ApiReq()
@RequireAdmin
def admin_isAdmin(req):
    return RetType.JSONSUCCESS

# -------------- Upload Files...
@ApiReq()
@RequireAdminRaw
def admin_UploadFilePage(req):
    return RetType.RAW, """
<form method='POST' enctype='multipart/form-data' action='/api/admin/UploadFileHandler'>
Filename: <input type="text" name="filename"><br>
<input type=file name="content"><br>
<input type=submit value="Upload">
</form>
    """

@ApiReq(allowGet=True)
@RequireAdminRaw
def admin_DoAdminStuff(req):
    cmds_POST = [
        ('RestoreFromBackupZip', 'Restore all files from backup'),
        ('RestoreFromFileDomainAndPages', 'Restore all page and domain stuff in datastore'),
        ('UploadFilePage', 'Upload a file'),
        ('invalidateFileBuilds', 'Invalidate Builds'),
        ('FlushAllMemcache', 'Flush all memcache'),
        ('CreateAllFileZip','Create a zip file with all the files and all the versions'),
        ('CreateBackupOfDomainAndPages', 'Create a file (json) with all the current page domains in the datastore'),
        ('clearAllBuildData','Clear all file builds incase of problems'),

        #('CreateBackupZipForTag', 'Create backup for a specific tag'),
    ]
    cmds_GET = [
        ('/account/admin/editfiles','Edit files'),
        ('/api/admin/setCurrentSessionVer?ver=-1','Switch to dev mode for files (most recent)'),
        ('/api/admin/setCurrentSessionVer','Switch to live mode for files (head -a- version)'),
        ('/api/admin/logout','Logout'),
    ]
    html_post = ["""<form method="POST" action="/api/admin/%s"><input type=submit value="%s"></form>""" % x for x in cmds_POST]
    html_get = ["""<a href="%s">%s</a><br/>""" % x for x in cmds_GET]
    return RetType.RAW, '\n'.join(html_post + html_get)

def internalAddFile(filename, content, userkey, extra_tags=None, genFromFile=None, genFromVer=None):
    """
    extra_tags is a set like {'a','m'} - but usually either None or {'a'} - 'z' always gets added.
    """
    fn = filename
    new_hash = getGitBlobHash(content)
    theDataKey = datamodel.DB_FileContent.all(keys_only=True).filter('__key__ =', db.Key.from_path(u'DB_FileContent', new_hash)).get()

    if not theDataKey:
        theDataKey = datamodel.DB_FileContent(key_name = new_hash, data = db.Blob(content)).put()
        hashAlreadyExists = False
    else:
        hashAlreadyExists = True

    latestVersion = datamodel.DB_FileVersion.getMostRecent(fn, 'z', keys_only=True)

    if latestVersion and latestVersion.parent().name() == new_hash:
        return False, {'text':'Failed because the latest version has the same hash'}

    if genFromFile and genFromVer:
        genFrom = datamodel.DB_FileVersion.getSpecificVersion(genFromFile, 'z', int(genFromVer), keys_only=True)
        if not genFrom:
            return False, {'text':'Generated from version doesn\'t exist'}
    else:
        genFrom = None

    isFirstVersion = False if latestVersion else True

    nextVersionNum = datamodel.DB_JV_AtomicCounter.GetNextCounter(_fileVerKey)

    if isFirstVersion:
        tags = {'z', 'a'}
    else:
        tags = {'z'}

    if extra_tags: tags.update(extra_tags)

    newFileVer = datamodel.DB_FileVersion(parent=theDataKey, key_name=str(nextVersionNum),
                                                filename=fn,version=nextVersionNum,uid=userkey.id(),tags=list(tags),
                                                generatedFrom=genFrom)


    newFileVer.put()

    forceCacheRebuild(fn, 'z')

    return True, {'ver': nextVersionNum, 'hash':new_hash, 'isFirstVersion':isFirstVersion, 'hashAlreadyExists':hashAlreadyExists, 'filename':fn}

@ApiReq()
@RequireAdmin
def admin_UploadFileHandler(req, user): # user is passed by RequireAdmin
    fn = req.get('filename')
    if not fn: return RetType.JSONFAIL, {'text':'No filename'}
    content = req.get('content', None)
    if not content or len(content) == 0:
        if not req.get('allowemptyfile') or content != '':
            return RetType.JSONFAIL, {'text':'No content or empty content'}


    if isinstance(content, unicode):
        logging.info('content is unicode, converting to 8bit using utf-8')
        content = content.encode('utf8')
    else:
        content = str(content) # just in case?


    success, extra_dict = internalAddFile(fn, content, user.key(), genFromFile = req.get('generatedFromFile'), genFromVer = req.get('generatedFromVer'))

    if not success: return RetType.JSONFAIL, extra_dict
    return RetType.JSONSUCCESS, extra_dict

@ApiReq()
@RequireAdmin
def admin_invalidateFileBuilds(req):
    # this will cause all the builds to be redone, and updated if needed. (as needed).

    # first, increment the file counter.
    nextVersionNum = datamodel.DB_JV_AtomicCounter.GetNextCounter(_fileVerKey)

    # next, force all the processes to get that new version number.
    #   so when filegen.getCurCacheVer gets called next time, the file version (fv) will be the new value
    from inmemconfig import InAppMemConfig
    pcd = InAppMemConfig.ForceVersionIncrement()

    # that should be it
    return RetType.JSONSUCCESS, {'configVer':pcd, 'fileVer':nextVersionNum}

@ApiReq()
@RequireAdmin
def admin_clearAllBuildData(req):
    all = getAllFromFromQuery(datamodel.DB_FileBuild.all(keys_only=True))

    for x in chunks(all, 1000):
        db.delete(x)

    nextVersionNum = datamodel.DB_JV_AtomicCounter.GetNextCounter(_fileVerKey)

    from inmemconfig import InAppMemConfig
    InAppMemConfig.ForceVersionIncrement()

    return RetType.JSONSUCCESS

@ApiReq()
@RequireAdmin
def admin_getCleanFileContent(req):
    fn = req.get('filename')
    tag = 'a' if req.get('head') else 'z'
    if req.get('ver'):
        res = datamodel.DB_FileVersion.getSpecificVersion(fn, tag, int(req.get('ver')), keys_only=True)
    else:
        res = datamodel.DB_FileVersion.getMostRecent(fn, tag, keys_only=True)
    if not res: return RetType.JSONFAIL, {'text':'File version not found'}
    theDataEnt = db.get(res.parent())
    if not theDataEnt: return RetType.JSONFAIL, {'text':'File version not found2'}
    return RetType.JSONSUCCESS, {'data':theDataEnt.data}

@ApiReq()
@RequireAdmin
def admin_adminTouchFileVersion(req):
    fn = req.get('filename')
    if not fn: return RetType.JSONFAIL, {'text':'No filename'}
    latestVersion = datamodel.DB_FileVersion.getMostRecent(fn, 'z')
    if not latestVersion: return RetType.JSONFAIL
    nextVersionNum = datamodel.DB_JV_AtomicCounter.GetNextCounter(_fileVerKey)
    latestVersion.version = nextVersionNum
    latestVersion.put()
    return RetType.JSONSUCCESS, {'newVer':nextVersionNum}

@ApiReq()
@RequireAdmin
def admin_getAllFileVersions(req):
    a = getAllFromFromQuery(datamodel.DB_FileVersion.all().order('version'))

    d = defaultdict(list)
    for x in a: d[x.filename].append([x.version]+x.tags)
    #for x in a: d[x.filename].append(x.version)
    return RetType.JSONSUCCESS, {'files':d}

@ApiReq()
@RequireAdmin
def admin_setFileVersionTag(req):
    fn = req.get('filename')
    res = datamodel.DB_FileVersion.getSpecificVersion(fn, 'z', int(req.get('ver')))
    if not res: return RetType.JSONFAIL, {'text':'File version not found'}

    addtag = req.get('addtag')
    deltag = req.get('deltag')
    delversion = req.get('delversion')
    if addtag:
        if addtag in res.tags:
            return RetType.JSONFAIL, {'text':'Tag already in file version'}
        res.tags.append(addtag)
        res.put()
        return RetType.JSONSUCCESS

    if deltag:
        if deltag not in res.tags:
            return RetType.JSONFAIL, {'text':'Tag not in file version'}
        res.tags.remove(deltag)
        res.put()
        return RetType.JSONSUCCESS

    if delversion and delversion == str(res.version):
        # delete both datamodel.DB_FileVersion and datamodel.DB_FileContent if no one else is using it (and no tags)
        if len(res.tags) > 1:
            return RetType.JSONFAIL, {'text':'File is tagged, can\'t delete'}
        theContentKey = res.key().parent()
        theHash = theContentKey.name()

        db.delete_async(res.key())

        usedByOtherResult = (RetType.JSONSUCCESS, {'text':'Version deleted, but content was not deleted since it is used by another version'})
        others = datamodel.DB_FileVersion.all(keys_only=True).ancestor(theContentKey).fetch(2)
        if len(others) != 1: return usedByOtherResult
        if others[0] != res.key(): return usedByOtherResult

        db.delete_async(theContentKey)

        return RetType.JSONSUCCESS

    return RetType.JSONFAIL, {'text': 'Nothing to do?'}

@ApiReq()
@RequireAdmin
def admin_CreateAllFileZip(req):
    import cStringIO
    import zipfile
    zipstream = cStringIO.StringIO()
    zf = zipfile.ZipFile(zipstream, 'w', zipfile.ZIP_DEFLATED)

    allFiles = getAllFromFromQuery(datamodel.DB_FileVersion.all())

    def cleanDate(dd): return str(dd).replace(':', '.').replace(' ', '-')

    for x in allFiles:
        content = x.parent().data
        aa = x.filename.rsplit('.', 1)
        aa.insert(1, '%s_%s%s' % (str(x.version).zfill(4), cleanDate(x.dateAdded), '_a' if 'a' in x.tags else '') )
        tfn = '.'.join(aa)
        zf.writestr(str(tfn), content)

    zf.close()

    outfile = 'onlinefiles-' + cleanDate(datetime.datetime.now()) + '.zip'

    res = zipstream.getvalue()
    return RetType.HEADERSANDRAW, {'Content-Type':'application/zip', 'Content-Disposition': 'attachment; filename="'+outfile+'"' }, res


@ApiReq()
@RequireAdmin
def admin_CreateBackupOfDomainAndPages(req):
    aa = getAllFromFromQuery(datamodel.DB_Domains.all())
    bb = getAllFromFromQuery(datamodel.DB_Pages.all())
    toIgnore = {'dateUpdated'}
    res_domains = [DB_SimpleToDict(x, toIgnore) for x in aa]
    res_pages = [DB_SimpleToDict(x, toIgnore) for x in bb]
    return RetType.JSONSUCCESS, {'domains':res_domains, 'pages':res_pages}

@ApiReq()
@RequireAdmin
def admin_RestoreFromFileDomainAndPages(req):
    if datamodel.DB_Domains.all().get() or datamodel.DB_Pages.all().get():
        return RetType.JSONFAIL, {'text':'Can\'t restore if there are already domains or pages in the datastore'}
    file = os.path.join(os.path.dirname(__file__), 'zips/defaultdomainandpages.json')
    with open(file) as f:
        jsonobj = json.load(f)
        tosave = [datamodel.DB_Domains(**x) for x in jsonobj.get('domains')] + \
            [datamodel.DB_Pages(**x) for x in jsonobj.get('pages')]
        db.put(tosave)
    return RetType.JSONSUCCESS


@ApiReq()
@RequireAdminRaw
def admin_CreateBackupZipForTag(req):
    import cStringIO
    import zipfile
    def cleanDate(dd): return str(dd).replace(':', '.').replace(' ', '-')

    whichTag = req.get('tag')
    if not whichTag: return RetType.RAW, 'Must specify tag'

    allFiles = getAllFromFromQuery(datamodel.DB_FileVersion.all().filter('tags =', whichTag))
    allFiles.sort(key=lambda x:x.version, reverse=True)

    zipstream = cStringIO.StringIO()
    zf = zipfile.ZipFile(zipstream, 'w', zipfile.ZIP_DEFLATED)

    alreadyWritten = set()
    for x in allFiles:
        if x.filename in alreadyWritten: continue
        alreadyWritten.add(x.filename)
        content = x.parent().data # reads data from datastore... slow
        zf.writestr(str(x.filename), content)

    zf.close()
    res = zipstream.getvalue()
    outfile = str('onlinefiles-%s-%s.zip' % (whichTag, cleanDate(datetime.datetime.now())))
    return RetType.HEADERSANDRAW, {'Content-Type':'application/zip', 'Content-Disposition': 'attachment; filename="'+outfile+'"' }, res


@ApiReq()
@RequireAdmin
def admin_RestoreFromBackupZip(req, user):
    import zipfile
    file = os.path.join(os.path.dirname(__file__), 'zips/orig.zip')
    zf = zipfile.ZipFile(file, 'r')

    allFiles = getAllFromFromQuery(datamodel.DB_FileVersion.all().order('version'))
    byName = {} # most recent version.
    for x in allFiles: byName[x.filename] = x

    extractStats = {}
    filesInZip = zf.namelist()

    forceFiles = req.get('forceFiles')
    if forceFiles == '__all__':
        forceFiles = set(filesInZip)
    elif forceFiles:
        forceFiles = set(forceFiles.split(','))
    else:
        forceFiles = set()

    for fiz in filesInZip:
        extractStats[fiz] = ''
        data = zf.read(fiz)
        new_hash = getGitBlobHash(data)
        if fiz in byName:
            curVer = byName[fiz]
            oldHash = curVer.key().parent().name()

            if oldHash == new_hash:
                extractStats[fiz] += 'Same version already the head version in the system. '
                continue
            else:
                extractStats[fiz] += 'Different version in zip file and system head. '
                if fiz not in forceFiles: continue

        theDataKey = datamodel.DB_FileContent.all(keys_only=True).filter('__key__ =', db.Key.from_path(u'DB_FileContent', new_hash)).get()
        if not theDataKey:
            theDataKey = datamodel.DB_FileContent(key_name = new_hash, data = db.Blob(data)).put()
            extractStats[fiz] += 'Added to cache. '
        else:
            extractStats[fiz] += 'Already in cache. '
        
        nextVersionNum = datamodel.DB_JV_AtomicCounter.GetNextCounter(_fileVerKey)
        tags = ['z', 'a'] # make it head
        newFileVer = datamodel.DB_FileVersion(parent=theDataKey, key_name=str(nextVersionNum),
                                                    filename=fiz,version=nextVersionNum,uid=user.key().id(),tags=tags)
        newFileVer.put()
        extractStats[fiz] += 'Added version %s with hash: %s ' % (nextVersionNum, new_hash)
    #forceCacheRebuild(fiz, 'z')

    zf.close()
    return RetType.JSONSUCCESS, {'stats':extractStats}

@ApiReq(allowGet=True)
def admin_setCurrentSessionVer(req):
    # if you only want to allow people who know the password to use other versions, set require_password
    require_password = None # maybe put this in the DB somewhere?
    if require_password and req.get('password') != require_password: return RetType.JSONFAIL

    session = get_current_session()
    if req.get('getver'):
        if 'jvdevver' in session:
            return RetType.JSONSUCCESS, {'version':session['jvdevver']}
        return RetType.JSONSUCCESS, {'version':None}

    vv = req.get('ver')
    if not vv:
        if 'jvdevver' in session:
            del session['jvdevver']
            return RetType.JSONSUCCESS, {'version':None}
    session['jvdevver'] = vv
    return RetType.JSONSUCCESS, {'version':vv}


