#  sudo pip3 install py4j && sudo pip3 install pandas && sudo pip3 install xlrd

# ATTENTION: we do not convert to  namedtuples (line 131 in compiler) because keys have special characters, and
# we use for example data["parkings"] instead of data.parkings

import datetime
import json
import math
from collections import OrderedDict
import numpy as np
import pandas as pd
from pycsp3 import *
from pycsp3.solvers.ace import Ace

date = "05/09/2019"  # hard coding for the moment (see also in the creation of the JSON solution file)
k_arrival, k_departure = 300, 300  #  hard coding for the time security in seconds

# note that data.ordonnancement, data.reductions, data.traitement and data.vols are not used

# ### about parkings
parkings = [c for c in data["parkings"]['Code'] if c[:2]!='AT']
parking_indexes = OrderedDict((parking, i) for i, parking in enumerate(parkings))  # keys are parkings (actually, their codes) and values their indexes
possible_parkings = OrderedDict()  # per plane type
for i, ta in enumerate(data["capacites"]['TA_CLE']):
    possible_parkings.setdefault(ta, []).append(data["capacites"]['RSC_COD'][i])

type_avion_indexes = OrderedDict()
all_type_avion = set(data["reductions"]['TA_CLE']+data["reductions"]['TA_CLE_REDUIT']+data["vols"]['Type avion'])

for i,el in enumerate(all_type_avion):
    type_avion_indexes[str(el)]=i

nParkings = len(parkings)

# ### about flights
flights = []
type_plane_flight_indexes = {}

for i in range(len(data['vols']['Type avion'])):
    v = {key:data['vols'][key][i] for key in data['vols'].keys()}
    if not pd.isnull(v['Date']):
        date_arr = f"{v['Date'].to_pydatetime().date().strftime('%d/%m/%Y')} {v['Heure'].strftime('%H:%M:%S')}"
    else:
        date_arr = None
    if not pd.isnull(v['Date_depart']):
        date_dep = f"{v['Date_depart'].to_pydatetime().date().strftime('%d/%m/%Y')} {v['Heure_depart'].strftime('%H:%M:%S')}"
    else:
        date_dep=None
    f = {'Date dep':date_dep,'Date arr':date_arr,'Type avion':str(v['Type avion']),'Comapgnie arr':v['Compagnie'],'Comapgnie dep':v['Compagnie dep']}

    if v['Type avion'] not in type_plane_flight_indexes.keys():
        type_plane_flight_indexes[v['Type avion']]=[]
    
    type_plane_flight_indexes[v['Type avion']].append(i)

    if f['Date arr'] is not None and date != f['Date arr'].split(" ")[0]:
        print(f'continue for flight {i} {date_arr} {date_dep}')
        continue
    elif f['Date dep'] is not None and date != f['Date dep'].split(" ")[0]: 
        print(f'continue for flight {i} {date_arr} {date_dep}')
        continue

    f['Poids vol arrivée'],f['Poids vol départ'],f['Poids total rotation'] = 0,0,0
    f['Stratégie code arr'] =  None 
    f['Stratégie code dep'] =  None

    indices = [i for i, x in enumerate(data["volsStrategies"]['Numéro de ligne arr']) if x == v['Ligne']]
    if len(indices)>0:
        indices2 = [i2 for i2, x in enumerate(data["volsStrategies"]['Comapgnie arr']) if x == v['Compagnie'] and i2 in indices]
        if len(indices2)>0:
            indices3 = [i3 for i3, x in enumerate(data["volsStrategies"]['Date arr']) if x == date_arr and i3 in indices2]
            if len(indices3)==1:
                f['Poids vol arrivée'] = data['volsStrategies']['Poids vol arrivée'][indices3[0]]
                f['Stratégie code arr'] = data['volsStrategies']['Stratégie code arr'][indices3[0]]

    indices = [i for i, x in enumerate(data["volsStrategies"]['Numéro de ligne dep']) if x == v['Ligne']]
    if len(indices)>0:
        indices2 = [i2 for i2, x in enumerate(data["volsStrategies"]['Comapgnie dep']) if x == v['Compagnie'] and i2 in indices]
        if len(indices2)>0:
            indices3 = [i3 for i3, x in enumerate(data["volsStrategies"]['Date dep']) if x == date_dep and i3 in indices2]
            if len(indices3)==1:
                f['Poids vol départ'] = data['volsStrategies']['Poids vol départ'][indices3[0]]
                f['Stratégie code dep'] = data['volsStrategies']['Stratégie code dep'][indices3[0]]

    f['Poids total rotation']=f['Poids vol arrivée']+f['Poids vol départ']
    flights.append(f)

nFlights = len(flights)
print(nFlights)



df_reductions=pd.DataFrame({'RSC_COD':data['reductions']['RSC_COD'],'TA_CLE':data['reductions']['TA_CLE'],'RSC_COD_REDUIT':data['reductions']['RSC_COD_REDUIT'],'TA_CLE':data['reductions']['RSC_COD_REDUIT']})





# Constant/Global Variable 
DEPAT = 90 
TMEP = 90
TTMA = 60
TTMD = 60
TMINDPL = 120
TMINROT = 45


### FUNCTION 

def to_datetime(s):
    if s is None:
        return None
    part1, part2 = s.split(" ")
    day, month, year, hour, minute, second = [int(v) for v in part1.split("/")] + [int(v) for v in part2.split(":")]
    return datetime.datetime(year, month, day, hour, minute, second)



def get_time(flight,is_breakable_3=False):
    ttma,ttmd,tmindpl = 0,0,0
    if flight['Comapgnie arr'] not in data['traitement']['CIE_CLE']:
        ttma = TTMA
    else:
        index = data['traitement']['CIE_CLE'].index(flight['Comapgnie arr'])
        ttma = data['traitement']['TTM_TTMA'][index] if not math.isnan(data['traitement']['TTM_TTMA'][index]) else TTMA 
    
    if flight['Comapgnie dep'] not in data['traitement']['CIE_CLE']:
        ttmd = TTMD
    else: 
        index = data['traitement']['CIE_CLE'].index(flight['Comapgnie arr'])
        ttmd = data['traitement']['TTM_TTM'][index] if not math.isnan(data['traitement']['TTM_TTMD'][index]) else TTMD

    if not is_breakable_3:
        tmindpl=0
    elif flight['Comapgnie dep'] not in data['traitement']['CIE_CLE'] and flight['Comapgnie arr'] not in data['traitement']['CIE_CLE']:
        tmindpl = TMINDPL
    else: 
        index = data['traitement']['CIE_CLE'].index(flight['Comapgnie arr']) if flight['Comapgnie arr'] not in data['traitement']['CIE_CLE'] else data['traitement']['CIE_CLE'].index(flight['Comapgnie dep'])
        tmindpl = data['traitement']['TTM_TMINDPL'][index] if not math.isnan(data['traitement']['TTM_TMINDPL'][index]) else TMINDPL
    return ttma,tmindpl,ttmd


def can_breakable(flight):
    if flight['Date arr'] is None or flight['Date dep'] is None:
        return False
    arr1 = to_datetime(flight['Date arr']) #- datetime.timedelta(seconds=k_arrival)
    dep1 = to_datetime(flight['Date dep']) #+ datetime.timedelta(seconds=k_departure)

    ttma,_,ttmd = get_time(flight,False)

    rotation =dep1-arr1

    return rotation.seconds >= ttma*60 + ttmd*60 and rotation.seconds >=TMINROT*60

def can_breakable_3_task(flight):
    if flight['Date arr'] is None or flight['Date dep'] is None:
        return False
    arr1 = to_datetime(flight['Date arr']) #- datetime.timedelta(seconds=k_arrival)
    dep1 = to_datetime(flight['Date dep']) #+ datetime.timedelta(seconds=k_departure)

    ttma,tmindpl,ttmd = get_time(flight,True)
    
    rotation =dep1-arr1


    return rotation.seconds >= ttma*60 + ttmd*60 + tmindpl*60 and rotation.seconds >=TMINROT*60

tasks = []
breakable2,breakable3,notbreak=0,0,0
for i,flight in enumerate(flights):
    canbreakable, can_breakable3 = can_breakable(flight), can_breakable_3_task(flight)

    if canbreakable and not can_breakable3:
        ttma,_,ttmd = get_time(flight)
        tmp = []
        arr1 = to_datetime(flight['Date arr']) #- datetime.timedelta(seconds=k_arrival) 
        dep1 = to_datetime(flight['Date dep']) #+ datetime.timedelta(seconds=k_departure)
        time1 = arr1 + datetime.timedelta(seconds=60 * ttma)
        tmp.append({'i':i,'arr':arr1,'dep':time1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
        tmp.append({'i':i,'arr':time1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
        tmp.append(None)
        breakable2+=1

        tasks.append(tmp)
    elif can_breakable3:

        ttma,tmindpl,ttmd = get_time(flight,True)
        arr1 = to_datetime(flight['Date arr']) #- datetime.timedelta(seconds=k_arrival) 
        dep1 = to_datetime(flight['Date dep']) #+ datetime.timedelta(seconds=k_departure)
        tmp = []
        time1 = arr1+datetime.timedelta(seconds=60*ttma)
        time2 = dep1-datetime.timedelta(seconds=60*ttmd)
        tmp.append({'i':i,'arr':arr1,'dep':time1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
        tmp.append({'i':i,'arr':time1,'dep':time2,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
        tmp.append({'i':i,'arr':time2,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
        tasks.append(tmp)
        breakable3+=1

    else:
        notbreak+=1
        tmp = [] 
        if flight['Date arr'] is not None and flight['Date dep'] is not None:
            arr1 = to_datetime(flight['Date arr']) #- datetime.timedelta(seconds=k_arrival) 
            dep1 = to_datetime(flight['Date dep']) #+ datetime.timedelta(seconds=k_departure)
            tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
            tmp.append(None)
            tmp.append(None)
        elif flight['Date arr'] is not None and flight['Date dep'] is None:
            arr1 = to_datetime(flight['Date arr']) #- datetime.timedelta(seconds=k_arrival) 
            ttma,_,ttmd = get_time(flight)
            dep1 = arr1 +datetime.timedelta(seconds=ttma*60)
            tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie arr']})
            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Compagnie arr']})
            tmp.append(None)
            tmp.append(None)
        else:
            dep = to_datetime(flight['Date dep']) #- datetime.timedelta(seconds=k_departure) 
            ttma,_,ttmd = get_time(flight)
            arr1 = dep-datetime.timedelta(seconds=ttmd*60)
            tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie dep']})
            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie dep']})
            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie dep']})
            tmp.append(None)
            tmp.append(None)

        tasks.append(tmp)

print(f'not_breakable={notbreak}, breakable3={breakable3}, breakable2={breakable2}, total_breakable={breakable2+breakable3}')


def table_shadings():
    p1, p2 = data["ombrages"]['RSC_COD'], data["ombrages"]['RSC_COD_OMBRE']
    assert len(p1) == len(p2)


    result = (
        {(i, i) for i in range(nParkings)}  # conflict if same parking(p[i][k],str(tasks[i][k]['Type avion']),p[j][k],str(tasks[j][k]['Type avion'])
        | {(parking_indexes[p1[i]], parking_indexes[p2[i]]) for i in range(len(p1))}  # conflict if shading between parkings
    )
    return result


def table_reductions(i,j):
    s = set()
    type_i,type_j = flights[i]['Type avion'],flights[j]['Type avion']
    tmp = df_reductions[df_reductions['TA_CLE']==type_i]

    for p in set(tmp['RSC_COD']):
        tmp2=tmp[tmp['RSC_COD']==p]
        s |=(parking_indexes[r['RSC_COD']],parking_indexes[r['RSC_COD']])
        if type_j not in tmp2['TA_CLE_REDUIT']:
            s |= (parking_indexes[r['RSC_COD']],parking_indexes[tmp2['RSC_COD_REDUIT']][0])
    return s 

def table_capacities(flight):
    return {parking_indexes[parking] for parking in possible_parkings[str(flight['Type avion'])] if parking[:2]!='AT'}


def table_rewards(flight):
    target_parkings = [strategy.split("/")[1] for strategy in data["strategies"]['Ressource'] if "/" in strategy]  # parkings without the character "/"
    table = set()
    for i, parking in enumerate(parkings):
        if flight['Stratégie code dep'] is None and flight['Stratégie code arr'] is None:
            table.add((i,0))
            continue
        elif  flight['Stratégie code dep'] is not None and flight['Stratégie code arr'] is None:
            strat = 'Stratégie code dep'
        else:
            strat = 'Stratégie code arr'
        
        value = data["strategies"][flight[strat]][target_parkings.index(parking)] if parking in target_parkings else 0
        if math.isnan(value):
            value=0
        table.add((i, int(value) if not math.isnan(value) else 0))
    return table

def are_overlapping_task(tasks1, tasks2):
    if tasks1 is None or tasks2 is None:
        return False
    arr1 = tasks1['arr'] - datetime.timedelta(seconds=k_arrival)
    dep1 = tasks1['dep'] + datetime.timedelta(seconds=k_departure)
    arr2 = tasks2['arr'] - datetime.timedelta(seconds=k_arrival)
    dep2 = tasks2['dep'] + datetime.timedelta(seconds=k_departure)
    return arr1 < dep2 and arr2 < dep1

def get_weight(flight,k):
    if can_breakable_3_task(flight):
        if k==0 or k==1:
            return flight['Poids vol arrivée']
        else:
            return flight['Poids vol départ']
    elif can_breakable(flight):
        if k==0:
            return flight['Poids vol arrivée']
        else: 
            return flight['Poids vol départ']
    else:
        return flight['Poids total rotation']


def mycombinations(r):
    return list(combinations(r,2)) + list(zip(r,r)) + list(combinations(reversed(r),2))

# p[i][j] is the parking (code) of the jth task of ith flight
p = VarArray(size=(nFlights,3), dom=range(0,nParkings))

# r[i][j] is the reward (strategy satisfaction between 0 and 100) of the jth task of ith flight  
r = VarArray(size=(nFlights,3), dom=range(101))


nNotBreak = Var(dom=range(nFlights*2))


satisfy(

    # taking into account only parkings authorized for flights
    [p[i][j] in table_capacities(t) for i,ts in enumerate(tasks) for j,t in enumerate(ts) if t is not None],

    #only allow breakable planes to be broken
    [AllEqual(p[i]) for i,t in enumerate(tasks) if not can_breakable(flights[i])],

    #only allow breakable planes with sufficient rotation time to be broken into 3 tasks
    [(p[i][1]==p[i][2]) for i,flight in enumerate(flights) if can_breakable(flight) and not can_breakable_3_task(flight)],

    # taking into account shadings 
    [(p[i][k1], p[j][k2]) not in table_shadings() for i, j in combinations(range(nFlights), 2) for k1,k2 in mycombinations(range(3))  if are_overlapping_task(tasks[i][k1], tasks[j][k2])],

    # taking into account reduction 
    [(p[i][k1], p[j][k2]) not in table_reductions(i,j) for i, j in combinations(range(nFlights), 2) for k1,k2 in mycombinations(range(3))  if are_overlapping_task(tasks[i][k1], tasks[j][k2])],

    # computing rewards
    [(p[i][k], r[i][k]) in table_rewards(flight) for i, flight in enumerate(flights) for k in range(3)],

    # all the flight must be affected
    [(p[i][0]>=0) for i in range(nFlights)],

    # calculate the number of breakable flights that have the same parking for all tasks 
    (nNotBreak==
    Sum([p[i][0]==p[i][1] for i in range(nFlights) if can_breakable(flights[i]) and not can_breakable_3_task(flights[i])]) + 
    Sum([(p[i][0]==p[i][1]) & (p[i][1]==p[i][2]) for i in range(nFlights) if can_breakable_3_task(flights[i])]))
)



maximize(
    nNotBreak + Sum([r[i][k] * get_weight(flight,k) for k in range(3) for i,flight in enumerate(flights)])
)
annotate(
    decision=r
)

###
# Below, compilation and execution of the solver
###

instance = compile()
status, solution = Ace().solve(instance, "limit=300runs,args=-cm,-lv,limit_time=170")
print("\n", status,solution)

if solution and solution.variables:
    def pretty_flight(i,j,t):

        i2 = i*3
        plane, company = t['Type avion'], t['Compagnie']
        arrival =  to_datetime(date + " 00:00:00") if t['arr'].strftime('%d')[0:2] == "04" else t['arr']  # hard coding for 03
        departure = to_datetime(date + " 23:00:00") if t['dep'].strftime('%d')[0:2] == "06" else t['dep']  # hard coding for 05
        
        parking, reward = parkings[int(solution.values[i2+j])], int(solution.values[nFlights*3 + i2 + j])
        n5 = int((departure - arrival).total_seconds()) / 300  # number of slots of 5 minutes
        result = {"index": i,"task":j, "plane": plane, "company": company, "arrival": arrival.strftime('%d/%m/%Y %H:%M:%S'), "departure": departure.strftime('%d/%m/%Y %H:%M:%S'), "parking": parking, "reward": reward, "n5": n5}
        print(result)
        return result


    with open("pproblems/adp/solutionPlaneParkingTask.json", 'w') as g:
        g.write("let flights = ")
        a = list(map(dict,set([tuple(sorted(pretty_flight(i,j, t).items())) for i, task in enumerate(tasks) for j,t in enumerate(task) if t is not None])))
        print(len(a),len(tasks)*3)
        json.dump(a, g, separators=(',', ':'))
    print("Generation of the JSON solution file solutionPlaneParking.json completed.")

            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie dep']})
            # tmp.append({'i':i,'arr':arr1,'dep':dep1,'Type avion':flight['Type avion'],'Compagnie':flight['Comapgnie dep']})
# solver = AbsconPy4J()
# solver.loadXCSP3(xml)
