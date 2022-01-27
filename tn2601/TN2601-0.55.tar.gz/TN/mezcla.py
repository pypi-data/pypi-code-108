import numpy as np

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
        print("siguiente orden: x, C, args.")

    def check(self, y, f, ti, tf, h, y0, args):
        if np.var(y)!=0:
            self.intentos += 1
        correct = True
        t_ref, y_ref = self._RK4(f, ti, tf, h, y0, args)
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
            print("def RK4(F, xi, xf, h, C0, args):")
            print("    N = int((xf-xi)/h)")
            print("    x = np.arange(xi, xf+h, h)")
            print("    C = np.zeros((len(x),len(C0)))")
            print("    C[0] = y0")
            print("    for i in range(N-1):")
            print("        g1 = F(x[i]    , C[i]       , args)")
            print("        g2 = F(x[i]+h/2, C[i]+h/2*g1, args)")
            print("        g3 = F(x[i]+h/2, C[i]+h/2*g2, args)")
            print("        g4 = F(x[i]+h  , C[i]+h*g3  , args)")
            print("        C[i+1] = C[i] + h/6*(g1+2*g2+2*g3+g4)")
            print("    return (x, C)")