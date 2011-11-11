
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], function($, jvu) {
  var init;
  init = function() {
    var bb;
    bb = $('body').empty();
    bb.append('Page not found');
    if (jv.appendNotFoundMessage) return bb.append(jv.appendNotFoundMessage);
  };
  return {
    init: init
  };
});
