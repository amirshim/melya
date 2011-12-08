# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

import datamodel,datetime,logging, os, json, base64
from google.appengine.api import urlfetch
from handlerhelpers import ApiReq
from handlerutils import RetType, getUserAndIsAdmin, RequireAdmin, RequireAdminRaw
from fileapi import internalAddFile

def doFetch(url, method='GET', resultType=None, urlPrefix = 'https://api.github.com/', expectCode=200, payload=None): # result type of None is JSON...
    result = urlfetch.fetch(urlPrefix + url, deadline=60, method=method, payload=payload)
    if result.status_code == expectCode:
        if resultType == 'RAW': return result.content
        return json.loads(result.content)
    logging.info('Not expected code %s: %s - %s' % (expectCode, result.status_code, result.content))
    return None

# ----- github reading methods -------

def getHeadsMasterSha(user, repo):
    obj = doFetch('''repos/%s/%s/git/refs/heads/master''' % (user,repo))
    if not obj or 'object' not in obj: return None
    return obj.get('object').get('sha')

def getCommit(user, repo, sha):
    return doFetch('''repos/%s/%s/git/commits/%s''' % (user,repo, sha))

def getTree(user, repo, sha, recursive=False):
    """ you can either pass a tree sha or a commit sha here.
    """
    return doFetch('''repos/%s/%s/git/trees/%s%s''' % (user,repo, sha, '?recursive=1' if recursive else ''))

def getHeadMasterTree(user, repo, recursive=False):
    sha = getHeadsMasterSha(user,repo)
    if not sha: return None
    return getTree(user, repo, sha, recursive) # we can use the commit sha instead of the tree sha

def getBlobContent(user, repo, sha):
    obj = doFetch('''repos/%s/%s/git/blobs/%s''' % (user,repo,sha))
    if not obj: return None
    if obj.get('encoding') == 'base64':
        return base64.standard_b64decode(obj.get('content'))
    return obj.get('content')

def getMasterCommit(user, repo):
    return getCommit(user,repo,getHeadsMasterSha(user,repo))

# ------- for writing ---------

def addBlob(user, repo, content, ghat=None, encoding=None):
    if not ghat: ghat = datamodel.DB_ConfigData.get_by_key_name('github_oauth')

    if encoding=='utf-8':
        postjson = {"content": content, 'encoding':'utf-8' }
    else:
        postjson = {"content": base64.standard_b64encode(content), 'encoding':'base64' }


    postjsonstr = json.dumps(postjson)
    res = doFetch('repos/%s/%s/git/blobs?%s' % (user,repo,ghat.access_token), method='POST', payload=postjsonstr, expectCode=201)
    return res.get('sha')


def addFileToTree(user, repo, base_tree_sha, path, content, ghat=None):
    """ returns the sha of the new tree """
    if not ghat: ghat = datamodel.DB_ConfigData.get_by_key_name('github_oauth')

    #postjson = {'base_tree':base_tree_sha, 'tree':[{"path": path, "mode": "100644", "type": "blob", "content": content }]}
    blob_sha = addBlob(user, repo, content, ghat)
    postjson = {'base_tree':base_tree_sha, 'tree':[{"path": path, "mode": "100644", "type": "blob", "sha": blob_sha }]}
    postjsonstr = json.dumps(postjson)
    res = doFetch('repos/%s/%s/git/trees?%s' % (user,repo,ghat.access_token), method='POST', payload=postjsonstr, expectCode=201)
    return res.get('sha')

def addManyFilesToTree(user, repo, base_tree_sha, path_content_tuples, ghat=None):
    """ returns the sha of the new tree
        path_content_tuples is an array of tuples (path, content)
    """
    if not ghat: ghat = datamodel.DB_ConfigData.get_by_key_name('github_oauth')

    #postjson = {'base_tree':base_tree_sha, 'tree':[{"path": path, "mode": "100644", "type": "blob", "content": content }]}
    blob_shas = [(x[0], addBlob(user, repo, x[1], ghat)) for x in path_content_tuples]

    postjson = {'base_tree':base_tree_sha, 'tree':[{"path": x[0], "mode": "100644", "type": "blob", "sha": x[1] } for x in blob_shas]}
    postjsonstr = json.dumps(postjson)
    res = doFetch('repos/%s/%s/git/trees?%s' % (user,repo,ghat.access_token), method='POST', payload=postjsonstr, expectCode=201)
    return res.get('sha')


def addNewCommit(user, repo, new_tree_sha, old_parent, message, ghat=None):
    if not ghat: ghat = datamodel.DB_ConfigData.get_by_key_name('github_oauth')
    postjson = {'message':message, 'tree':new_tree_sha, 'parents':[old_parent]}
    postjsonstr = json.dumps(postjson)
    res = doFetch('repos/%s/%s/git/commits?%s' % (user,repo,ghat.access_token), method='POST', payload=postjsonstr, expectCode=201)
    return res.get('sha')

def updateHeadMasterCommit(user, repo, new_commit_sha, ghat=None):
    if not ghat: ghat = datamodel.DB_ConfigData.get_by_key_name('github_oauth')
    postjson = {'sha':new_commit_sha}
    postjsonstr = json.dumps(postjson)
    res = doFetch('repos/%s/%s/git/refs/heads/master?%s' % (user,repo,ghat.access_token), method='POST', payload=postjsonstr, expectCode=200)
    return res.get('ref') == "refs/heads/master"


# ------ Setup api - for writing ------

@ApiReq(allowGet=True)
@RequireAdmin
def github_UpdateGitHubApplicationData(req):
    ghc = datamodel.DB_ConfigData(key_name='github', ClientID=req.get('ClientID'), Secret=req.get('Secret'))
    ghc.put()
    return RetType.REDIRECT, '''https://github.com/login/oauth/authorize?client_id=%s&scope=user,public_repo,repo,gist''' % ghc.ClientID


@ApiReq(allowGet=True)
@RequireAdmin
def github_oauthcallback(req):
    ghc = datamodel.DB_ConfigData.get_by_key_name('github')
    access_token = doFetch('login/oauth/access_token?client_id=%s&client_secret=%s&code=%s' % (ghc.ClientID, ghc.Secret, req.get('code')),
        method='POST', resultType='RAW', urlPrefix='https://github.com/')
    logging.info(access_token)
    datamodel.DB_ConfigData(key_name='github_oauth', access_token=access_token).put() # overrites old one.

    #DB_GitHubAccessTokens(key_name=).put()
    return RetType.RAW, access_token

@ApiReq(allowGet=True)
@RequireAdmin
def github_redirectToOauth(req):
    ghc = datamodel.DB_ConfigData.get_by_key_name('github')
    return RetType.REDIRECT, '''https://github.com/login/oauth/authorize?client_id=%s&scope=user,public_repo,repo,gist''' % ghc.ClientID

# ----- api for initial update ------

@ApiReq(allowGet=True)
@RequireAdmin
def github_AddFileFromGitHub(req, user):
    gh_user = 'amirshim'
    gh_repo = 'melya'
    prefix = 'onlinesrc/'

    # quite inefficient, but who cares
    rr = getHeadMasterTree(gh_user, gh_repo, True)
    if not rr: return RetType.JSONFAIL
    file_sha_map = dict((x.get('path').split('/',1)[1], x.get('sha')) for x in rr.get('tree') if x.get('path').startswith(prefix) and x.get('type') == 'blob')

    fn = req.get('filename')
    if not fn: return RetType.JSONFAIL, {'text':'no file specified'}

    if fn not in file_sha_map: return RetType.JSONFAIL, {'text':'File not found on github'}
    sha = file_sha_map[fn]
    content = getBlobContent(gh_user, gh_repo, sha)
    if content is None: return RetType.JSONFAIL, {'text':'Failed to get file content from github'}

    ok, res = internalAddFile(fn, content, user.key())
    if ok: return RetType.JSONSUCCESS, res
    return RetType.JSONFAIL, res

@ApiReq(allowGet=True)
@RequireAdmin
def github_PopulateMissingFiles(req, user):
    gh_user = 'amirshim'
    gh_repo = 'melya'
    prefix = 'onlinesrc/'
    add_if_missing = True # maybe make this optional?

    rr = getHeadMasterTree(gh_user, gh_repo, True)
    if not rr: return RetType.JSONFAIL


    aa = [ (x.get('path').split('/',1)[1], x.get('sha')) for x in rr.get('tree') if x.get('path').startswith(prefix) and x.get('type') == 'blob']

    res = []
    for path,sha in aa:
        fv = datamodel.DB_FileVersion.getMostRecent(path, 'z', keys_only=True)
        if not fv:
            if add_if_missing:
                content = getBlobContent(gh_user, gh_repo, sha)
                if content:
                    ok, resobj = internalAddFile(path, content, user.key())
                    if ok:
                        res.append('Added file: %s (%s)<br/>\n' % (path, sha))
                    else:
                        res.append('Added file failed: %s (%s)<br/>\n' % (path, sha))
                else:
                    res.append('Failed to get content for: %s (%s)<br/>\n' % (path, sha))
            else:
                res.append('GitHub file not found locally: %s (%s)<br/>\n' % (path, sha))
        else:
            found_sha = fv.parent().name()
            if sha == found_sha:
                res.append('GitHub file found with same sha: %s (%s)<br/>\n' % (path, sha))
            else:
                res.append('GitHub file found with different sha: %s (github: %s - local: %s)<br/>\n' % (path, sha, found_sha))

    return RetType.RAW, ''.join(sorted(res))

    #aa = [ [x.get('path'), x.get('sha')] for x in rr.get('tree') ]
    #return RetType.JSONSUCCESS, {'text':aa, 'ver':ApiFileVer}
    #return RetType.JSONSUCCESS, {'text':'Some stuff', 'ver':ApiFileVer}


