# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], ($, jvu) ->
	init = ->
		bb = $('body').empty()
		bb.append('Page not found')
		if jv.appendNotFoundMessage then bb.append jv.appendNotFoundMessage
	return {init}
