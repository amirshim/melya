# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv ?= {}
do ->
	defaultJsVer = '$$jv:ver$$'
	moduleLoadVerReg = {} # module version registry.
	return if jv.getModule
	jv.startLoadTime = '' # '?t=' + Math.floor(+new Date()/1000) # used if there is a problem with 'z' modules getting cached.
	
	if !jv.log
		if window.console
			jv.log = (a) -> console.log a
		else
			jv.log = ->
	modules = {}
	getModuleNotYetCalled = true
	
	
	jv.getModule = (moduleName, onReady) ->
		getModuleNotYetCalled = false
		if moduleName.charAt(0) == '^'
			$LAB.script(moduleName.substring(1)).wait -> onReady null
			return
		if moduleName not of modules
			# state 1 - not yet loaded - trying to load from network.
			modules[moduleName] = {state:1, pendingOnReady:onReady, intVersion:-1}
			if +jv.mainPageOpts.loadVer == -1 # TODO: support specific versions?
				$LAB.script """/api/d/z/#{moduleName}#{jv.startLoadTime}""" # load the newest version... disregard the cache with a time param?
			else # load head version (a)
				if moduleName of moduleLoadVerReg # someone set the version to load...
					$LAB.script """/api/d/a#{moduleLoadVerReg[moduleName]}/#{moduleName}"""
				else
					# if we have to load a file and we don't know the version, then use
					#   the fver set in jv.doDispatch({}) or the version of this file.
					$LAB.script """/api/d/a#{jv.mainPageOpts?.fver || defaultJsVer}/#{moduleName}"""
			return

		mm = modules[moduleName]
		
		if mm.state == 5 # if the module is ready, return it immediately
			onReady mm.theModule
			
		if mm.pendingOnReady
			temp = mm.pendingOnReady
			mm.pendingOnReady = (aa) -> temp(aa); onReady(aa)
		else
			mm.pendingOnReady = onReady
			
		if mm.state != 2 # if we are loading (execution stage or from network)... let it happen...
			return
			
		if +jv.mainPageOpts.loadVer == -1 # TODO: support specific versions?
			if mm.isInline
				# if the module was loaded inline - i.e. before any getModule call
				# and we are in dev mode, then reload the newest version
				mm.isInline = false
				mm.state = 1
				mm.intVersion = -1
				$LAB.script """/api/d/z/#{moduleName}#{jv.startLoadTime}""" # load the newest version... disregard the cache with a time param?
				return
				
			
		doExecModuleAndReady = ->
			mm.state = 4 # running init
			mm.theModule = mm.loadFunc(mm.loadedDeps...)
			if mm.theModule?.jvDeferModuleLoading
				mm.theModule.jvDeferModuleLoading ->
					delete mm.theModule.jvDeferModuleLoading
					mm.state = 5 # ready...
					mm.pendingOnReady mm.theModule
				return
			mm.state = 5 # ready...
			mm.pendingOnReady mm.theModule

		mm.state = 3 # loading deps...
		if mm.moduleDeps && mm.moduleDeps.length > 0
			mm.leftToLoad = mm.moduleDeps.length
			mm.loadedDeps = []
			for x, index in mm.moduleDeps
				do (x, index) ->
					jv.getModule x, (aa) ->
						mm.loadedDeps[index] = aa
						mm.leftToLoad--
						if mm.leftToLoad == 0
							doExecModuleAndReady()
		else
			mm.loadedDeps = []
			doExecModuleAndReady()
		return
		
	jv.defModule = (moduleName, intVersion, moduleDeps, loadFunc) ->
		overrideInline = (typeof intVersion == 'string') && intVersion.length > 0 && intVersion.substr(0,1) == '+'
		intVersion = +intVersion # convert to int
		if moduleName of modules
			mm = modules[moduleName]
			if mm.state > 2
				if mm.intVersion == intVersion
					jv.log 'Module redefined after use: for same version, ignoring'
				else if	mm.intVersion < intVersion
					jv.log 'Module redefined after use: newer version... could be a problem'
				else
					jv.log 'Module redefined after use: older version... probably fine... older version ignored'
				return
				
			if	mm.intVersion >= intVersion
				jv.log 'Module redefined before use: old or same version... ignoring'
				return
			if mm.intVersion > -1
				jv.log """Module redefined before use: newer version... replacing"""
		else
			mm = {}
		mm.state=2 # state 2 - not yet executed - but defined - can replace with newer version.
		mm.intVersion=intVersion
		mm.moduleDeps=moduleDeps
		mm.loadFunc=loadFunc
		mm.theModule = null
		mm.isInline = getModuleNotYetCalled && !overrideInline
		modules[moduleName] = mm

		# if we already have someone waiting for this module, force it to load...
		if mm.pendingOnReady
			jv.getModule moduleName, ->
				
	jv.regModVer = (moduleName, loadVer) -> # set which version of the module to load... for cache reasons.
		moduleLoadVerReg[moduleName] = loadVer

jv.defModule 'jquery', '+170', ['^http://ajax.googleapis.com/ajax/libs/jquery/1.7.0/jquery.min.js'], -> jQuery


