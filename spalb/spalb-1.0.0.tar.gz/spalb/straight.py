

# In[1]:


import random
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np


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
        # add number of precedence relations of a task to a list
        temp = [task,len(pre_of_task),time_of_tasks[task-1]] # [งาน, จำนวนงานก่อนหน้า, เวลาของงาน]
        num_of_precedences.append(temp) # นำ temp ไปใส่ใน num_of_precedences
        tasks_suc.insert(1, suc_of_task)
        tasks.insert(1, pre_of_task)
        # list ที่มีข้อมูลความสัมพันธืก่อนหลังของงาน เช่น  [[1, []], [2, [1]], [3, [2,1]],...]
        number_of_precedences.append(tasks)
        successors.append(tasks_suc)
        a = [time_of_tasks[task-1],task,len(pre_of_task),len(suc_of_task)] #[เวลาของงาน, งาน, จำนวนงานก่อนหน้า, จำนวนงานตามหลัง]
        time_work.append(a) #นำตัวแปร a ไปใส่ใน time_work
    LCR_list = sorted(time_work,reverse=True) #สร้าง list สำหรับทำ lcr โดยทำการจัดเรียงเวลา
    
    return number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, LCR_list


# In[3]:


def ShowAns(workstation, workstations, time_of_tasks, time_of_stations, Cycle_time, ac,  num_of_precedences, number_of_tasks, number_of_precedences):
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
    #ตารางคำตอบ
    df = pd.DataFrame(columns=['Station','Work Element','Station Time'])
    for i in range(1,workstation):
        df.loc[i] = ['Station' + str(i)] + [ac[i]] + [time_of_stations[i-1]]
    print(df)
    print("."*100)
    print('Efficiency = %.2f' %(Efficiency))
    print('Balance Delay = %.2f' %(BalanceDelay))
    print('Smoothness Index = %.2f' %(SI))
    print("."*100)
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


def comsoal(filename) :
    # COMSOAL
    Cycle_time = float(input("Enter the cycle time : ")) #ใส่รอบเวลา
    Answer = []
    Ans = {}
    Eff = [] #list เก็บประสิทธิภาพของทุกคำตอบ
    for ai in range(1,11):
        number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, LCR_list = readfile(filename)
        if Cycle_time < max(time_of_tasks) :
            print("Cycle time is less than maximum processing time")
            Cycle_time = float(input("Please enter the new cycle time : "))
        Ef = [] #list เก็บประสิทธิภาพของแต่ละคำตอบ
        ac = [[0]]
        A = num_of_precedences.copy()
        workstations = {} #เก็บข้อมูลว่าแต่ละสถานีงาน มีงานอะไรบ้าง
        workstation = 1 #นับจำนวนสถานีงาน
        assign_counter = 0 #นับจำนวนงานที่ถูกจัดลงสถานีงานแล้วทั้งหมด
        assembly_line_time = 0
        time_of_stations = []  # list สำหรับเก็บเวลาของแต่ละสถานีงาน
        while assign_counter < number_of_tasks:   #ทำงานจนกว่าทุกงานจะถูกจัดสรรครบทั้งหมด

            station_time = 0 # เวลาของแต่ละสถานีงาน โดยจะเริ่มที่ 0
            station_tasks = []  # list สำหรับเก็บงานที่ถูกจัดสรรลงในสถานีงาน

            while station_time <= Cycle_time:  # เวลาของสถานีงานต้องไม่เกินรอบเวลา

                # เลือกงานที่มีงานก่อนหน้า = 0
                tasks_none_precedences = [i[0] for i in A if i[1] == 0]
                # เลือกงานจาก list บน ให้มีเฉพาะงานที่ถ้าจัดลงสถานีแล้วจะไม่เกินรอบเวลา
                candidate_tasks = [task for task in tasks_none_precedences if station_time + time_of_tasks[task-1] <= Cycle_time]
                    
                if candidate_tasks == []:  # ถ้า candidate_tasks ว่าง จะเปิดสถานีงานใหม่
                    time_of_stations.append(station_time)
                    workstations[workstation] = station_tasks  #นำงานที่ถูกจัดลงสถานีไปใส่ใน dict workstations
                    workstation = workstation + 1  # เปิดสถานีงานใหม่
                    break
                else:
                    selected_task = random.choice(candidate_tasks) #สุ่มงานจาก candidate_tasks
                    #เลือกงานที่มี selected_task เป็นงานก่อนหน้า
                    pre_of_selected_task = [number_of_precedences[task][0] for task in range(number_of_tasks) if selected_task in number_of_precedences[task][1]]
                    #ลบจำนวนงานก่อนหน้า - 1
                    for task in range(number_of_tasks):  
                        for i in pre_of_selected_task:
                            if  A[task][0] == i :
                                A[task][1] = A[task][1] - 1 
                    #งานที่เป็นถูกเลือกแล้วจะเปลี่ยนเป็นคำว่า Done
                    A[selected_task-1][1] = "Done" 
                        #if  A[task][1] == selected_task and A[task][2] == 0 :
                            #A[task][2] = "Done"  # mark the chosen task
                    station_time = station_time + time_of_tasks[selected_task-1]  # คำนวณเวลาในสถานีงาน
                    station_tasks.append(selected_task)  # เพิ่ม selected_task ลงในสถานีงาน
                    assign_counter = assign_counter + 1  # นับจำนวนงานที่ถูกเลือก
        Efficiency = (sum(time_of_tasks)/(max(time_of_stations)*(workstation-1)))*100 #คำนวนประสิทธิภาพของแต่ละคำตอบ
        Ef.append(Efficiency) # เพิ่ม Efficiency ใน Ef
        Ef.append(ai) # เพิ่มคำตอบที่ ใน Ef เช่น คำตอบที่ 1, 2
        Eff.append(Ef) 
        Eff = sorted(Eff, reverse=True)
        Ans[ai] = [workstation,time_of_stations,workstations]
    #แสดงคำตอบ
    ShowAns(Ans[Eff[0][1]][0], Ans[Eff[0][1]][2], time_of_tasks, Ans[Eff[0][1]][1], Cycle_time, ac,  num_of_precedences, number_of_tasks, number_of_precedences)


# In[5]:


def lcr(filename) :
    number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, LCR_list = readfile(filename)
    # Largest Candidate Rule
    Cycle_time = float(input("Enter the cycle time : ")) #ใส่รอบเวลา
    if Cycle_time < max(time_of_tasks) :
        print("Cycle time is less than maximum processing time") #ถ้ารอบเวลาน้อยกว่าเวลาของงานที่มากที่สุดจะแสดงข้อความให้กรอกใหม่
        Cycle_time = float(input("Please enter the new cycle time : "))
    ac = [[0]]
    A = LCR_list.copy() # copy LCR_list
    workstations = {} #เก็บข้อมูลว่าแต่ละสถานีงาน มีงานอะไรบ้าง
    workstation = 1 #นับจำนวนสถานีงาน
    assign_counter = 0 #นับจำนวนงานที่ถูกจัดลงสถานีงานแล้วทั้งหมด
    #assembly_line_time = 0
    time_of_stations = []  # list สำหรับเก็บเวลาของแต่ละสถานีงาน

    while assign_counter < number_of_tasks:  #ทำงานจนกว่าทุกงานจะถูกจัดสรรครบทั้งหมด

        station_time = 0 # เวลาของแต่ละสถานีงาน โดยจะเริ่มที่ 0
        station_tasks = []  # list สำหรับเก็บงานที่ถูกจัดสรรลงในสถานีงาน

        while station_time <= Cycle_time:  # เวลาของสถานีงานต้องไม่เกินรอบเวลา

            # เลือกงานที่มีงานก่อนหน้า = 0
            tasks_none_precedences = [i[1] for i in A if i[2] == 0]
            # เลือกงานจาก list บน ให้มีเฉพาะงานที่ถ้าจัดลงสถานีแล้วจะไม่เกินรอบเวลา
            candidate_tasks = [task for task in tasks_none_precedences if station_time + time_of_tasks[task-1] <= Cycle_time]
                
            if candidate_tasks == []:  # ถ้า candidate_tasks ว่าง จะเปิดสถานีงานใหม่
                time_of_stations.append(station_time)
                workstations[workstation] = station_tasks #นำงานที่ถูกจัดลงสถานีไปใส่ใน dict workstations
                workstation = workstation + 1  # เปิดสถานีงานใหม่
                break
            else:
                selected_task = candidate_tasks[0] #เลือกงานที่เวลามากที่สุดจาก candidate_tasks
                #เลือกงานที่มี selected_task เป็นงานก่อนหน้า
                pre_of_selected_task = [number_of_precedences[task][0] for task in range(number_of_tasks) if selected_task in number_of_precedences[task][1]]
                #ลบจำนวนงานก่อนหน้า - 1
                for task in range(number_of_tasks):  
                    for i in pre_of_selected_task:
                        if  A[task][1] == i :
                            A[task][2] = A[task][2] - 1 
                    #งานที่เป็นถูกเลือกแล้วจะเปลี่ยนเป็นคำว่า Done
                    if  A[task][1] == selected_task and A[task][2] == 0 :
                        A[task][2] = "Done"  # mark the chosen task
                station_time = station_time + time_of_tasks[selected_task-1]  # คำนวณเวลาในสถานีงาน
                station_tasks.append(selected_task)  # เพิ่ม selected_task ลงในสถานีงาน
                assign_counter = assign_counter + 1  # นับจำนวนงานที่ถูกเลือก
    #แสดงคำตอบ
    ShowAns(workstation, workstations, time_of_tasks, time_of_stations, Cycle_time, ac,  num_of_precedences, number_of_tasks, number_of_precedences)
    


# In[6]:


def rpw(filename) :
    number_of_precedences, num_of_precedences, time_work, number_of_tasks, time_of_tasks, LCR_list = readfile(filename)
    # Rank Position Weight
    Cycle_time = float(input("Enter the cycle time : ")) #ใส่รอบเวลา
    if Cycle_time < max(time_of_tasks) :
        print("Cycle time is less than maximum processing time") #ถ้ารอบเวลาน้อยกว่าเวลาของงานที่มากที่สุดจะแสดงข้อความให้กรอกใหม่
        Cycle_time = float(input("Please enter the new cycle time : "))
    rpw_time = {} #list เก็บงานที่ตามหลังทั้งหมดของแต่ละงาน
    rpw = []
    for a in range(1,number_of_tasks+1):
        i = 1
        AB = [number_of_precedences[s][0] for s in range(number_of_tasks) if a in number_of_precedences[s][1] or number_of_precedences[s][0] == a ]
        while i <= number_of_tasks :
            pre_work = []
            A = number_of_precedences.copy()
            for s in AB:
                for task in range(number_of_tasks):
                    if s in A[task][1] :
                        AB.append(A[task][0])
            AB = list(dict.fromkeys(AB)) #ตัดข้อมูลซ้ำออกจาก List
            rpw_time[a] = AB # เพิ่มงานที่ตามหลังทั้งหมดของแต่ละงานใน rpw_time
            i = i+1
            continue
    
    time_of_rpw = [] #เก็บค่า rpw 
    for a in range(1,number_of_tasks+1):
        s = 1
        time_work = [] #เก็บเวลาของทุกงานที่ตามหลัง
        for task in rpw_time[a]:
            time_work.append(time_of_tasks[task-1])
        time_work = sum(time_work) #คำนวณค่า rpw
        time_of_rpw.append(time_work)
        s = s+1
        continue
    
    rpw_work = [] #เก็บค่า rpw, งาน และจำนวนงานก่อนหน้า
    for a in range(1,number_of_tasks+1):
        lists = [time_of_rpw[a-1],a,len(number_of_precedences[a-1][1])]
        rpw_work.append(lists)
    rpw_work = sorted(rpw_work,reverse=True) #เรียงค่า rpw จากมากไปน้อย
    ac = [[0]]
    A = rpw_work.copy()
    workstations = {} #เก็บข้อมูลว่าแต่ละสถานีงาน มีงานอะไรบ้าง
    workstation = 1 #นับจำนวนสถานีงาน
    assign_counter = 0 #นับจำนวนงานที่ถูกจัดลงสถานีงานแล้วทั้งหมด
    assembly_line_time = 0
    time_of_stations = []  # list สำหรับเก็บเวลาของแต่ละสถานีงาน

    while assign_counter < number_of_tasks:  # all tasks has to assign a station

        station_time = 0 # เวลาของแต่ละสถานีงาน โดยจะเริ่มที่ 0
        station_tasks = []  # list สำหรับเก็บงานที่ถูกจัดสรรลงในสถานีงาน

        while station_time <= Cycle_time:  # เวลาของสถานีงานต้องไม่เกินรอบเวลา

            # เลือกงานที่มีงานก่อนหน้า = 0
            tasks_none_precedences = [i[1] for i in A if i[2] == 0]
            # เลือกงานจาก list บน ให้มีเฉพาะงานที่ถ้าจัดลงสถานีแล้วจะไม่เกินรอบเวลา
            candidate_tasks = [task for task in tasks_none_precedences if station_time + time_of_tasks[task-1] <= Cycle_time]

            if candidate_tasks == []:  # ถ้า candidate_tasks ว่าง จะเปิดสถานีงานใหม่
                time_of_stations.append(station_time)
                workstations[workstation] = station_tasks #นำงานที่ถูกจัดลงสถานีไปใส่ใน dict workstations 
                workstation = workstation + 1  # เปิดสถานีงานใหม่
                break
            else:
                selected_task = candidate_tasks[0] #เลือกงานที่ rpw มากที่สุดจาก candidate_tasks
                #เลือกงานที่มี selected_task เป็นงานก่อนหน้า
                pre_of_selected_task = [number_of_precedences[task][0] for task in range(number_of_tasks) if selected_task in number_of_precedences[task][1]]
                #ลบจำนวนงานก่อนหน้า - 1
                for task in range(number_of_tasks):  
                    for i in pre_of_selected_task:
                        if  A[task][1] == i :
                            A[task][2] = A[task][2] - 1 
                    #งานที่เป็นถูกเลือกแล้วจะเปลี่ยนเป็นคำว่า Done
                    if  A[task][1] == selected_task and A[task][2] == 0 :
                        A[task][2] = "Done"  # mark the selected_task
                station_time = station_time + time_of_tasks[selected_task-1]  # คำนวณเวลาในสถานีงาน
                station_tasks.append(selected_task)  # เพิ่ม selected_task ลงในสถานีงาน
                assign_counter = assign_counter + 1  # นับจำนวนงานที่ถูกเลือก
    #แสดงคำตอบ
    ShowAns(workstation, workstations, time_of_tasks, time_of_stations, Cycle_time, ac,  num_of_precedences, number_of_tasks, number_of_precedences)

