from google.colab import _message
import numpy as np

class ex1:
    def __init__(self):
        pass

    def hint(self):
        print("Recuerde que debe llamar a solve_ivp con los argumentos:")
        print("fd1, (ti,tf), [y0], args=(args,)")

    def check(self):
        nbstr = _message.blocking_request('get_ipynb', request='', timeout_sec=6)
        for i in range(len(nbstr['ipynb']["cells"])):
            if nbstr['ipynb']["cells"][i]["source"][0]=="from scipy.integrate import solve_ivp\n":
                ans = nbstr['ipynb']["cells"][i]["source"][-1]
                if ans.replace(" ","").upper()=="SOL=SOLVE_IVP(FD1,(TI,TF),[Y0],ARGS=(ARGS,))":
                    print("Correcto!")
                else:
                    print("Incorrecto")

    def solution(self):
        print("sol = solve_ivp(fd1, (ti, tf), [y0], args=(args,))")


class ex2:
    def __init__(self):
        self.intentos = 0
        pass

    def _RK4(self, f, ti, tf, N, y0, args):
        t = np.linspace(ti,tf,N)
        h = t[1] - t[0]
        y_RK4 = np.zeros(N)
        y_RK4[0] = y0
        for i in range(N-1):
            g1 = f(t[i]    , y_RK4[i]       , args)
            g2 = f(t[i]+h/2, y_RK4[i]+h/2*g1, args)
            g3 = f(t[i]+h/2, y_RK4[i]+h/2*g2, args)
            g4 = f(t[i]+h  , y_RK4[i]+h*g3  , args)
            y_RK4[i+1] = y_RK4[i] + h/6*(g1+2*g2+2*g3+g4)
        return (t, y_RK4)

    def hint(self):
        print("Recuerde que para programar RK4 debe calcular primero los g1, g2, g3, g4 y luego")
        print("actualizar la solución. La función de lado derecho recibe los argumentos en el")
        print("siguiente orden: t (tiempo), y, args.")

    def check(self, y, f, ti, tf, N, y0, args):
        comparison = y==np.zeros(N)
        if not comparison.all():
            self.intentos += 1
        correct = True
        t_ref, y_ref = self._RK4(f, ti, tf, N, y0, args)
        if len(y_ref) != len(y):
            print("Incorrecto, el largo de los arreglos no coincide.")
            print()
            correct = False
        else:
            for i in range(len(y_ref)):
                if abs(y[i]-y_ref[i])>0.01*abs(y_ref[i]):
                    print("Incorrecto, los valores no coinciden.")
                    print()
                    correct = False
                    break
        if correct:
            print("Correcto.")
            print()

        return (t_ref, y_ref)

    def solution(self):
        if self.intentos==0:
            print("Debe intentarlo al menos una vez")
        else:
            print("A continuación, se presenta un código que genera la solución:")
            print()
            print("def RK4(f, ti, tf, N, y0, args):")
            print("    t = np.linspace(ti,tf,N)")
            print("    h = t[1] - t[0]")
            print("    y_RK4 = np.zeros(N)")
            print("    y_RK4[0] = y0")
            print("    for i in range(N-1):")
            print("        g1 = f(t[i]    , y_RK4[i]       , args)")
            print("        g2 = f(t[i]+h/2, y_RK4[i]+h/2*g1, args)")
            print("        g3 = f(t[i]+h/2, y_RK4[i]+h/2*g2, args)")
            print("        g4 = f(t[i]+h  , y_RK4[i]+h*g3  , args)")
            print("        y_RK4[i+1] = y_RK4[i] + h/6*(g1+2*g2+2*g3+g4)")
            print("    return (t, y_RK4)")