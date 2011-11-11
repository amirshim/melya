# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

import hashlib
import google.appengine.ext.db as db

def getGitBlobHash(blob): # the same hash as Git uses...
     return hashlib.sha1('blob %s\0%s' %(len(blob), blob)).hexdigest()

# database object pretty print
def DB_PrettyPrint(t, prefix='', already_printed = None):
    if already_printed is None:
        already_printed = set()
    if type(t) == type([]):
        return "\n".join([DB_PrettyPrint(x, prefix + '  ', already_printed) for x in t])
    res = prefix + (str(t.key().name() or t.key().id()) + "\n")
    tl = list(t.properties())
    if isinstance(t, db.Expando):
        tl.extend(t.dynamic_properties())
    for x in tl:
        a = getattr(t,x)
        if isinstance(a, db.Model):
            kk = str(a.key())
            if kk in already_printed:
                res += prefix + "  %s: %s\n" % (x, kk)
            else:
                already_printed.add(kk)
                res += prefix + "  %s: %s\n" % (x, kk)
                res += DB_PrettyPrint(a, prefix + '    ', already_printed)
        else:
            res += prefix + "  %s: %s\n" % (x, a)
    return res

def DB_SimpleToDict(t, ignore = frozenset()):
    res = {}
    tl = list(t.properties())
    if isinstance(t, db.Expando):
        tl.extend(t.dynamic_properties())
    for x in tl:
        if x in ignore: continue
        a = getattr(t,x)
        res[x] = a
    return res

def getAllFromFromQuery(theQuery):
    res = []
    while 1:
        x = theQuery.fetch(1000)
        res.extend(x)
        if len(x) < 1000: break;
        theQuery.with_cursor(theQuery.cursor())
    return res

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def getStrSortableHexNum(a):
    """
    Returns a hex representation (string) of the integer a that can be used in an
     ascii sort... for example... in a key or string property in the datastore, so
     it can be sorted.
    """
    if a < 0: raise Exception('Does not support negative numbers')
    c = 0; t = a
    while t > 0xf: c += 1; t >>= 4
    return ('~'*c)+"{0:x}".format(a)