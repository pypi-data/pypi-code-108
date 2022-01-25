import numpy as np
import h5py, sqlite3, os, sys, json

def getConstants(strDB):
    conn = sqlite3.connect(strDB)
    c=conn.cursor()
    c.execute('select jsConstants from tblConstants')
    res=c.fetchone()
    # r[0] is jsConstants
    CONSTANTS=json.loads(res[0])    
    conn.close()
    return(CONSTANTS)

def checkImageLocationTypes(targetFolder,strDB):
    types=['.h5','.klb']
    basename=os.path.basename(strDB)
    basename=os.path.splitext(basename)
    basename=basename[0]
    for t in types:
        target=os.path.join(targetFolder,basename+t)
        if os.path.exists(target):
            return(target)
    return False

def getImageFileName(strDB,CONSTANTS):
    # 1st check folder with .LEVER file
    target=os.path.dirname(strDB)
    leverFile=os.path.basename(strDB)
    imageFile=checkImageLocationTypes(target,strDB)
    if False!=imageFile:        
        return imageFile
    # 2nd check CONSTANTS.imageDir
    target=CONSTANTS['imageDir']
    imageFile=checkImageLocationTypes(target,strDB)
    if False!=imageFile:        
        return imageFile
    print(strDB+' :: image file not found',file=sys.stderr)
    # finally, check lever.json override
    # ACK todo
def readImage(strDB,time=0,channel=0):
    """ readImage
            strDB - full path to lever file
            CONSTANTS - from leverjs.readConstants()
            time - scalar
            channel - list of channels
    """
    CONSTANTS=getConstants(strDB)
    imageFile=getImageFileName(strDB,CONSTANTS)    
    with  h5py.File(imageFile, 'r') as f:
        fTarget=f['Images']['Original']
        im=fTarget[time,channel,:,:,:]
        # note t must be scalar, so axis order 
        # im is (c,z,y,x) - reverse axis order for (x,y,z,c)        
        im=np.transpose(im)    
    return (im,CONSTANTS)