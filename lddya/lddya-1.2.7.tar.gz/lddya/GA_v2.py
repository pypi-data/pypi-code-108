#
# 删除了每代画画，因为可能问题模型与解画不出来
#
#1.新增cross_decimal
#
# 
import random as rand
from math import *
import copy
import matplotlib.pyplot as plt
import numpy as np

class GA():
    def __init__(self,population=50, max_iter = 100, cross_pro=0.95, mut_pro=0.15,chro_lenght = 10,chro_limit = [0,10], want_max = True):
        '''
            Function:
            ---------
                对GA的一些必要参数进行初始化，如种群大小、最大迭代、交叉概率、变异概率，染色体长度等进行初始化
            
            Params:
            -------
                eval_fun : fun
                    GA的染色体的评价函数，输入为染色体，输出为评价值,默认加载类自带的fun方法(函数最值求解模型)，
                    也可以通过类方法重写的形式替换fun方法
                chro_decode : fun
                    GA的染色体的解码函数，默认为自带的decode方法，即为二进制转十进制解码方法。
                population: int
                    种群大小
                max_iter :  int
                    最大迭代次数，默认为100
                cross_pro : float
                    交叉概率，区间(0,1)，默认为0.95
                mut_pro : float
                    变异概率，区间(0.1)，默认为0.15
                chro_lenght : int
                    染色体长度
                chro_limit  : list(size = 2)
                    控制十进制染色体的单个染色体片段的上下界限。默认为[0, 10]
                want_max : True or False
                    控制selection选择较大值还是较小值

            Return:
            ------
                None
        '''
        self.population = population
        self.max_iter = max_iter
        self.cross_pro = cross_pro
        self.mut_pro = mut_pro
        self.chro_lenght = chro_lenght
        self.chroms_list = []   # 染色体信息库
        self.child_list = []    #子代染色体信息库
        self.plot_ave = []
        self.plot_max = []
        self.plot_min = []
        self.best_x = []
        self.has_been_init_fun = False    # GA函数模块初始化标志变量，GA优化动作前必须先对相关函数模块初始化
        self.chro_limit = chro_limit
        self.want_max = want_max
        self.best_y = -999999 if want_max == True else 999999

    def init_fun(self,eval_fun=None,chro_decode = None,generate = None, cross = None,mutation = None):
        '''
            Function:
            ---------
                支持对GA中的一些功能函数模块进行二次开发更替。相关函数接口请查阅MD文档。
            
            Params:
            -------
                eval_fun :      评价函数，默认为内置fun函数
                chro_decode :   解码函数，默认为内置decode函数
                generate    :   个体生成函数，默认为内置generate_binary,另外提供十进制的生成函数generate_decimal
                cross       :   交叉函数，默认为内置cross_binary,另外提供十进制的交叉函数cross_decimal
                mutation    :   变异函数，默认为内置mutation_binary,另外提供十进制的变异函数mutation_decimal
        '''
        self.has_been_init_fun = True   
        self.eval_fun = eval_fun if eval_fun != None else self.fun
        self.decode = chro_decode if chro_decode != None else self.decode 
        self.generate_fun = generate if generate != None else self.generate_binary
        self.cross_fun = self.cross_decimal  if cross != None else self.cross_binary
        self.mutation_fun = self.mutation_decimal if mutation != None else self.mutation_binary
    
    def generate_binary(self,chro_lenght):
        '''
            Function:
            ---------
                按要求生成种群，即生成染色体，仅生成一个个体.

            Params:
            -------
                chro_lenght : int
                    染色体长度
                limit : list(lenght=2)
                    染色体每个元素的上下界，当为None时，即为二进制生成，否则若为[a,b]，则a为下限，b为上限。
            
            Return:
            -------
                chro_1 : list (lenght = chro_lenght)
                    一条染色体信息
        '''
        chro_1 = []
        for i in range(chro_lenght):
            chro_1.append(rand.randint(0,1))
        return chro_1

    def generate_decimal(self, chro_lenght,repeat = False):
        '''
            Function:
            --------
                生成规定的十进制的染色体。
            
            Params:
            -------
                chro_lenght : int
                    染色体长度
                
                repeat:
                    控制允许染色体的基因片段数字是否可以重复出现，默认为True
                
            Return:
            -------
                chro_1 : list(lenght = chro_lenght)
                    一条染色体信息
        '''
        chro_1 = []
        if repeat == True:
            for i in range(chro_lenght):
                chro_1.append(rand.randint(self.chro_limit[0],self.chro_limit[1]))
        else:
            chro_1 = np.argsort(np.random.rand(chro_lenght))
            chro_1 = chro_1.tolist()
        
        return chro_1
        
    def fun(self,x):
        '''
            Function:
            ---------
                该函数被设计仅作为资源模块供eval_fun初始化使用，不建议作为方法去调用！该函数的内容主要为
                f函数的极值搜索模型。
            
            Params:
            -------
                x : float/int
                decode解码后的染色体真实值
            
            Return:
            -------
                y : float/int
                对应函数的y值
                
            
        '''
        y =  x + 10*sin(5*x) + 7*cos(4*x)
        return y

    def decode(self,chro, limit = [0,10]):
        '''
            Function:
            ---------
                对一条染色体信息进行解码，默认模式为将二进制数据解码成十进制。
            
            Params:
            --------
                chro : list
                    染色体信息
                limit : list 
                    为十进制数据的范围
            
            Return:
            -------
                decode_value : int
                    十进制数据       
        '''
        chro_1 = copy.deepcopy(chro)
        chro_1.reverse()
        a_1 = 0
        for i in range(len(chro_1)):
            a_1 += chro_1[i]*(2**i)
        e = (a_1/(2**(len(chro_1))-1))*(limit[1]-limit[0]) + limit[0]
        return e

    def run(self):
        if self.has_been_init_fun == False:
            print('无法优化！GA函数模块未初始化，请执行init_fun()方法初始化！')
            return None
        else:
            print('GA优化开始...')
        # Step 1: 初始化生成若干个初代个体
        for i in range(self.population):
            self.chroms_list.append(self.generate_fun(chro_lenght=self.chro_lenght))
        for i in range(self.max_iter):
            # Step 2：执行种群选择
            self.selection()
            #print('#####up:#####')
            self.evalution()
            # Step 3: 交叉 
            self.cross_fun()
            #print('#####down:#####')
            #self.evalution()
            # Step 4: 变异
            self.mutation_fun()
            self.chroms_list = copy.deepcopy(self.child_list)
            #input()
            
    def selection(self):
        '''
            Function:
            ---------
                本选择法为竞标赛选择法。每次随机选择3个个体出来竞争，最优秀的那个个体的染色体信息继承到下一代。
            
            Params:
            --------
                None

            Return:
            -------
                child_1:    list-list
                    子代的染色体信息
        '''
        chroms_1 = copy.deepcopy(self.chroms_list)
        child_1 = []
        for i in range(self.population):
        #for i in range(3):
            a_1 = []    # 3个选手
            b_1 = []    # 3个选手的成绩
            for j in range(3):
                a_1.append(rand.randint(0,len(chroms_1)-1))
            for j in a_1:
                b_1.append(self.eval_fun(self.decode(chroms_1[j])))
            if self.want_max == True:
                c_1 = b_1.index(max(b_1))  # 最好的是第几个
            else:
                c_1 = b_1.index(min(b_1))
            child_1.append(chroms_1[a_1[c_1]])  #最好者进入下一代
            #print("待选三人成绩:",b_1,'选中成绩：',b_1[c_1])
        #print('*******************************************************')
        #input()
        
        self.child_list = child_1

    def cross_binary(self):
        '''
            Function:
            ---------
                PMX交叉法，对子代进行交叉
                
            Params:
            -------
                None
            
            Return:
            -------
                child_1:list-list
                    交叉后的子代信息
        '''
        child_1 = []   # 参与交叉的个体
        for i in self.child_list:  #依据交叉概率挑选个体
            if rand.random()<self.cross_pro:
                child_1.append(i)
        if len(child_1)%2 != 0:    #如果不是双数
            child_1.append(child_1[rand.randint(0,len(child_1)-1)])  #随机复制一个个体
        for i in range(0,len(child_1),2):
            child_2 = child_1[i]       #交叉的第一个个体
            child_3 = child_1[i+1]     #交叉的第二个个体
            a = rand.randint(0,len(child_2)-1)  #生成一个剪切点
            b = rand.randint(0,len(child_2)-1)  #生成另一个剪切点
            a = a if a<b else b                 #保证a点在b点左边，即小于
            if (a==b):                            #如果a=b，则b+1或者a-1，取决于a与b值的合法性
                if b<len(child_2)-1:
                    b += 1
                else:
                    a -= 1
            child_2_1 = child_2[0:a]+child_3[a:b]+child_2[b:]   #交叉重组
            child_3_1 = child_3[0:a]+child_2[a:b]+child_3[b:]
            child_1[i] = child_2_1            #新的覆盖原染色体信息
            child_1[i+1] = child_3_1
        for i in child_1:                     #交叉后的染色体个体加入子代群集中
            self.child_list.append(i)

    def cross_decimal(self):
        child_1 = []   # 参与交叉的个体
        for i in self.child_list:  #依据交叉概率挑选个体
            if rand.random()<self.cross_pro:
                child_1.append(copy.deepcopy(i))
        if len(child_1)%2 != 0:    #如果不是双数
            child_1.append(child_1[rand.randint(0,len(child_1)-1)])  #随机复制一个个体
        for i in range(0,len(child_1),2):
            #print(i)
            child_2 = child_1[i]       #交叉的第一个个体
            child_3 = child_1[i+1]     #交叉的第二个个体
            a = rand.randint(0,len(child_2)-1)  #生成一个剪切点
            b = rand.randint(0,len(child_2)-1)  #生成另一个剪切点
            if b<a :
                c = a                 #保证a点在b点左边，即小于
                a = b
                b = c
            if (a==b):                            #如果a=b，则b+1或者a-1，取决于a与b值的合法性
                if b<len(child_2)-1:
                    b += 1
                else:
                    a -= 1
            ######################################
            # 交叉核心代码
            l1 = child_2
            l2 = child_3

            l1_1 = copy.deepcopy(l1)
            l2_1 = copy.deepcopy(l2)
            for i in range(a,b):
                try:
                    x1 = l1_1.index(l2_1[i])
                    l1[i] = l1_1[x1]
                    l1[x1] = l1_1[i]
                except:
                    pass

                try:
                    x2 = l2_1.index(l1_1[i])
                    l2[i] = l2_1[x2]
                    l2[x2] = l2_1[i]
                except:
                    pass
                l1_1 = copy.deepcopy(l1)
                l2_1 = copy.deepcopy(l2)
            child_2_1 = copy.deepcopy(l1)
            child_3_1 = copy.deepcopy(l2)
            ######################################
            #child_2_1 = child_2[0:a]+child_3[a:b]+child_2[b:]   #交叉重组
            #child_3_1 = child_3[0:a]+child_2[a:b]+child_3[b:]
            child_1[i] = child_2_1            #新的覆盖原染色体信息
            child_1[i+1] = child_3_1
        
        for i in child_1:                     #交叉后的染色体个体加入子代群集中
            self.child_list.append(i)

    def mutation_binary(self):
        '''
            Function:
            ---------
                单点变异，随机某染色体的某节点0-1互换。

            Params:
            -------
                None
            
            Return:
            -------
                None
        '''
        for i in range(len(self.child_list)):
            if rand.random()<self.mut_pro:
                a_1 = rand.randint(0,len(self.child_list[0])-1)
                if self.child_list[i][a_1] == 0:
                    self.child_list[i][a_1] = 1
                else:
                    self.child_list[i][a_1] = 0
    
    def mutation_decimal(self):
        '''
            Function:
            ---------
                单点变异，随机某染色体的某节点数据突变。

            Params:
            -------
                None
            
            Return:
            -------
                None
        '''
        for i in range(len(self.child_list)):
            if rand.random()<self.mut_pro:
                a_1 = rand.randint(0,len(self.child_list[0])-1)
                #print('编译前:',self.child_list[i])
                while True:
                    b_1 = rand.randint(self.chro_limit[0],self.chro_limit[1])
                    if not(b_1 in self.child_list[i]):
                        break
                self.child_list[i][a_1] = b_1
                #print('编译后:',self.child_list[i])
                      
    def evalution(self):
        e = []
        x_1 = []
        y_1 = []
        for i in self.child_list:
            #i.reverse()
            x_2 = self.decode(i)
            x_1.append(x_2)
            y_2 = self.eval_fun(x_2)
            y_1.append(y_2)
            e.append(y_2)
        self.plot_ave.append(sum(e)/len(e))
        self.plot_max.append(max(e))
        self.plot_min.append(min(e))
        if self.want_max == True:
            if max(e)>=self.best_y:
                self.best_y = max(e)
                k = e.index(max(e))
                self.best_x = self.child_list[k]
        else:
            if min(e)<=self.best_y:
                self.best_y = min(e)
                k = e.index(min(e))
                self.best_x = self.child_list[k]
            #print('找到更好值:',self.best_y, end='  ')
            #print(ga.decode(self.best_x))
        #print(e)
        
    def setting(self, eval_fun = None, population=None, max_iter = None, cross_pro=None, mut_pro=None):
        '''
            Function:
            ---------
                该方法允许你随时更新GA中的相关参数。你唯一要注意的是使其合法的生效即可。

            Params:
            -------
                pass

            Return:
            -------
                None
        '''
        if eval_fun != None:
            self.eval_fun = eval_fun
        if population != None:
            self.population = population
        if max_iter != None:
            self.max_iter = max_iter
        if cross_pro != None:
            self.cross_pro = cross_pro
        if mut_pro != None:
            self.mut_pro = mut_pro










   
