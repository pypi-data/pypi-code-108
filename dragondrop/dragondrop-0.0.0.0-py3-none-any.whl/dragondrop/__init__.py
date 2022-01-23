from IPython.display import display, HTML

def dragondrop(name):
    html = '''
<style>
  #drop_zone {
    border: 5px solid #0F0;
    width:  100%;
    height: 100px;
  }
  .content {
  position: absolute;
  left: 50%;
  top: 50%;
  -webkit-transform: translate(-50%, -50%);
  transform: translate(-50%, -50%);
  }
</style>
<div id="drop_zone" ondrop="dropHandler(event);" ondragover="dragOverHandler(event);">
  <div class="content">DRAG AN IMAGE</div>
</div>    
<script>
  function dragOverHandler(ev) {
    console.log('File(s) in drop zone');
  
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();
  }
  
  function _arrayBufferToBase64( buffer ) {
      var binary = '';
      var bytes = new Uint8Array( buffer );
      var len = bytes.byteLength;
      for (var i = 0; i < len; i++) {
          binary += String.fromCharCode( bytes[ i ] );
      }
      return window.btoa( binary );
  }
  
  async function dropHandler(ev) {
    console.log('File(s) dropped');
  
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();
  
    var contents;
  
    if (ev.dataTransfer.items) {
      // Use DataTransferItemList interface to access the file(s)
      for (var i = 0; i < ev.dataTransfer.items.length; i++) {
        // If dropped items aren't files, reject them
        if (ev.dataTransfer.items[i].kind === 'file') {
          var file = ev.dataTransfer.items[i].getAsFile();
          console.log('... file[' + i + '].name = ' + file.name);
          contents = await file.arrayBuffer();
        }
      }
    } 
    else {
       // Use DataTransfer interface to access the file(s)
      for (var i = 0; i < ev.dataTransfer.files.length; i++) {
          var file = ev.dataTransfer.items[i].getAsFile();      
         console.log('... file[' + i + '].name = ' + ev.dataTransfer.files[i].name);
          contents = await ev.dataTransfer.files[i].arrayBuffer();
       }
     }
  
     var base64String = _arrayBufferToBase64(contents);
  
   var kernel = IPython.notebook.kernel;
  
  kernel.execute("''' + name + ''' = Image.open(BytesIO(base64.b64decode('" + base64String + "')))");
  
}
</script>
'''
    display(HTML(html))
