from chibi_command import Command


class Echo( Command ):
    """
    estandar echo de linux

    Arguments
    ==========
    text: string
        texto que imprimira en consola
    """
    command = 'echo'
    captive = False


class Cowsay( Echo ):
    command = 'cowsay'


class Ponysay( Echo ):
    command = 'cowsay'


class CirnoSay( Echo ):
    command = 'cirnosay'


echo = Echo()
cowsay = Cowsay()
ponysay = Ponysay()
cirnosay = CirnoSay()
