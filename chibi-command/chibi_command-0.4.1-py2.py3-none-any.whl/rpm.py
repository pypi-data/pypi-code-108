from chibi_command import Command


class RPM( Command ):
    command = 'rpm'
    captive = False
    kw_format = '--{key} {value}'

    @classmethod
    def rpm_import( cls, repository ):
        return cls( **{ 'import': repository } )()
