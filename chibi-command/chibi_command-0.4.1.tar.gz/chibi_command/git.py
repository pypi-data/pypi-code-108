import logging
#from git import Repo
from chibi.file import Chibi_path
from chibi_command import Command
from chibi_requests import Chibi_url


logger = logging.getLogger( 'chibi_command.git' )


class Git( Command ):
    command = 'git'
    captive = False

    @staticmethod
    def get_repo_name( url ):
        url = Chibi_url( url )
        name = url.base_name.rsplit( '.git', 1 )[0]

    @classmethod
    def repo( cls, src ):
        if src is None:
            src = Chibi_path.current_dir()
        return Repo( src )

    @classmethod
    def clone( cls, url, dest=None, **kw ):
        """
        clona el repositorio de la url

        Parameters
        ==========
        url: string
            url del repositorio
        dest: string ( optional )
            destino de donde se clonara el repositorio
            por default es el directorio de trabajo
        """
        if dest is not None:
            dest = Chibi_path( dest )
            command = cls( 'clone', url, dest, **kw )
        else:
            command = cls( 'clone', url, **kw )
        return command.run()

    @classmethod
    def pull( cls, src=None, **kw ):
        """
        hace pull a un repositorio

        Parameters
        ==========
        src: string
            ruta del repositorio que se quiere hacer pull
        """
        if src is not None:
            src = Chibi_path( src )
            command = cls(
                f'--git-dir={src}/.git', f'--work-tree={src}',
                'pull' )
        else:
            command = cls( 'pull', **kw )
        return command.run()

    @classmethod
    def checkout( cls, branch=None, src=None, **kw ):
        if src is not None:
            src = Chibi_path( src )
            if not src.exists:
                logger.error( f"el directorio {src} no existe" )
                return
        if branch is not None:
            if src:
                command = cls(
                    f'--git-dir={src}/.git', f'--work-tree={src}',
                    'checkout', branch, **kw )
            else:
                command = cls( 'checkout', branch, **kw )
        else:
            if src:
                command = cls(
                    f'--git-dir={src}/.git', f'--work-tree={src}',
                    'checkout', **kw )
            else:
                command = cls( 'checkout', **kw )
        return command.run()

    @classmethod
    def checkout_track( cls, branch=None, src=None, **kw ):
        if src is not None:
            src = Chibi_path( src )
            if not src.exists:
                logger.error( f"el directorio {src} no existe" )
                return
        if branch is not None:
            if src:
                command = cls(
                    f'--git-dir={src}/.git', f'--work-tree={src}',
                    'checkout', '--track', branch, **kw )
            else:
                command = cls( 'checkout', '--track', branch, **kw )
            return command.run()
        raise NotImplementedError()
