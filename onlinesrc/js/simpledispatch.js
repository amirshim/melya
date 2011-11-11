
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['js/utils.js', 'pages/mapping.js'], function(jvu, pagemap) {
  var checkIsAdmin, init;
  checkIsAdmin = function(nextLevel) {
    var doCheck;
    return doCheck = function(opts, onContinue) {
      return jvu.doJsonApiPOST('admin/isAdmin', {
        success: function(data) {
          if (data.success) return onContinue(nextLevel);
          jv.appendNotFoundMessage = '<div>Maybe you need to login?</div>';
          return onContinue(null);
        }
      });
    };
  };
  init = function(opts) {
    var load, mm, processRec, rootmap, spl, url;
    url = window.location.pathname;
    load = function(modname) {
      return jv.getModule(modname, function(a) {
        return a.init({
          url: url
        });
      });
    };
    rootmap = pagemap.getMapping(opts.dname, {
      checkIsAdmin: checkIsAdmin
    });
    if (url === '/') return load(rootmap.index);
    mm = rootmap;
    spl = url.split('/');
    processRec = function(mm, curSplPos) {
      var next;
      if (!mm) return load(rootmap.notfound);
      if ('function' === typeof mm) {
        return mm({
          url: url
        }, function(res) {
          return processRec(res, curSplPos);
        });
      }
      if ('string' === typeof mm) return load(mm);
      next = spl[curSplPos];
      if (!next) next = 'index';
      return processRec(mm[next], curSplPos + 1);
    };
    return processRec(rootmap, 1);
  };
  return {
    init: init
  };
});

window.jv.doDispatch = function(opts) {
  jv.mainPageOpts = opts;
  return jv.getModule('js/simpledispatch.js', function(a) {
    return a.init(opts);
  });
};
