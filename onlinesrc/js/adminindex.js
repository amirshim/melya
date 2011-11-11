
jv.defModule('$$jv:fn$$', '$$jv:ver$$', ['jquery', 'js/utils.js'], function($, jvu) {
  var init;
  init = function() {
    return $(function() {
      var body, updateVer, verDiv;
      document.title = 'Melya Admin Page';
      jvu.loadCss('/api/d/a/css/reset.css');
      jvu.addCssRule('.floatformleft form', 'float:left;');
      jvu.addCssRule('.clearboth', 'clear:both;');
      body = $('body');
      verDiv = $('<div/>');
      body.empty().append(verDiv);
      updateVer = function() {
        return jvu.doJsonApiPOST('admin/setCurrentSessionVer', {
          data: {
            getver: 1
          },
          success: function(data) {
            if (-1 === +data.version) {
              return verDiv.empty().append("Current using dev files (latest versions) <a class=\"switchfileversion\" data-destver=\"\" href=\"#\">Switch to head version</a>");
            } else {
              return verDiv.empty().append("Current using head files (marked with tag 'a') <a class=\"switchfileversion\" data-destver=\"-1\" href=\"#\">Switch to dev version</a>");
            }
          }
        });
      };
      updateVer();
      body.on('click', 'a.switchfileversion', function() {
        jvu.doJsonApiPOST('admin/setCurrentSessionVer', {
          data: {
            ver: $(this).attr('data-destver')
          },
          success: function() {
            return updateVer();
          }
        });
        return false;
      });
      body.on('click', 'a.execAdminPost', function() {
        jvu.doJsonApiPOST('admin/' + $(this).attr('data-aurl'), {
          success: function(data) {
            return alert(JSON.stringify(data));
          }
        });
        return false;
      });
      return body.append("<br/>\n<a href=\"/account/admin/editfiles\">Edit files and select head versions</a><br/>\n<a href=\"/account/admin/editpages\">Edit static pages on the site</a><br/>\n<a href=\"/account/admin/editdomains\">Edit domain list</a><br/>\n\n<br/>\n<a href=\"#\" class=\"execAdminPost\" data-aurl=\"invalidateFileBuilds\">Invalidate Builds</a><br/>\n<a href=\"#\" class=\"execAdminPost\" data-aurl=\"FlushAllMemcache\">Flush all memcache</a><br/>\n<a href=\"#\" class=\"execAdminPost\" data-aurl=\"clearAllBuildData\">Clear all file builds incase of problems</a><br/>\n\n<br/>\n\n\n<div class=\"\">   		\n<form method=\"POST\" action=\"/api/admin/CreateAllFileZip\"><input type=submit value=\"Create a zip file with all the files and all the versions\"></form>\n<form method=\"POST\" action=\"/api/admin/CreateBackupZipForTag?tag=z\"><input type=submit value=\"Create zip files with just the latest file vesions\"></form>\n<form method=\"POST\" action=\"/api/admin/CreateBackupZipForTag?tag=a\"><input type=submit value=\"Create zip files with just the head vesions\"></form>\n<form method=\"POST\" action=\"/api/admin/CreateBackupOfDomainAndPages\"><input type=submit value=\"Create a file (json) with all the current page domains in the datastore\"></form>\n</div>\n\n<div class=\"clearboth\" />\n\n<br/>\n<a href=\"/api/admin/logout\">Logout</a><br/><br/>\n\nUpload a file to the system:\n<form method='POST' enctype='multipart/form-data' action='/api/admin/UploadFileHandler'>\nFilename (e.g. \"pages/index.js\"): <input type=\"text\" name=\"filename\"><br>\n<input type=file name=\"content\"><br>\n<input type=submit value=\"Upload\">\n</form>");
    });
  };
  return {
    init: init
  };
});
