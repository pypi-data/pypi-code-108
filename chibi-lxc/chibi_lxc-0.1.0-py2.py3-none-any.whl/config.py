from chibi.config import Configuration, configuration
from chibi_lxc.container import Container


class Containers( Configuration ):
    def add( self, container ):
        correct_type = (
            isinstance( container, type )
            and issubclass( container, Container ) )
        if correct_type:
            self[ container.name ] = container
        else:
            raise NotImplementedError(
                f"no esta implementado agregar un typo {type(container)}"
                f" como un contenedor"
            )


configuration.chibi_lxc.containers = Containers()
