
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], function($, jvu) {
  var createEditor, currentSaveFunc, editor, getText, nextLabjs, publicFuncs, renderer, resizeEditor, session, setSaveKeyCB, setText;
  publicFuncs = {};
  nextLabjs = $LAB.script('/api/z/ace20/ace.js').wait().script('/api/z/ace20/theme-twilight.js');
  editor = null;
  session = null;
  renderer = null;
  currentSaveFunc = function() {};
  createEditor = function(containingDiv, filetype, onReady) {
    var aceEditor;
    if (filetype == null) filetype = "text";
    if (filetype !== 'text') {
      nextLabjs = nextLabjs.script('/api/z/ace20/mode-' + filetype + '.js');
    }
    aceEditor = $('<div id="aceEditor" style="margin:0;position:absolute;top:0;bottom:0;left:0;right:0;font-size:14px;"></div>');
    containingDiv.append(aceEditor);
    nextLabjs.wait(function() {
      var TheMode, canon;
      editor = ace.edit("aceEditor");
      editor.setTheme("ace/theme/twilight");
      editor.setScrollSpeed(jvu.parsedUrlArgs.scrollspeed || 4);
      TheMode = require("ace/mode/" + filetype).Mode;
      canon = require('pilot/canon');
      session = editor.getSession();
      renderer = editor.renderer;
      session.setMode(new TheMode());
      session.setUseWrapMode(false);
      session.setUseSoftTabs(false);
      renderer.setShowPrintMargin(false);
      canon.addCommand({
        name: 'onSave',
        bindKey: {
          win: 'Ctrl-S',
          mac: 'Command-S',
          sender: 'editor'
        },
        exec: function(env, args, request) {
          return currentSaveFunc(env, args, request);
        }
      });
      canon.removeCommand('replace');
      if (onReady) onReady(publicFuncs);
    });
  };
  setText = function(text) {
    return session.setValue(text);
  };
  getText = function() {
    return session.getValue();
  };
  resizeEditor = function() {
    return editor.resize();
  };
  setSaveKeyCB = function(onSaveCB) {
    if (onSaveCB) {
      return currentSaveFunc = onSaveCB;
    } else {
      return currentSaveFunc = function() {};
    }
  };
  publicFuncs = {
    createEditor: createEditor,
    setText: setText,
    getText: getText,
    setSaveKeyCB: setSaveKeyCB,
    resizeEditor: resizeEditor
  };
  return publicFuncs;
});
