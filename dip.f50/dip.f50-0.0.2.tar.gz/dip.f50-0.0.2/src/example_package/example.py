class AName:
    print("""staticmethods : 
        Inputname()
        Outputname()
        
        Save the output of Inputname() in a var 
        and then call Outputname() with the var.
        
        ex: a = AName.Inputname()
        ex: AName.Outputname(a)
        """)
    @staticmethod
    def Inputname():
        nm = input("Write your name : ")
        return nm 
    
    @staticmethod
    def Outputname(nm):
        print(f"Your name is {nm}")
