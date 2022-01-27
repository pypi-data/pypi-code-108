import numpy as np

class ex1:
    def __init__(self):
        self.intentos = 0
        pass

    def _Euler_Retrogrado(self, ti, tf, h, y0, args):
        R, alpha, gamma1, C = args
        N = int((tf-ti)/h)
        t = np.linspace(ti,tf,N)
        y_e = np.zeros(N)
        y_e[0] = y0
        for i in range(N-1):
            y_e[i+1] = y_e[i]/(1-h*(R-alpha*gamma1*C))
        return (t, y_e)

    def hint(self):
        print("Recuerde que debe generar una recurrencia particular para este problema.")
        print("Para ello reemplace f(t,T_e)=(R-alpha*gamma1*C)*T_e en la recurrencia para Euler retrógrado,")
        print("con esto podrá despejar T_e[i+1].")
        pass

    def check(self, y, ti, tf, h, y0, args):
        N = int((tf-ti)/h)
        if not np.var(y)==0:
            self.intentos += 1
        correct = True
        t_ref, y_ref = self._Euler_Retrogrado(ti, tf, h, y0, args)
        if len(y_ref) != len(y):
            print("Incorrecto, el largo de los arreglos no coincide.")
            print()
            correct = False
        else:
            for i in range(len(y_ref)):
                if abs(y[i]-y_ref[i])>0.1*abs(y_ref[i]):
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
            print("def euler_retrogrado(ti, tf, h, y0, args):")
            print("    R, alpha, gamma1, C = args")
            print("    N = int((tf-ti)/h)")
            print("    t = np.linspace(ti,tf,N)")
            print("    y_e = np.zeros(N)")
            print("    y_e[0] = y0")
            print("    for i in range(N-1):")
            print("        y_e[i+1] = y_e[i]/(1-h*(R-alpha*gamma1*C))")
            print("    return (t, y_e)")
        pass