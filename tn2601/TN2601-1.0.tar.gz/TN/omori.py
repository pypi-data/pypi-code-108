import numpy as np

class ex1:
    def __init__(self):
        self.intentos = 0
        pass
    
    def _RK4(self, f, ti, tf, h, y0, args):
        N = int((tf-ti)/h)
        t = np.linspace(ti,tf,N)
        y_RK4 = np.zeros(N)
        y_RK4[0] = y0
        for i in range(N-1):
            g1 = f(t[i]    , y_RK4[i]       , args)
            g2 = f(t[i]+h/2, y_RK4[i]+h/2*g1, args)
            g3 = f(t[i]+h/2, y_RK4[i]+h/2*g2, args)
            g4 = f(t[i]+h  , y_RK4[i]+h*g3  , args)
            y_RK4[i+1] = y_RK4[i] + h/6*(g1+2*g2+2*g3+g4)
        return y_RK4

    def hint(self):
        print("Recuerde que debe imponer la misma condición inicial que las partes anteriores.")
        print("El método de RK4 se basa en calcular g1, g2, g3 y g4, luego calcular el siguiente")
        print("elemento de la solución con la recurrencia conocida.")
        pass 

    def check(self,y,f,ti,tf,h,y0,args):
        if np.var(y)!=0:
            self.intentos += 1
        correct = True
        y_ref = self._RK4(f, ti, tf, h, y0, args)
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

        return y_ref
        

    def solution(self):
        if self.intentos == 0:
            print("Debe intentarlo al menos una vez.")
        else:
            print("Se plantea el siguiente código como solución:")
            print()
            print("def RK4(f, ti, tf, h, y0, args):")
            print("    N = int((tf-ti)/h)")
            print("    t = np.linspace(ti,tf,N)")
            print("    y_RK4 = np.zeros(N)")
            print("    y_RK4[0] = y0")
            print("    for i in range(N-1):") 
            print("        g1 = f(t[i]    , y_RK4[i]       , args)")  
            print("        g2 = f(t[i]+h/2, y_RK4[i]+h/2*g1, args)")  
            print("        g3 = f(t[i]+h/2, y_RK4[i]+h/2*g2, args)")   
            print("        g4 = f(t[i]+h  , y_RK4[i]+h*g3  , args)")   
            print("        y_RK4[i+1] = y_RK4[i] + h/6*(g1+2*g2+2*g3+g4)")
            print("    return y_RK4")
        pass