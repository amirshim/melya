
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], function($, jvu) {
  var init, onReady, showYesNoDialog, theTemplates, urls, yesNoDialog;
  urls = {};
  urls.knockout130beta = '/api/d/a/libs/knockout-1.3.0beta.js';
  urls.jquerytmpl = '/api/d/a/libs/jquery.tmpl100pre.min.js';
  urls.jqueryUIjs = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js';
  urls.jqueryUIcss = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/smoothness/jquery-ui.css';
  urls.jqueryTools = 'http://cdn.jquerytools.org/1.2.6/full/jquery.tools.min.js';
  theTemplates = "<script id=\"deTemplate\" type=\"text/html\">\n<table>\n      <thead>\n        <tr>\n            <th>ID</th>\n            <th>Name to pass to client</th>\n            <th>Regex for domain</th>\n            <th>Default Title</th>\n            <th>Match Order</th>\n        </tr>\n     </thead>    \n\n<tbody data-bind=\"foreach: domains\">\n<tr>\n	<td><span data-bind=\"text: key\" /></td>\n	<td><input data-bind=\"value: name, valueUpdate: 'afterkeydown'\" /></td>\n    	<td><input data-bind=\"value: regex, valueUpdate: 'afterkeydown'\" /></td>\n    	<td><input data-bind=\"value: defaultTitle, valueUpdate: 'afterkeydown'\" /></td>\n    	<td><input data-bind=\"value: order, valueUpdate: 'afterkeydown'\" /></td>\n    	<!-- ko if: _canDelete --> \n    	<td><a class=\"delete-row\" href=\"#\">Delete</a> &nbsp; </td>\n    	<!-- /ko -->\n    	<!-- ko if: _changed --> \n    	<td><a class=\"save-row\" href=\"#\">Save</a></td>\n    	<!-- /ko -->\n</tr>\n</tbody>\n</table>\n    <br/>\n    <a href=\"#\" class=\"add-row\">Add Row</a>\n    </script>";
  yesNoDialog = $("<div id=\"dialog-confirm\" title=\"Are you sure?\">\n	<p><span class=\"ui-icon ui-icon-alert\" style=\"float:left; margin:0 7px 20px 0;\"></span>Are you sure?</p>\n</div>");
  showYesNoDialog = function(text, okCB) {
    $("#dialog-confirm").attr('title', text);
    return $("#dialog-confirm").dialog({
      resizable: false,
      height: 240,
      modal: true,
      buttons: {
        Yes: function() {
          $(this).dialog("close");
          return okCB();
        },
        Cancel: function() {
          return $(this).dialog("close");
        }
      }
    });
  };
  onReady = function(ajaxDomains) {
    var bb, doSort, viewModel, x, _i, _len;
    bb = $('body');
    bb.empty().append(theTemplates).append("<div data-bind='template: \"deTemplate\"'></div>").append(yesNoDialog);
    yesNoDialog.hide();
    viewModel = {
      domains: ko.observableArray(),
      addDomain: function(x) {
        var a, y;
        a = {};
        for (y in x) {
          x[y] = '' + x[y];
          a[y] = new ko.observable(x[y]);
        }
        a._origState = x;
        a._changed = new ko.dependentObservable(function() {
          var k, v, _ref;
          _ref = a._origState;
          for (k in _ref) {
            v = _ref[k];
            if (v !== a[k]()) return true;
          }
          return false;
        });
        a._canDelete = new ko.dependentObservable(function() {
          return true;
        });
        return viewModel.domains.push(a);
      },
      sort: function() {
        return this.domains.sort(function(a, b) {
          return +a.order() - +b.order();
        });
      }
    };
    for (_i = 0, _len = ajaxDomains.length; _i < _len; _i++) {
      x = ajaxDomains[_i];
      viewModel.addDomain(x);
    }
    doSort = function() {};
    viewModel.sort();
    ko.applyBindings(viewModel);
    bb.on('click', 'a.save-row', function() {
      var aa, temp;
      temp = $(this).parent();
      aa = ko.dataFor(this);
      $(temp).empty().append('Saving...');
      return jvu.doJsonApiPOST('admin/SaveDomain', {
        data: {
          jsonobj: ko.toJSON(aa)
        },
        success: function(data) {
          return jvu.doJsonApiPOST('admin/GetDomainList', {
            data: {
              key: data.domainKey
            },
            success: function(data) {
              viewModel.domains.remove(aa);
              viewModel.addDomain(data.domains[0]);
              return viewModel.sort();
            }
          });
        }
      });
    });
    bb.on('click', 'a.delete-row', function() {
      var aa, temp;
      temp = $(this).parent();
      aa = ko.dataFor(this);
      showYesNoDialog('Delete this domain?', function() {
        $(temp).empty().append('Deleting...');
        return jvu.doJsonApiPOST('admin/DeleteDomain', {
          data: {
            key: aa.key()
          },
          success: function(data) {
            return viewModel.domains.remove(aa);
          }
        });
      });
      return false;
    });
    return $('a.add-row').click(function() {
      viewModel.domains.push({
        "regex": "",
        "name": "",
        "defaultTitle": "",
        "key": null,
        "dateUpdated": null,
        "order": 1
      });
      return false;
    });
  };
  init = function() {
    return $(function() {
      jvu.loadCss('/api/d/a/css/reset.css');
      jvu.loadCss(urls.jqueryUIcss);
      return $LAB.script([urls.knockout130beta, urls.jquerytmpl, urls.jqueryUIjs, urls.jqueryTools]).wait(function() {
        return jvu.doJsonApiPOST('admin/GetDomainList', {
          success: function(data) {
            return jvu.waitCss($("body"), 'ui-helper-hidden', function() {
              return onReady(data.domains);
            });
          }
        });
      });
    });
  };
  return {
    init: init
  };
});
