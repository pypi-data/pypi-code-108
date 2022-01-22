#coding:utf-8

def writeCalcConfig(folderPath, coords, groupEles):
    with open(folderPath + "\\1d.cor", 'w') as f:
        for inode,coord in coords.items():
            line = str(inode) + " "
            for x in coord:
                line += (str(x) + ' ')
            line += '\n'
            f.write(line)
    
    with open(folderPath + "\\1d.ele", 'w') as f:
        print('i0,nnode,ngele')
        for igroup,eles in groupEles.items():
            nnode = 0
            for ele in eles:
                nnode = ele.nnode
                line = str(ele.id) + ' ' + str(ele.nnode) + '  '
                for inode in ele.lnods:
                    line += (str(inode) + ' ')
                line += str(ele.igroup)
                line += '\n'
                f.write(line)
            print(str(igroup) + '  ' + str(nnode) + '  ' + str(len(eles)))

    
