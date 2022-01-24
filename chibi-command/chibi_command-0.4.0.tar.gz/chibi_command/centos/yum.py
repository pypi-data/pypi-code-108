from chibi_hybrid.chibi_hybrid import Chibi_hybrid

from chibi_command import Command


__all__ = [ 'Yum' ]


class Yum( Command ):
    command = 'yum'
    captive = False
    args = ( '-y', )

    @classmethod
    def update( cls, *packages ):
        """
        invoca el comando de yum para actualizar paquetes

        Parameters
        ==========
        pkgs: tuple of strings
            lista de los paquetes que se quieren installar
        """
        result = cls( 'update', *packages )()
        return result

    @classmethod
    def install( cls, *packages ):
        """
        invoca el comando de yum para instalar paquetes

        Parameters
        ==========
        pkgs: tuple of strings
            lista de los paquetes que se quieren installar
        """
        result = cls( 'install', *packages )()
        return result

    @classmethod
    def local_install( cls, *packages ):
        """
        invoca el comando de yum para instalar paquetes locales

        Parameters
        ==========
        pkgs: tuple of strings
            lista de los paquetes que se quieren installar
        """
        result = cls( 'localinstall', *packages )()
        return result

    @classmethod
    def clean( cls ):
        """
        invoca el comando de yum para limpiar
        """
        result = cls( 'clean', 'all' )()
        return result


class Firewall_cmd( Command ):
    command = "firewall-cmd"

    @classmethod
    def reload( cls ):
        """
        """
        result = cls( '--reload' )()
        return result

    @classmethod
    def add_port( cls, ports, kind='tcp', permanent=True ):
        """
        agrega un puerto usando firewall-cmd

        Parameters
        ==========
        ports: str
            formato de puertos puede ser el numero o un rango
            25672, 5671-5672
        kind: str
            tipo del puerto tcp o udp
        permanent: bool
        """
        if not permanent:
            raise NotImplementedError
        else:
            permanent = '--permanent'
        return cls( permanent, "--add-port={}/{}".format( ports, kind ) )


