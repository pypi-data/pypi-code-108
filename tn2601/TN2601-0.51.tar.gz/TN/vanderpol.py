import numpy as np 

class ex1:
    def __init__(self):
        self.intentos = 0
        pass

    def _Heun(self, f, ti, tf, N, X0, args):
        t = np.linspace(ti, tf, N)
        h = t[1] - t[0]
        ndim = len(X0)
        X = np.zeros((N,ndim))
        X[0] = X0
        for i in range(N-1):
            X_tilda = X[i] + h*f(t[i],X[i],args)
            X[i+1] = X[i] + h/2*(f(t[i],X[i],args)+f(t[i+1],X_tilda,args))
        return (t,X)

    def hint(self):
        print("Recuerde que para el método de Heun debe calcular primero un paso previo para y,")
        print("que llamamos y_tilda y luego actualizar la solución.")
        pass

    def check(self, y, f, ti, tf, N, y0, args):
        if np.var(y) != 0:
            self.intentos += 1
        correct = True
        t_ref, y_ref = self._Heun(f, ti, tf, N, y0, args)
        if len(y_ref) != len(y):
            print("Incorrecto, el largo de los arreglos no coincide.")
            print()
            correct = False
        else:
            for i in range(len(y_ref)):
                if abs(y[i][0]-y_ref[i][0])>0.01*abs(y_ref[i][0]) or abs(y[i][1]-y_ref[i][1])>0.01*abs(y_ref[i][1]):
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
            print("Debe intertarlo al menos una vez.")
        else:
            print("Se deja un código que devuelve la solución esperada:")
            print()
            print("def Heun(f, ti, tf, N, X0, args):")
            print("    t = np.linspace(ti, tf, N)")
            print("    h = t[1] - t[0]")
            print("    ndim = len(X0)")
            print("    X = np.zeros((N,ndim))")
            print("    X[0] = X0")
            print("    for i in range(N-1):")
            print("        X_tilda = X[i] + h*f(t[i],X[i],args)")
            print("        X[i+1] = X[i] + h/2*(f(t[i],X[i],args)+f(t[i+1],X_tilda,args))")
            print("    return (t,X)")
        pass