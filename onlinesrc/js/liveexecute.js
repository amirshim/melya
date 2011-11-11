
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/ace20.js', 'js/utils.js'], function($, ace, jvu) {
  var init, onEditorReady, rightc, setupCss;
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
  setupCss = function() {
    jvu.addCssRule('body', 'padding:0; margin:0 0 0 50%; width:50%; min-height:100%; float:right;');
    jvu.addCssRule('#left_col', 'float:left; width:100%; margin-left:-100%;position:relative;');
    return jvu.addCssRule('#right_col', 'position:relative;');
  };
  rightc = null;
  onEditorReady = function() {
    var onExecBut;
    onExecBut = $('<a href="#">Execute</a>');
    rightc.append(onExecBut);
    onExecBut.click(function() {
      $.post('/api/admin/DangerousExecutePythonCode', {
        code: ace.getText()
      }, function(data) {
        return $('#result-ta').val(data);
      });
      return false;
    });
    return rightc.append("<br/><textarea id=\"result-ta\" style=\"position:absolute; bottom:0; left:0;right:0; top:20px;\" />");
  };
  init = function() {
    return $(function() {
      var bb, leftc, onWindowResize;
      bb = $('body');
      bb.empty();
      jvu.loadCss('/api/d/a/css/reset.css');
      setupCss();
      bb.append('<div id="left_col"></div><div id="right_col"></div>');
      leftc = $('#left_col');
      rightc = $('#right_col');
      onWindowResize = function() {
        leftc.height($(window).height() + 'px');
        return rightc.height($(window).height() + 'px');
      };
      onWindowResize();
      return ace.createEditor(leftc, 'python', function() {
        onEditorReady();
        return $(window).resize(onWindowResize);
      });
    });
  };
  return {
    init: init
  };
});
