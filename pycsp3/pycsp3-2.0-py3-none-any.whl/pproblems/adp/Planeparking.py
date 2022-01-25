#  sudo pip3 install py4j && sudo pip3 install pandas && sudo pip3 install xlrd

# ATTENTION: we do not convert to  namedtuples (line 131 in compiler) because keys have special characters, and
# we use for example data["parkings"] instead of data.parkings

import datetime
import json
import math
from collections import OrderedDict

from pycsp3 import *
from pycsp3.solvers.ace import Ace

date = "04/09/2019"  # hard coding for the moment (see also in the creation of the JSON solution file)
k_arrival, k_departure = 300, 300  #  hard coding for the time security in seconds

# note that data.ordonnancement, data.reductions, data.traitement and data.vols are not used

# ### about parkings
parkings = data["parkings"]['Code']
parking_indexes = OrderedDict((parking, i) for i, parking in enumerate(parkings))  # keys are parkings (actually, their codes) and values their indexes
possible_parkings = OrderedDict()  # per plane type
for i, ta in enumerate(data["capacites"]['TA_CLE']):
    possible_parkings.setdefault(ta, []).append(data["capacites"]['RSC_COD'][i])
nParkings = len(parkings)

# ### about flights
flights = [{key: data["volsStrategies"][key][i] for key in data["volsStrategies"].keys()} for i in range(len(data["volsStrategies"]['Date arr']))
           if date in {data["volsStrategies"]['Date arr'][i].split(" ")[0], data["volsStrategies"]['Date dep'][i].split(" ")[0]}]
nFlights = len(flights)


def table_capacities(flight):
    return {parking_indexes[parking] for parking in possible_parkings[flight['Type Avion']]}


def table_rewards(flight):
    target_parkings = [strategy.split("/")[1] for strategy in data["strategies"]['Ressource'] if "/" in strategy]  # parkings without the character "/"
    table = set()
    for i, parking in enumerate(parkings):
        value = data["strategies"][flight['Stratégie code dep']][target_parkings.index(parking)] if parking in target_parkings else 0
        table.add((i, int(value) if not math.isnan(value) else 0))
    return table


def table_shadings():
    p1, p2 = data["ombrages"]['RSC_COD'], data["ombrages"]['RSC_COD_OMBRE']
    assert len(p1) == len(p2)
    return (
        {(i, i) for i in range(nParkings)}  # conflict if same parking
        | {(parking_indexes[p1[i]], parking_indexes[p2[i]]) for i in range(len(p1))}  # conflict if shading between parkings
    )


def to_datetime(s):
    part1, part2 = s.split(" ")
    day, month, year, hour, minute, second = [int(v) for v in part1.split("/")] + [int(v) for v in part2.split(":")]
    return datetime.datetime(year, month, day, hour, minute, second)


def are_overlapping(flight1, flight2):
    arr1 = to_datetime(flight1['Date arr']) - datetime.timedelta(seconds=k_arrival)
    dep1 = to_datetime(flight1['Date dep']) + datetime.timedelta(seconds=k_departure)
    arr2 = to_datetime(flight2['Date arr']) - datetime.timedelta(seconds=k_arrival)
    dep2 = to_datetime(flight2['Date dep']) + datetime.timedelta(seconds=k_departure)
    return arr1 < dep2 and arr2 < dep1


# p[i] is the parking (code) of the ith flight
p = VarArray(size=nFlights, dom=range(nParkings))

# r[i] is the reward (strategy satisfaction between 0 and 100) of the ith flight  
r = VarArray(size=nFlights, dom=range(101))

satisfy(

    # taking into account only parkings authorized for flights
    [p[i] in table_capacities(flight) for i, flight in enumerate(flights)],

    # computing rewards
    [(p[i], r[i]) in table_rewards(flight) for i, flight in enumerate(flights)],

    # taking into account shadings
    [(p[i], p[j]) not in table_shadings() for i, j in combinations(range(nFlights), 2) if are_overlapping(flights[i], flights[j])]
)

maximize(
    r * [flight['Poids total rotation'] for flight in flights]
)

annotate(
    decision=r
)

###
# Below, compilation and execution of the solver
###

instance = compile()
status, solution = Ace().solve(instance, "limit=135runs,v,args=-cm,-lv,-t=180s")
print("\n", solution)

if solution and solution.variables:
    def pretty_flight(i, flight):
        plane, company = flight['Type Avion'], flight['Comapgnie arr']
        arrival = date + " 00:00:00" if flight['Date arr'][0:2] == "03" else flight['Date arr']  # hard coding for 03
        departure = date + " 23:55:00" if flight['Date dep'][0:2] == "05" else flight['Date dep']  # hard coding for 05
        parking, reward = parkings[int(solution.values[i])], int(solution.values[nFlights + i])
        n5 = int((to_datetime(departure) - to_datetime(arrival)).total_seconds()) / 300  # number of slots of 5 minutes
        return {"index": i, "plane": plane, "company": company, "arrival": arrival, "departure": departure, "parking": parking, "reward": reward, "n5": n5}


    with open("g7_todo/solutionPlaneParking.json", 'w') as g:
        g.write("let flights = ")
        json.dump([pretty_flight(i, flight) for i, flight in enumerate(flights)], g, separators=(',', ':'))
    print("Generation of the JSON solution file solutionPlaneParking.json completed.")


# solver = AbsconPy4J()
# solver.loadXCSP3(xml)
