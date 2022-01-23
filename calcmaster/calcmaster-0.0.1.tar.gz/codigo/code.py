#programa que permita el ingreso de dos numeros y que calcule la suma, resta,
#multiplicación y división y muestre el resultado en pantalla.
class Calculadora:
    def __init__(self):             #metodo constructor para inicializar el programa
        self.num1 = float(input("Ingrese el primer número: "))
        self.num2 = float(input("Ingrese el segundo número: "))
    
    def Suma(self):                 #método para sumar dos números
        suma = self.num1 + self.num2
        print("El resultado de la suma es: ", suma)
    
    def Resta(self):                #método para restar dos números
        resta = self.num1 - self.num2
        print("El resultado de la resta es: ", resta)
    
    def Producto(self):             #método para multiplicar dos números
        producto = self.num1 * self.num2
        print("El resultado del producto es: ", producto)
    
    def Division(self):             #método para dividir dos números
        division = self.num1 / self.num2
        print("El resultado de la división es: ", division)
    
    def imprimir(self):             #método para mostrar los números ingresados
        print("Los números ingresados son ")
        print("Primer número: ", self.num1)
        print("Segundo número: ", self.num2)
