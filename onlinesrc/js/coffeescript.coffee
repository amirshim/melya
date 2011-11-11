# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['^/api/d/a/libs/coffee-script-113.js'], ->
	compileToJS = (source) ->
		compiledJS = null
		try
			return [true, CoffeeScript.compile source, bare: on]
		catch error
			return [false, error.message]
	return {compileToJS}
