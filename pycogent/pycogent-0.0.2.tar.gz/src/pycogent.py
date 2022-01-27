import h5py
import numpy as np

class Block4D:
    '''Block of the COGENT 4d grid, containting:
    X1ce, X2ce, X3ce, X4ce - grid at cell edges
    (indicies 1, 2, 3, 4 correspond to x, y, vpar, mu)
    i0, i1 - range of indicies along x
    j0, j1 - range of indicies along y
    l0, l1 - range of indicies along vpar
    k0, k1 - range of indicies along mu
    Fce - (extrapolated from cell centers!) data values at cell edges'''
    def __init__(self, X1ce, X2ce, X3ce, X4ce, i0, i1, j0, j1, k0, k1, l0, l1, Fce):
        self.X1ce = X1ce
        self.X2ce = X2ce
        self.X3ce = X3ce
        self.X4ce = X4ce
        self.i0 = i0
        self.i1 = i1
        self.j0 = j0
        self.j1 = j1
        self.k0 = k0
        self.k1 = k1
        self.l0 = l0
        self.l1 = l1
        self.Fce = Fce

class Cogent4D:
    '''Data from 4d.hdf5 output from COGENT
    block structure with Xce, X2ce, X3ce, X4ce, and Fce for each block
    time found in output file
    cell-edge grid (Xce and X2ce, X3ce, X4ce) for all blocks
    cell-center data (Fcc) for all blocks
    number of processors
    number of blocks
    number of ghost cells at each end in X
    number of ghost cells at each end in Y
    '''
    def __init__(self,X1ce, X2ce, X3ce, X4ce,
                 Fcc, numProcs, blocks, numGhostX, numGhostY, time):
        self.X1ce = X1ce
        self.X2ce = X2ce
        self.X3ce = X3ce
        self.X4ce = X4ce
        self.Fcc = Fcc
        self.numProcs = numProcs
        self.blocks = blocks
        self.numBlocks = len(blocks)
        self.numGhostX = numGhostX
        self.numGhostY = numGhostY
        self.time = time

def importData4D(fileName) -> Cogent4D:
    '''Import 4D data from single COGENT output file.
  
     Input is an address string to the HDF5 file.
     ex. 'simulation_folder/file.hdf5'
     
     Output is a Cogent4D object with data from HDF5 file:
     block structure with Xce, X2ce, X3ce, X4ce, and Fce for each block
     time found in output file
     cell-edge grid (Xce and X2ce, X3ce, X4ce) for all blocks
     cell-center data (Fcc) for all blocks
     number of processors
     number of blocks
     number of ghost cells at each end in X
     number of ghost cells at each end in Y
     '''
    thisFile = h5py.File(fileName, 'r')

    #normalized time:
    time = thisFile['level_0'].attrs['time']

    #ranges of indexes on phase grid cuboid:
    prob_domain = np.array(thisFile['level_0'].attrs['prob_domain'])

    ghost = np.array(thisFile['level_0']['data_attributes'].attrs['ghost'])

    nx1  = prob_domain['hi_i']-prob_domain['lo_i']+1
    nx2 = prob_domain['hi_j']-prob_domain['lo_j']+1
    nx3 = prob_domain['hi_k']-prob_domain['lo_k']+1
    nx4 = prob_domain['hi_l']-prob_domain['lo_l']+1

    procs=np.array(thisFile['level_0']['Processors'])
    numProcs = procs.size

    vecData  = np.array(thisFile['level_0']['data:datatype=0'])
    offsets  = np.array(thisFile['level_0']['data:offsets=0'])
    boxes    = np.array(thisFile['level_0']['boxes'])

    #initialize empty lists:
    lo_i, lo_j, lo_k, lo_l, hi_i, hi_j, hi_k, hi_l =[],[],[],[],[],[],[],[]

    for iP in np.arange(numProcs):
        lo_i.append(boxes[iP][0]-ghost['intvecti'])
        lo_j.append(boxes[iP][1]-ghost['intvectj'])
        lo_k.append(boxes[iP][2]-ghost['intvectk'])
        lo_l.append(boxes[iP][3]-ghost['intvectl'])
        hi_i.append(boxes[iP][4]+ghost['intvecti'])
        hi_j.append(boxes[iP][5]+ghost['intvectj'])
        hi_k.append(boxes[iP][6]+ghost['intvectk'])
        hi_l.append(boxes[iP][7]+ghost['intvectl'])

    #some indices are negative, make positive:
    hi_i += -np.min(lo_i)
    lo_i += -np.min(lo_i)
    hi_j += -np.min(lo_j)
    lo_j += -np.min(lo_j)
    hi_k += -np.min(lo_k)
    lo_k += -np.min(lo_k)
    hi_l += -np.min(lo_l)
    lo_l += -np.min(lo_l)

    thisFileMap = h5py.File(fileName[0:-5]+'.map.hdf5')
    vecMap = np.array(thisFileMap['level_0']['data:datatype=0'])
    offsetsMap = np.array(thisFileMap['level_0']['data:offsets=0'])
    boxesMap = np.array(thisFileMap['level_0']['boxes'])

    #initialize empty lists:
    lo_i_Map, lo_j_Map, lo_k_Map, lo_l_Map = [],[],[],[]
    hi_i_Map, hi_j_Map, hi_k_Map, hi_l_Map = [],[],[],[]

    for iP in np.arange(numProcs):
        lo_i_Map.append(boxesMap[iP][0]-ghost['intvecti'])
        lo_j_Map.append(boxesMap[iP][1]-ghost['intvectj'])
        lo_k_Map.append(boxesMap[iP][2]-ghost['intvectk'])
        lo_l_Map.append(boxesMap[iP][3]-ghost['intvectl'])
        hi_i_Map.append(boxesMap[iP][4]+ghost['intvecti'])
        hi_j_Map.append(boxesMap[iP][5]+ghost['intvectj'])
        hi_k_Map.append(boxesMap[iP][6]+ghost['intvectk'])
        hi_l_Map.append(boxesMap[iP][7]+ghost['intvectl'])

    #some indices are negative, make positive:
    hi_i_Map += -np.min(lo_i_Map)
    lo_i_Map += -np.min(lo_i_Map)
    hi_j_Map += -np.min(lo_j_Map)
    lo_j_Map += -np.min(lo_j_Map)
    hi_k_Map += -np.min(lo_k_Map)
    lo_k_Map += -np.min(lo_k_Map)
    hi_l_Map += -np.min(lo_l_Map)
    lo_l_Map += -np.min(lo_l_Map)

    #Note that boxes and boxesMap are always the same, while
    #data is at the center and grid at cell-edges:

    #map to reshaped grid:
    X1  = np.zeros((nx1+1,nx2+1,nx3+1,nx4+1))  #at cell edge
    X2 = np.zeros((nx1+1,nx2+1,nx3+1,nx4+1))  #at cell edge
    X3 = np.zeros((nx1+1,nx2+1,nx3+1,nx4+1))  #at cell edge
    X4 = np.zeros((nx1+1,nx2+1,nx3+1,nx4+1))  #at cell edge

    data0cc = np.zeros((nx1, nx2, nx3, nx4)) #at cell center
    map0cc = np.zeros((nx1,nx2,nx3,nx4))     #at cell center

    for m in np.arange(numProcs):


        gridMap = vecMap[offsetsMap[m]:offsetsMap[m+1]]
        thisMapX1 = gridMap[0:gridMap.size//4]
        thisMapX2 = gridMap[gridMap.size//4:gridMap.size//2]
        thisMapX3 = gridMap[gridMap.size//2:3*gridMap.size//4]
        thisMapX4 = gridMap[3*gridMap.size//4:]

        #formulate grid at cell edges:
        i0 = lo_i_Map[m]
        i1 = hi_i_Map[m]+1
        nX1sub = i1-i0+1
        j0 = lo_j_Map[m]
        j1 = hi_j_Map[m]+1
        nX2sub = j1-j0+1
        k0 = lo_k_Map[m]
        k1 = hi_k_Map[m]+1
        nX3sub = k1-k0+1
        l0 = lo_l_Map[m]
        l1 = hi_l_Map[m]+1
        nX4sub = l1-l0+1
        X1[i0:i1+1,j0:j1+1,k0:k1+1,l0:l1+1] = np.reshape(thisMapX1,(nX1sub,nX2sub,nX3sub,nX4sub),order='F')
        X2[i0:i1+1,j0:j1+1,k0:k1+1,l0:l1+1] =np.reshape(thisMapX2,(nX1sub,nX2sub,nX3sub,nX4sub),order='F')
        X3[i0:i1+1,j0:j1+1,k0:k1+1,l0:l1+1] =np.reshape(thisMapX3,(nX1sub,nX2sub,nX3sub,nX4sub),order='F')
        X4[i0:i1+1,j0:j1+1,k0:k1+1,l0:l1+1] =np.reshape(thisMapX4,(nX1sub,nX2sub,nX3sub,nX4sub),order='F')

        #formulate function matrix on cell-center grid:
        i0data = offsets[m]
        i1data = offsets[m+1]
        i0 = lo_i[m]
        i1 = hi_i[m]
        nX1sub = i1-i0+1
        j0 = lo_j[m]
        j1 = hi_j[m]
        nX2sub = j1-j0+1
        k0 = lo_k[m]
        k1 = hi_k[m]
        nX3sub = k1-k0+1
        l0 = lo_l[m]
        l1 = hi_l[m]
        nX4sub = l1-l0+1
        data0cc[i0:i1+1,j0:j1+1,k0:k1+1,l0:l1+1] = np.reshape(vecData[i0data:i1data],
                                       (nX1sub,nX2sub,nX3sub,nX4sub),order='F')
        map0cc[i0:i1+1,j0:j1+1,k0:k1+1,l0:l1+1] = \
         np.ones(np.shape(data0cc[i0:i1+1,j0:j1+1,k0:k1+1,l0:l1+1]))

    #use binary map0cc to determine indicies for different blocks, 
    #and save each block to list:
    nx, ny, nvpar, nmu = data0cc.shape

    i0, j0, k0, l0 = [], [], [], []
    i1, j1, k1, l1 = [], [], [], []

    blocks = []
    for i in np.arange(nx, dtype = 'int32'):
        for j in np.arange(ny, dtype = 'int32'):
            if map0cc[i,j,0,0] == 1: #get lower index for thisBox
                i0.append(i)
                j0.append(j)
                k0.append(0)
                l0.append(0)

                for j2 in np.arange(j,ny, dtype = 'int32'): #get upper index for thisBox
                    if map0cc[i,j2,0,0] == 0:
                        j1.append(j2)
                        break
                    if j2 == ny-1:
                        j1.append(ny)
            
                for i2 in np.arange(i,nx,dtype='int32'):
                    if map0cc[i2,j,0,0] == 0:
                        i1.append(i2)
                        break
                    if i2 == nx-1:
                        i1.append(nx)

                k1.append(nvpar)
                l1.append(nmu)

                #zero out thisBox so don't find it twice:
                map0cc[i0[-1]:i1[-1],j0[-1]:j1[-1],k0[-1]:k1[-1],l0[-1]:l1[-1]] = \
                 np.zeros(np.shape(map0cc[i0[-1]:i1[-1],j0[-1]:j1[-1],k0[-1]:k1[-1],l0[-1]:l1[-1]]))

                #save grid and data for this block:
                nx1b = i1[-1]-i0[-1]
                nx2b = j1[-1]-j0[-1]
                nx3b = k1[-1]-k0[-1]
                nx4b = l1[-1]-l0[-1]

                #extend cell center data by one in each dimension
                #for compatability with cell edge grid:
                data0ce = np.zeros((nx1b+1,nx2b+1,nx3b+1,nx4b+1))
                data0ce[0:-1,0:-1,0:-1,0:-1] = \
                    data0cc[i0[-1]:i1[-1],j0[-1]:j1[-1],k0[-1]:k1[-1],l0[-1]:l1[-1]]
                data0ce[-1,:,:,:] = data0ce[-2,:,:,:]
                data0ce[:,-1,:,:] = data0ce[:,-2,:,:]
                data0ce[:,:,-1,:] = data0ce[:,:,-2,:]
                data0ce[:,:,:,-1] = data0ce[:,:,:,-2]

                blocks.append(Block4D(X1ce=X1,
                                      X2ce=X2,
                                      X3ce=X3,
                                      X4ce=X4,
                                      i0=i0[-1],
                                      i1=j1[-1],
                                      j0=j0[-1],
                                      j1=j1[-1],
                                      k0=k0[-1],
                                      k1=k1[-1],
                                      l0=l0[-1],
                                      l1=l1[-1],
                                      Fce=data0ce))

    #write data into the output structure:
    return Cogent4D(X1ce=X1,
            X2ce=X2,
            X3ce=X3,
            X4ce=X4,
            Fcc=data0cc,
            numProcs=numProcs,
            blocks=blocks,
            numGhostX=ghost['intvecti'],
            numGhostY=ghost['intvectj'],
            time=time)

class Block2D:
    '''Block of the COGENT 2d grid, containing:
    Xce, Yce - grid at cell edges
    i0, i1 - range of indicies along x
    j0, j1 - range of indicies along y
    Fce - (extrapolated from cell centers!) data values at cell edges'''
    def __init__(self, Xce, Yce, Fce, i0, i1, j0, j1):
        self.Xce = Xce
        self.Yce = Yce
        self.Fce = Fce
        self.i0 = i0
        self.i1 = i1
        self.j0 = j0
        self.j1 = j1

class Cogent2D:
    '''Data from 4d.hdf5 output from COGENT
    block structure with Xce, Yce, and Fce for each block
    time found in output file
    cell-edge grid (Xce Yce) for all blocks
    cell-center data (Fcc) for all blocks
    number of processors
    number of blocks
    number of ghost cells at each end in X
    number of ghost cells at each end in Y'''
    def __init__(self, Xce, Yce, Fcc, numProcs, 
                num_components, blocks, 
                numGhostX, numGhostY, time):
        self.Xce = Xce
        self.Yce = Yce
        self.Fcc = Fcc
        self.numProcs = numProcs
        self.num_components = num_components
        self.blocks = blocks
        self.numBlocks = len(blocks)
        self.numGhostX = numGhostX
        self.numGhostY = numGhostY
        self.time = time

def importData2D(fileName) -> Cogent2D:
    '''Import 2D data from single COGENT output file.
    
    Input is an address string to the HDF5 file.
    ex. 'simulation_folder/file.hdf5'
    
    Output is a Cogent2D object with data from HDF5 file:
    block structure with Xce, Yce, and Fce for each block
    time found in output file
    cell-edge grid (Xce Yce) for all blocks
    cell-center data (Fcc) for all blocks
    number of processors
    number of blocks
    number of ghost cells at each end in X
    number of ghost cells at each end in Y'''
    thisFile = h5py.File(fileName,'r')

    #normalized time
    time = thisFile['level_0'].attrs['time']

    #ranges of indexes on phase grid cuboid:
    prob_domain = np.array(thisFile['level_0'].attrs['prob_domain'])

    ghost = np.array(thisFile['level_0']['data_attributes'].attrs['ghost'])

    num_components = thisFile.attrs['num_components']

    nx = prob_domain['hi_i']-prob_domain['lo_i']+1
    ny = prob_domain['hi_j']-prob_domain['lo_j']+1

    procs=np.array(thisFile['level_0']['Processors'])
    numProcs = procs.size

    vecData  = np.array(thisFile['level_0']['data:datatype=0'])
    offsets  = np.array(thisFile['level_0']['data:offsets=0'])
    boxes    = np.array(thisFile['level_0']['boxes'])

    #initialize empty lists:
    lo_i, lo_j, hi_i, hi_j =[],[],[],[]

    for iP in np.arange(numProcs):
        lo_i.append(boxes[iP][0]-ghost['intvecti'])
        lo_j.append(boxes[iP][1]-ghost['intvectj'])
        hi_i.append(boxes[iP][2]+ghost['intvecti'])
        hi_j.append(boxes[iP][3]+ghost['intvectj'])

    #some indicies are negative, make positive:
    hi_i+= -np.min(lo_i)
    lo_i+= -np.min(lo_i)
    hi_j+= -np.min(lo_j)
    lo_j+= -np.min(lo_j)

    thisFileMap = h5py.File(fileName[0:-5]+'.map.hdf5')
    vecMap = np.array(thisFileMap['level_0']['data:datatype=0'])
    offsetsMap = np.array(thisFileMap['level_0']['data:offsets=0'])
    boxesMap = np.array(thisFileMap['level_0']['boxes'])

    #initialize empty lists:
    lo_i_Map, lo_j_Map, hi_i_Map, hi_j_Map = [], [], [], []

    for iP in np.arange(numProcs):
        lo_i_Map.append(boxesMap[iP][0]-ghost['intvecti'])
        lo_j_Map.append(boxesMap[iP][1]-ghost['intvectj'])
        hi_i_Map.append(boxesMap[iP][2]+ghost['intvecti'])
        hi_j_Map.append(boxesMap[iP][3]+ghost['intvectj'])

    #some indicies are negative, make positive:
    hi_i_Map+= -np.min(lo_i_Map)
    lo_i_Map+= -np.min(lo_i_Map)
    hi_j_Map+= -np.min(lo_j_Map)
    lo_j_Map+= -np.min(lo_j_Map)

    #Note that boxes and boxesMap are always the same, while
    #data is at the center and grid at cell-edges

    #map to reshaped grid:
    X  = np.zeros((nx+1,ny+1))  #at cell edge
    Y  = np.zeros((nx+1,ny+1))  #at cell edge

    data0cc = np.zeros((nx,ny,num_components))  #at cell center
    map0cc  = np.zeros((nx,ny))  #at cell center

    for m in np.arange(numProcs):
        gridMap = vecMap[offsetsMap[m]:offsetsMap[m+1]]
        thisMapX = gridMap[0:gridMap.size//2]
        thisMapY = gridMap[gridMap.size//2:]

        #formulate grid at cell edges:
        i0 = lo_i_Map[m]
        i1 = hi_i_Map[m]+1
        nXsub = i1-i0+1
        j0 = lo_j_Map[m]
        j1 = hi_j_Map[m]+1
        nYsub = j1-j0+1
        X[i0:i1+1,j0:j1+1] = np.reshape(thisMapX,(nXsub,nYsub),order='F')
        Y[i0:i1+1,j0:j1+1] = np.reshape(thisMapY,(nXsub,nYsub),order='F')
        
        #formulate function matrix on cell-center grid
        i0data = offsets[m]
        i1data = offsets[m+1]
        i0 = lo_i[m]
        i1 = hi_i[m]
        nXsub = i1-i0+1
        j0 = lo_j[m]
        j1 = hi_j[m]
        nYsub = j1-j0+1
        thisVecData = vecData[i0data:i1data]
        subSize = thisVecData.size/num_components
        for n in np.arange(num_components):
            nlow = int(n*subSize)
            nup = int((n+1)*subSize)
            thisVecData0 = thisVecData[nlow:nup]
            data0cc[i0:i1+1,j0:j1+1,n] = np.reshape(thisVecData0,(nXsub,nYsub),order='F')
        map0cc[i0:i1+1,j0:j1+1] = np.ones((nXsub,nYsub))

    #use binary maps to determine indicies for different blocks,
    #and save each block to list:
    nx, ny = data0cc.shape[0], data0cc.shape[1]

    i0, j0, i1, j1 = [], [], [], []
    blocks = []
    for i in np.arange(nx, dtype='int32'):
        for j in np.arange(ny, dtype='int32'):
            if map0cc[i,j] == 1:
                i0.append(i)
                j0.append(j)
                for j2 in np.arange(j, ny, dtype='int32'):
                    if map0cc[i,j2] == 0:
                        j1.append(j2)
                    if j2 == ny-1:
                        j1.append(ny)

                for i2 in np.arange(i, nx, dtype='int32'):
                    if map0cc[i2,j] == 0:
                        i1.append(i2)
                    if i2 == nx-1:
                        i1.append(nx)

                #zero out thisBox so don't find it twice:
                map0cc[i0[-1]:i1[-1],j0[-1]:j1[-1]] = \
                 np.zeros(np.shape(map0cc[i0[-1]:i1[-1],j0[-1]:j1[-1]]))

                #save grid and data for this block:
                nx = i1[-1]-i0[-1]
                ny = j1[-1]-j0[-1]
                
                #extend cc data by one in each dimension
                #for compatability with cell edge grid:
                data0ce = np.zeros((nx+1,ny+1,num_components))
                data0ce[0:-1,0:-1,:] = data0cc[i0[-1]:i1[-1],j0[-1]:j1[-1],:]
                data0ce[-1,:,:] = data0ce[-2,:,:]
                data0ce[:,-1,:] = data0ce[:,-2,:]

                blocks.append(Block2D(Xce = X[i0[-1]:i1[-1],j0[-1]:j1[-1]],
                                      Yce = Y[i0[-1]:i1[-1],j0[-1]:j1[-1]],
                                      Fce = data0ce,
                                      i0 = i0[-1],
                                      i1 = i1[-1],
                                      j0 = j0[-1],
                                      j1 = j1[-1]))

    #write data into the output structure:
    return Cogent2D(Xce = X,
                    Yce = Y,
                    Fcc = data0cc,
                    numProcs = numProcs,
                    num_components = num_components,
                    blocks = blocks,
                    numGhostX = ghost['intvecti'],
                    numGhostY = ghost['intvectj'],
                    time = time)

def parseInputDeck(fileName):
    '''Reads input deck line-by-line and
    turns it into a Python dictionary'''
    def dictFromKeys(keys, value):
        dictionary = nest = {}
        for key in keys[:-1]:
            nest[key] = {}
            nest = nest[key]
        nest[keys[-1]] = value
        return dictionary

    def isfloat(string):
        try:
            float(string)
            return True
        except:
            return False

    def parseStringToInputDeck(inputDeck, string):
        #remove comment from string
        string = string.split('#',1)[0]
        if string == '':
            return inputDeck

        keysString, valueString = string.split('=',1)

        keysString = keysString.replace(' ', '')
        if keysString == 'gksystem.magnetic_geometry_mapping':
            #edge case: gksystem.magnetic_geometry_mapping = "type"
            #and        gksystem.magnetic_geometry_mapping.type = ...
            #does not fit into the dictionary template, therefore
            #gksystem.magnetic_geometry_mapping = "type" will be
            #mapped to gksystem.magnetic_geometry_mapping.type = "type"
            keysString = 'gksystem.magnetic_geometry_mapping.type'

        keys = keysString.split('.')

        #parse value:
        valueString = valueString.strip()
        valueString = " ".join(valueString.split())
        if valueString == 'true':
            value = True
        elif valueString == 'false':
            value = False
        elif isfloat(valueString):
            value = float(valueString)
        elif valueString.count('"') == 2:
            value = valueString.strip('"') #quotated name
        #if more than 2 "'s, then list:
        elif valueString.count('"') > 0 & \
            valueString.count('"') % 2 == 0:
            value = [x for x in \
             valueString.replace(' ','').split('"') if x != '']
        elif all([isfloat(x) for x in valueString.split(' ')]):
            value = [float(x) for x in valueString.split(' ')]
        else:
            value = valueString #no parsing rule found

        d = inputDeck
        nest = inputDeck
        keyID = -1
        for key in keys:
            keyID +=1
            d = d.get(key, None)
            if d is None:
                if len(keys[keyID+1:]) == 0:
                    nest[key] = value
                else:
                    nest[key] = dictFromKeys(keys[keyID+1:],value)
                break
            else:
                nest = nest[key]

        return inputDeck

    file = open(fileName,'r')
    lines = file.readlines()
    file.close()
    inputDeck = {'unparsed original' : open(fileName,'r').read()}
    for line in lines:
        inputDeck = parseStringToInputDeck(inputDeck,line[:-1])
    return inputDeck

def addInputDeckToHDF5File(inputDeckFile, HDF5File):
    '''Read input deck from inputDeckFile and save it
    to attributes of HDF5file'''
    f = h5py.File(HDF5File, "r+")
    assert f.attrs.get('inputDeck',None) is None, \
     'This HDF5 file already stores an inputDeck.'
    f.attrs['inputDeck'] = open(inputDeckFile,'r').read()

def removeInputDeckFromHDF5File(HDF5File):
    '''Delets input deck from attributes of HDF5File'''
    f = h5py.File(HDF5File,"r+")
    assert f.attrs.get('inputDeck',None) is not None, \
     'This HDF5 file does not strore any inputDeck'
    f.attrs.pop('inputDeck',None)