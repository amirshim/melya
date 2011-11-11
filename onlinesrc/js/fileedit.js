
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/ace20.js', 'js/utils.js', 'js/coffeescript.js'], function($, ace, jvu, coffee) {
  var createEmptyFile, filename, filetype, init, messageText, onEditorReady, onSaveEditor, saveButton;
  saveButton = null;
  messageText = null;
  filename = jvu.parsedUrlArgs['filename'];
  filetype = 'text';
  if (filename) {
    if (jvu.endsWith(filename, '.coffee')) filetype = 'coffee';
    if (jvu.endsWith(filename, '.py')) filetype = 'python';
    if (jvu.endsWith(filename, '.js')) filetype = 'javascript';
    if (jvu.endsWith(filename, '.css')) filetype = 'css';
    if (jvu.endsWith(filename, '.html')) filetype = 'html';
  }
  onSaveEditor = function() {
    var jsfilename, postSave, result, success, _ref;
    postSave = function() {};
    if (jvu.endsWith(filename, '.coffee')) {
      jsfilename = filename.substring(0, filename.length - 7) + '.js';
      _ref = coffee.compileToJS(ace.getText()), success = _ref[0], result = _ref[1];
      if (!success) {
        messageText.text('Can\'t save. CoffeeScript Error: ' + result);
        return;
      }
      postSave = function(parentData) {
        messageText.text('Coffescript file saved, saving generated javascript');
        return jvu.doJsonApiPOST('admin/UploadFileHandler', {
          data: {
            filename: jsfilename,
            content: result,
            generatedFromFile: parentData.filename,
            generatedFromVer: parentData.ver
          },
          success: function(data) {
            if (!data.success) {
              messageText.text('Problem saving generated javascript file: ' + jsfilename + ' ' + (data.text || ''));
              return;
            }
            return messageText.text('Generated file "' + jsfilename + '" saved');
          }
        });
      };
    }
    return jvu.doJsonApiPOST('admin/UploadFileHandler', {
      data: {
        filename: filename,
        content: ace.getText()
      },
      success: function(data) {
        if (!data.success) {
          messageText.text('Problem saving file: ' + filename + ' ' + (data.text || ''));
          return;
        }
        messageText.text('File "' + filename + '" saved');
        return postSave(data);
      }
    });
  };
  createEmptyFile = function(fn) {
    messageText.text('Creating "' + fn + '"');
    return jvu.doJsonApiPOST('admin/UploadFileHandler', {
      data: {
        filename: fn,
        content: '',
        allowemptyfile: 1
      },
      success: function(data) {
        if (!data.success) {
          messageText.text('Problem creating file: ' + fn + ' ' + (data.text || ''));
          return;
        }
        messageText.text('File "' + fn + '" created');
        return window.location.reload();
      }
    });
  };
  onEditorReady = function() {
    saveButton.click(function() {
      onSaveEditor();
      return false;
    });
    ace.setSaveKeyCB(function() {
      return onSaveEditor();
    });
    if (!filename) {
      messageText.text('No filename specified');
      return;
    }
    messageText.text('Loading ' + filename + '...');
    return jvu.doJsonApiPOST('admin/getCleanFileContent', {
      data: {
        filename: filename
      },
      success: function(data) {
        if (!data.success) {
          messageText.text('File does NOT exist: ' + filename + ' ' + (data.text || '') + ' ');
          ace.setText('');
          return;
        }
        messageText.text('');
        return ace.setText(data.data);
      }
    });
  };
  init = function() {
    return $(function() {
      var bb, onWindowResize, space, theRest, topBar;
      bb = $('body');
      bb.empty();
      jvu.loadCss('/api/d/a/css/reset.css');
      saveButton = $('<a href="#">Save</a>');
      messageText = $('<span/>');
      topBar = $('<div></div>');
      space = ' ';
      topBar.append(saveButton).append(space).append(messageText);
      bb.append(topBar);
      theRest = $('<div style="position:relative;"/>');
      bb.append(theRest);
      onWindowResize = function(forceResize) {
        if (forceResize == null) forceResize = true;
        theRest.css('height', ($(window).height() - 20) + 'px');
        theRest.css('width', ($(window).width() - 20) + 'px');
        if (forceResize) return ace.resizeEditor();
      };
      onWindowResize(false);
      return ace.createEditor(theRest, filetype, function() {
        onEditorReady();
        return $(window).resize(onWindowResize);
      });
    });
  };
  return {
    init: init
  };
});
