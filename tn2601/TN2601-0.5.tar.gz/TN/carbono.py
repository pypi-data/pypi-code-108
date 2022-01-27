from google.colab import _message
import numpy as np

class ex1:
    def __init__(self):
        pass

    def hint(self):
        print("Recuerden que debe ocupar lo mismo que en la parte anterior solo cambiando el argumento")
        print("de solve_ivp para el método de BDF.")

    def check(self):
        nbstr = _message.blocking_request('get_ipynb', request='', timeout_sec=10)
        for i in range(len(nbstr['ipynb']["cells"])):
            if nbstr['ipynb']["cells"][i]["source"][0]=="from scipy.integrate import solve_ivp\n":
                ans = nbstr['ipynb']["cells"][i]["source"][-1]
                if ans.replace(" ","").upper()=="SOL=SOLVE_IVP(F,(TI,TF),X0,METHOD='BDF',ARGS=ARGS)":
                    print("Correcto!")
                else:
                    print("Incorrecto")

    def solution(self):
        print("sol = solve_ivp(F, (ti,tf), X0, method='BDF', args=args)")