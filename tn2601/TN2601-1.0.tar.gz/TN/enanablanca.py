import numpy as np

class ex1:
    def __init__(self):
        self.intentos = 0
        pass

    def _Heun(self,f,zi,zf,h,X0,a,args):
        N = int((zf-zi)/h)
        z = np.linspace(zi, zf, N)
        ndim = len(X0)
        X = np.zeros((N, ndim))
        X[0] = X0
        for i in range(N-1):
            X_tilda = X[i] + h*f(z[i],X[i],args)
            X[i+1] = X[i] + h/2*(f(z[i],X[i],args)+f(z[i+1],X_tilda,args))
            if X[i+1,0] <= a:
                j = i
                break 
        X = X[0:j]
        z = z[0:j]
        return (z,X)

    def hint(self):
        print("Recuerde que para el método de Heun debe calcular primero un paso intermedio, para luego actualizar")
        print("la solución. Además, para este problema debe imponer que si X[:,0] es menor que a,")
        print("entonces el método se detiene y trunque z y X hasta dicha iteración.")
        print("Si obtiene el error: Los largos no coinciden, puede que tenga un problema al truncar las soluciones.")
        print("")

    def check(self, y, f, ti, tf, h, y0, a, args):
        if np.var(y) != 0:
            self.intentos += 1
        correct = True
        t_ref, y_ref = self._Heun(f, ti, tf, h, y0, a, args)
        if abs(len(y_ref)-len(y)) > 1:
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
            print("Correcto!")
            print()

        return (t_ref, y_ref)

    def solution(self):
        if self.intentos==0:
            print("Debe intentarlo al menos una vez.")
        else:
            print("A continuación, se deja un código que implementa lo pedido.")
            print()
            print("def Heun(f, zi, zf, h, X0, a, args):")
            print("    N = int((zf-zi)/h)")
            print("    z = np.linspace(zi, zf, N)")
            print("    ndim = len(X0)")
            print("    X = np.zeros((N, ndim))")
            print("    X[0] = X0")
            print("    for i in range(N-1):")
            print("        X_tilda = X[i] + h*f(z[i], X[i], args)")
            print("        X[i+1] = X[i] + h/2*(f(z[i], X[i], args)+f(z[i+1], X_tilda, args))")
            print("        if X[i+1,0]<=a:")
            print("            j = i")
            print("            break ")
            print("    X = X[0:j]")
            print("    z = z[0:j]")
            print("    return (z,X)")