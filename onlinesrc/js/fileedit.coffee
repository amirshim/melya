# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/ace20.js', 'js/utils.js', 'js/coffeescript.js'], ($, ace, jvu, coffee) ->
	saveButton = null
	messageText = null
	filename = jvu.parsedUrlArgs['filename']
	filetype = 'text'
	if filename
		# TODO: clean this up...
		if jvu.endsWith filename, '.coffee'
			filetype='coffee'
		if jvu.endsWith filename, '.py'
			filetype='python'
		if jvu.endsWith filename, '.js'
			filetype='javascript'
		if jvu.endsWith filename, '.css'
			filetype='css'
		if jvu.endsWith filename, '.html'
			filetype='html'

	onSaveEditor = ->
		postSave = -> # in general don't do anything
		
		if jvu.endsWith filename, '.coffee'
			jsfilename = filename.substring(0, filename.length-7) + '.js'
			[success, result] = coffee.compileToJS ace.getText()
			if !success
				messageText.text 'Can\'t save. CoffeeScript Error: ' + result
				return
			postSave = (parentData) ->
				messageText.text 'Coffescript file saved, saving generated javascript'
				jvu.doJsonApiPOST 'admin/UploadFileHandler',
					data: {filename:jsfilename, content:result,generatedFromFile:parentData.filename,generatedFromVer:parentData.ver}
					success: (data) ->
						if !data.success
							messageText.text 'Problem saving generated javascript file: ' + jsfilename + ' ' + (data.text || '')
							return
						messageText.text 'Generated file "' + jsfilename + '" saved'

			
		jvu.doJsonApiPOST 'admin/UploadFileHandler',
			data: {filename, content:ace.getText()}
			success: (data) ->
				if !data.success
					messageText.text 'Problem saving file: ' + filename + ' ' + (data.text || '')
					return
				messageText.text 'File "' + filename + '" saved'
				postSave data
				
	createEmptyFile = (fn) ->
		messageText.text 'Creating "' + fn + '"'
		jvu.doJsonApiPOST 'admin/UploadFileHandler',
			data: {filename:fn, content:'', allowemptyfile:1}
			success: (data) ->
				if !data.success
					messageText.text 'Problem creating file: ' + fn + ' ' + (data.text || '')
					return
				messageText.text 'File "' + fn + '" created'
				window.location.reload()
		


	onEditorReady = ->
		#ace.resizeEditor()
		saveButton.click -> onSaveEditor(); false
		ace.setSaveKeyCB -> onSaveEditor()
		if not filename
			messageText.text 'No filename specified'
			return
		messageText.text 'Loading ' + filename + '...'
		jvu.doJsonApiPOST 'admin/getCleanFileContent',
			data: {filename}
			success: (data) ->
				if !data.success
					messageText.text 'File does NOT exist: ' + filename + ' ' + (data.text || '') + ' '
					ace.setText ''
					#createFileButton = $ '<a href="#">Create Empty File</a>'
					#messageText.append createFileButton
					#createFileButton.click -> createEmptyFile(filename); false
					
					return
				messageText.text ''
				ace.setText data.data


	init = ->
		$ ->
			bb = $ 'body'
			bb.empty() 
			jvu.loadCss '/api/d/a/css/reset.css'
			saveButton = $ '<a href="#">Save</a>'
			messageText = $ '<span/>'
			topBar = $ '<div></div>'
			space = ' '
			topBar.append(saveButton).append(space).append(messageText)
			bb.append topBar
			
			theRest = $ '<div style="position:relative;"/>'
			bb.append theRest
			onWindowResize = (forceResize=true) ->
				theRest.css 'height', ($(window).height() - 20) + 'px'
				theRest.css 'width', ($(window).width() - 20) + 'px'
				if forceResize
					ace.resizeEditor()
					
			onWindowResize false # resize for now...
				
			ace.createEditor theRest, filetype, ->
				onEditorReady()
				$(window).resize onWindowResize

	return {init}

			
