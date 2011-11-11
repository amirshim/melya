
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['^/api/d/a/libs/coffee-script-113.js'], function() {
  var compileToJS;
  compileToJS = function(source) {
    var compiledJS;
    compiledJS = null;
    try {
      return [
        true, CoffeeScript.compile(source, {
          bare: true
        })
      ];
    } catch (error) {
      return [false, error.message];
    }
  };
  return {
    compileToJS: compileToJS
  };
});
