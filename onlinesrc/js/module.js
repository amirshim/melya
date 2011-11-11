
if (typeof jv === "undefined" || jv === null) jv = {};

(function() {
  var defaultJsVer, getModuleNotYetCalled, moduleLoadVerReg, modules;
  defaultJsVer = '$$jv:ver$$';
  moduleLoadVerReg = {};
  if (jv.getModule) return;
  jv.startLoadTime = '';
  if (!jv.log) {
    if (window.console) {
      jv.log = function(a) {
        return console.log(a);
      };
    } else {
      jv.log = function() {};
    }
  }
  modules = {};
  getModuleNotYetCalled = true;
  jv.getModule = function(moduleName, onReady) {
    var doExecModuleAndReady, index, mm, temp, x, _fn, _len, _ref, _ref2;
    getModuleNotYetCalled = false;
    if (moduleName.charAt(0) === '^') {
      $LAB.script(moduleName.substring(1)).wait(function() {
        return onReady(null);
      });
      return;
    }
    if (!(moduleName in modules)) {
      modules[moduleName] = {
        state: 1,
        pendingOnReady: onReady,
        intVersion: -1
      };
      if (+jv.mainPageOpts.loadVer === -1) {
        $LAB.script("/api/d/z/" + moduleName + jv.startLoadTime);
      } else {
        if (moduleName in moduleLoadVerReg) {
          $LAB.script("/api/d/a" + moduleLoadVerReg[moduleName] + "/" + moduleName);
        } else {
          $LAB.script("/api/d/a" + (((_ref = jv.mainPageOpts) != null ? _ref.fver : void 0) || defaultJsVer) + "/" + moduleName);
        }
      }
      return;
    }
    mm = modules[moduleName];
    if (mm.state === 5) onReady(mm.theModule);
    if (mm.pendingOnReady) {
      temp = mm.pendingOnReady;
      mm.pendingOnReady = function(aa) {
        temp(aa);
        return onReady(aa);
      };
    } else {
      mm.pendingOnReady = onReady;
    }
    if (mm.state !== 2) return;
    if (+jv.mainPageOpts.loadVer === -1) {
      if (mm.isInline) {
        mm.isInline = false;
        mm.state = 1;
        mm.intVersion = -1;
        $LAB.script("/api/d/z/" + moduleName + jv.startLoadTime);
        return;
      }
    }
    doExecModuleAndReady = function() {
      var _ref2;
      mm.state = 4;
      mm.theModule = mm.loadFunc.apply(mm, mm.loadedDeps);
      if ((_ref2 = mm.theModule) != null ? _ref2.jvDeferModuleLoading : void 0) {
        mm.theModule.jvDeferModuleLoading(function() {
          delete mm.theModule.jvDeferModuleLoading;
          mm.state = 5;
          return mm.pendingOnReady(mm.theModule);
        });
        return;
      }
      mm.state = 5;
      return mm.pendingOnReady(mm.theModule);
    };
    mm.state = 3;
    if (mm.moduleDeps && mm.moduleDeps.length > 0) {
      mm.leftToLoad = mm.moduleDeps.length;
      mm.loadedDeps = [];
      _ref2 = mm.moduleDeps;
      _fn = function(x, index) {
        return jv.getModule(x, function(aa) {
          mm.loadedDeps[index] = aa;
          mm.leftToLoad--;
          if (mm.leftToLoad === 0) return doExecModuleAndReady();
        });
      };
      for (index = 0, _len = _ref2.length; index < _len; index++) {
        x = _ref2[index];
        _fn(x, index);
      }
    } else {
      mm.loadedDeps = [];
      doExecModuleAndReady();
    }
  };
  jv.defModule = function(moduleName, intVersion, moduleDeps, loadFunc) {
    var mm, overrideInline;
    overrideInline = (typeof intVersion === 'string') && intVersion.length > 0 && intVersion.substr(0, 1) === '+';
    intVersion = +intVersion;
    if (moduleName in modules) {
      mm = modules[moduleName];
      if (mm.state > 2) {
        if (mm.intVersion === intVersion) {
          jv.log('Module redefined after use: for same version, ignoring');
        } else if (mm.intVersion < intVersion) {
          jv.log('Module redefined after use: newer version... could be a problem');
        } else {
          jv.log('Module redefined after use: older version... probably fine... older version ignored');
        }
        return;
      }
      if (mm.intVersion >= intVersion) {
        jv.log('Module redefined before use: old or same version... ignoring');
        return;
      }
      if (mm.intVersion > -1) {
        jv.log("Module redefined before use: newer version... replacing");
      }
    } else {
      mm = {};
    }
    mm.state = 2;
    mm.intVersion = intVersion;
    mm.moduleDeps = moduleDeps;
    mm.loadFunc = loadFunc;
    mm.theModule = null;
    mm.isInline = getModuleNotYetCalled && !overrideInline;
    modules[moduleName] = mm;
    if (mm.pendingOnReady) return jv.getModule(moduleName, function() {});
  };
  return jv.regModVer = function(moduleName, loadVer) {
    return moduleLoadVerReg[moduleName] = loadVer;
  };
})();

jv.defModule('jquery', '+170', ['^http://ajax.googleapis.com/ajax/libs/jquery/1.7.0/jquery.min.js'], function() {
  return jQuery;
});
