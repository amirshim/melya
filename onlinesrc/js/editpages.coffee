# Melya Framework for Google App Engine
# (c) 2011 Amir Shimoni
# Melya may be freely distributed under the MIT license.

jv.defModule '$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], ($, jvu) ->
	urls = {}
	urls.knockout130beta = '/api/d/a/libs/knockout-1.3.0beta.js'
	urls.jquerytmpl = '/api/d/a/libs/jquery.tmpl100pre.min.js'
	urls.jqueryUIjs = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js'
	urls.jqueryUIcss = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/smoothness/jquery-ui.css'
	urls.jqueryTools = 'http://cdn.jquerytools.org/1.2.6/full/jquery.tools.min.js'
	
	
	theTemplates = """
	<script id="deTemplate" type="text/html">
	<table>
      <thead>
        <tr>
            <th>ID</th>
            <th>Which domain</th>
            <th>Regex for page</th>
            <th>File to show</th>
            <th>Match Order</th>
        </tr>
     </thead>    

	<tbody data-bind="foreach: entities">
	<tr>
		<td><span data-bind="text: key" /></td>
		<td><input data-bind="value: domainName, valueUpdate: 'afterkeydown'" /></td>
    	<td><input data-bind="value: regex, valueUpdate: 'afterkeydown'" /></td>
    	<td><input data-bind="value: fileName, valueUpdate: 'afterkeydown'" /></td>
    	<td><input data-bind="value: flags, valueUpdate: 'afterkeydown'" /></td>
    	<td><input data-bind="value: order, valueUpdate: 'afterkeydown'" /></td>
    	<td style="width:70px;"><a data-bind="visible: _changed" class="save-row" href="#">Save</a> &nbsp; </td>
    	<td style="width:70px;"><a data-bind="visible: _canDelete" class="delete-row" href="#">Delete</a> &nbsp; </td>
    	<td style="width:70px;"><a target="_blank" data-bind="visible: _editUrl, attr: { href: _editUrl }">Edit Page</a> &nbsp; </td>
    	<td><span data-bind="text: _currentMessage" /></td>
	</tr>
	</tbody>
	</table>
    <br/>
    <a href="#" class="add-row">Add Row</a>
    </script>
	"""
	
	yesNoDialog = $ """
<div id="dialog-confirm" title="Are you sure?">
	<p><span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 20px 0;"></span>Are you sure?</p>
</div>
	"""
	
	# data-bind="click: function() { viewModel.removeDomain(dm) }"
	
	#setupCss = ->
	#	jvu.addCssRule '.modal', """background-color:#fff;display:none;width:350px;padding:15px;text-align:left;border:2px solid #333;
	#		opacity:0.8;-moz-border-radius:6px;-webkit-border-radius:6px;-moz-box-shadow: 0 0 50px #ccc;-webkit-box-shadow: 0 0 50px #ccc;"""
	#	jvu.addCssRule '.modal h2', """margin:0px;padding:10px 0 10px 45px;border-bottom:1px solid #333;font-size:20px;"""
	
	showYesNoDialog = (text, okCB) ->
		$( "#dialog-confirm" ).attr 'title', text
		$( "#dialog-confirm" ).dialog
			resizable: false
			height:240
			modal: true
			buttons:
				Yes: -> $(this).dialog( "close" ); okCB()
				Cancel: -> $(this).dialog( "close" )
	
	onReady = (inputEntities) ->
		#setupCss()
		bb = $ 'body'
		
		bb.empty()
			.append(theTemplates)
			.append("""<div data-bind='template: "deTemplate"'></div>""")
			.append yesNoDialog
			
		yesNoDialog.hide()
			
		viewModel = 
			entities: ko.observableArray()
			addEntity: (x) ->
				a = {}
				for y of x
					x[y] = '' + x[y] # convert to string - for order comparison
					a[y] = new ko.observable(x[y])
				a._origState = x
				a._currentMessage = new ko.observable '' # for messages like saving/deleting/etc...
				a._changed = new ko.dependentObservable ->
					return false if a._currentMessage() != ''
					for k, v of a._origState
						return true if v != a[k]() # if any field changed, show "Save"
					false
				a._canDelete = new ko.dependentObservable ->
					return false if a._currentMessage() != ''
					true
				a._editUrl = new ko.dependentObservable ->
					t = a.fileName()
					return null if not t || a._currentMessage() != ''
					return """/account/admin/editfile?filename=#{t}"""
				
				viewModel.entities.push a
			sort: -> @entities.sort (a , b) -> +a.order() - +b.order()
			
		for x in inputEntities
			viewModel.addEntity x

		#addDomain: -> viewModel.contacts.push({ firstName: "", lastName: "", phones: [] });
		viewModel.sort()
		ko.applyBindings viewModel

		bb.on 'click', 'a.save-row', ->
			temp = $(this).parent()
			aa = ko.dataFor(this)
			aa._currentMessage('Saving...')
			jvu.doJsonApiPOST 'admin/SavePage',
				data: {jsonobj: ko.toJSON(aa)}
				success: (data) ->
					aa._currentMessage('')
					jvu.doJsonApiPOST 'admin/GetPageList',
						data: {key: data.pageKey}
						success: (data) ->
							viewModel.entities.remove aa
							viewModel.addEntity data.pages[0] # should return only one when quering by key
							viewModel.sort()
			


		bb.on 'click', 'a.delete-row', ->
			temp = $(this).parent()
			aa = ko.dataFor(this)
			showYesNoDialog 'Delete this page?', ->
				aa._currentMessage('Deleting...')
				jvu.doJsonApiPOST 'admin/DeletePage',
					data: {key: aa.key()}
					success: (data) ->
						aa._currentMessage('')
						viewModel.entities.remove aa
			false

		$('a.add-row').click ->
			viewModel.addEntity {"regex":'',"domainName":"","fileName":"","key":'',"dateUpdated":null,"flags":"", "order":1}
			false


	init = -> $ -> 
		jvu.loadCss '/api/d/a/css/reset.css'
		jvu.loadCss(urls.jqueryUIcss)
		$LAB.script([urls.knockout130beta, urls.jquerytmpl, urls.jqueryUIjs, urls.jqueryTools]).wait ->
			jvu.doJsonApiPOST 'admin/GetPageList',
				success: (data) -> 
					jvu.waitCss $("body"), 'ui-helper-hidden', -> # wait for jqueryUI css to load
						onReady data.pages

	return {init}