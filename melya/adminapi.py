# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.
from handlerhelpers import ApiReq, RetType, getUserAndIsAdmin, RequireAdmin
import google.appengine.ext.db as db
from google.appengine.api import memcache
import datamodel,json, logging, types
from utils import getAllFromFromQuery
_memcache = memcache.Client()

@ApiReq()
@RequireAdmin
def admin_GetDomainList(req):
    whichKey = req.get('key')
    if whichKey:
        all = datamodel.DB_Domains.get_by_id(int(whichKey)) # load a specific one
        if not all: return RetType.JSONFAIL, {'text':'Domain not found by key'}
        all = [all]
    else:
        all = getAllFromFromQuery(datamodel.DB_Domains.all())
    res = [{'key':x.key().id(),'name':x.name, 'regex':x.regex, 'defaultTitle':x.defaultTitle, 'order':x.order, 'dateUpdated':str(x.dateUpdated)} for x in all]
    return RetType.JSONSUCCESS, {'domains':res}

@ApiReq()
@RequireAdmin
def admin_DeleteDomain(req):
    whichKey = req.get('key')
    dd = datamodel.DB_Domains.get_by_id(int(whichKey)) # load a specific one
    if not dd: return RetType.JSONFAIL, {'text':'Domain not found by key'}
    dd.delete()
    return RetType.JSONSUCCESS

@ApiReq()
@RequireAdmin
def admin_SaveDomain(req):
    jsonobj = req.get('jsonobj')
    if not jsonobj: return RetType.JSONFAIL
    jsonobj = json.loads(jsonobj)

    key = jsonobj.get('key')
    name = jsonobj.get('name')
    regex = jsonobj.get('regex')
    dt = jsonobj.get('defaultTitle')
    o = jsonobj.get('order')

    if not name or not regex or not dt or not o: return RetType.JSONFAIL, {'text':'All fields must be valid'}

    if key:
        theDomain = datamodel.DB_Domains.get_by_id(int(key)) # load the old one
        if not theDomain:
            return RetType.JSONFAIL, {'text':'Domain not found by key'}
    else:
        theDomain = datamodel.DB_Domains() # create a new one.

    theDomain.name = name
    theDomain.regex = regex
    theDomain.defaultTitle = dt
    theDomain.order = float(o)

    theDomain.put()

    return RetType.JSONSUCCESS, {'domainKey':theDomain.key().id()}

# The API for pages

@ApiReq()
@RequireAdmin
def admin_GetPageList(req):
    whichKey = req.get('key')
    if whichKey:
        all = datamodel.DB_Pages.get_by_id(int(whichKey)) # load a specific one
        if not all: return RetType.JSONFAIL, {'text':'page not found by key'}
        all = [all]
    else:
        all = getAllFromFromQuery(datamodel.DB_Pages.all())
    res = [{'key':x.key().id(),'domainName':x.domainName, 'regex':x.regex, 'fileName':x.fileName, 'flags':x.flags,
            'order':x.order, 'dateUpdated':str(x.dateUpdated)} for x in all]
    return RetType.JSONSUCCESS, {'pages':res}

@ApiReq()
@RequireAdmin
def admin_DeletePage(req):
    whichKey = req.get('key')
    dd = datamodel.DB_Pages.get_by_id(int(whichKey)) # load a specific one
    if not dd: return RetType.JSONFAIL, {'text':'Page not found by key'}
    dd.delete()
    return RetType.JSONSUCCESS

@ApiReq()
@RequireAdmin
def admin_SavePage(req):
    jsonobj = req.get('jsonobj')
    if not jsonobj: return RetType.JSONFAIL
    jsonobj = json.loads(jsonobj)

    valDict = dict((x, jsonobj.get(x)) for x in ['order', 'domainName', 'regex', 'fileName', 'flags'])
    nonNull = [valDict[x] for x in ['order', 'regex', 'fileName']] # which ones need to be non-null

    if not all(nonNull): return RetType.JSONFAIL, {'text':'Fields must be valid'}
    key = jsonobj.get('key')

    if key:
        thePage = datamodel.DB_Pages.get_by_id(int(key)) # load the old one
        if not thePage:
            return RetType.JSONFAIL, {'text':'Page not found by key'}
    else:
        thePage = datamodel.DB_Pages() # create a new one.

    for x,y in valDict.items():
        dmt = getattr(datamodel.DB_Pages, x)
        if dmt.data_type == types.FloatType: # add bool?
            setattr(thePage, x, float(y))
        else:
            setattr(thePage, x, y)


    thePage.put()

    return RetType.JSONSUCCESS, {'pageKey':thePage.key().id()}



def execute_dyn_python_code(statement):
    import traceback,sys
    from cStringIO import StringIO
    out = StringIO()

    # the python compiler doesn't like network line endings
    statement = statement.replace('\r\n', '\n')

    # add a couple newlines at the end of the statement. this makes
    # single-line expressions such as 'class Foo: pass' evaluate happily.
    statement += '\n\n'

    try:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = out
            sys.stderr = out

            compiled = compile(statement, '<string>', 'exec')
            exec compiled
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    except:
        out.write(traceback.format_exc())

    contents = out.getvalue()
    out.close()
    return contents

@ApiReq()
@RequireAdmin
def admin_DangerousExecutePythonCode(req):
    res = execute_dyn_python_code(req.get('code'))
    return RetType.HEADERSANDRAW, {'Content-Type':'text/plain'}, res

@ApiReq()
@RequireAdmin
def admin_FlushAllMemcache(req):
    _memcache.flush_all()
    return RetType.JSONSUCCESS
