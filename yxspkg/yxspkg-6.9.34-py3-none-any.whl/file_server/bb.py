import base64
f = '/media/yxs/Blacksong/mpxs/web/photo/album/黑丝/jquery.min.js'
k = base64.b64encode(open(f,'rb').read())
print(k)