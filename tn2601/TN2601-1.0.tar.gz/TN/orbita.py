from google.colab import _message
import numpy as np

class ex1:
    def __init__(self):
        pass

    def hint(self):
        print("Recuerden que debe llamar a solve_ivp con los argumentos:")
        print("F, (ti,tf), X0, args=(args,)")

    def check(self):
        print("Revisando su solución...")
        print()
        nbstr = _message.blocking_request('get_ipynb', request='', timeout_sec=15)
        for i in range(len(nbstr['ipynb']["cells"])):
            if nbstr['ipynb']["cells"][i]["source"][0]=="from scipy.integrate import solve_ivp\n":
                ans = nbstr['ipynb']["cells"][i]["source"][-1]
                if ans.replace(" ","").upper()=="SOL=SOLVE_IVP(F,(TI,TF),X0,ARGS=(ARGS,))":
                    print("Correcto!")
                else:
                    print("Incorrecto")

    def solution(self):
        print("sol = solve_ivp(F, (ti, tf), X0, args=(args,))")