#coding:utf-8

def WriteFlaviaMsh(filePath, coords, groupEles):
    with open(filePath,'w') as f:
        f.write('MESH    dimension 2 ElemType Triangle      Nnode 3 \n')
        f.write('Coordinates \n')
        for inode,coord in coords.items():
            line = str(inode) + " "
            for x in coord:
                line += (str(x) + ' ')
            line += '\n'
            f.write(line)
        f.write('End Coordinates \n')

        #单元
        for igroup,eles in groupEles.items():
            line = ''
            nnode = eles[1].nnode
            if nnode == 3 or nnode > 4:
                line = 'MESH    dimension 2 ElemType Triangle      Nnode 3\n'
            elif nnode == 4:
                line = 'MESH    dimension 2 ElemType Quadrilateral      Nnode 4\n'
            f.write(line)
            f.write('Coordinates\nEnd Coordinates\n')
            f.write('Elements\n')
            if nnode == 3 or nnode == 4:
                for ele in eles:
                    line = str(ele.id) + ' '
                    for inode in ele.lnods:
                        line += (str(inode) + ' ')
                    line += str(ele.igroup)
                    line += '\n'
                    f.write(line)
            else:
                #拆分为三角形
                for ele in eles:
                    for i in range(ele.nnode - 2):
                        line = str(ele.id) + ' ' + str(ele.lnods[0])+ ' ' + str(ele.lnods[i + 1])+ ' ' + str(ele.lnods[i + 2])+ ' ' + str(ele.igroup) + '\n'
                        f.write(line)
            f.write('End Elements\n')

            
