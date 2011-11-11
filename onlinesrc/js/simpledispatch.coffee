# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['js/utils.js', 'pages/mapping.js'], (jvu, pagemap) ->
	
	checkIsAdmin = (nextLevel) ->
		doCheck = (opts, onContinue) ->
			jvu.doJsonApiPOST 'admin/isAdmin',
				success: (data) ->
					if data.success then return onContinue nextLevel
					jv.appendNotFoundMessage = '<div>Maybe you need to login?</div>'
					return onContinue null
	
	init = (opts) -> # opts.dname is the domain we are on.
		url = window.location.pathname
		load = (modname) -> jv.getModule modname, (a) -> a.init({url})
		rootmap = pagemap.getMapping opts.dname, {checkIsAdmin}
		if url == '/' then return load rootmap.index
		mm = rootmap
		spl = url.split('/')
		processRec = (mm, curSplPos) ->
			if !mm then return load rootmap.notfound
			if 'function' == typeof mm then	return mm {url}, (res) -> processRec res, curSplPos
			if 'string' == typeof mm then return load mm
			next = spl[curSplPos]
			if !next then next = 'index' # default is 'index'
			processRec mm[next], curSplPos + 1
		processRec rootmap, 1 # ignore the '' before the first '/'
	return {init}

# should call from func
window.jv.doDispatch = (opts) -> jv.mainPageOpts = opts; jv.getModule 'js/simpledispatch.js', (a) -> a.init(opts)
