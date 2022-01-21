import pygame as pg
import numpy as np
import time

class Map():
    def __init__(self) -> None:
        pass
        self.data = []    # map中的数据
    def map_reverse(self,fp='map.dll'):
        with open(fp,'r') as f:
            data = f.readlines()
        data.reverse()
        with open('map2.dll','w') as f:
            f.writelines(data)

    def recognition(self,fig_path,size):
        pg.init()
        pic = pg.image.load(fig_path)
        screen = pg.display.set_mode(pic.get_size())
        print('请点击栅格图的四个顶点！')
        screen.blit(pic,[0,0])
        pg.display.flip()
        dingdian = []   #四个顶点的坐标
        running = True
        while running:
            for i in pg.event.get():
                if i.type == pg.MOUSEBUTTONDOWN:
                    dingdian.append(i.pos)
                    if len(dingdian) == 4:
                        running = False
                        break
                    else:
                        pg.draw.circle(screen,[255,0,0],i.pos,3)
                        pg.display.flip()
        abs_x = max([abs(dingdian[i][0] - dingdian[i+1][0]) for i in range(0,3)])
        abs_y = max([abs(dingdian[i][1] - dingdian[i+1][1]) for i in range(0,3)])
        left_up_pos = dingdian[np.argmin([dingdian[i][0]+dingdian[i][1] for i in range(4)])]
        pg.draw.rect(screen,[0,255,0],[left_up_pos[0],left_up_pos[1],abs_x,abs_y],width=2)
        pg.display.flip()
        self.data = []
        self.record = []
        for y in range(size):    #row
            l1 = []
            l2 = []
            for x in range(size):   #column
                pos_1 = [left_up_pos[0]+(x/size)*abs_x+(abs_x/size)/2,left_up_pos[1]+(y/size)*abs_y+(abs_y/size)/2]
                neigh_pos = [                    [pos_1[0],pos_1[1]-2],
                            [pos_1[0]-2,pos_1[1]],                     [pos_1[0]+2,pos_1[1]],
                                                 [pos_1[0],pos_1[1]+2],
                ]
                key = 1  
                for i in neigh_pos:   
                    r,b,g,a = screen.get_at([int(i[0]),int(i[1])])
                    if max(r,g,b) <60:
                        continue
                    else:
                        key= 0
                        break
                if key == 1:
                    pg.draw.circle(screen,[0,0,255],pos_1,3)
                    l1.append(1)
                else:
                    pg.draw.circle(screen,[255,0,0],pos_1,3)
                    l1.append(0)
                l2.append(pos_1)
                pg.display.flip()
            self.data.append(l1)
            self.record.append(l2)
        print('识别完毕！\n')
        print('请观察界面中的识别结果(红色可通行，蓝色不可通行)，若识别错误请点击目标位置进行修改!\n确认完毕请关闭界面！')
        running = True
        while running:
            for i in pg.event.get():
                if i.type == pg.QUIT:
                    running = False
                elif i.type == pg.MOUSEBUTTONDOWN:
                    self.change(i.pos,screen)
    def change(self,i_pos,screen):
        print('修改行为:',end=' ')
        dis = 9999
        best_pos = []
        for i in range(len(self.record)):
            for j in range(len(self.record[i])):
                pos_1= self.record[i][j]
                if (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2<dis:
                    dis = (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2
                    best_pos = [i,j]
        print('目标位置:',best_pos,end=' ')
        if self.data[best_pos[0]][best_pos[1]] == 0:
            self.data[best_pos[0]][best_pos[1]] = 1 
            pg.draw.circle(screen,[0,0,255],self.record[best_pos[0]][best_pos[1]],3)
            print('结果: 变蓝')
        else:
            self.data[best_pos[0]][best_pos[1]] = 0
            pg.draw.circle(screen,[255,0,0],self.record[best_pos[0]][best_pos[1]],3)
            print('结果: 变红')
        pg.display.flip()

    
    def save(self,fp = 'map.dll'):
        str_data = []
        for i in self.data:
            s = ''
            for j in i:
                s+=str(j)
            s+='\n'
            str_data.append(s)
        with open(fp,'w')  as f:
            f.writelines(str_data)
        
            




    








