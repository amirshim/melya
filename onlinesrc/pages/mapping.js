
jv.defModule('$$jv:fn$$', '$$jv:ver$$', [], function() {
  var getMapping;
  getMapping = function(domainName, mapUtils) {
    var mapping;
    mapping = {
      index: 'pages/index.js',
      notfound: 'js/pagenotfound.js',
      account: {
        admin: mapUtils.checkIsAdmin({
          index: 'js/adminindex.js',
          editdomains: 'js/editdomains.js',
          editpages: 'js/editpages.js',
          editfiles: 'js/showfilevers.js',
          editfile: 'js/fileedit.js',
          livepython: 'js/liveexecute.js'
        })
      }
    };
    return mapping;
  };
  return {
    getMapping: getMapping
  };
});
