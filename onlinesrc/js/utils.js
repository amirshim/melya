var __slice = Array.prototype.slice;

jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery'], function($) {
  var addRuleFunc, jvu;
  jvu = function() {};
  jvu.delay = function(ms, func) {
    return setTimeout(func, ms);
  };
  jvu.cancelDelay = function(token) {
    return clearTimeout(token);
  };
  jvu.execute_once = function(func) {
    var is_exec;
    is_exec = false;
    return function() {
      var a;
      a = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      if (is_exec) return;
      is_exec = true;
      return func.apply(null, a);
    };
  };
  jvu.parsedUrlArgs = (function() {
    var a, b, p, x, _i, _len, _ref, _ref2;
    p = {};
    _ref = (location.href.split('?')[1] || '').split('&');
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      x = _ref[_i];
      if (!(x)) continue;
      _ref2 = x.split('='), a = _ref2[0], b = _ref2[1];
      p[a] = b;
    }
    return p;
  })();
  jvu.startsWith = function(str, find) {
    return find === str.substr(0, find.length);
  };
  jvu.endsWith = function(str, find) {
    return str.substr(-find.length) === find;
  };
  jvu.ifStartsWith = function(str, find, cb) {
    if (jvu.startsWith(str, find)) {
      cb(str.substr(find.length));
      return true;
    } else {
      return false;
    }
  };
  jvu.doJsonApiPOST = function(apicommand, opts) {
    return $.ajax({
      url: '/api/' + apicommand,
      dataType: 'json',
      type: 'POST',
      data: opts.data,
      success: opts.success,
      error: opts.error || function(e) {
        if (!jvu.isCurrentlyReloading) return alert('Error');
      }
    });
  };
  jvu.loadCss = function(csshref, linkid) {
    var link_ref;
    if (linkid) {
      $("head").append("<link id=\"" + linkid + "\" />");
    } else {
      $("head").append("<link/>");
    }
    link_ref = $("head").children(":last");
    return link_ref.attr({
      rel: "stylesheet",
      type: "text/css",
      href: csshref
    });
  };
  jvu.waitCss = function(visibleDiv, cssClass, onReady, maxWait) {
    var doCheck, multiCheck, tempspan;
    if (maxWait == null) maxWait = 13000;
    tempspan = $("<span class=\"" + cssClass + "\">&nbsp;</span>");
    visibleDiv.append(tempspan);
    doCheck = function() {
      if (!tempspan.is(":visible")) {
        tempspan.remove();
        onReady(true);
        return true;
      }
      return false;
    };
    if (doCheck()) return;
    multiCheck = function(curDelay) {
      if (curDelay >= maxWait) return onReady(false);
      jvu.delay(curDelay, function() {
        if (doCheck()) return;
        return multiCheck(curDelay * 2);
      });
    };
    multiCheck(50);
  };
  addRuleFunc = null;
  jvu.addCssRule = function(selector, rule) {
    var sheet, stylesheet;
    if (!addRuleFunc) {
      stylesheet = document.createElement("style");
      stylesheet.type = "text/css";
      document.getElementsByTagName("head")[0].appendChild(stylesheet);
      sheet = stylesheet.sheet || stylesheet.styleSheet;
      if ('insertRule' in sheet) {
        addRuleFunc = function(sel, css) {
          return sheet.insertRule(sel.concat('{' + css + '}'), 0);
        };
      } else {
        addRuleFunc = function(sel, css) {
          return sheet.addRule(sel, css, 0);
        };
      }
    }
    return addRuleFunc(selector, rule);
  };
  jvu.loadWebPuttyCss = function(puttyKey) {
    jvu.loadCss('http://www.webputty.net/css/' + puttyKey, puttyKey);
    if (window.location !== window.parent.location || window.location.search.indexOf('__preview_css__') > -1) {
      return $LAB.script('http://www.webputty.net/js/' + puttyKey);
    }
  };
  return jvu;
});
