var __hasProp = Object.prototype.hasOwnProperty, __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (__hasProp.call(this, i) && this[i] === item) return i; } return -1; };

jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], function($, jvu) {
  var init, initCssRules, messageDiv, setFileVersionTag;
  initCssRules = function() {
    jvu.addCssRule('.jvisdeletemode', 'background-color:pink;');
    jvu.addCssRule('.jvisheadver', 'background-color:red;');
    jvu.addCssRule('.jvafterheadver', 'background-color:yellow;');
    jvu.addCssRule('.jvthefilename', 'width: 200px;display:inline-block;');
    jvu.addCssRule('.jvleftsp5', 'margin-left: 5px;');
    return jvu.addCssRule('.bigandred', 'font-size: 40px; background-color:  red;');
  };
  messageDiv = $('<div/>');
  setFileVersionTag = function(opts, cb) {
    return jvu.doJsonApiPOST('admin/setFileVersionTag', {
      data: opts,
      success: function(data) {
        if (data.success) return cb(data);
        return $("body").append('<div>problem: ' + (data.text || 'unknown') + '</div>');
      }
    });
  };
  init = function() {
    return $(function() {
      var doRealDelete, isCurrentlyDeleteMode, mainDiv, rootef;
      initCssRules();
      mainDiv = $('<div/>');
      $('body').empty().append(mainDiv);
      mainDiv.append('Loading...');
      isCurrentlyDeleteMode = false;
      doRealDelete = function(filename, ver, theVerEl, onComplete) {
        return setFileVersionTag({
          filename: filename,
          ver: ver,
          delversion: ver
        }, function(data) {
          theVerEl.remove();
          if (data.text) {
            $("body").append('<div>Delete text: ' + (data.text || 'unknown') + '</div>');
          }
          if (onComplete) return onComplete();
        });
      };
      mainDiv.on('click', 'a.invalidateFileBuilds', function() {
        jvu.doJsonApiPOST('admin/invalidateFileBuilds', {
          success: function(data) {
            if (data.success) {
              messageDiv.removeClass('bigandred');
              return alert('Successfully invalidated all file builds. Current file version is ' + data.fileVer);
            } else {
              return alert('Failed to invalidate file builds!');
            }
          }
        });
        return false;
      });
      mainDiv.on('click', 'a.onversionclickable', function() {
        var filename, isHead, theVerEl, ver;
        theVerEl = $(this);
        filename = theVerEl.closest('div').data('filename');
        ver = theVerEl.data('ver');
        isHead = theVerEl.hasClass('jvisheadver');
        if (isCurrentlyDeleteMode) {
          doRealDelete(filename, ver, theVerEl);
          return false;
        }
        if (isHead) {
          setFileVersionTag({
            filename: filename,
            ver: ver,
            deltag: 'a'
          }, function() {
            return theVerEl.removeClass('jvisheadver');
          });
        } else {
          setFileVersionTag({
            filename: filename,
            ver: ver,
            addtag: 'a'
          }, function() {
            return theVerEl.addClass('jvisheadver');
          });
        }
        messageDiv.addClass('bigandred');
        return false;
      });
      rootef = '/account/admin/editfile';
      return jvu.doJsonApiPOST('admin/getAllFileVersions', {
        data: {},
        success: function(data) {
          var aa, alljq, fillpart1, fillpart2, filterList, holder, lastHigh, prefix, prefixList, setupSpecialDelete, switchToDeleteMode, tf, theFilters, thelink, toadd, vertext, x, y, z, _fn, _i, _j, _len, _len2, _ref, _ref2, _ref3;
          mainDiv.empty();
          messageDiv.append('Remember to <a class="invalidateFileBuilds" href="#">Invalidate the builds</a> after updating the head versions.');
          mainDiv.append(messageDiv);
          theFilters = $('<div/>');
          mainDiv.append('<br/>').append(theFilters).append('<br/>').append('Click on the filename to edit that file. Click on the version number to toggle ' + 'that version being tagged as a head version or not. Red means head version. We highlight version(s) after the last head version with yellow.');
          filterList = {};
          prefixList = {};
          if (!data.success) {
            alert(data.text || 'Error!');
            return;
          }
          toadd = [];
          _ref = data.files;
          for (x in _ref) {
            y = _ref[x];
            holder = $('<div/>');
            vertext = $('<span/>');
            lastHigh = null;
            for (_i = 0, _len = y.length; _i < _len; _i++) {
              z = y[_i];
              thelink = $("<a class=\"onversionclickable jvleftsp5\" href=\"#\">" + z[0] + "</a> ");
              thelink.data('ver', z[0]);
              if (__indexOf.call(z, 'a') >= 0) {
                thelink.addClass('jvisheadver');
                lastHigh = thelink;
              }
              vertext.append(thelink);
            }
            holder.append("<a class=\"jvthefilename\" target=\"_blank\" href=\"" + rootef + "?filename=" + x + "\">" + x + "</a>").append(vertext);
            if (lastHigh) {
              lastHigh.nextAll().addClass('jvafterheadver');
            } else {
              vertext.find('.onversionclickable').addClass('jvafterheadver');
            }
            holder.data('filename', x);
            holder.data('versions', y);
            prefix = x.substring(0, x.lastIndexOf('/') + 1);
            if (prefix && prefix !== '') {
              if ((_ref2 = filterList[prefix]) == null) filterList[prefix] = [];
              filterList[prefix].push(holder);
            }
            toadd.push([x, holder]);
            aa = x.lastIndexOf('.');
            if (aa > -1) {
              tf = x.substring(aa);
              holder.data('filter', tf);
              if ((_ref3 = filterList[tf]) == null) filterList[tf] = [];
              filterList[tf].push(holder);
            }
          }
          toadd.sort(function(a, b) {
            if (a[0] < b[0]) {
              return -1;
            } else {
              return 1;
            }
          });
          alljq = [];
          for (_j = 0, _len2 = toadd.length; _j < _len2; _j++) {
            x = toadd[_j];
            mainDiv.append(x[1]);
            alljq.push(x[1]);
          }
          filterList['all'] = alljq;
          fillpart1 = $('<div>Filter by type: </div>');
          fillpart2 = $('<div>Filter by dir: </div>');
          theFilters.append(fillpart1);
          theFilters.append(fillpart2);
          _fn = function(y) {
            var fb;
            fb = $("<a class=\"jvleftsp5\" href=\"#\">" + x + "</a>");
            if (jvu.endsWith(x, '/')) {
              fillpart2.append(fb);
            } else {
              fillpart1.append(fb);
            }
            return fb.click(function() {
              var x, _k, _l, _len3, _len4, _ref4;
              _ref4 = filterList['all'];
              for (_k = 0, _len3 = _ref4.length; _k < _len3; _k++) {
                x = _ref4[_k];
                x.hide();
              }
              for (_l = 0, _len4 = y.length; _l < _len4; _l++) {
                x = y[_l];
                x.show();
              }
              return false;
            });
          };
          for (x in filterList) {
            y = filterList[x];
            _fn(y);
          }
          setupSpecialDelete = function() {
            return $('a.jvthefilename').click(function(e) {
              var allv, cld, deleteNextAsync, filename, headv, lastver, todelete, ver, x, xx, _k, _len3;
              if (e.ctrlKey) {
                cld = $(this).closest('div');
                filename = cld.data('filename');
                allv = $.makeArray(cld.find('a.onversionclickable'));
                headv = null;
                lastver = 0;
                todelete = [];
                for (_k = 0, _len3 = allv.length; _k < _len3; _k++) {
                  x = allv[_k];
                  if (headv) {
                    alert('Head version is not the last one');
                    return false;
                  }
                  xx = $(x);
                  ver = +xx.text();
                  if (ver <= 0) {
                    alert('Bad version!');
                    return false;
                  }
                  if (ver <= lastver) {
                    alert('versions are not increasing');
                    return false;
                  }
                  lastver = ver;
                  if (xx.hasClass('jvisheadver')) {
                    if (headv) {
                      alert('to many head versions');
                      return false;
                    }
                    headv = ver;
                  } else {
                    todelete.push(ver);
                  }
                }
                if (!headv) {
                  alert('no head version');
                  return false;
                }
                if (headv !== lastver) {
                  alert('head version is not the last one');
                  return false;
                }
                if (todelete.length === 0) {
                  alert('nothing to delete');
                  return false;
                }
                deleteNextAsync = function() {
                  var nn;
                  nn = $(cld.find('a.onversionclickable').get(0));
                  ver = +nn.text();
                  if (__indexOf.call(todelete, ver) >= 0) {
                    return doRealDelete(filename, ver, nn, function() {
                      return deleteNextAsync();
                    });
                  }
                };
                deleteNextAsync();
              }
              return false;
            });
          };
          switchToDeleteMode = $('<a href="#">Switch to DELETE mode</a>');
          switchToDeleteMode.click(function() {
            $('body').addClass('jvisdeletemode');
            isCurrentlyDeleteMode = true;
            setupSpecialDelete();
            return false;
          });
          mainDiv.append('<br/>').append(switchToDeleteMode);
          return mainDiv.append('<br/><br/><form method="POST" action="/api/admin/CreateAllFileZip"><input type=submit value="Create a zip file with all the files and all the versions"></form>');
        }
      });
    });
  };
  return {
    init: init
  };
});
