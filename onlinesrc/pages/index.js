
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], function($, jvu) {
  var init;
  init = function() {
    return $(function() {
      var body;
      jvu.loadCss('/api/d/a/css/reset.css');
      body = $('body');
      return body.empty().append("Welcome to the Melya Framwork for Google App Engine.<br/>\nTo get started, please visit <a href=\"https://github.com/amirshim/melya/wiki\">the wiki</a>.");
    });
  };
  return {
    init: init
  };
});
