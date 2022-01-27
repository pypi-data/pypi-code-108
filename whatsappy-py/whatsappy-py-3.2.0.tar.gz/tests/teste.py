from whatsappy import Whatsapp
from rich.console import Console

whatsapp = Whatsapp()
console = Console()

whatsapp.login(visible=True)

contacts = whatsapp.contact_list

console.print(contacts)
console.print(len(contacts))

whatsapp.close()