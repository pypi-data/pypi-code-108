

# In[1]:


import random
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np
from random import uniform 
from random import randint as rnd


# In[2]:


def readfile(filename) :
    read_file = open(filename, "r") #อ่านไฟล์
    datas = [row.split("\n")[0] for row in read_file]
    number_of_tasks = int(datas[0]) #จำนวนงาน
    time_of_tasks = [float(datas[row]) for row in range(1, number_of_tasks+1)] #เวลาของแต่ละงาน
    # สร้างความสัมพันธ์จากรูปแบบ "i,j" เป็น list ในรูปแบบ [['1', '2'], ['1', '5'], ['1', '7'], ['1', '10'],...]
    predecessor = [datas[row].split(",") for row in range(number_of_tasks+1, len(datas))]
    if predecessor[-1] == ['']:
        predecessor.remove(predecessor[-1])
    number_of_precedences = [] #list สำหรับเก็บจำนวนงานก่อนหน้า เช่น [5, [2, 3]] คือ งานที่ 5 มีงานก่อนหน้า คือ งาน 2, 3
    successors = []
    num_of_precedences = [] #list สำหรับเก็บจำนวนงานก่อนหน้า เช่น [2, 1, 0.3] คือ งานที่ 2 มีงานก่อนหน้า 1 งาน และเวลาของงานที่ 2 คือ 0.3
    time_work = [] #list สำหรับเก็บข้อมูลในรูปแบบ [0.5, 1, 0, 3] คือ [เวลาของงาน, งาน, จำนวนงานก่อนหน้า, จำนวนงานตามหลัง]
    for task in range(1, number_of_tasks+1):
        tasks = [task]
        tasks_suc = [task]
        pre_of_task = [int(pre[0]) for pre in predecessor if int(pre[1]) == task]
        suc_of_task = [int(pre[1]) for pre in predecessor if int(pre[0]) == task]
        temp = [task,len(pre_of_task),time_of_tasks[task-1]] # [งาน, จำนวนงานก่อนหน้า, เวลาของงาน]
        num_of_precedences.append(temp) # นำ temp ไปใส่ใน num_of_precedences
        tasks_suc.insert(1, suc_of_task)
        tasks.insert(1, pre_of_task)
        # list ที่มีข้อมูลความสัมพันธืก่อนหลังของงาน เช่น  [[1, []], [2, [1]], [3, [2,1]],...]
        number_of_precedences.append(tasks)
        successors.append(tasks_suc)
        a = [time_of_tasks[task-1],task,len(pre_of_task),len(suc_of_task)] #[เวลาของงาน, งาน, จำนวนงานก่อนหน้า, จำนวนงานตามหลัง]
        time_work.append(a) #นำตัวแปร a ไปใส่ใน time_work
    LCR_list = time_work
    return LCR_list, number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, successors


# In[3]:


def ShowAns(filename, population, Cycle_time): # แสดงคำตอบ u_ga
    workstation, workstations, time_of_tasks, time_of_stations, ac,  num_of_precedences, number_of_tasks, number_of_precedences = Fitness(filename, population, Cycle_time )
    #สร้าง list สำหรับเอาไปใส่ตารางคำตอบ
    for p in range(1,workstation) :
        ac.append(workstations[p])
    #update number of precedences relations 
    num_of_precedences = []
    for task in range(number_of_tasks):
        temp = [task+1, len(number_of_precedences[task][1])]
        num_of_precedences.append(temp)
    #คำนวณประสิทธิภาพ
    Efficiency = (sum(time_of_tasks)/(max(time_of_stations)*(workstation-1)))*100
    #คำนวณ BalanceDelay
    BalanceDelay = 100 - Efficiency
    #คำนวณ Smoothness Index
    SI = []
    for i in range(1,workstation):
        q = (max(time_of_stations) - time_of_stations[i-1])**2
        SI.append(q)
    SI = math.sqrt(sum(SI))
    #Cycle time จริง
    Actual_Cycle_time = max(time_of_stations)
    #แสดงคำตอบ
    print("."*100)
    #ตารางคำตอบ มี 3 คอลัมน์ คือ station, work element, station time
    df = pd.DataFrame(columns=['Station','Work Element','Station Time'])
    for i in range(1,workstation):
        df.loc[i] = ['Station' + str(i)] + [ac[i]] + [time_of_stations[i-1]]
    print(df)
    print("."*100)
    print('Efficiency = %.2f' %(Efficiency)) # แสดง Efficiency ของคำตอบ
    print('Balance Delay = %.2f' %(BalanceDelay)) # แสดง Balance Delay ของคำตอบ
    print('Smoothness Index = %.2f' %(SI)) # แสดง Smoothness Index ของคำตอบ
    print("."*100)
    # กราฟของคำตอบ
    for i in range(workstation-1):
        plt.bar(i+1,time_of_stations[i], color='deepskyblue') 
    plt.axhline(Cycle_time, color='r', lw=1, label="Cycle time")
    plt.axhline(Actual_Cycle_time, color='g', lw=1, label="Actual_Cycle_time")
    plt.title('Assembly Line Balancing')
    plt.xlabel('Station')
    plt.ylabel('Station Time')
    plt.legend()
    plt.show()


# In[4]:


def ShowAns_Pa(filename, population, Cycle_time): #แสดงคำตอบ parallel_ga
    workstation, workstations, time_of_tasks, time_of_stations, ac, num_of_precedences, number_of_tasks, number_of_precedences, time, stat, Parallel_station = Fitness_Pa(filename, population, Cycle_time )
    #สร้าง list สำหรับเอาไปใส่ตารางคำตอบ
    for p in range(1,workstation) :
        ac.append(workstations[p])
    #update number of precedences relations 
    num_of_precedences = []
    for task in range(number_of_tasks):
        temp = [task+1, len(number_of_precedences[task][1])]
        num_of_precedences.append(temp)
    #คำนวณประสิทธิภาพ
    Efficiency = (sum(time_of_tasks)/(max(time)*(stat)))*100
    #คำนวณ BalanceDelay
    BalanceDelay = 100 - Efficiency
    #คำนวณ Smoothness Index
    SI = []
    for i in range(1,workstation):
        if  time_of_stations[i-1] > Cycle_time:
            q = (max(time) - (time_of_stations[i-1]/2))*2
            q = q**2
            SI.append(q)
        else :
            p = (max(time) - time_of_stations[i-1])**2
            SI.append(p)
    SI = math.sqrt(sum(SI))
    #Cycle time จริง
    Actual_Cycle_time = max(time)
    #แสดงคำตอบ
    print("."*100)
    #ตารางคำตอบ มี 3 คอลัมน์ คือ station, work element, station time, Parallel Stations
    df = pd.DataFrame(columns=['Station','Work Element','Station Time','Parallel Stations'])
    for i in range(1,workstation):
        df.loc[i] = ['Station' + str(i)] + [ac[i]] + [time_of_stations[i-1]] + [Parallel_station[i-1]]
    print(df)
    print("."*100)
    print('Efficiency = %.2f' %(Efficiency)) # แสดง Efficiency ของคำตอบ
    print('Balance Delay = %.2f' %(BalanceDelay)) # แสดง Balance Delay ของคำตอบ
    print('Smoothness Index = %.2f' %(SI)) # แสดง Smoothness Index ของคำตอบ
    print("."*100)
    # กราฟของคำตอบ
    for i in range(workstation-1):
        plt.bar(i+1,time_of_stations[i], color='deepskyblue')
    plt.axhline(Cycle_time, color='r', lw=1, label="Cycle time")
    plt.axhline(Actual_Cycle_time, color='g', lw=1, label="Actual_Cycle_time")
    plt.title('Assembly Line Balancing')
    plt.xlabel('Station')
    plt.ylabel('Station Time')
    plt.legend()
    plt.show()


# In[5]:


def Fitness(filename, population, Cycle_time): # หาค่า fitness ของ u_ga
    LCR_list, number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, successors = readfile(filename)
    ac = [[0]]
    A = LCR_list.copy()
    workstations = {} #เก็บข้อมูลว่าแต่ละสถานีงาน มีงานอะไรบ้าง
    workstation = 1 #นับจำนวนสถานีงาน
    assign_counter = 0 #นับจำนวนงานที่ถูกจัดลงสถานีงานแล้วทั้งหมด
    time_of_stations = []  # list สำหรับเก็บเวลาของแต่ละสถานีงาน

    while assign_counter < number_of_tasks:  #ทำงานจนกว่าทุกงานจะถูกจัดสรรครบทั้งหมด
                    
        station_time = 0 # เวลาของแต่ละสถานีงาน โดยจะเริ่มที่ 0
        station_tasks = []  # list สำหรับเก็บงานที่ถูกจัดสรรลงในสถานีงาน
        
        while station_time <= Cycle_time:  # เวลาของสถานีงานต้องไม่เกินรอบเวลา
            # เลือกงานที่มีงานก่อนหน้าหรืองานตามหลัง = 0
            tasks_none_precedences = [i[1] for i in A if i[2] == 0 or i[3] == 0]
            # เลือกงานจาก list บน ให้มีเฉพาะงานที่ถ้าจัดลงสถานีแล้วจะไม่เกินรอบเวลา
            candidate_tasks = [task for task in tasks_none_precedences if station_time + time_of_tasks[task-1] <= Cycle_time]
                               
            if candidate_tasks == []:  # ถ้า candidate_tasks ว่าง จะเปิดสถานีงานใหม่
                time_of_stations.append(station_time)
                workstations[workstation] = station_tasks  #นำงานที่ถูกจัดลงสถานีไปใส่ใน dict workstations
                workstation = workstation + 1   # เปิดสถานีงานใหม่
                break

            else:
                # หาค่า priority มากสุดของงานที่สามารถจัดลงสถานีงานได้
                priority_list = []
                for i in candidate_tasks:
                    pri = population[i-1]
                    priority_list.append(pri)
                max_pri = max(priority_list)
                # เปลี่ยนค่า priority มาเป็นงานที่เราเลือก
                for i in range(number_of_tasks):
                    if population[i] == max_pri:
                        task = i+1
                selected_task = task #เลือกงานจาก candidate_tasks ที่มีค่า priority สูงสุด

                # งานที่มี selected_task เป็นงานก่อนหน้า       
                pre_of_selected_task = [number_of_precedences[task][0] for task in range(number_of_tasks) if selected_task in number_of_precedences[task][1]]  
                # งานที่มี selected_task เป็นงานหลัง     
                suc_of_selected_task = [successors[task][0] for task in range(number_of_tasks) if selected_task in successors[task][1]]
                
                for task in range(number_of_tasks): 
                    # ลบจำนวนงานก่อนหน้า - 1
                    for i in pre_of_selected_task:
                        if  A[task][2] == "Done":
                            continue
                        else :
                            if  A[task][1] == i :
                                A[task][2] = A[task][2] - 1
                    # ลบจำนวนงานตามหลัง - 1
                    for i in suc_of_selected_task :
                        if  A[task][3] == "Done":
                            continue
                        else:
                            if  A[task][1] == i :
                                A[task][3] = A[task][3] - 1
                A[selected_task-1][2] = "Done" #งานที่ถูกเลือกจะถูกเปลี่ยนเป็น Done
                A[selected_task-1][3] = "Done" #งานที่ถูกเลือกจะถูกเปลี่ยนเป็น Done
                station_time = station_time + time_of_tasks[selected_task-1]  # คำนวณเวลาในสถานีงาน
                station_tasks.append(selected_task)  # เพิ่ม selected_task ลงในสถานีงาน
                assign_counter = assign_counter + 1  # นับจำนวนงานที่ถูกเลือก 
    return workstation, workstations, time_of_tasks, time_of_stations, ac,  num_of_precedences, number_of_tasks, number_of_precedences


# In[6]:


def Fitness_Pa(filename, population, Cycle_time): # หาค่า fitness ของ parallel_ga
    LCR_list, number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, successors = readfile(filename)
    ac = [[0]]
    A = LCR_list.copy()
    workstations = {} #เก็บข้อมูลว่าแต่ละสถานีงาน มีงานอะไรบ้าง
    workstation = 1 #นับจำนวนสถานีงาน
    assign_counter = 0 #นับจำนวนงานที่ถูกจัดลงสถานีงานแล้วทั้งหมด
    time_of_stations = [] # list สำหรับเก็บเวลาของแต่ละสถานีงาน
    Parallel_station = [] # list สถานีงานขนานของแต่ละสถานีงาน
    for task in range(number_of_tasks):
        A[task][3] = "Done"

    while assign_counter < number_of_tasks: #ทำงานจนกว่าทุกงานจะถูกจัดสรรครบทั้งหมด
        Parallel_work = 0 #จำนวนสถานีงานขนาน เริ่มต้นที่ 0
        parallel = 1 # เมื่อเปิดสถานีงานขนานจะ +1 แล้วนำไปคูณกับรอบเวลา
        station_time = 0 # เวลาของแต่ละสถานีงาน โดยจะเริ่มที่ 0
        station_tasks = []  # list สำหรับเก็บงานที่ถูกจัดสรรลงในสถานีงาน
        cc = Cycle_time # คืนค่ารอบเวลาเริ่มต้นทุกครั้ง เมื่อเริ่มสถานีงานใหม่
        
        while station_time <= cc:  # เวลาของสถานีงานต้องไม่เกินรอบเวลา
            # เลือกงานที่มีงานก่อนหน้า = 0
            tasks_none_precedences = [i[1] for i in A if i[2] == 0]
            # เลือกงานจาก list บน ให้มีเฉพาะงานที่ถ้าจัดลงสถานีแล้วจะไม่เกินรอบเวลา
            candidate_tasks = [task for task in tasks_none_precedences if station_time + time_of_tasks[task-1] <= cc]
            # เลือกงานจาก list บน ให้มีเฉพาะงานที่ถ้าจัดลงสถานีงานแล้วจะไม่เกินรอบเวลาคูณ 2 และเวลาของงานมากกว่ารอบเวลาปกติ
            Overtime = [task for task in tasks_none_precedences if station_time + time_of_tasks[task-1] <= (Cycle_time*2) and time_of_tasks[task-1] > cc]
            
            if candidate_tasks != [] and Overtime != [] : # ถ้า candidate_tasks และ Overtime ไม่ว่างจะนำงานในทั้ง 2 list มารวมกัน
                candidate_tasks = candidate_tasks + Overtime
            
            if candidate_tasks == [] and station_tasks == [] : # ถ้า candidate_tasks ว่างและยังไม่มีงานถูกจัดลงในสถานีงาน จะนำงานในทั้ง 2 list มารวมกัน
                candidate_tasks = candidate_tasks + Overtime
                
            if candidate_tasks == [] :  # ถ้า candidate_tasks ว่างและมีงานถูกจัดลงในสถานีงานแล้ว จะเปิดสถานีงานใหม่
                cc = Cycle_time #เมื่อเปิดสถานีงานใหม่ คืนค่ารอบเวลากลับเป็นค่าเริ่มต้น
                time_of_stations.append(station_time)
                Parallel_station.append(Parallel_work) #เก็บจำนวนสถานีงานขนานใน Parallel_station
                workstations[workstation] = station_tasks 
                workstation = workstation + 1  # เปิดสถานีงานใหม่
                break

            if candidate_tasks != [] : # ถ้า candidate_tasks ไม่ว่าง ทำการเลือกงาน
                # หาค่า priority มากสุดของงานที่สามารถจัดลงสถานีงานได้
                priority_list = []
                for i in candidate_tasks:
                    pri = population[i-1]
                    priority_list.append(pri)
                max_pri = max(priority_list)
                # เปลี่ยนค่า priority มาเป็นงานที่เราเลือก
                for i in range(number_of_tasks):
                    if population[i] == max_pri:
                        task = i+1
                selected_task = task #งานที่ถูกเลือกเป็นงานที่มีค่า priority มากสุดของงานที่สามารถจัดลงสถานีงานได้
            
            # ถ้างานที่เลือกมีเวลาการทำงานมากกว่ารอบเวลา และยังไม่มีการเปิดสถานีงานขนาน จะทำการเปิดสถานีงานขนาน    
            if station_time + time_of_tasks[selected_task-1] > cc and time_of_tasks[selected_task-1] > cc :
                if parallel < 2 : # ถ้ายังไม่มีการเปิดสถานีงานขนาน
                    parallel = parallel+1
                    Parallel_work = Parallel_work+1
                    cc = Cycle_time * parallel #เมื่อเปิดสถานีงานขนาน ให้รอบเวลา * 2
                else : 
                    pass
            # เวลาของสถานีงานยังน้อยกว่ารอบเวลาอยู่
            if station_time + time_of_tasks[selected_task-1] <= cc:
                # งานที่มี selected_task เป็นงานก่อนหน้า 
                pre_of_selected_task = [number_of_precedences[task][0] for task in range(number_of_tasks) if selected_task in number_of_precedences[task][1]]
                # ลบจำนวนงานก่อนหน้า - 1
                for task in range(number_of_tasks):  
                    for i in pre_of_selected_task:
                        if  A[task][1] == i and A[task][2] != "Done"  :
                            A[task][2] = A[task][2] - 1
                A[selected_task-1][2] = "Done" #งานที่ถูกเลือกจะถูกเปลี่ยนเป็น Done
                station_time = station_time + time_of_tasks[selected_task-1]  # คำนวณเวลาในสถานีงาน
                station_tasks.append(selected_task)  # เพิ่ม selected_task ลงในสถานีงาน
                assign_counter = assign_counter + 1  # นับจำนวนงานที่ถูกเลือก 
                
    stat = (workstation-1) + sum(Parallel_station) # จำนวนสถานีงานปกติ + สถานีงานขนาน
    time = [] # เก็บเวลาของแต่ละสถานีงาน
    for i in range(len(time_of_stations)):
        if time_of_stations[i] > Cycle_time: # ถ้าเปิดสถานีงานขนาน นำรอบเวลาของสถานีนั้นหาร 2
            time.append((time_of_stations[i])/2)
        else: # ถ้าไม่เปิดสถานีงานขนาน ใช้รอบเวลาปกติ
            time.append(time_of_stations[i])
    return workstation, workstations, time_of_tasks, time_of_stations, ac, num_of_precedences, number_of_tasks, number_of_precedences, time, stat, Parallel_station


# In[7]:


def Efficiency(filename, population, Cycle_time):#คำนวณค่าประสิทธิภาพของ u_ga
    workstation, workstations, time_of_tasks, time_of_stations, ac,  num_of_precedences, number_of_tasks, number_of_precedences = Fitness(filename, population, Cycle_time)
    Efficiency = (sum(time_of_tasks)/(max(time_of_stations)*(workstation-1)))*100
    return Efficiency
def sm_index(filename, population, Cycle_time):#คำนวณค่า smoothness index ของ u_ga
    workstation, workstations, time_of_tasks, time_of_stations, ac, num_of_precedences, number_of_tasks, number_of_precedences = Fitness(filename, population, Cycle_time)
    SI1 = []
    for i in range(1,workstation):
        q = (max(time_of_stations) - time_of_stations[i-1])**2
        SI1.append(q)
    SI1 = math.sqrt(sum(SI1))
    return SI1


# In[8]:


def Efficiency_Pa(filename, population, Cycle_time): #คำนวณค่าประสิทธิภาพของ parallel_ga
    workstation, workstations, time_of_tasks, time_of_stations, ac, num_of_precedences, number_of_tasks, number_of_precedences, time, stat, Parallel_station = Fitness_Pa(filename, population, Cycle_time)
    Efficiency = (sum(time_of_tasks)/(max(time)*(stat)))*100
    return Efficiency

def sm_index_Pa(filename, population, Cycle_time): #คำนวณค่า smoothness index ของ parallel_ga
    workstation, workstations, time_of_tasks, time_of_stations, ac, num_of_precedences, number_of_tasks, number_of_precedences, time, stat, Parallel_station = Fitness_Pa(filename, population, Cycle_time)
    SI1 = []
    for i in range(1,workstation):
        if  time_of_stations[i-1] > Cycle_time:
            q = (max(time) - (time_of_stations[i-1]/2))**2
            SI1.append(q)
        else :
            p = (max(time) - time_of_stations[i-1])**2
            SI1.append(p)
    SI1 = math.sqrt(sum(SI1))
    return SI1


# In[9]:


def WeightMappingCrossOver(chromosome1, chromosome2):#crossover ด้วยการ weight mapping crossover
    newChromosome1, newChromosome2 = chromosome1.copy(), chromosome2.copy()
    x = rnd(0,4) #สุ่มเลข 0-4
    y = rnd(5,9) #สุ่มเลข 5-9
    substring1 = newChromosome1[x:y]
    mapping1 = random.sample(range(len(substring1)), len(substring1)) #สุ่มเลขที่มีจำนวนตัวเท่ากับ [x:y] เช่น [1:4] จะสุ่มเลข 3 ตัว เช่น [2,0,1]
    substring2 = newChromosome2[x:y]
    mapping2 = random.sample(range(len(substring1)), len(substring1)) #สุ่มเลขที่มีจำนวนตัวเท่ากับ [x:y] เช่น [1:4] จะสุ่มเลข 3 ตัว เช่น [2,0,1]
    del newChromosome1[x:y] # ลบค่าในตำแหน่ง [x:y] ของ newChromosome1 ออก
    del newChromosome2[x:y] # ลบค่าในตำแหน่ง [x:y] ของ newChromosome2 ออก
    new_substring1 = [] # list เก็บค่า chromosome ที่จะนำไปแทนในตำแหน่ง [x:y] ที่ถูกลบออกไป
    new_substring2 = [] # list เก็บค่า chromosome ที่จะนำไปแทนในตำแหน่ง [x:y] ที่ถูกลบออกไป
    for y in range(len(substring1)):
        for x in range(len(substring1)):
            if mapping2[y] == mapping1[x] :        
                new_substring1.append(substring1[x]) 
            if mapping1[y] == mapping2[x] :            
                new_substring2.append(substring2[x]) 
    newChromosome1[x:y] = new_substring1
    newChromosome2[x:y] = new_substring2
    return newChromosome1, newChromosome2

def Crossover(chromosome1, chromosome2):# ทำการ crossover
    return WeightMappingCrossOver(chromosome1, chromosome2)

def Crossover_selection(population, Crossover_rate):#เลือกประชากรที่จะนำไป crossover
    selectionList = []
    for i in range(0, len(population), 2): # วนรอบแบบเพิ่มขึ้นทีละ 2 เช่น 0, 2, 4
        if len(population) == i + 1: # ถ้าวนจนถึงประชากรตัวสุดท้ายแล้วให้หยุด เพราะตัวสุดท้ายไม่มีประชากรตัวถัดไป ให้นำไป croosover ด้วยแล้ว
            break
        if uniform(0, 1) < Crossover_rate: #สุ่มเลข 0-1 ของประชากรแต่ละตัว ถ้าตัวไหนมีค่าน้อยกว่า Crossover_rate ตัวเองและตัวถัดไปจะถูกนำไป crossover
            selectionList.append((population[i], population[i+1]))
    return selectionList


# In[10]:


def SwapMutation(chromosome): # mutation แบบ swapmutation
    newChromosome = chromosome.copy()
    mutated = np.random.permutation(len(newChromosome))[:2] # สุ่มเลขขึ้นมา 2 ตัว x, y เช่น 1, 4
    mutated0 = newChromosome[mutated[0]]
    mutated1 = newChromosome[mutated[1]]
    #สลับค่า โดยเอาค่าในตำแหน่ง x กับ y มาสลับกัน
    newChromosome[mutated[0]] = mutated1 # เช่น 4 มาอยู่ตำแหน่งของ 1 
    newChromosome[mutated[1]] = mutated0
    return newChromosome  

def Mutation(chromosome): # ทำการ mutation
    return SwapMutation(chromosome)

def Mutation_selection(population, Mutation_rate):# เลือกประชากรที่จะนำมา mutation
    selectionList = []
    for chromosome in population:
        if uniform(0, 1) < Mutation_rate: #สุ่มเลข 0-1 ของประชากรแต่ละตัว ถ้าตัวไหนมีค่าน้อยกว่า Mutation_rate ตัวเองและตัวถัดไปจะถูกนำไป Mutation
            selectionList.append(chromosome)
    return selectionList


# In[11]:


#คัดเลือกประชากรที่มีค่า Fitness น้อยที่สุดจำนวนเท่ากับ popsize ของ u_ga
def BestFit(filename, population, Crossover_population, Mutation_population, Cycle_time, init_eff, init_sm, PopSize):
    newpopulation = [] # list สำหรับเก็บประชากรรุ่นใหม่
    oldpopulation = population + Crossover_population + Mutation_population #ประชากรรุ่นเก่าทั้งหมดที่จะนำมาคัดเลือก
    fitnessed_eff = [] #เก็บค่า efficiency ของประชารุ่นเก่าทุกตัว
    fitnessed_sm = [] #เก็บค่า smoothness index ของประชารุ่นเก่าทุกตัว
    Fitness_rank = [] #จัดเรียงค่า Fitness ของประชากรรุ่นเก่า
    for p in oldpopulation :
        fitnessed_eff.append(Efficiency(filename, p, Cycle_time)) #คำนวณค่า efficiency
        fitnessed_sm.append(sm_index(filename, p, Cycle_time)) #คำนวณค่า smoothness index
    for i in range(len(oldpopulation)):
        #Fitness_rank.append([fitnessed[i], oldpopulation[i]])
        Fitness_rank.append([((init_eff/fitnessed_eff[i])+(fitnessed_sm[i]/init_sm)), oldpopulation[i]]) #คำนวณค่า Fitness
    Fitness_rank = sorted(Fitness_rank) #จัดเรียงค่า Fitness จากน้อยไปมาก
    Fitness_rank = Fitness_rank[:PopSize] #คัดเลือกประชากรจำนวนเท่ากับ popsize ไปเป็นประชากรรุ่นใหม่
    #for i in range(len(Fitness_rank)):
        #Fitness_rank[i][0] = sm_index(filename, Fitness_rank[i][1], Cycle_time)
    #Fitness_rank = sorted(Fitness_rank)
    return Fitness_rank


# In[12]:


#คัดเลือกประชากรที่มีค่า Fitness น้อยที่สุดจำนวนเท่ากับ popsize ของ u_ga
def BestFit_Pa(filename, population, Crossover_population, Mutation_population, Cycle_time, init_eff, init_sm, PopSize):
    newpopulation = [] # list สำหรับเก็บประชากรรุ่นใหม่
    oldpopulation = population + Crossover_population + Mutation_population #ประชากรรุ่นเก่าทั้งหมดที่จะนำมาคัดเลือก
    fitnessed_eff = [] #เก็บค่า efficiency ของประชารุ่นเก่าทุกตัว
    fitnessed_sm = [] #เก็บค่า smoothness index ของประชารุ่นเก่าทุกตัว
    Fitness_rank = [] #จัดเรียงค่า Fitness ของประชากรรุ่นเก่า
    
    for p in oldpopulation :
        fitnessed_eff.append(Efficiency_Pa(filename, p, Cycle_time)) #คำนวณค่า efficiency
        fitnessed_sm.append(sm_index_Pa(filename, p, Cycle_time)) #คำนวณค่า smoothness index
    for i in range(len(oldpopulation)):
        Fitness_rank.append([((init_eff/fitnessed_eff[i])+(fitnessed_sm[i]/init_sm)), oldpopulation[i]])
    Fitness_rank = sorted(Fitness_rank) #จัดเรียงค่า Fitness จากน้อยไปมาก
    Fitness_rank = Fitness_rank[:PopSize] #คัดเลือกประชากรจำนวนเท่ากับ popsize ไปเป็นประชากรรุ่นใหม่
    #for i in range(len(Fitness_rank)):
        #Fitness_rank[i][0] = sm_index(filename, Fitness_rank[i][1], Cycle_time)
    #Fitness_rank = sorted(Fitness_rank)
    return Fitness_rank


# In[13]:


def Newpopulation(population, PopSize): #สำหรับสร้างประชากรรุ่นใหม่
    newpop = [] # list สำหรับเก็บประชากรรุ่นใหม่
    for i in range (PopSize):
        newpop.append(population[i][1])
    return newpop


# In[14]:


def u_ga(filename):
    Cycle_time = float(input("Enter the cycle time : ")) #ใส่รอบเวลา
    PopSize = input("Enter the population size : ") #ใส่จำนวนประชากร
    if PopSize == "d": #ถ้าใส่ d ค่า PopSize จะถูกกำหนดให้เท่ากับ 20
        PopSize = 30
    else :
        PopSize = int(PopSize)
    Crossover_rate = input("Enter the crossover rate : ") #ใส่ Crossover_rate
    if Crossover_rate == "d": #ถ้าใส่ d ค่า Crossover_rate จะถูกกำหนดให้เท่ากับ 0.7
        Crossover_rate = 0.7
    else :
        Crossover_rate = float(Crossover_rate)
    Mutation_rate = input("Enter the mutation rate : ") #ใส่ Mutation_rate
    if Mutation_rate == "d": #ถ้าใส่ d ค่า Mutation_rate จะถูกกำหนดให้เท่ากับ 0.3
        Mutation_rate = 0.3
    else :
        Mutation_rate = float(Mutation_rate)
    maxGen = input("Enter the max generation : ") #ใส่จำนวนรุ่นสูงสุด
    if maxGen == "d": #ถ้าใส่ d ค่า maxGen จะถูกกำหนดให้เท่ากับ 100
        maxGen = 100
    else :
        maxGen = int(maxGen)
    # รับข้อมูลจาก function readfile    
    LCR_list, number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, successors = readfile(filename) 
    if Cycle_time < max(time_of_tasks) :
        print("Cycle time is less than maximum processing time")
        Cycle_time = float(input("Please enter the new cycle time : "))
    eff_0 = [] # เก็บค่าประสิทธิภาพของประชากรรุ่นแรกทุกตัว
    sm_0 = [] # เก็บค่า smoothness index ของประชากรรุ่นแรกทุกตัว
    population = [] #เก็บประชากร
    fitness = []
    bestFitness = 0 # เก็บค่า fitness ที่น้อยที่สุด
    bestFitnessList = [] # เก็บค่า fitness ทุกครั้งที่เจอค่าที่น้อยลง
    for z in range(1, PopSize+1):
        population.append(random.sample(range(1,number_of_tasks+1), number_of_tasks)) #สร้างประชากรเริ่มต้น
    for p in population :
        eff_0.append(Efficiency(filename, p, Cycle_time)) #คำนวณค่า efficiency
        sm_0.append(sm_index(filename, p, Cycle_time)) #คำนวณค่า smoothness index
    init_eff = max(eff_0) #ค่า efficiency ที่มากที่สุดของประชากรรุ่นแรก
    init_sm = min(sm_0) # ค่า smoothness index ที่น้อยที่สุดของประชากรรุ่นแรก
    
    for q in range(maxGen):# ทำซ้ำจนกว่าจะครบรอบ จำนวนรุ่นสูงสุด ที่กำหนดไว้
        
        #Crossover
        Crossover_population = [] #เก็บประชากรที่จะถูกนำไป crossover
        Crossover_selectionlist = Crossover_selection(population, Crossover_rate) #คัดเลือกประชากรที่จะถูกนำมาครอสโอเวอร์ 
        for i in range(0, len(Crossover_selectionlist)):
            Crossed_pop = Crossover(Crossover_selectionlist[i][0], Crossover_selectionlist[i][1])#ทำการ crossover 
            Crossover_population.append(Crossed_pop[0])
            Crossover_population.append(Crossed_pop[1])
            
        #Mutation
        Mutation_population = [] #เก็บประชากรที่จะถูกนำไป mutation
        Mutation_selectionList = Mutation_selection(population, Mutation_rate) #คัดเลือกประชากรที่จะถูกนำมา mutation
        for i in range(len(Mutation_selectionList)):
            Mutation_population.append(Mutation(Mutation_selectionList[i])) #ทำการ mutation
            
        BestofFit = BestFit(filename, population, Crossover_population, Mutation_population, Cycle_time, init_eff, init_sm, PopSize)
        BestofFitness = BestofFit[0][0] #เก็บค่า fitness ที่น้อยที่สุด
        
        bestFitnessList.append(BestofFitness) #นำค่า fitness ที่น้อยที่สุดของประชากรทุกรุ่นไปไว้ใน bestFitnessList
        # ถ้าค่า BestofFitness น้อยกว่าค่า fitness ที่น้อยที่สุดเดิม จะเปลี่ยนค่า bestFitness เป็นค่า BestofFitness แทน
        if BestofFitness < bestFitness: 
            bestFitness = BestofFitness
            #print(BestofFitness, q)
        population = Newpopulation(BestofFit, PopSize) #ประชากรรุ่นใหม่ที่จะนำไปคิดในครั้งถัดไป
    #plt.plot(range(maxGen), bestFitnessList)
    ShowAns(filename, population[0], Cycle_time) #แสดงคำตอบ
    #return population[0]


# In[15]:


def parallel_ga(filename):
    Cycle_time = float(input("Enter the cycle time : "))
    PopSize = input("Enter the population size : ") #ใส่จำนวนประชากร
    if PopSize == "d": #ถ้าใส่ d ค่า PopSize จะถูกกำหนดให้เท่ากับ 20
        PopSize = 30
    else :
        PopSize = int(PopSize)
    Crossover_rate = input("Enter the crossover rate : ") #ใส่ Crossover_rate
    if Crossover_rate == "d": #ถ้าใส่ d ค่า Crossover_rate จะถูกกำหนดให้เท่ากับ 0.7
        Crossover_rate = 0.7
    else :
        Crossover_rate = float(Crossover_rate)
    Mutation_rate = input("Enter the mutation rate : ") #ใส่ Mutation_rate
    if Mutation_rate == "d": #ถ้าใส่ d ค่า Mutation_rate จะถูกกำหนดให้เท่ากับ 0.3
        Mutation_rate = 0.3
    else :
        Mutation_rate = float(Mutation_rate)
    maxGen = input("Enter the max generation : ") #ใส่จำนวนรุ่นสูงสุด
    if maxGen == "d": #ถ้าใส่ d ค่า maxGen จะถูกกำหนดให้เท่ากับ 100
        maxGen = 100
    else :
        maxGen = int(maxGen)
    # รับข้อมูลจาก function readfile
    LCR_list, number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, successors = readfile(filename) 
    if Cycle_time < max(time_of_tasks)/2 : # ถ้ารอบเวลาน้อยกว่า เวลาของงานมากที่สุด/2 จะให้ใส่รอบเวลาใหม่
        print("Maximum processing time exceed twice the cycle time")
        Cycle_time = float(input("Please enter the new cycle time : "))
    eff_0 = [] # เก็บค่าประสิทธิภาพของประชากรรุ่นแรกทุกตัว
    sm_0 = [] # เก็บค่า smoothness index ของประชากรรุ่นแรกทุกตัว
    population = [] #เก็บประชากร
    fitness = []
    bestFitness = 0 # เก็บค่า fitness ที่น้อยที่สุด
    bestFitnessList = [] # เก็บค่า fitness ที่น้อยที่สุดทุกรุ่น
    #Create initial population
    for z in range(1, PopSize+1):
        population.append(random.sample(range(1,number_of_tasks+1), number_of_tasks))
    for p in population :
        eff_0.append(Efficiency_Pa(filename, p, Cycle_time)) #คำนวณค่า efficiency
        sm_0.append(sm_index_Pa(filename, p, Cycle_time)) #คำนวณค่า smoothness index
    init_eff = max(eff_0) #ค่า efficiency ที่มากที่สุดของประชากรรุ่นแรก
    init_sm = min(sm_0) # ค่า smoothness index ที่น้อยที่สุดของประชากรรุ่นแรก
       
    for q in range(maxGen): # ทำซ้ำจนกว่าจะครบรอบ จำนวนรุ่นสูงสุด ที่กำหนดไว้
        
        #Crossover
        Crossover_population = [] #เก็บประชากรที่จะถูกนำไป crossover
        Crossover_selectionlist = Crossover_selection(population, Crossover_rate) #คัดเลือกประชากรที่จะถูกนำมาครอสโอเวอร์
        for i in range(0, len(Crossover_selectionlist)):
            Crossed_pop = Crossover(Crossover_selectionlist[i][0], Crossover_selectionlist[i][1]) #ทำการ crossover 
            Crossover_population.append(Crossed_pop[0])
            Crossover_population.append(Crossed_pop[1])
            
        #Mutation
        Mutation_population = [] #เก็บประชากรที่จะถูกนำไป mutation
        Mutation_selectionList = Mutation_selection(population, Mutation_rate) #คัดเลือกประชากรที่จะถูกนำมา mutation
        for i in range(len(Mutation_selectionList)):
            Mutation_population.append(Mutation(Mutation_selectionList[i])) #ทำการ mutation
        # list ที่จัดเรียงค่า fitness แล้ว    
        BestofFit = BestFit_Pa(filename, population, Crossover_population, Mutation_population, Cycle_time, init_eff, init_sm, PopSize)
        BestofFitness = BestofFit[0][0] #เก็บค่า fitness ที่น้อยที่สุด
        
        bestFitnessList.append(BestofFitness) #นำค่า fitness ที่น้อยที่สุดของประชากรทุกรุ่นไปไว้ใน bestFitnessList
        # ถ้าค่า BestofFitness น้อยกว่าค่า fitness ที่น้อยที่สุดเดิม จะเปลี่ยนค่า bestFitness เป็นค่า BestofFitness แทน
        if BestofFitness < bestFitness:
            bestFitness = BestofFitness
            print(BestofFitness, q)
        population = Newpopulation(BestofFit, PopSize)  #ประชากรรุ่นใหม่ที่จะนำไปคิดในครั้งถัดไป
    #plt.plot(range(maxGen), bestFitnessList)
    ShowAns_Pa(filename, population[0], Cycle_time) # แสดงคำตอบ
    #return population[0]


# In[16]:





# In[ ]:




