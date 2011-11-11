jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery'], function($) {
  var jvDeferModuleLoading, waitfor;
  waitfor = $LAB.script('http://cdn.jquerytools.org/1.2.6/all/jquery.tools.min.js');
  jvDeferModuleLoading = function(cb) {
    return waitfor.wait(function() {
      return cb();
    });
  };
  return {
    jvDeferModuleLoading: jvDeferModuleLoading
  };
});