from chibi_hybrid.chibi_hybrid import Chibi_hybrid

from chibi_command import Command


__all__ = [ 'Dnf', ]


class Dnf( Command ):
    command = 'dnf'
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

    @classmethod
    def config_manager( cls, package ):
        result = cls( 'config-manager', '--set-enabled', package )()
        return result
