import numpy as np
from pathlib import Path
import re
import sys
import json

def read_plot3d_fmt(filename,sep=None):
    if isinstance(filename,str) or isinstance(filename,Path):
        fp = open(filename)
    else:
        fp = filename
        filename = fp.name
    n_block = fp.readline().strip()
    if n_block.isdigit():
        n_block = int(n_block)
        if sep is None:
            blocks = [fp.readline().strip().split() for _ in range(n_block)]
        else:
            blocks = [fp.readline().replace(sep,' ').strip().split() for _ in range(n_block)]
    else:
        if sep is None:
            blocks = [n_block.split(),]
        else:
            blocks = [n_block.replace(sep,' ').split(),]
        n_block = 1
    blocks = np.array(blocks,dtype='int')

    def multi_replace(pa):
        n,s = pa.group(0).split('*')
        f = (s+' ')*int(n)
        return f
    data = fp.read()
    if sep is not None:
        data = data.replace(sep,' ')
    if data.find(',')!=-1:
        data = data.replace(',',' ')
    if data.find('*')!=-1:
        data = re.sub('\d+\*\S+',multi_replace,data)
        n = data.find('*')
    data = np.array(data.split(),dtype='float64')
    a = 0
    for i,j,k in blocks:
        a+=i*j*k
    dimension = len(blocks[0])
    np_dim = data.size // a
    assert a*np_dim == data.size
    size0=0
    result = []
    for shape in blocks:
        if dimension==3:
            imax,jmax,kmax = shape
            size = imax*jmax*kmax*np_dim
        else:
            imax,jmax = shape
            size = imax*jmax*np_dim

        bl_data = data[size0:size0+size]
        size0 += size 
        if dimension == 3:
            bl_data.shape = (np_dim,kmax,jmax,imax)
            bl_data = bl_data.transpose((0,3,2,1))
            t = dict(zip('XYZ',bl_data))
        else:
            bl_data.shape = (np_dim,jmax,imax)
            bl_data = bl_data.swapaxes(2,1)
            t = dict(zip('XY',bl_data))
        if dimension != np_dim:
            # exists IBLANK
            t['IBLANK'] = bl_data[-1]
        result.append(t)
    return result
def write_plot3d_fmt(filename,data,fmt='%.15e'):
    '''
    data:list-like,element is a dict like {'X':...,'Y':...,'Z':...,'IBLANK':...}
    Z and IBLANK are optional
    '''
    # fp = open(filename,'w')
    if isinstance(filename,str) or isinstance(filename,Path):
        fp = open(filename,'w')
        is_fp = False
    else:
        fp = filename
        is_fp = True
        filename = fp.name

    IBLANK =False if not data[0].get('IBLANK',False) else True
    dimension =2 if data[0].get('Z',False) is False else 3

    if len(data) > 1:
        fp.write('{:5d}\n'.format(len(data)))
    for i in data:
        shape = i['X'].shape
        if dimension == 3:
            s_format = '  {} {} {}\n'
        else:
            s_format = '  {} {}\n'
        fp.write(s_format.format(*shape))

    for i in data:
        if IBLANK is not False:
            if dimension == 3:
                t = (i['X'],i['Y'],i['Z'],i['IBLANK'])
            else:
                t = (i['X'],i['Y'],i['IBLANK'])
        else:
            if dimension == 3:
                t = (i['X'],i['Y'],i['Z'])
            else:
                t = (i['X'],i['Y']) 
        t = np.stack(t)
        if dimension == 3:
            t_shape = (0,3,2,1)
        else:
            t_shape = (0,2,1)
        array = t.transpose(t_shape).reshape(-1,i['X'].shape[0])
        np.savetxt(fp,array,fmt = fmt)
    if not is_fp:
        fp.close()
    return
def read_plot3d_unfmt(filename,read_aux_data=False):
    float_type = {4:'float32',8:'float64'}
    int_type = {4:'int32',8:"int64"}
    if isinstance(filename,str) or isinstance(filename,Path):
        fp = open(filename,'rb')
    else:
        fp = filename
        filename = fp.name
    multiblock = np.frombuffer(fp.read(4), dtype = 'int32')[0]
    if multiblock==4:
        n_blocks = np.frombuffer(fp.read(8), dtype = 'int32')[0]
    else:
        n_blocks = 1
        fp.seek(0,0)

    k = np.frombuffer(fp.read(4), dtype= 'int32' )[0]
    blocks = np.frombuffer(fp.read(k), dtype = 'int32').reshape(n_blocks,-1)
    fp.read(4)
    dimension = (k // 4) // n_blocks

    result = []
    precision=None
    for shape in blocks:
        k = np.frombuffer(fp.read(4), dtype= 'int32' )[0]
        
        if dimension==3:
            imax,jmax,kmax = shape
            size = imax*jmax*kmax
        else:
            imax,jmax = shape
            size = imax*jmax
        if precision is None:
            precision = k //(size) //dimension 
            if precision ==4 or precision == 8:
                IBLANK = False 
                np_dim = dimension
            else:
                np_dim = dimension + 1
                precision = k //(size) //np_dim
                IBLANK = True
        if IBLANK:
            bl_data = np.frombuffer(fp.read(k),dtype = float_type[precision])
        else:
            bl_data = np.frombuffer(fp.read(k),dtype = float_type[precision])
        fp.read(4)
        if dimension == 3:
            bl_data.shape = (np_dim,kmax,jmax,imax)
            bl_data = bl_data.transpose((0,3,2,1))
            t = dict(zip('XYZ',bl_data))
        else:
            bl_data.shape = (np_dim,jmax,imax)
            bl_data = bl_data.swapaxes(2,1)
            t = dict(zip('XY',bl_data))
        if IBLANK:
            shape0 = bl_data[-1].shape
            t['IBLANK'] = np.frombuffer(bl_data[-1].copy().data,dtype='int32')
            t['IBLANK'].shape = shape0
        result.append(t)
    if read_aux_data:
        dict_str = fp.read().decode('utf8')
        return result,json.loads(dict_str)
    else:
        return result

def write_plot3d_unfmt(filename,data):
    '''
    data:list-like,element is a dict like {'X':...,'Y':...,'Z':...,'IBLANK':...}
    Z and IBLANK are optional
    '''
    # fp = open(filename,'wb')
    if isinstance(filename,str) or isinstance(filename,Path):
        fp = open(filename,'wb')
        is_fp = False
    else:
        fp = filename
        filename = fp.name
        is_fp = True
    k_array = np.array([4],dtype = 'int32')
    if len(data) > 1:
        k_array.tofile(fp)
        k_array[0] = len(data)
        k_array.tofile(fp)
        k_array[0]=4
        k_array.tofile(fp)
    shapes = [i['X'].shape for i in data]
    t = np.array(shapes,dtype='int32').flatten()
    k_array[0]=t.size*4
    k_array.tofile(fp)
    t.tofile(fp)
    k_array.tofile(fp)

    IBLANK = data[0].get('IBLANK',False)
    dimension = data[0].get('Z',False)
    if dimension is False:
        dimension = 2
    else:
        dimension = 3

    for i in data:
        if IBLANK is not False:
            if dimension == 3:
                t = (i['X'],i['Y'],i['Z'],i['IBLANK'])
            else:
                t = (i['X'],i['Y'],i['IBLANK'])
        else:
            if dimension == 3:
                t = (i['X'],i['Y'],i['Z'])
            else:
                t = (i['X'],i['Y']) 
        t = np.stack(t)
        if dimension == 3:
            t_shape = (0,3,2,1)
        else:
            t_shape = (0,2,1)
        array = t.transpose(t_shape).flatten()
        
        k_array[0] = array.size*array.itemsize
        k_array.tofile(fp)
        array.tofile(fp)
        k_array.tofile(fp)
    if not is_fp:
        fp.close()
    return

def read_a_fortran_write(fp):
    t = fp.read(4)
    if not t:
        return None
    k = np.frombuffer(t, dtype = 'int32')[0]
    t = fp.read(k)
    k2 = np.frombuffer(fp.read(4), dtype = 'int32')[0]
    assert k == k2 
    return t
def read_aux_data_qfile(fp):
    float_type = {4:'float32',8:'float64'}
    int_type   = {4:'int32',8:'int64'}
    float_int   = {'float':float_type,'int':int_type}
    s = read_a_fortran_write(fp)
    if not s:
        return None,None
    else:
        if s.find(b'#') == -1:
            fp.seek(-(len(s)+8),1)
            return None,None
        key,ktype=s.decode().split('#')
        n = np.frombuffer(read_a_fortran_write(fp), dtype = 'int32')[0]
        result = []
        var_type = float_int[ktype]
        for _ in range(n):
            s = read_a_fortran_write(fp)

            f = np.frombuffer(s, dtype = var_type[len(s)])[0]
            result.append(f)
        return  key,result
def read_plot3d_q_unfmt(filename,read_aux_data=False):
    float_type = {4:'float32',8:'float64'}
    if isinstance(filename,str) or isinstance(filename,Path):
        fp = open(filename,'rb')
    else:
        fp = filename
        filename = fp.name
    k = np.frombuffer(fp.read(4), dtype = 'int32')[0]
    if k==4:
        n_blocks = np.frombuffer(fp.read(8), dtype = 'int32')[0]
        k = np.frombuffer(fp.read(4), dtype= 'int32' )[0]
        blocks = np.frombuffer(fp.read(k), dtype = 'int32').reshape(n_blocks,-1)
        fp.read(4)
    else:
        n_blocks = 1
        blocks = np.frombuffer(fp.read(k), dtype = 'int32').reshape(n_blocks,-1)
        fp.read(4)
    dimension = len(blocks[0])
    parameters = None
    result = []
    qtype=None
    for shape in blocks:
        if dimension==3:
            imax,jmax,kmax = shape
            multi = imax*jmax*kmax
            parameters = 5
            standard_qfile = True
        elif dimension == 2:
            imax,jmax = shape
            multi = imax*jmax
            parameters = 4
            standard_qfile = True
        elif dimension == 4:
            imax,jmax,kmax,parameters = shape
            multi = imax*jmax*kmax
            standard_qfile = False

        k = np.frombuffer(fp.read(4), dtype= 'int32' )[0]

        if qtype is None:
            if standard_qfile:
                qtype = k//4
            else:
                qtype = k//(multi*parameters)
                assert k == multi*parameters*qtype
            qtype = float_type[qtype]
        
        if standard_qfile:
            t = np.frombuffer(fp.read(k), dtype= qtype)
        
            xmach, alpha, reue, time = t
            t = np.frombuffer(fp.read(4), dtype= 'int32' )[0]
          
            k = np.frombuffer(fp.read(4), dtype= 'int32' )[0]


        bl_data = np.frombuffer(fp.read(k),dtype = qtype)
        t = np.frombuffer(fp.read(4), dtype= 'int32' )
        assert t == k
        if dimension == 3 or dimension == 4:
            bl_data.shape = (parameters,kmax,jmax,imax)
            bl_data = bl_data.transpose((0,3,2,1))
        else:
            bl_data.shape = (parameters,jmax,imax)
            bl_data = bl_data.swapaxes(2,1)
        t = dict(enumerate(bl_data))
        if standard_qfile:
            t['mach'] = xmach
            t['alpha'] = alpha
            t['Re'] = reue 
            t['time'] = time
        result.append(t)
    # read_aux_data
    if read_aux_data:
        aux = dict()
        while True:
            key,val = read_aux_data_qfile(fp)
            if key:
                aux[key] = val 
            else: 
                break 
        return result,aux
    else:
        return result
def write_plot3d_q_unfmt(filename,data):
    if isinstance(filename,str) or isinstance(filename,Path):
        fp = open(filename,'wb')
    else:
        fp = filename
        filename = fp.name
    n_blocks = len(data)
    if data[0].get('time') is None:
        standard_qfile = False
        n_parameters = len(data[0])
    else:
        standard_qfile = True
        n_parameters = len(data[0]) - 4
    dimension = len(data[0][0].shape)
    if n_blocks > 1:
        k_array = np.array([4,n_blocks,4],dtype = 'int32')
        k_array.tofile(fp)
    shapes = np.array([i[0].shape for i in data])
    if not standard_qfile:
        pas = np.array([n_parameters]*n_blocks)
        shapes = np.hstack((shapes,pas[:,None])).flatten()
    else:
        shapes = shapes.flatten()
    k_array = np.array([4*shapes.size],dtype = 'int32')
    k_array.tofile(fp)
    shapes.astype('int32').tofile(fp)
    k_array.tofile(fp)
    if dimension == 3:
        t_shape = (0,3,2,1)
    else:
        t_shape = (0,2,1)
    data_type = None
    for block in data:
        t = block[0]
        if data_type is None:
            data_type = str(t.dtype)
        if standard_qfile:
            k_array = np.array([t.itemsize*4],dtype = 'int32')
            k_array.tofile(fp)
            np.array(
                [block[i] for i in ('mach', 'alpha', 'Re', 'time')],
                dtype = t.dtype
            ).tofile(fp)
            k_array.tofile(fp)
        size = t.size*n_parameters*t.itemsize
        k_array = np.array([size],dtype='int32')
        k_array.tofile(fp)
        bds = np.stack([block[i] for i in range(n_parameters)])
        array = bds.transpose(t_shape).flatten()
        if str(array.dtype) != data_type:
            array = array.astype(data_type)
        array.tofile(fp)
        k_array.tofile(fp)
 
def read(filename,**kargs):
    read_aux_data=kargs.get('read_aux_data',False)
    if isinstance(filename,str) or isinstance(filename,Path):
        p = Path(filename)
    else:
        p = Path(filename.name)
    if p.suffix.lower() in ['.fmt']:
        data = open(p,'r').read(1000)
        if data.find(',')!=-1:
            sep = ','
        else:
            sep = ' '
        return read_plot3d_fmt(filename,sep = sep)
    elif p.suffix.lower() == '.q':
        return read_plot3d_q_unfmt(filename,read_aux_data=read_aux_data)
    else:
        return read_plot3d_unfmt(filename,read_aux_data=read_aux_data)
def write(filename,data):
    if isinstance(filename,str) or isinstance(filename,Path):
        p = Path(filename)
    else:
        p = Path(filename.name)

    
    if p.suffix.lower() in ['.fmt']:
        return write_plot3d_fmt(filename,data)
    elif p.suffix.lower() == '.q':
        return write_plot3d_q_unfmt(filename,data)
    else:
        return write_plot3d_unfmt(filename,data)
def extract(filename,outputs,start = 1,step = 1):
    fp = open(filename,'rb')
    k = read(fp)
    length = fp.tell()
    outputs = Path(outputs)
    stem = outputs.stem
    suffix = outputs.suffix
    # write_plot3d_unfmt(outputs.with_name('{}_{:04d}{}'.format(stem,start,suffix)),k)
    fp.seek(0,0)
    nn = start 
    while True:
        d = fp.read(length)
        if not d:
            break 
        assert len(d) == length
        out_name = outputs.with_name('{}_{:04d}{}'.format(stem,nn,suffix))
        open(out_name,'wb').write(d)
        nn+=step
def main():
    if len(sys.argv)>1 and sys.argv[1].lower() == '-x':
        filename = sys.argv[2]
        output_name = sys.argv[3]
    else:
        return
    extract(filename,output_name)
if __name__=='__main__':
    # main()
    read('/media/yxs/abc/test/rot323single-HB-test/rot323single_HB2_init_test/res_output_1.q')
    pass