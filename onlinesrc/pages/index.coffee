# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], ($, jvu) ->
	init = -> $ ->
		jvu.loadCss '/api/d/a/css/reset.css'
		body = $ 'body'
		body.empty().append """
		Welcome to the Melya Framwork for Google App Engine.<br/>
		To get started, please visit <a href="https://github.com/amirshim/melya/wiki">the wiki</a>.
		"""
	return {init}