'''*******************************************************
  * Python Example Problems                             *
  *                                                     *
  * file coco.py                                        *
  * Example for the use of the Python language          *
  * (Complete Coco Problem.                             *
  *  Specify phase by PHASE parameter.                  *
  *  Data input in the model, not via data files.)      *
  *                                                     *
  * (c) 2018 Fair Isaac Corporation                     *
  *******************************************************'''

from __future__ import print_function
import xpress as xp

PHASE = 5

'''* Phase = 3: Multi-period parameterised model; mines always open
   * Phase = 4: Mines may open/closed freely; when closed save 20000 per month
   * Phase = 5: Once closed always closed; larger saving
'''

NT = 4       # Number of time periods
RP = [0, 1]  # Range of products (p)
RF = [0, 1]  # Range of factories (f)
RR = [0, 1]  # Range of raw materials (r)

RT = [i for i in range(NT)]  # time periods (t)

CPSTOCK = 2.0    # Unit cost to store any product p
CRSTOCK = 1.0    # Unit cost to store any raw mat. r
MXRSTOCK = 300   # Max. amount of r that can be stored each f and t

Post = [i for i in range(0, NT+1)]

# Amount of product p made at factory f
make = xp.vars(RP, RF, RT, name='make')

# Amount of product p sold from factory f in period t
sell = xp.vars(RP, RF, RT, name='sell')

# Amount of raw material r bought for factory f in period t
buy = xp.vars(RR, RF, RT, name='buy')

# Stock level of product p at factory f at start of period t
pstock = xp.vars(RP, RF, Post, name='pst')

# Stock level of raw material r at factory f at start of period t
rstock = xp.vars(RR, RF, Post, name='rst')

# 1 if factory f is open in period t, else 0
openm = xp.vars(RF, RT, name='openm', vartype=xp.binary)

REV = [[400, 380, 405, 350],
       [410, 397, 412, 397]]
CMAKE = [[150, 153],
         [75,  68]]
CBUY = [[100,  98,  97, 100],
        [200, 195, 198, 200]]
COPEN = [50000, 63000]
REQ = [[1.0, 0.5],
       [1.3, 0.4]]
MXSELL = [[650, 600, 500, 400],
          [600, 500, 300, 250]]
MXMAKE = [400, 500]
PSTOCK0 = [[50, 100],
           [50,  50]]
RSTOCK0 = [[100, 150],
           [50, 100]]

prob = xp.problem()
prob.addVariable(make, buy, sell, pstock, rstock, openm)

# Objective: maximize total profit
MaxProfit = (
    xp.Sum(REV[p][t] * sell[p, f, t] for p in RP
           for f in RF for t in RT) -              # revenue
    xp.Sum(CMAKE[p][f] * make[p, f, t] for p in RP
           for f in RF for t in RT) -            # prod. cost
    xp.Sum(CBUY[r][t] * buy[r, f, t] for r in RR
           for f in RF for t in RT) -              # raw mat. cost
    xp.Sum(CPSTOCK * pstock[p, f, t] for p in RP
           for f in RF for t in range(1, NT+1)) -  # p stor. cost
    xp.Sum(CRSTOCK * rstock[r, f, t] for r in RR
           for f in RF for t in range(1, NT+1)))   # r stor. cost

if PHASE == 4:                 # Factory fixed cost
    MaxProfit -= xp.Sum((COPEN[f] - 20000) * openm[f, t]
                        for f in RF for t in RT)
elif PHASE == 5:
    MaxProfit -= xp.Sum(COPEN[f] * openm[f, t] for f in RF for t in RT)

prob.setObjective(MaxProfit, sense=xp.maximize)

# Product stock balance
prob.addConstraint(pstock[p, f, t+1] == pstock[p, f, t]
                   + make[p, f, t] - sell[p, f, t]
                   for p in RP for f in RF for t in RT)

# Raw material stock balance
prob.addConstraint(rstock[r, f, t+1] == rstock[r, f, t] + buy[r, f, t] -
                   xp.Sum(REQ[p][r]*make[p, f, t] for p in RP)
                   for r in RR for f in RF for t in RT)

# Capacity limit at factory f
prob.addConstraint(xp.Sum(make[p, f, t] for p in RP) <= MXMAKE[f] * openm[f, t]
                   for f in RF for t in RT)

# Limit on the amount of prod. p to be sold
prob.addConstraint(xp.Sum(sell[p, f, t] for f in RF) <= MXSELL[p][t]
                   for p in RP for t in RT)

# Raw material stock limit
prob.addConstraint(xp.Sum(rstock[r, f, t] for r in RR) <= MXRSTOCK
                   for f in RF for t in range(NT))

if PHASE == 5:                 # Once closed, always closed
    prob.addConstraint(openm[f, t+1] <= openm[f, t]
                       for f in RF for t in range(NT - 1))

# Initial product levels
prob.addConstraint(pstock[p, f, 1] == PSTOCK0[p][f] for p in RP for f in RF)
# Initial raw material levels
prob.addConstraint(rstock[r, f, 1] == RSTOCK0[r][f] for r in RR for f in RF)

if PHASE < 4:
    prob.addConstraint(openm[f, t] == 1 for f in RF for t in RT)

prob.solve()  # Solve the LP or MIP-problem

# Print out the solution
print("Solution:\n Objective: ", prob. getObjVal())

hline = 60*"-"

print("Total profit: ", prob.getObjVal())
print(hline)
print(8*" ", "Period", end='')
for t in range(NT+1):
    print("{:8}".format(t), end='')
print("\n", hline)
print("Finished products\n",
      "=================")

for f in RF:
    print(" Factory", f)
    for p in RP:
        print(3*" ", "P", p, ":  Prod", 12*" ", end='', sep='')
        for t in RT:
            print("{:8.2f}".format(prob.getSolution(make[p, f, t])), end='')
        print('')
        print(8*" ", "Sell", 12*" ", end='', sep='')
        for t in RT:
            print("{:8.2f}".format(prob.getSolution(sell[p, f, t])), end='')
        print('')
        print(7*" ", "(Stock)", end='')
        for t in range(NT+1):
            print("  (", "{:4.1f}".format(prob.getSolution(pstock[p, f, t])),
                  ")", end='', sep='')
        print('')

print(hline)
print("Raw material\n",
      "============")
for f in RF:
    print(" Factory", f)
    for r in RR:
        print(3*" ", "R", r, ":  Buy", 12*" ", end='', sep='')
        for t in RT:
            print("{:8.2f}".format(prob.getSolution(buy[r, f, t])), end='')
        print('')
        print(8*" ", "Use", 12*" ", end='', sep='')
        for t in RT:
            print("{:8.2f}".format(sum(REQ[p][r] *
                                       prob.getSolution(make[p, f, t])
                                       for p in RP)), end='')
        print('')
        print(7*" ", "(Stock)", end='')
        for t in range(NT+1):
            print(" (", "{:4.1f}".format(prob.getSolution(rstock[r, f, t])),
                  ")", end='', sep='')
        print('')

print(hline)
