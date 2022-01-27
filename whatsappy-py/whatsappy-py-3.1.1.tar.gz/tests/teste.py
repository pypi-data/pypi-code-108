from whatsappy import Whatsapp

whatsapp = Whatsapp()

whatsapp.login(visible=False)
grupo = whatsapp.new_group("Teste", ["Felpudo Priminho"])
print(grupo)