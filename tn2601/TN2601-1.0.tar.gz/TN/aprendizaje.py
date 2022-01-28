import numpy as np

class ex1:
    def __init__(self):
        self.intentos = 0
        pass

    def _RK4(self, f, ti, tf, N, y0):
        t = np.linspace(ti,tf,N)
        h = t[1] - t[0]
        y_RK4 = np.zeros(N)
        y_RK4[0] = y0
        for i in range(N-1):
            g1 = f(t[i]    , y_RK4[i]       )
            g2 = f(t[i]+h/2, y_RK4[i]+h/2*g1)
            g3 = f(t[i]+h/2, y_RK4[i]+h/2*g2)
            g4 = f(t[i]+h  , y_RK4[i]+h*g3  )
            y_RK4[i+1] = y_RK4[i] + h/6*(g1+2*g2+2*g3+g4)
        return (t, y_RK4)

    def hint(self):
        print("Recuerde que para programar RK4 debe calcular primero los g1, g2, g3, g4 y luego actualizar la")
        print("solución. La función de lado derecho recibe los argumentos en el siguiente orden: t (tiempo), E.")

    def check(self, y, f, ti, tf, N, y0):
        if np.var(y)!=0:
            self.intentos += 1
        correct = True
        t_ref, y_ref = self._RK4(f, ti, tf, N, y0)
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
            print("Correcto!")
            print()

        return (t_ref, y_ref)

    def solution(self):
        if self.intentos==0:
            print("Debe intentarlo al menos una vez.")
        else:
            print("A continuación, se presenta un código que genera la solución:")
            print()
            print("def RK4(f, ti, tf, N, E0):")
            print("    t = np.linspace(ti,tf,N)")
            print("    h = t[1] - t[0]")
            print("    E_RK4 = np.zeros(N)")
            print("    E_RK4[0] = E0")
            print("    for i in range(N-1):")
            print("        g1 = f(t[i]    , E_RK4[i]       )")
            print("        g2 = f(t[i]+h/2, E_RK4[i]+h/2*g1)")
            print("        g3 = f(t[i]+h/2, E_RK4[i]+h/2*g2)")
            print("        g4 = f(t[i]+h  , E_RK4[i]+h*g3  )")
            print("        E_RK4[i+1] = E_RK4[i] + h/6*(g1+2*g2+2*g3+g4)")
            print("    return (t, E_RK4)")