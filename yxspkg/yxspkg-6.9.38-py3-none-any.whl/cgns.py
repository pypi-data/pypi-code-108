import h5py
import numpy as np
from pathlib import Path
import os
# import meshio
def get_h5_tree(h,name,h_list):
    if hasattr(h[name],'keys'):
        for i in h[name].keys():
            key = name+'/'+i
            h_list.append(key)
            get_h5_tree(h,key,h_list)
    
    
def rewrite_h5_tree(h,name,wh,h_list):
    if hasattr(h[name],'keys'):
        for i in h[name].keys():
            key = name+'/'+i
            h_list.append(key)
            rewrite_h5_tree(h,key,wh,h_list)
    else:
        wh[name] = h[name][()]
        
class zone_vals(dict):
    def __init__(self,hdf5,val_dict):
        self.hdf5 = hdf5 
        self.val_dict = val_dict 
        for i in val_dict.keys():
            self[i] = None
    def __getitem__(self,key):
        val = super().__getitem__(key)
        if val is None:
            val = self.hdf5[self.val_dict[key]][()]
            self[key] = val
        return val
class cgnsData(dict):
    def __init__(self,cgns):
        super().__init__()
        if isinstance(cgns,Path) or isinstance(cgns,str):
            self._read_cgns(cgns)      
        else:
            raise Exception('type error') 
    def _read_cgns(self,cgns):
        self.h5f = h5py.File(cgns,'r')
        project3d = self.h5f['project3d']
        self.zone_name = list(project3d.keys())[2:]
        s1 = 'project3d/{zone}/GridCoordinates/{val}/ data'
        s2 = 'project3d/{zone}/sol1/{val}/ data'
        for zone in self.zone_name:
            val_dict = {i:s1.format(zone=zone,val=i) for i in project3d[zone+'/GridCoordinates'].keys()}
            v2 = {i:s2.format(zone=zone,val=i) for i in project3d[zone+'/sol1'].keys()}
            val_dict.update(v2)
            self[zone] = zone_vals(self.h5f,val_dict)

def read(cgns):
    c = cgnsData(cgns)
    return c

def write(cgns):
    pass 
class write_cgns:
    def __init__(self,filename,cgns):
        self.filename = Path(filename)
        self.h5f = h5py.File(self.filename.with_name(self.filename.name+'.temph'),'w')
        self.h5f_closed=False
        self.cgns = cgns
        s_format =b'IEEE_LITTLE_32'
        s_format += bytes(15-len(s_format))
        s_format = np.frombuffer(s_format,dtype='int8')
        
        hdf5version = b'HDF5 Version 1.8.17'
        hdf5version += bytes(33 - len(hdf5version))
        hdf5version = np.frombuffer(hdf5version,dtype='int8')

        CGNSLibraryVersion_data = np.array([3.3],dtype='float32') 

        self.h5f.create_dataset(' format',data=s_format)
        self.h5f.create_dataset(' hdf5version',data=hdf5version)
        self.h5f.create_dataset('CGNSLibraryVersion/ data',data=CGNSLibraryVersion_data)

        self.write_fluid_solution()
        self.write_project3d()
        print('*'*90)
        print(self.h5f.keys())
        print(self.h5f['fluid_solution'].keys())
        print(self.h5f['fluid_solution/domain1'].keys())
        
    def write_fluid_solution(self):
        cgns = self.cgns
        fluid_solution_data = np.array([3,3],dtype='int32')
        fscalars = np.array([0],dtype='float64')
        self.h5f.create_dataset('fluid_solution/ data',data=fluid_solution_data)
        self.h5f.create_dataset('fluid_solution/scalars/PREF/ data',data=fscalars)
        data = np.zeros((3,3),dtype='int32')
        fluid_solution = self.h5f['fluid_solution']
        for zone_name in cgns.keys():
            print(zone_name)
            zone_h5 = fluid_solution.create_group(zone_name)
            zone = cgns[zone_name]
            shapes = list(set([zone[i].shape for i in zone.keys() if zone[i] is not None]+[(0,),]))
            shapes.sort(key=lambda x:-sum(x))
            if len(shapes[0])>1:
                ZoneType = np.frombuffer(b'Structured',dtype='int8')
                GridLocation = np.frombuffer(b'CellCenter',dtype='int8')
                data[:] = 0
                for i,shape in enumerate(shapes):
                    if i==1 and shape[0] == 0:
                        data[i] = [j-1 if j>1 else 1 for j in shapes[0]]
                    else:
                        data[i] = shape
                print(data)
                if hasattr(zone,'blockName'):
                    blockName = zone.blockName
                else:
                    blockName = np.frombuffer(b'_',dtype='int8')
            else:
                raise Exception( "Unstructured error")
            zone_h5[' data']=data
            zone_h5['ZoneType/ data'] = ZoneType
            zone_h5['blockName/blockName/ data'] = ZoneType
            zone_h5['sol1/CridLocation/ data'] = GridLocation
            zone_h5['sol1/Density/ data'] = zone['Density'][:-1,:-1,:-1]
            break
    def write_project3d(self):
        cgns = self.cgns
        self.h5f['project3d/ data'] = np.array([3,3],dtype='int32')
        project3d = self.h5f['project3d']
        project3d['VERSION/Euranus Version/ data'] = np.frombuffer(b'13.1',dtype='int8')
        data = np.zeros((3,3),dtype='int32')
        for zone_name in cgns.keys():
            print(zone_name)
            zone_h5 = project3d.create_group(zone_name)
            zone = cgns[zone_name]
            shapes = list(set([zone[i].shape for i in zone.keys() if zone[i] is not None]+[(0,),]))
            shapes.sort(key=lambda x:-sum(x))
            if len(shapes[0])>1:
                ZoneType = np.frombuffer(b'Structured',dtype='int8')
                GridLocation = np.frombuffer(b'CellCenter',dtype='int8')
                data[:] = 0
                for i,shape in enumerate(shapes):
                    if i==1 and shape[0] == 0:
                        data[i] = [j-1 if j>1 else 1 for j in shapes[0]]
                    else:
                        data[i] = shape
            else:
                raise Exception( "Unstructured error")
            zone_h5[' data']=data
            for val in 'XYZ':
                key = 'Coordinate'+val 
                zone_h5['GridCoordinates/'+key+'/ data'] = zone[key]
            # zone_h5['ZoneType/ data'] = ZoneType
            # zone_h5['blockName/blockName/ data'] = ZoneType
            # zone_h5['sol1/CridLocation/ data'] = GridLocation
            # zone_h5['sol1/Density/ data'] = zone['Density'][:-1,:-1,:-1]
            break
    def __del__(self):
        if not self.h5f_closed:
            self.close()
    def close(self):
        self.h5f.close()
        tempname = self.filename.with_name(self.filename.name+'.temph')
        os.rename(tempname,self.filename)
        self.h5f_closed = True
if __name__=='__main__':
    read('Aachen_111_SA.cgns')