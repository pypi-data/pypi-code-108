import random

def criar(key, classe="", tamanho=0, unidades=0):
    if(key == 0):
        if(classe.upper() == "A"):
            Ox01 = "abcdefghijklmnopqrstuvwxyz"
            Ox02 = 0

            if(unidades <= 0):
                unidades += 1
            
            if(tamanho <= 0):
                tamanho += 20
            
            while(Ox02 != unidades):
                Ox02 += 1
                Ox03 = ""

                for Ox04 in range(tamanho):
                    Ox03 += random.choice(Ox01)
            
                return Ox03
        
        if(classe.upper() == "B"):
            Ox01 = "0123456789"
            Ox02 = 0

            if(unidades <= 0):
                unidades += 1

            if(tamanho <= 0):
                tamanho += 20

            while(Ox02 != unidades):
                Ox02 += 1
                Ox03 = ""
                
                for Ox04 in range(tamanho):
                    Ox03 += random.choice(Ox01)
                
                return Ox03
        
        if(classe.upper() == "C"):
            Ox01 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            Ox02 = 0

            if(unidades <= 0):
                unidades += 1

            if(tamanho <= 0):
                tamanho += 20

            while(Ox02 != unidades):
                Ox02 += 1
                Ox03 = ""
                
                for Ox04 in range(tamanho):
                    Ox03 += random.choice(Ox01)
                
                return Ox03