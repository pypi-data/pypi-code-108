import IPython.display
import time, json

class view(object):
    '''A class for constructing embedded iCn3D viewer in ipython notebooks.
       The results are completely static which means there is no need for there
       to be an active kernel but also that there is no communication between
       the javascript viewer and ipython.
    '''
    def __init__(self,width=640,height=480,query='',viewergrid=None,para={},command=''):
        '''Create a iCn3D view.
            width -- width in pixels of container
            height -- height in pixels of container
            query -- optional argument
            options -- optional options
            js -- url for iCn3D'''
        divid = "icn3dviewerUNIQUEID"
        warnid = "icn3dwarningUNIQUEID"
        self.uniqueid = None
        self.startjs = '''<div id="%s"  style="position: relative; width: %dpx; height: %dpx">
        <p id="%s" style="background-color:#ffcccc;color:black">You appear to be running in JupyterLab (or JavaScript failed to load for some other reason).  You need to install the extension: <br>
        <tt>jupyter labextension install jupyterlab_3dmol</tt></p>
        </div>\n''' % (divid,width,height,warnid)
        self.startjs += '<script>\n'
        self.endjs = '</script>'
        
        self.updatejs = '' # code added since last show
        #load 3dmol, but only once, can't use jquery :-(
        #https://medium.com/@vschroeder/javascript-how-to-execute-code-from-an-asynchronously-loaded-script-although-when-it-is-not-bebcbd6da5ea
        self.startjs += """
var loadScriptAsync = function(uri){
  return new Promise((resolve, reject) => {
    var tag = document.createElement('script');
    tag.src = uri;
    //tag.async = true;
    tag.onload = () => {
      resolve();
    };
  var firstScriptTag = document.getElementsByTagName('link')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
  });
};

var loadCssAsync = function(uri){
  return new Promise((resolve, reject) => {
var tag = document.createElement('link');
tag.rel = 'stylesheet';
tag.href = uri;
//tag.async = true;
tag.onload = () => {
  resolve();
};
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
  });
};

if(typeof js1 === 'undefined') {
  js1 = loadScriptAsync('https://www.ncbi.nlm.nih.gov/Structure/icn3d/lib/jquery_es5.min.js');
  js2 = loadScriptAsync('https://www.ncbi.nlm.nih.gov/Structure/icn3d/lib/jquery-ui_es5.min.js');
  js3 = loadScriptAsync('https://www.ncbi.nlm.nih.gov/Structure/icn3d/lib/three_es5.min.js');
  js4 = loadScriptAsync('https://www.ncbi.nlm.nih.gov/Structure/icn3d/icn3d_full_ui.min.js');
  
  css1 = loadCssAsync('https://www.ncbi.nlm.nih.gov/Structure/icn3d/lib/jquery-ui.min.css');
  css2 = loadCssAsync('https://www.ncbi.nlm.nih.gov/Structure/icn3d/icn3d_full_ui.css');
}

var viewerUNIQUEID = null;
var warn = document.getElementById("%s");
if(warn) {
    warn.parentNode.removeChild(warn);
}

css1
.then(function() { return css2; })
.then(function() { return js4; })
.then(function() { return js3; })
.then(function() { return js2; })
.then(function() { return js1; })
.then(function() {
""" % (warnid)

        self.endjs = "});\n" + self.endjs
        self.viewergrid = None
        
        queryArray = query.split(":")

        self.startjs += 'cfg = {divid: "%s", "%s": "%s", width: "%spx", height: "%spx", mobilemenu: 1};\n' % (divid, queryArray[0], queryArray[1], width, height)

        self.startjs += 'viewerUNIQUEID = new iCn3DUI(cfg);\n'
        
        self.endjs = "viewerUNIQUEID.show3DStructure();\n" + self.endjs;
        
    def _make_html(self):
        self.uniqueid = str(time.time()).replace('.','')
        self.updatejs = ''
        html = (self.startjs+self.endjs).replace('UNIQUEID',self.uniqueid)
        return html    

    def _repr_html_(self):
        html = self._make_html()
        return IPython.display.publish_display_data({'application/3dmoljs_load.v0':html, 'text/html': html})
