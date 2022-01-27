import os
import logging
from chibi.atlas import Chibi_atlas
from chibi.file import Chibi_path
from chibi_command.lxc import lxc
from chibi_command.lxc import delegate as lxc_delegate
from chibi_command.rsync import Rsync
from chibi_hybrid import Class_property
from chibi_lxc.file.config import Chibi_lxc_config
from chibi_donkey.donkey import Donkey
from chibi.config import configuration


donkey = Donkey( '.' )


logger = logging.getLogger( 'chibi_lxc.container' )


class Not_exists_error( Exception ):
    pass


class Creation_error( Exception ):
    pass


class Destruction_error( Exception ):
    pass


class Container_meta( type ):
    def __new__( cls, clsname, bases, clsdict ):
        clsobj = super().__new__( cls, clsname, bases, clsdict )
        if isinstance( clsobj.provision_folders, dict ):
            for k, v in clsobj.provision_folders.items():
                clsobj.provision_folders[k] = Chibi_path( v )

        containers = list(
            filter( lambda x: issubclass( x, Container ), bases ) )
        containers_with_env_vars = list(
            filter( lambda x: x.env_vars, containers ) )
        containers_with_scripts = list(
            filter( lambda x: x.scripts, containers ) )
        containers_with_status_scripts = list(
            filter( lambda x: x.status_scripts, containers ) )

        cls.set_scripts( clsobj, containers_with_scripts )
        cls.set_status_scripts( clsobj, containers_with_status_scripts )

        cls.set_env_vars( clsobj, containers_with_env_vars )

        names = ( c.name for c in containers )
        equal_names = ( clsobj.name == name for name in names )
        if any( equal_names ):
            clsobj.name = clsobj.__name__

        return clsobj

    @staticmethod
    def set_env_vars( cls_obj, containers_with_env_vars ):
        _env_vars = list(
            e for c in containers_with_env_vars for e in c.env_vars.items() )

        # _set_env_vars = set()
        env_vars = Chibi_atlas()
        for k, v in _env_vars:
            env_vars[ k ] = v

        env_vars.update( cls_obj.env_vars )
        cls_obj.env_vars = env_vars

    @staticmethod
    def set_scripts( cls_obj, containers_with_scripts ):
        _scripts = (
            s for c in containers_with_scripts for s in c.scripts )
        _set_scripts = set()
        scripts = []
        for script in _scripts:
            if script not in _set_scripts:
                scripts.append( script )
                _set_scripts.add( script )

        if cls_obj.scripts:
            for script in cls_obj.scripts:
                if script not in _set_scripts:
                    scripts.append( script )
                    _set_scripts.add( script )
            cls_obj.scripts = tuple( scripts )
        else:
            cls_obj.scripts = scripts

    @staticmethod
    def set_status_scripts( cls_obj, containers_with_scripts ):
        _set_status_scripts = set()

        _status_scripts = (
            s for c in containers_with_scripts for s in c.status_scripts )
        status_scripts = []
        for script in _status_scripts:
            if script not in _set_status_scripts:
                status_scripts.append( script )
                _set_status_scripts.add( script )

        if cls_obj.status_scripts:
            for script in cls_obj.status_scripts:
                if script not in _set_status_scripts:
                    status_scripts.append( script )
                    _set_status_scripts.add( script )
            cls_obj.status_scripts = tuple( status_scripts )
        else:
            cls_obj.status_scripts = status_scripts


class Container( metaclass=Container_meta ):
    name = "unset"
    distribution = 'centos'
    arch = 'amd64'
    version = '8'

    provision_root = Chibi_path( 'home/chibi/provision/' )
    provision_folders = Chibi_atlas()
    scripts = None
    status_scripts = None
    extra_hosts = None

    delegate = True

    env_vars = Chibi_atlas( {
        'PROVISION_PATH': '/' + str( provision_root ) + 'scripts'
    } )

    @Class_property
    def lxc( cls ):
        if cls.delegate:
            return lxc_delegate
        else:
            return lxc

    @Class_property
    def info( cls ):
        result = cls.lxc.Info.name( cls.name ).run()
        if not result:
            raise Not_exists_error( result.error )
        return result.result

    @Class_property
    def config( cls ):
        if os.getuid() != 0:
            return Chibi_path(
                f'~/.local/share/lxc/{cls.name}/config',
                chibi_file_class=Chibi_lxc_config )
        return Chibi_path(
            f'/var/lib/lxc/{cls.name}/config',
            chibi_file_class=Chibi_lxc_config )

    @Class_property
    def exists( cls ):
        result = cls.lxc.Info.name( cls.name ).run()
        return bool( result )

    @Class_property
    def root( cls ):
        if os.getuid() != 0:
            return Chibi_path( f'~/.local/share/lxc/{cls.name}/rootfs' )
        return Chibi_path( f'/var/lib/lxc/{cls.name}/rootfs' )

    @Class_property
    def provision_folder( cls ):
        return Chibi_atlas( {
            k: cls.root + '..' + k
            for k, v in cls.provision_folders.items() } )

    @Class_property
    def script_folder( cls ):
        return '/' + cls.provision_root + 'scripts/'

    @Class_property
    def is_running( cls ):
        return cls.info.state == 'running'

    @classmethod
    def create( cls ):
        template = cls.lxc.Create.name( cls.name ).template( 'download' )
        template = template.parameters(
            '-d', cls.distribution, '-r', cls.version,
            '--arch', cls.arch )
        print( template.preview() )
        result = template.run()
        if not result:
            raise Creation_error(
                "un error en la creacion del contenedor"
                f" '{result.return_code}' revise los output" )
        return result

    @classmethod
    def start( cls, daemon=True ):
        command = cls.lxc.Start.name( cls.name )
        if daemon:
            command.daemon()
        result = command.run()
        return result

    @classmethod
    def stop( cls ):
        command = cls.lxc.Stop.name( cls.name )
        result = command.run()
        return result

    @classmethod
    def destroy( cls, stop=False ):
        if cls.is_running and stop:
            cls.stop()
        template = cls.lxc.Destroy.name( cls.name )
        result = template.run()
        if not result:
            raise Destruction_error(
                "un error en la destruscion del contenedor"
                f" '{result.return_code}' revise los output" )
        return result

    @classmethod
    def provision( cls ):
        config = cls.config.open().read()
        hosts = configuration.chibi_lxc.hosts

        for k, v in cls.provision_folders.items():
            real_folder = cls.provision_folder[k]
            mount = (
                f"{real_folder}  {cls.provision_root}/{k} "
                "none bind,create=dir 0 0" )

            if "mount" not in config.lxc:
                config.lxc.mount = Chibi_atlas( entry=[] )
            entries = config.lxc.mount.entry
            if not isinstance( entries, list ):
                entries = [ entries ]
            for entry in entries:
                if entry == mount:
                    break
            else:
                entries.append( mount )
                cls.config.open().write( config )
                config = cls.config.open().read()

            if not real_folder.exists:
                real_folder.mkdir()
            if v.is_a_folder and not v.endswith( '/' ):
                v = str( v ) + '/'
            if not real_folder.exists:
                real_folder.mkdir()
            Rsync.clone_dir().human().verbose().run(
                v, real_folder )
            if hosts and hosts.exists:
                hosts.copy( real_folder + 'hosts' )

    @Class_property
    def hosts( cls ):
        if cls.extra_hosts:
            return [ cls.name, *cls.extra_hosts ]
        return [ cls.name ]

    @classmethod
    def attach( cls ):
        attach = cls.lxc.Attach.name( cls.name )
        for k, v in cls.env_vars.items():
            attach.set_var( k, v )
        return attach

    @classmethod
    def attach_script( cls, script, *args ):
        attach = cls.attach()
        for k, v in cls.env_vars.items():
            attach.set_var( k, v )
        command, script = cls._prepare_script( script )
        return attach.run( command, cls.script_folder + script, *args )

    @classmethod
    def run_scripts( cls ):
        for script in cls.scripts:
            if isinstance( script, tuple ):
                args = cls._prepare_script_arguments( *script[1:] )
                script = script[0]
                result = cls.attach_script( script, *args )
            else:
                result = cls.attach_script( script )
            if not result:
                logger.error(
                    f"fallo el script '{script}' se regreso el codigo "
                    f"{result.return_code}" )
                return result

    @classmethod
    def run_status_scripts( cls ):
        for script in cls.status_scripts:
            if isinstance( script, tuple ):
                args = cls._prepare_script_arguments( *script[1:] )
                script = script[0]
                result = cls.attach_script( script, *args )
            else:
                result = cls.attach_script( script )
            if not result:
                logger.error(
                    f"fallo el status script '{script}' se regreso el codigo "
                    f"{result.return_code}" )
                return result

    @classmethod
    def _prepare_script_arguments( cls, *args ):
        result = []
        for a in args:
            if isinstance( a, str ):
                if a.startswith( 'cls.' ):
                    a = a[4:]
                    result.append( getattr( cls, a ) )
                    continue
            result.append( a )
        return result

    @staticmethod
    def _prepare_script( script ):
        if script.endswith( 'py' ):
            return 'python3', script
        return 'bash', script
