# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery'], ($) ->
	jvu = ->
	jvu.delay = (ms, func) -> setTimeout func, ms # returns token than can be used by jvu.cancelDelay
	jvu.cancelDelay = (token) -> clearTimeout token # token is returned by jvu.delay

	jvu.execute_once = (func) ->
		is_exec = false
		return (a...) ->
			return if is_exec
			is_exec = true
			func(a...)

	jvu.parsedUrlArgs = do ->
		p = {}
		for x in (location.href.split('?')[1] || '').split('&') when x
			[a,b] = x.split('=')
			p[a] = b
		p

	jvu.startsWith = (str, find) -> find == str.substr 0, find.length # string str begins with find
	jvu.endsWith = (str, find) -> str.substr(-find.length) == find # string str ends with find?

	jvu.ifStartsWith = (str,find, cb) ->
			if jvu.startsWith str, find
				cb str.substr(find.length)
				true
			else
				false

	jvu.doJsonApiPOST = (apicommand, opts) ->
		$.ajax
			url:'/api/' + apicommand
			dataType:'json'
			type:'POST'
			data: opts.data
			success: opts.success
			error: opts.error || (e) ->	alert 'Error' if !jvu.isCurrentlyReloading

	jvu.loadCss = (csshref, linkid) ->
		if linkid
			$("head").append("""<link id="#{linkid}" />""")
		else
			$("head").append("""<link/>""")
		link_ref = $("head").children(":last")
		link_ref.attr
			rel:  "stylesheet"
			type: "text/css"
			href: csshref			

	jvu.waitCss = (visibleDiv, cssClass, onReady, maxWait=13000) ->
		# for jquery ui cssClass = 'ui-helper-hidden'
		tempspan = $ """<span class="#{cssClass}">&nbsp;</span>"""
		visibleDiv.append tempspan
		doCheck = ->
			if !tempspan.is(":visible")
				tempspan.remove()
				onReady(true)
				return true
			return false # try again.
		return if doCheck()
		multiCheck = (curDelay) ->
			if curDelay >= maxWait
				return onReady(false)
			jvu.delay curDelay, ->
				return if doCheck()
				multiCheck curDelay*2
			return

		#50 100 200 400 800 1.6 3.2 6.4 12.8 -> Sum = ~23?
		multiCheck 50
		return

	addRuleFunc = null
	jvu.addCssRule = (selector, rule) -> # custom css rules...
		if !addRuleFunc
			stylesheet = document.createElement("style")
			stylesheet.type = "text/css"
			#stylesheet.setAttribute("type", "text/css")
			document.getElementsByTagName("head")[0].appendChild(stylesheet)
			sheet = stylesheet.sheet || stylesheet.styleSheet
			if 'insertRule' of sheet 
				addRuleFunc = (sel, css) -> sheet.insertRule sel.concat('{' + css + '}'), 0
			else
				addRuleFunc = (sel, css) -> sheet.addRule sel, css, 0
				
		addRuleFunc selector, rule
				

	# the awesome webputty.net
	jvu.loadWebPuttyCss = (puttyKey) ->
		jvu.loadCss 'http://www.webputty.net/css/' + puttyKey, puttyKey
		if window.location != window.parent.location || window.location.search.indexOf('__preview_css__') > -1
			$LAB.script 'http://www.webputty.net/js/' + puttyKey

	return jvu
