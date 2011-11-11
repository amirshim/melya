# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', [], ->
	# getMapping() is called by js/simpledispatch.coffee to resolve dynamic page loads.
	getMapping = (domainName, mapUtils) -> 
		# if you want to have different mapping for different domains, you can simply return 
		#   a different map depending on domainName
		# mapUtils contains utils for mapping... right now, there is only one.
		#   mapUtils.checkIsAdmin() is a function that makes any page lower
		#   than that level require admin access
		mapping = 
			index: 'pages/index.js' # the root page.
			notfound: 'js/pagenotfound.js'
			account:
				admin: mapUtils.checkIsAdmin
					index: 'js/adminindex.js'
					editdomains: 'js/editdomains.js'
					editpages: 'js/editpages.js'
					editfiles: 'js/showfilevers.js'
					editfile: 'js/fileedit.js'
					livepython: 'js/liveexecute.js'
					
		return mapping
					
	return {getMapping}