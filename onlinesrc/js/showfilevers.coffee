# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], ($, jvu) ->
	
	initCssRules = ->
		jvu.addCssRule '.jvisdeletemode', 'background-color:pink;'
		jvu.addCssRule '.jvisheadver', 'background-color:red;'
		jvu.addCssRule '.jvafterheadver', 'background-color:yellow;'
		jvu.addCssRule '.jvthefilename', 'width: 200px;display:inline-block;'
		
		jvu.addCssRule '.jvleftsp5', 'margin-left: 5px;'
		
		jvu.addCssRule '.bigandred', 'font-size: 40px; background-color:  red;'
	
	messageDiv = $ '<div/>'

	setFileVersionTag = (opts, cb) ->
		# http://www.albumpl.us/api/v2/setFileVersionTag?filename=js/ace20.js&ver=108&addtag=a
		# or deltag
		jvu.doJsonApiPOST 'admin/setFileVersionTag',
			data: opts
			success: (data) ->
				if data.success then return cb(data)
				$("body").append('<div>problem: ' + (data.text || 'unknown') + '</div>')
	
	init = -> $ ->
		initCssRules()
		mainDiv = $ '<div/>'
		$('body').empty().append mainDiv
		
		mainDiv.append 'Loading...'
		
		isCurrentlyDeleteMode = false
		
		doRealDelete = (filename, ver, theVerEl, onComplete) ->
			setFileVersionTag {filename, ver, delversion:ver}, (data) ->
				theVerEl.remove()
				if data.text
					$("body").append('<div>Delete text: ' + (data.text || 'unknown') + '</div>')
				if onComplete
					onComplete()
					
					
		mainDiv.on 'click', 'a.invalidateFileBuilds', ->
			jvu.doJsonApiPOST 'admin/invalidateFileBuilds',
				success: (data) ->
					if data.success
						messageDiv.removeClass 'bigandred'
						alert 'Successfully invalidated all file builds. Current file version is ' + data.fileVer
					else
						alert 'Failed to invalidate file builds!'
			false
					
		
		mainDiv.on 'click', 'a.onversionclickable', ->
			theVerEl = $(this)
			filename = theVerEl.closest('div').data 'filename'
			ver = theVerEl.data 'ver'
			isHead = theVerEl.hasClass 'jvisheadver'
			
			if isCurrentlyDeleteMode
				doRealDelete filename, ver, theVerEl
				return false
			
			if isHead
				setFileVersionTag {filename, ver, deltag:'a'}, -> theVerEl.removeClass 'jvisheadver'
			else
				setFileVersionTag {filename, ver, addtag:'a'}, -> theVerEl.addClass 'jvisheadver'
				
			messageDiv.addClass 'bigandred'
			false
			
		rootef = '/account/admin/editfile' # '/dynsrv/z6/html/simpleeditor.html'
		
		jvu.doJsonApiPOST 'admin/getAllFileVersions',
			data: {}
			success: (data) ->
				mainDiv.empty()
				messageDiv.append 'Remember to <a class="invalidateFileBuilds" href="#">Invalidate the builds</a> after updating the head versions.'
				mainDiv.append messageDiv
				
				theFilters = $ '<div/>'
				mainDiv.append('<br/>').append(theFilters).append('<br/>').append('Click on the filename to edit that file. Click on the version number to toggle ' +
					'that version being tagged as a head version or not. Red means head version. We highlight version(s) after the last head version with yellow.')
				filterList = {}
				prefixList = {}
				
				if !data.success
					alert data.text || 'Error!'
					return
				toadd = []
				for x,y of data.files
					holder = $ '<div/>'
					vertext = $ '<span/>'
					lastHigh = null
					for z in y
						thelink = $ """<a class="onversionclickable jvleftsp5" href="#">#{z[0]}</a> """
						thelink.data 'ver', z[0]
						if 'a' in z
							thelink.addClass 'jvisheadver'
							lastHigh = thelink
						vertext.append thelink
					
					holder.append("""<a class="jvthefilename" target="_blank" href="#{rootef}?filename=#{x}">#{x}</a>""").append(vertext)
					if lastHigh
						lastHigh.nextAll().addClass 'jvafterheadver'
					else
						# if we don't have even one head version, then highlight all versions.
						vertext.find('.onversionclickable').addClass 'jvafterheadver'
					holder.data 'filename', x
					holder.data 'versions', y
					prefix = x.substring(0, x.lastIndexOf('/') + 1)
					if prefix && prefix != ''
						filterList[prefix] ?= []
						filterList[prefix].push holder
						
					toadd.push [x, holder]
					
					aa = x.lastIndexOf('.')
					if aa > -1
						tf = x.substring(aa)
						holder.data 'filter', tf
						filterList[tf] ?= []
						filterList[tf].push holder
				
				toadd.sort (a , b) -> if a[0] < b[0] then -1 else 1
					
				alljq = []
				for x in toadd
					mainDiv.append x[1]
					alljq.push x[1]
					
				filterList['all'] = alljq
				
				fillpart1 = $ '<div>Filter by type: </div>'
				fillpart2 = $ '<div>Filter by dir: </div>'
				theFilters.append fillpart1
				theFilters.append fillpart2
					
				for x,y of filterList
					do (y) ->
						fb = $ """<a class="jvleftsp5" href="#">#{x}</a>"""
						if jvu.endsWith x, '/'
							fillpart2.append fb
						else
							fillpart1.append fb
						fb.click ->
							for x in filterList['all']
								x.hide()
							for x in y
								x.show()
								
							false
							
				setupSpecialDelete = ->
					$('a.jvthefilename').click (e) ->
						if e.ctrlKey
							cld = $(this).closest('div')
							filename = cld.data 'filename'
							allv = $.makeArray(cld.find('a.onversionclickable'))
							headv = null
							lastver = 0
							todelete = []
							for x in allv
								if headv
									alert 'Head version is not the last one'
									return false
								xx = $(x)
								ver = +xx.text()
								
								if ver <= 0
									alert 'Bad version!'
									return false
									
								if ver <= lastver
									alert 'versions are not increasing'
									return false
									
								lastver = ver
									
								if xx.hasClass 'jvisheadver'
									if headv
										alert 'to many head versions'
										return false
									headv = ver
								else
									todelete.push ver
							
							if !headv
								alert 'no head version'
								return false
							if headv != lastver
								alert 'head version is not the last one'
								return false
							if todelete.length == 0
								alert 'nothing to delete'
								return false
								
							deleteNextAsync = ->
								nn = $ cld.find('a.onversionclickable').get(0)
								ver = +nn.text()
								if ver in todelete
									doRealDelete filename, ver, nn, -> deleteNextAsync()
								
							deleteNextAsync()
								
						false
							
				switchToDeleteMode = $ '<a href="#">Switch to DELETE mode</a>'
				switchToDeleteMode.click ->
					$('body').addClass 'jvisdeletemode'
					isCurrentlyDeleteMode = true
					setupSpecialDelete()
					false
				mainDiv.append('<br/>').append switchToDeleteMode
				mainDiv.append('<br/><br/><form method="POST" action="/api/admin/CreateAllFileZip"><input type=submit value="Create a zip file with all the files and all the versions"></form>')
					
		
		
	return {init}
