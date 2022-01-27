from google.colab import _message
import numpy as np

class ex1:
    def __init__(self):
        pass

    def hint(self):
        print("Recuerde que debe crear X0 y los argumentos en el mismo orden en que los recibe la función F2.")
        print("Además, debe llamar a solve_ivp con los argumentos F2, (0,T), X0, args=(args,) y específicar el")
        print("método con el argumento method.")

    def check(self):
        pos_answ1 = [
            "X0,ARGS=[A0,M0,1-A0-M0],(K1,K2,ALPHA)",
            "X0,ARGS=[A0,M0,S0],(K1,K2,ALPHA)",
            "X0,ARGS=[A0,M0,1-A0-M0],[K1,K2,ALPHA]",
            "X0,ARGS=[A0,M0,S0],[K1,K2,ALPHA]"
        ]
        pos_answ2 = [
            "SOL=SOLVE_IVP(F2,(0,T),X0,METHOD='RK23',ARGS=(ARGS,))",
            "SOL=SOLVE_IVP(F2,(0,T),X0,METHOD='DOP853',ARGS=(ARGS,))",
            "SOL=SOLVE_IVP(F2,(0,T),X0,METHOD='RADAU',ARGS=(ARGS,))",
            "SOL=SOLVE_IVP(F2,(0,T),X0,METHOD='DBF',ARGS=(ARGS,))",
            "SOL=SOLVE_IVP(F2,(0,T),X0,METHOD='LSODA',ARGS=(ARGS,))",
            'SOL=SOLVE_IVP(F2,(0,T),X0,METHOD="RK23",ARGS=(ARGS,))',
            'SOL=SOLVE_IVP(F2,(0,T),X0,METHOD="DOP853",ARGS=(ARGS,))',
            'SOL=SOLVE_IVP(F2,(0,T),X0,METHOD="RADAU",ARGS=(ARGS,))',
            'SOL=SOLVE_IVP(F2,(0,T),X0,METHOD="DBF",ARGS=(ARGS,))',
            'SOL=SOLVE_IVP(F2,(0,T),X0,METHOD="LSODA",ARGS=(ARGS,))'

        ]

        nbstr = _message.blocking_request('get_ipynb', request='', timeout_sec=10)
        for i in range(len(nbstr['ipynb']["cells"])):
            if nbstr['ipynb']["cells"][i]["source"][0]=="from scipy.integrate import solve_ivp\n":
                ans1 = nbstr['ipynb']["cells"][i]["source"][-2]
                ans2 = nbstr['ipynb']["cells"][i]["source"][-1]
                if ans1.replace(" ","").upper() not in pos_answ1:
                    print("Incorrecto, debe ingresar un vector de condición inicial y una lista o tupla")
                    print("para los argumentos, recuerde el orden de estos.")
                    return None 
                elif ans2.replace(" ","").upper()=="SOL=SOLVE_IVP(F2,(0,T),X0,METHOD='RK45',ARGS=(ARGS,))":
                    print("Incorrecto, debe ocupar un método distinto a RK45.")
                    return None
                elif ans2.replace(" ","").upper() not in pos_answ2:
                    print("Incorrecto, recuerde que debe colocar los argumentos en el orden correcto")
                    print("y específicar que método va a utilizar.")
                    return None
                else:
                    print("Correcto!")
                    return None

    def solution(self):
        print("Se deja una solución que utiliza el método LSODA:")
        print()
        print("X0, args = [a0, m0, 1-a0-m0], (k1, k2, alpha)")
        print("sol = solve_ivp(F2, (0,T), X0, method='LSODA', args=(args,))")