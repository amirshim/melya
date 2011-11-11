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
            <th>Name to pass to client</th>
            <th>Regex for domain</th>
            <th>Default Title</th>
            <th>Match Order</th>
        </tr>
     </thead>    

	<tbody data-bind="foreach: domains">
	<tr>
		<td><span data-bind="text: key" /></td>
		<td><input data-bind="value: name, valueUpdate: 'afterkeydown'" /></td>
    	<td><input data-bind="value: regex, valueUpdate: 'afterkeydown'" /></td>
    	<td><input data-bind="value: defaultTitle, valueUpdate: 'afterkeydown'" /></td>
    	<td><input data-bind="value: order, valueUpdate: 'afterkeydown'" /></td>
    	<!-- ko if: _canDelete --> 
    	<td><a class="delete-row" href="#">Delete</a> &nbsp; </td>
    	<!-- /ko -->
    	<!-- ko if: _changed --> 
    	<td><a class="save-row" href="#">Save</a></td>
    	<!-- /ko -->
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
	
	onReady = (ajaxDomains) ->
		#setupCss()
		bb = $ 'body'
		
		bb.empty()
			.append(theTemplates)
			.append("""<div data-bind='template: "deTemplate"'></div>""")
			.append yesNoDialog
			
		yesNoDialog.hide()
			
		viewModel = 
			domains: ko.observableArray()
			addDomain: (x) ->
				a = {}
				for y of x
					x[y] = '' + x[y] # convert to string
					a[y] = new ko.observable(x[y])
				a._origState = x
				a._changed = new ko.dependentObservable ->
					for k, v of a._origState
						return true if v != a[k]() # if any field changed, show "Save"
					false
				a._canDelete = new ko.dependentObservable ->
					true
				viewModel.domains.push a
				
			sort: -> @domains.sort (a , b) -> +a.order() - +b.order()
			
		for x in ajaxDomains
			viewModel.addDomain x

		#addDomain: -> viewModel.contacts.push({ firstName: "", lastName: "", phones: [] });
		doSort = ->
		viewModel.sort()
		ko.applyBindings viewModel

		bb.on 'click', 'a.save-row', ->
			temp = $(this).parent()
			aa = ko.dataFor(this)
			$(temp).empty().append('Saving...') # this is wrong, but for now...
			jvu.doJsonApiPOST 'admin/SaveDomain',
				data: {jsonobj: ko.toJSON(aa)}
				success: (data) ->
					jvu.doJsonApiPOST 'admin/GetDomainList',
						data: {key: data.domainKey}
						success: (data) ->
							viewModel.domains.remove aa
							viewModel.addDomain data.domains[0]
							viewModel.sort()
			


		bb.on 'click', 'a.delete-row', ->
			temp = $(this).parent()
			aa = ko.dataFor(this)
			showYesNoDialog 'Delete this domain?', ->
				$(temp).empty().append('Deleting...') # this is wrong, but for now...
				jvu.doJsonApiPOST 'admin/DeleteDomain',
					data: {key: aa.key()}
					success: (data) ->
						viewModel.domains.remove aa
			false

		$('a.add-row').click ->
			viewModel.domains.push {"regex":"","name":"","defaultTitle":"","key":null,"dateUpdated":null,"order":1}
			false


	init = -> $ -> 
		jvu.loadCss '/api/d/a/css/reset.css'
		jvu.loadCss(urls.jqueryUIcss)
		$LAB.script([urls.knockout130beta, urls.jquerytmpl, urls.jqueryUIjs, urls.jqueryTools]).wait ->
			jvu.doJsonApiPOST 'admin/GetDomainList',
				success: (data) -> 
					jvu.waitCss $("body"), 'ui-helper-hidden', -> # wait for jqueryUI css to load
						onReady data.domains

	return {init}