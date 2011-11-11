# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], ($, jvu) ->
	publicFuncs = {}
	nextLabjs = $LAB
		.script('/api/z/ace20/ace.js').wait() # Make sure this gets loaded first
		.script('/api/z/ace20/theme-twilight.js')
		#.script('/contentz/1/ace20/mode-javascript.js')
		#.script('/contentz/1/ace20/mode-coffee.js')

	editor = null
	session = null
	renderer = null

	currentSaveFunc = -> #(env, args, request) ->
	
	createEditor = (containingDiv, filetype="text", onReady) ->
		if filetype != 'text'
			nextLabjs = nextLabjs.script('/api/z/ace20/mode-' + filetype + '.js')
		aceEditor = $ '<div id="aceEditor" style="margin:0;position:absolute;top:0;bottom:0;left:0;right:0;font-size:14px;"></div>'
		containingDiv.append aceEditor
		nextLabjs.wait ->
			editor = ace.edit("aceEditor")
			editor.setTheme("ace/theme/twilight")
			editor.setScrollSpeed(jvu.parsedUrlArgs.scrollspeed || 4);

			TheMode = require("ace/mode/" + filetype).Mode
			canon = require('pilot/canon');
			session = editor.getSession()
			renderer = editor.renderer
			session.setMode(new TheMode())
			session.setUseWrapMode(false)
			session.setUseSoftTabs(false)
			renderer.setShowPrintMargin(false)

			canon.addCommand
				name:'onSave'
				bindKey:
					win: 'Ctrl-S',
					mac: 'Command-S',
					sender: 'editor'
				exec: (env, args, request) -> currentSaveFunc(env, args, request)
				
			canon.removeCommand 'replace' # for now remove replace (ctrl-r)... can do replace all with ctrl-shift-r

			if onReady
				onReady(publicFuncs)
				
			return
			
		return
				
	setText = (text) ->
		session.setValue text

	getText = ->
		session.getValue()

	resizeEditor = ->
		editor.resize()

	# set the function to be called on ctrl-s
	setSaveKeyCB = (onSaveCB) ->
		if onSaveCB
			currentSaveFunc = onSaveCB
		else
			currentSaveFunc = ->

	publicFuncs = {createEditor,setText,getText,setSaveKeyCB, resizeEditor}
	publicFuncs
