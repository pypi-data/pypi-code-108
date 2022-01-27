from google.colab import _message
import numpy as np

class ex1:
    def __init__(self):
        pass

    def hint(self):
        print("Recuerden que debe llamar a solve_ivp con los argumentos F_l, (0,a), X0 y entregando como")
        print("argumentos extras (args2,).")

    def check(self):
        nbstr = _message.blocking_request('get_ipynb', request='', timeout_sec=10)
        for i in range(len(nbstr['ipynb']["cells"])):
            if nbstr['ipynb']["cells"][i]["source"][0]=="from scipy.integrate import solve_ivp\n":
                ans = nbstr['ipynb']["cells"][i]["source"][-1]
                if ans.replace(" ","").upper()=="SOL=SOLVE_IVP(F_L,(0,A),X0,ARGS=(ARGS2,))":
                    print("Correcto!")
                else:
                    print("Incorrecto")

    def solution(self):
        print("sol = solve_ivp(F_l, (0, a), X0, args=(args2,))")