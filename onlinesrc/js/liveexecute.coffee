# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/ace20.js', 'js/utils.js'], ($, ace, jvu) ->

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


	setupCss = ->
		jvu.addCssRule 'body', 'padding:0; margin:0 0 0 50%; width:50%; min-height:100%; float:right;'
		jvu.addCssRule '#left_col', 'float:left; width:100%; margin-left:-100%;position:relative;'
		jvu.addCssRule '#right_col', 'position:relative;'

	rightc = null
	onEditorReady = ->
		onExecBut = $ '<a href="#">Execute</a>'
		rightc.append onExecBut
		onExecBut.click -> 
			$.post '/api/admin/DangerousExecutePythonCode', {code:ace.getText()}, (data) ->
				$('#result-ta').val data
			false
			
		rightc.append """<br/><textarea id="result-ta" style="position:absolute; bottom:0; left:0;right:0; top:20px;" />"""

	init = -> $ ->
		bb = $ 'body'
		bb.empty() 
		jvu.loadCss '/api/d/a/css/reset.css'
		setupCss()
		bb.append '<div id="left_col"></div><div id="right_col"></div>'
		leftc = $ '#left_col'
		rightc = $ '#right_col'
		
		onWindowResize = ->
			leftc.height $(window).height() + 'px'
			rightc.height $(window).height() + 'px'
			#ace.resizeEditor()
			
		onWindowResize()
		
		ace.createEditor leftc, 'python', ->
			onEditorReady()
			$(window).resize onWindowResize

	return {init}

			
