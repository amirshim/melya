# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], ($, jvu) ->
	init = -> $ ->
		document.title = 'Melya Admin Page'
		jvu.loadCss '/api/d/a/css/reset.css'
		jvu.addCssRule '.floatformleft form', 'float:left;'
		jvu.addCssRule '.clearboth', 'clear:both;'
		
		body = $ 'body'
		verDiv = $ '<div/>'
		body.empty().append(verDiv)
		updateVer = ->
			jvu.doJsonApiPOST 'admin/setCurrentSessionVer',
				data: {getver:1}
				success: (data) -> 
					if -1 == +data.version
						verDiv.empty().append """Current using dev files (latest versions) <a class="switchfileversion" data-destver="" href="#">Switch to head version</a>"""
					else
						verDiv.empty().append """Current using head files (marked with tag 'a') <a class="switchfileversion" data-destver="-1" href="#">Switch to dev version</a>"""
			
		updateVer()
		
		body.on 'click', 'a.switchfileversion', ->
			jvu.doJsonApiPOST 'admin/setCurrentSessionVer',
				data: {ver:$(@).attr('data-destver')}
				success: -> updateVer()
			false

		body.on 'click', 'a.execAdminPost', ->
			jvu.doJsonApiPOST 'admin/' + $(@).attr('data-aurl'),
				success: (data) -> alert JSON.stringify(data)
			false


		# other stuff.
		body.append """
		<br/>
		<a href="/account/admin/editfiles">Edit files and select head versions</a><br/>
		<a href="/account/admin/editpages">Edit static pages on the site</a><br/>
		<a href="/account/admin/editdomains">Edit domain list</a><br/>
		
		<br/>
		<a href="#" class="execAdminPost" data-aurl="invalidateFileBuilds">Invalidate Builds</a><br/>
		<a href="#" class="execAdminPost" data-aurl="FlushAllMemcache">Flush all memcache</a><br/>
		<a href="#" class="execAdminPost" data-aurl="clearAllBuildData">Clear all file builds incase of problems</a><br/>
		
		<br/>
		
		
		<div class="">   		
		<form method="POST" action="/api/admin/CreateAllFileZip"><input type=submit value="Create a zip file with all the files and all the versions"></form>
		<form method="POST" action="/api/admin/CreateBackupZipForTag?tag=z"><input type=submit value="Create zip files with just the latest file vesions"></form>
		<form method="POST" action="/api/admin/CreateBackupZipForTag?tag=a"><input type=submit value="Create zip files with just the head vesions"></form>
		<form method="POST" action="/api/admin/CreateBackupOfDomainAndPages"><input type=submit value="Create a file (json) with all the current page domains in the datastore"></form>
		</div>
		
		<div class="clearboth" />
		
		<br/>
		<a href="/api/admin/logout">Logout</a><br/><br/>
		
		Upload a file to the system:
		<form method='POST' enctype='multipart/form-data' action='/api/admin/UploadFileHandler'>
		Filename (e.g. "pages/index.js"): <input type="text" name="filename"><br>
		<input type=file name="content"><br>
		<input type=submit value="Upload">
		</form>
		"""
			
	
	return {init}