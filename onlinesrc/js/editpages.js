
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], function($, jvu) {
  var init, onReady, showYesNoDialog, theTemplates, urls, yesNoDialog;
  urls = {};
  urls.knockout130beta = '/api/d/a/libs/knockout-1.3.0beta.js';
  urls.jquerytmpl = '/api/d/a/libs/jquery.tmpl100pre.min.js';
  urls.jqueryUIjs = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js';
  urls.jqueryUIcss = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/smoothness/jquery-ui.css';
  urls.jqueryTools = 'http://cdn.jquerytools.org/1.2.6/full/jquery.tools.min.js';
  theTemplates = "<script id=\"deTemplate\" type=\"text/html\">\n<table>\n      <thead>\n        <tr>\n            <th>ID</th>\n            <th>Which domain</th>\n            <th>Regex for page</th>\n            <th>File to show</th>\n            <th>Match Order</th>\n        </tr>\n     </thead>    \n\n<tbody data-bind=\"foreach: entities\">\n<tr>\n	<td><span data-bind=\"text: key\" /></td>\n	<td><input data-bind=\"value: domainName, valueUpdate: 'afterkeydown'\" /></td>\n    	<td><input data-bind=\"value: regex, valueUpdate: 'afterkeydown'\" /></td>\n    	<td><input data-bind=\"value: fileName, valueUpdate: 'afterkeydown'\" /></td>\n    	<td><input data-bind=\"value: flags, valueUpdate: 'afterkeydown'\" /></td>\n    	<td><input data-bind=\"value: order, valueUpdate: 'afterkeydown'\" /></td>\n    	<td style=\"width:70px;\"><a data-bind=\"visible: _changed\" class=\"save-row\" href=\"#\">Save</a> &nbsp; </td>\n    	<td style=\"width:70px;\"><a data-bind=\"visible: _canDelete\" class=\"delete-row\" href=\"#\">Delete</a> &nbsp; </td>\n    	<td style=\"width:70px;\"><a target=\"_blank\" data-bind=\"visible: _editUrl, attr: { href: _editUrl }\">Edit Page</a> &nbsp; </td>\n    	<td><span data-bind=\"text: _currentMessage\" /></td>\n</tr>\n</tbody>\n</table>\n    <br/>\n    <a href=\"#\" class=\"add-row\">Add Row</a>\n    </script>";
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
  onReady = function(inputEntities) {
    var bb, viewModel, x, _i, _len;
    bb = $('body');
    bb.empty().append(theTemplates).append("<div data-bind='template: \"deTemplate\"'></div>").append(yesNoDialog);
    yesNoDialog.hide();
    viewModel = {
      entities: ko.observableArray(),
      addEntity: function(x) {
        var a, y;
        a = {};
        for (y in x) {
          x[y] = '' + x[y];
          a[y] = new ko.observable(x[y]);
        }
        a._origState = x;
        a._currentMessage = new ko.observable('');
        a._changed = new ko.dependentObservable(function() {
          var k, v, _ref;
          if (a._currentMessage() !== '') return false;
          _ref = a._origState;
          for (k in _ref) {
            v = _ref[k];
            if (v !== a[k]()) return true;
          }
          return false;
        });
        a._canDelete = new ko.dependentObservable(function() {
          if (a._currentMessage() !== '') return false;
          return true;
        });
        a._editUrl = new ko.dependentObservable(function() {
          var t;
          t = a.fileName();
          if (!t || a._currentMessage() !== '') return null;
          return "/account/admin/editfile?filename=" + t;
        });
        return viewModel.entities.push(a);
      },
      sort: function() {
        return this.entities.sort(function(a, b) {
          return +a.order() - +b.order();
        });
      }
    };
    for (_i = 0, _len = inputEntities.length; _i < _len; _i++) {
      x = inputEntities[_i];
      viewModel.addEntity(x);
    }
    viewModel.sort();
    ko.applyBindings(viewModel);
    bb.on('click', 'a.save-row', function() {
      var aa, temp;
      temp = $(this).parent();
      aa = ko.dataFor(this);
      aa._currentMessage('Saving...');
      return jvu.doJsonApiPOST('admin/SavePage', {
        data: {
          jsonobj: ko.toJSON(aa)
        },
        success: function(data) {
          aa._currentMessage('');
          return jvu.doJsonApiPOST('admin/GetPageList', {
            data: {
              key: data.pageKey
            },
            success: function(data) {
              viewModel.entities.remove(aa);
              viewModel.addEntity(data.pages[0]);
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
      showYesNoDialog('Delete this page?', function() {
        aa._currentMessage('Deleting...');
        return jvu.doJsonApiPOST('admin/DeletePage', {
          data: {
            key: aa.key()
          },
          success: function(data) {
            aa._currentMessage('');
            return viewModel.entities.remove(aa);
          }
        });
      });
      return false;
    });
    return $('a.add-row').click(function() {
      viewModel.addEntity({
        "regex": '',
        "domainName": "",
        "fileName": "",
        "key": '',
        "dateUpdated": null,
        "flags": "",
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
        return jvu.doJsonApiPOST('admin/GetPageList', {
          success: function(data) {
            return jvu.waitCss($("body"), 'ui-helper-hidden', function() {
              return onReady(data.pages);
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
