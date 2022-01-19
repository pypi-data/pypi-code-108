from math import sqrt
import decimal
import os

def clear():
  os.system("clear" if os.name!='nt' else "cls")

def factorielle(n):
   if n == 0:
      return 1
   else:
      F = 1
      for k in range(2,n+1):
         F = F * k
      return F

class Pi:
  def __init__(self, precision=10):
    self.val = self.calculatePi(precision)

  def calculatePi(self, precision):
    D = decimal.Decimal
    decimal.getcontext().prec = precision+1
    somme = 0

    for i in range(precision):
      somme += ((D(factorielle(4*i)))/(D((factorielle(i))**4))*(D((1103+26390*i))/(D((4*99)**(4*i)))))

    inverse_pi = D(somme*(D((D(2*sqrt(2)))/9801)))
    pi = D(1/inverse_pi)
    return pi


class E:
  def __init__(self, precision=10):
    self.val = self.calculate_e(precision)

  def calculate_e(self, precision):
    e=0
    for i in range(precision+1):
      e+=1/factorielle(i)
    return e


def kparmin(k,n):
  parmi=int((factorielle(n))/((factorielle(k))*factorielle(n-k)))
  return parmi

def parmi3(i,j,k,p):
  parmi=int(factorielle(p)/(factorielle(i)*factorielle(j)*factorielle(k)))
  return parmi

def trinome_newton(p):
  expression=""
  for i in range(p+1):
    for j in range(p-i+1):
      k=p-i-j
      if i==0:
        texta=""
      else:
        texta="a"
      if j==0:
        textb=""
      else:
        textb="b"
      if k==0:
        textc=""
      else:
        textc="c"
      if i==1 or i==0:
        puissancetexta=""
      else:
        puissancetexta="^"+str(i)
      if j==1 or j==0:
        puissancetextb=""
      else:
        puissancetextb="^"+str(j)
      if k==1 or k==0:
        puissancetextc=""
      else:
        puissancetextc="^"+str(k)
      if i==0 and j==0:
        if parmi3(int(i),int(j),int(k),int(p))==1:
          parmitext=""
        expression=parmitext+texta+puissancetexta+textb+puissancetextb+textc+puissancetextc
      else:
        if parmi3(int(i),int(j),int(k),int(p))==1:
          parmitext=""
        else:
          parmitext=str(parmi3(int(i),int(j),int(k),int(p)))
        expression=parmitext+texta+puissancetexta+textb+puissancetextb+textc+puissancetextc+" + "+expression
  return expression

def binome_newton(p):
  expression=""
  for k in range(p+1):
    if k==1 or k==0:
      puissancetext=""
    else:
      puissancetext="^"+str(k)
    if p-k==1 or p-k==0:
      puissancetext2=""
    else:
      puissancetext2="^"+str(p-k)
    if k==0:
      texta=""
    else:
      texta="a"
    if p-k==0:
      textb=""
    else:
      textb="b"
    if k==0:
      if kparmin(int(k),int(p))==1:
        parmitext=""
      expression=parmitext+texta+puissancetext+textb+puissancetext2
    else:
      if kparmin(int(k),int(p))==1:
        parmitext=""
      else:
        parmitext=str(kparmin(int(k),int(p)))
      expression=parmitext + texta + puissancetext + textb + puissancetext2 + " + " + expression
  return expression


def is_prime2(x):
  #x=int(input("quel est le nombre dont tu veuiles vérifier la primalité ?\n"))
  y=2

  a=1
  while a==1:
    if x==1:
      return 0
      #print("ce n'est pas un nombre premier")
      break
    elif x==2:
      return 1
      #print("c'est  un nombre premier")
      break
    else:
      while y<x:
        if x%y==0:
          return 0
          #print("ce n'est pas un nombre premier")
          a+=1
          break


        else:
          y+=1
          if x==y:
            return 1
            #print("c'est un nombre premier")


def is_prime1(i):
  run = True
  while run==True :
    #i=int(input("Tapez un nombre "))
    primalite=[]
    for a in range(1,i+1):
      if i%a==0:
        primalite.append(a)
    if primalite==[1, i]:
      return 1
      #print(i,"est un nombre premier")
    else :
      return 0
      #print(i,"n'est pas un nombre premier")
  return



class Polynome:
  def __init__(self, a, b, c):
    self.a = a
    self.b = b
    self.c = c
    self.tableauVariations = ""
    self.variations = ""
    self.extremum = []
    self.nombre_racines = 0
    self.racines = []
    self.calculate()

  def etude(self):
    print("Etude du polynôme:", str(self.a), "x^2 ", '+' if self.b>=0 else "", str(self.b), "x", '+' if self.c>=0 else "", str(self.c))
    print("\n\n")
    print("Racines")
    print("\n")
    for racine in self.racines:
      print(racine, end="")
    print("\n\n\n")
    print("Variations:")
    print("\n")
    print("\n".join(self.variations))
    print("\n\n")
    print("Tableau de variation:")
    print("\n")
    print(self.tableauVariations)
    print("\n\n")
    print("Extremum:")
    print("\n")
    print(self.extremum[0],":", str(self.extremum[1]), "atteint en", str(self.extremum[2]))


  def calculate(self):
    if self.a!=0:
      d=(self.b**2)-(4*self.a*self.c)
      if d<0:
        #print("\n\nIl n'y a pas de racines")
        self.nombre_racines = 0
        self.racines = []
        if self.a<0:
          #print("\nla fonction est strictement négative")
          self.variations = ["FONCTION STRICTEMENT NEGATIVE"]
          #print("\n\nNous allons maintenant vous tracer un tableau de variation de très grande qualité (avec des valeurs tronquées pour plus de facilité dans la lecture). A vous de remplacer les valeurs valeurs arrondies par les racines. On ne va quand même pas tout vous faire...")
          xm=(-self.b)/(2*self.a)
          xmd=int(xm)
          #print("\n\n |+∞    "+str(xmd)+"   -∞|\n |   ↗   |  ↘  |\n |_______|_____|")
          self.tableauVariations = "|+∞    "+str(xmd)+"   -∞|\n |   ↗   |  ↘  |\n |_______|_____|"
          m=(-self.d)/(4*self.a)
          #print("\n\n Le maximum est donc "+str(m)+" atteint en "+str(xm))
          self.extremum = ("MAX", m, xm)
        elif self.a>0:
          #print("\nla fonction est strictement positive")
          self.variations = ["FONCTION STRICTEMENT POSITIVE"]
          #print("\n\nNous allons maintenant vous tracer un tableau de variation de très grande qualité (avec des valeurs tronquées pour plus de facilité dans la lecture). A vous de remplacer les valeurs valeurs arrondies par les racines. On ne va quand même pas tout vous faire...")
          xm=(-self.b)/(2*self.a)
          xmd=int(xm)
          #print("\n\n |+∞    "+str(xmd)+"   -∞|\n |   ↘  |  ↗  |\n |______|_____|")
          self.tableauVariations = "|+∞    "+str(xmd)+"   -∞|\n |   ↘  |  ↗  |\n |______|_____|"
          m=(-d)/(4*self.a)
          #print("\n\n Le mininum est donc "+str(m)+" atteint en "+str(xm))
          self.extremum = ("MIN", m, xm)
      elif d>0:
        x1=((-self.b)+sqrt(d))/(2*self.a)
        x2=((-self.b)-sqrt(d))/(2*self.a)
        #print("\nLe polynome a deux racines : "+str(x1)+" et "+str(x2))
        self.nombre_racines = 2
        self.racines = [x1, x2]
        if self.a<0:
          if x1<x2:
            self.variations = ["la fonction est négative sur ]-∞;"+str(x1)+"]U["+str(x2)+";+∞[", "la fonction est positive sur ["+str(x1)+";"+str(x2)+"]"]
            # print("la fonction est négative sur ]-∞;"+str(x1)+"]U["+str(x2)+";+∞[")
            # print("la fonction est positive sur ["+str(x1)+";"+str(x2)+"]")
            xm=(-self.b)/(2*self.a)
            m=(-d)/(4*self.a)
            print("\n\n Le maximum est donc "+str(m)+" atteint en "+str(xm))
            self.maximum = ("MAX", m, xm)
          if x1>x2:
            self.variations = ["la fonction est négative sur ]-∞;"+str(x2)+"]U["+str(x1)+";+∞[", "la fonction est positive sur ["+str(x2)+";"+str(x1)+"]"]
            # print("la fonction est négative sur ]-∞;"+str(x2)+"]U["+str(x1)+";+∞[")
            # print("la fonction est positive sur ["+str(x2)+";"+str(x1)+"]")
          #print("\n\nNous allons maintenant vous tracer un tableau de variation de très grande qualité (avec des valeurs tronquées pour plus de facilité dans la lecture). A vous de remplacer les valeurs valeurs arrondies par les racines. On ne va quand même pas tout vous faire...")
          xm=(-self.b)/(2*self.a)
          xmd=int(xm)
          #print("\n\n |+∞    "+str(xmd)+"   -∞|\n |   ↗  |  ↘  |\n |______|_____|")
          self.tableauVariations = "|+∞    "+str(xmd)+"   -∞|\n |   ↗  |  ↘  |\n |______|_____|"
          m=(-self.d)/(4*self.a)
          #print("\n\n Le maximum est donc "+str(m)+" atteint en "+str(xm))
          self.maximum = ("MAX", m, xm)
        if self.a>0:
          if x1<x2:
            self.variations = ["la fonction est positive sur ]-∞;"+str(x1)+"]U["+str(x2)+";+∞[", "la fonction est négative sur ["+str(x1)+";"+str(x2)+"]"]
            # print("la fonction est positive sur ]-∞;"+str(x1)+"]U["+str(x2)+";+∞[")
            # print("la fonction est négative sur ["+str(x1)+";"+str(x2)+"]")
          if x1>x2:
            self.variations = ["la fonction est positive sur ]-∞;"+str(x2)+"]U["+str(x1)+";+∞[", "la fonction est négative sur ["+str(x2)+";"+str(x1)+"]"]
            # print("la fonction est positive sur ]-∞;"+str(x2)+"]U["+str(x1)+";+∞[")
            # print("la fonction est négative sur ["+str(x2)+";"+str(x1)+"]")
          #print("\n\nNous allons maintenant vous tracer un tableau de variation de très grande qualité (avec des valeurs tronquées pour plus de facilité dans la lecture). A vous de remplacer les valeurs valeurs arrondies par les racines. On ne va quand même pas tout vous faire...")
          xm=(-self.b)/(2*self.a)
          xmd=int(xm)
          self.tableauVariations = "|+∞    "+str(xmd)+"   -∞|\n |   ↘  |  ↗  |\n |______|_____|"
          #print("\n\n |+∞    "+str(xmd)+"   -∞|\n |   ↘  |  ↗  |\n |______|_____|")
          m=(-d)/(4*self.a)
          #print("\n\n Le mininum est donc "+str(m)+" atteint en "+str(xm))
          self.extremum = ("MIN", m, xm)
      else:
        #print("\nGros naze, c'est simplifiable !!!!!")
        x0=(-self.b)/(2*self.a)
        self.racines = x0
        self.nombre_racines = 1
        #print("\nLe polynome a une racine : "+str(x0))
        if self.a<0:
          self.variations = ["la fonction est négative ou nulle"]
          #print("\nla fonction est négative ou nulle")
          #print("\n\nMaintenant, la programme a la flemme de faire un tableau de variation pour quelqu'un qui ne sait même pas résoudre une équation du second degré simplifiable...\nMais comme le programme est très gentil, docile et a pitié de votre stupidité, il va vous préciser le maximum")
          self.tableauVariations = None
          #print("Le maximum est "+c+"atteint en 0")
          self.extremum = ("MAX", self.c, 0)
        elif self.a>0:
          self.variations = "la fonction est positive ou nulle"
          #print("\nla fonction est positive ou nulle")
          #print("\n\nMaintenant, la programme a la flemme de faire un tableau de variation pour quelqu'un qui ne sait même pas résoudre une équation du second degré simplifiable...\nMais comme le programme est très gentil, docile et a pitié de votre stupidité, il va vous préciser le minimum")
          #print("Le minimum est "+str(c)+" atteint en 0")
          self.extremum = ("MIN", self.c, 0)
    else:
      print("a doit être différent de zéro sinon c'est du prmier degré et tu n'as pas besoin de moi pour résoudre ça stupide padawan")

polynome = Polynome(1, 1, 1)
