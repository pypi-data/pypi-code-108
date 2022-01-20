"""
PostgreSQL users and databases
==============================

This module provides tools for creating PostgreSQL users and databases.

"""
import os

import six

from fabric.api import cd, hide, sudo, settings

from burlap import Satchel
from burlap.constants import *
from burlap.db import DatabaseSatchel
from burlap.decorators import task

POSTGIS = 'postgis'
POSTGRESQL = 'postgresql'

def _run_as_pg(command):
    """
    Run command as 'postgres' user
    """
    with cd('~postgres'):
        return sudo(command, user='postgres')


def user_exists(name):
    """
    Check if a PostgreSQL user exists.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        res = _run_as_pg('''psql -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = '%(name)s';"''' % locals())
    return (res == "1")


def create_user(name, password, superuser=False, createdb=False,
                createrole=False, inherit=True, login=True,
                connection_limit=None, encrypted_password=False):
    """
    Create a PostgreSQL user.

    Example::

        import burlap

        # Create DB user if it does not exist
        if not burlap.postgres.user_exists('dbuser'):
            burlap.postgres.create_user('dbuser', password='somerandomstring')

        # Create DB user with custom options
        burlap.postgres.create_user('dbuser2', password='s3cr3t',
            createdb=True, createrole=True, connection_limit=20)

    """
    options = [
        'SUPERUSER' if superuser else 'NOSUPERUSER',
        'CREATEDB' if createdb else 'NOCREATEDB',
        'CREATEROLE' if createrole else 'NOCREATEROLE',
        'INHERIT' if inherit else 'NOINHERIT',
        'LOGIN' if login else 'NOLOGIN',
    ]
    if connection_limit is not None:
        options.append('CONNECTION LIMIT %d' % connection_limit)
    password_type = 'ENCRYPTED' if encrypted_password else 'UNENCRYPTED'
    options.append("%s PASSWORD '%s'" % (password_type, password))
    options = ' '.join(options)
    _run_as_pg('''psql -c "CREATE USER %(name)s %(options)s;"''' % locals())


def drop_user(name):
    """
    Drop a PostgreSQL user.

    Example::

        import burlap

        # Remove DB user if it exists
        if burlap.postgres.user_exists('dbuser'):
            burlap.postgres.drop_user('dbuser')

    """
    _run_as_pg('''psql -c "DROP USER %(name)s;"''' % locals())


def database_exists(name):
    """
    Check if a PostgreSQL database exists.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        return _run_as_pg('''psql -d %(name)s -c ""''' % locals()).succeeded


def create_database(name, owner, template='template0', encoding='UTF8',
                    locale='en_US.UTF-8'):
    """
    Create a PostgreSQL database.

    Example::

        import burlap

        # Create DB if it does not exist
        if not burlap.postgres.database_exists('myapp'):
            burlap.postgres.create_database('myapp', owner='dbuser')

    """
    _run_as_pg('''createdb --owner %(owner)s --template %(template)s \
                  --encoding=%(encoding)s --lc-ctype=%(locale)s \
                  --lc-collate=%(locale)s %(name)s''' % locals())


def create_schema(name, database, owner=None):
    """
    Create a schema within a database.
    """
    if owner:
        _run_as_pg('''psql %(database)s -c "CREATE SCHEMA %(name)s AUTHORIZATION %(owner)s"''' % locals())
    else:
        _run_as_pg('''psql %(database)s -c "CREATE SCHEMA %(name)s"''' % locals())


class PostgreSQLSatchel(DatabaseSatchel):
    """
    Represents a PostgreSQL server.
    """

    name = 'postgresql'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['postgresql-11'],
            (UBUNTU, '12.04'): ['postgresql-9.1'],
            (UBUNTU, '14.04'): ['postgresql-9.3'],
            (UBUNTU, '16.04'): ['postgresql-10'],
            (UBUNTU, '18.04'): ['postgresql-11'],
            (UBUNTU, '20.04'): ['postgresql-13'],
        }

    def set_defaults(self):
        super().set_defaults()

        # Note, if you use gzip, you can't use parallel restore.
        #self.env.dump_command = 'time pg_dump -c -U {db_user} --no-password --blobs --format=c --schema=public --host={db_host} {db_name} > {dump_fn}'
        self.env.dump_command = 'time pg_dump -c -U {db_user} --no-password --blobs --format=c --schema=public --host={db_host} --dbname={db_name} | ' \
            'gzip -c > {dump_fn}'
        self.env.dump_fn_template = '{dump_dest_dir}/db_{db_type}_{SITE}_{ROLE}_{db_name}_$(date +%Y%m%d).sql.gz'

        #self.env.load_command = 'gunzip < {remote_dump_fn} | pg_restore --jobs=8 -U {db_root_username} --format=c --create --dbname={db_name}'
        self.env.load_command = 'gunzip < {remote_dump_fn} | ' \
            'pg_restore -U {db_root_username} --host={db_host} --format=c --clean --if-exists --schema=public --dbname={db_name}'

        self.env.createlangs = ['plpgsql'] # plpythonu
        self.env.postgres_user = 'postgres'
        self.env.encoding = 'UTF8'
        self.env.locale = 'en_US.UTF-8'
        self.env.custom_load_cmd = ''
        self.env.port = 5432
        self.env.pgpass_path = '~/.pgpass'
        self.env.pgpass_chmod = 600
        self.env.force_version = None
        self.env.version_command = r'`psql --version | grep -m 1 -o -E "[0-9]+\.[0-9]+" | head -1`'
        self.env.engine = POSTGRESQL # 'postgresql' | postgis

        # If true, treats the current database as existing as a schema in a multi-tenant environment,
        # so commands to drop/create the entire database will be replaced with commands to drop/create a schema.
        self.env.schema_mt = False

        self.env.db_root_username = 'postgres'
        self.env.db_root_password = 'password'

        self.env.apt_repo_enabled = False

        # https://askubuntu.com/questions/831292/how-to-install-postgresql-9-6-on-any-ubuntu-version
        # Populated from https://www.postgresql.org/download/linux/ubuntu/
        self.env.apt_repo = None

        self.env.apt_key = 'https://www.postgresql.org/media/keys/ACCC4CF8.asc'

        self.env.service_commands = {
            START:{
                UBUNTU: 'service postgresql start',
            },
            STOP:{
                UBUNTU: 'service postgresql stop',
            },
            ENABLE:{
                UBUNTU: 'update-rc.d postgresql defaults',
            },
            DISABLE:{
                UBUNTU: 'update-rc.d -f postgresql remove',
            },
            RESTART:{
                UBUNTU: 'service postgresql restart',
            },
            STATUS:{
                UBUNTU: 'service postgresql status',
            },
        }

    #https://askubuntu.com/questions/831292/how-to-install-postgresql-9-6-on-any-ubuntu-version
    @property
    def packager_repositories(self):
        ver = self.os_version
        if ver.type == LINUX:
            if ver.distro == UBUNTU:
                if ver.release == '16.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
                if ver.release == '18.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
                if ver.release == '20.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ focal-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
        raise NotImplementedError

    @task
    def write_pgpass(self, name=None, site=None, use_sudo=0, root=0):
        """
        Write the file used to store login credentials for PostgreSQL.
        """

        r = self.database_renderer(name=name, site=site)

        root = int(root)

        use_sudo = int(use_sudo)

        r.run('touch {pgpass_path}')
        if '~' in r.env.pgpass_path:
            r.run('chmod {pgpass_chmod} {pgpass_path}')
        else:
            r.sudo('chmod {pgpass_chmod} {pgpass_path}')

        if root:
            r.env.shell_username = r.env.get('db_root_username', 'postgres')
            r.env.shell_password = r.env.get('db_root_password', 'password')
        else:
            r.env.shell_username = r.env.db_user
            r.env.shell_password = r.env.db_password

        r.append(
            '{db_host}:{port}:*:{shell_username}:{shell_password}',
            r.env.pgpass_path,
            use_sudo=use_sudo)

    @task
    def dumpload(self, site=None, role=None):
        """
        Dumps and loads a database snapshot simultaneously.
        Requires that the destination server has direct database access
        to the source server.

        This is better than a serial dump+load when:
        1. The network connection is reliable.
        2. You don't need to save the dump file.

        The benefits of this over a dump+load are:
        1. Usually runs faster, since the load and dump happen in parallel.
        2. Usually takes up less disk space since no separate dump file is
            downloaded.
        """
        r = self.database_renderer(site=site, role=role)
        r.run('pg_dump -c --host={host_string} --username={db_user} '
            '--blobs --format=c {db_name} -n public | '
            'pg_restore -U {db_postgresql_postgres_user} --create '
            '--dbname={db_name}')

    @task
    def drop_views(self, name=None, site=None):
        """
        Drops all views.
        """
        raise NotImplementedError
    #        SELECT 'DROP VIEW ' || table_name || ';'
    #        FROM information_schema.views
    #        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    #        AND table_name !~ '^pg_';
            # http://stackoverflow.com/questions/13643831/drop-all-views-postgresql
    #        DO$$
    #        BEGIN
    #
    #        EXECUTE (
    #           SELECT string_agg('DROP VIEW ' || t.oid::regclass || ';', ' ')  -- CASCADE?
    #           FROM   pg_class t
    #           JOIN   pg_namespace n ON n.oid = t.relnamespace
    #           WHERE  t.relkind = 'v'
    #           AND    n.nspname = 'my_messed_up_schema'
    #           );
    #
    #        END
    #        $$

    @task
    def exists(self, name='default', site=None, use_root=False):
        """
        Returns true if a database with the given name exists. False otherwise.
        """

        r = self.database_renderer(name=name, site=site)

        if int(use_root):
            kwargs = dict(
                db_user=r.env.get('db_root_username', 'postgres'),
                db_password=r.env.get('db_root_password', 'password'),
                db_host=r.env.db_host,
                db_name=r.env.db_name,
            )
            r.env.update(kwargs)

        # Set .pgpass file.
        if r.env.db_password:
            self.write_pgpass(name=name, root=use_root)

        ret = r.run(
            'psql --username={db_user} --host={db_host} -l | grep -v test_ | grep {db_name} | wc -l', ignore_errors=True
        )
        if ret is not None:
            if 'password authentication failed' in ret:
                ret = False
            else:
                ret = int(ret.split('\n')[-1]) >= 1

            print('%s database on site %s %s exist' % (r.env.db_name, self.genv.SITE, 'DOES' if ret else 'DOES NOT'))

        return ret

    @task
    def execute(
        self, sql, name='default', site=None, as_db_root_user=False, ignore_errors=False, no_db=False, no_pager=False,
        timeout=None, **kwargs
    ):
        """
        Run SQL command with psql.

        Args:
            sql (str): Command to run
            name (str): Database name
            site (str): Site name
            as_db_root_user (int/bool): If truthy, run as db_root_username; otherwise, run as db_user
            ignore_errors (int/bool): If truthy, wrap task in settings(warn_only=True)
            no_db (int/bool): If truthy, omit --dbname argument (as when creating a database)
            no_pager (int/bool): If truthy, disable psql pager, to prevent interactive less-style prompt.
            timeout (int/None): If not None, terminate command after this many seconds.
        """
        r = self.database_renderer(name=name, site=site)

        sql = sql.strip()
        if not sql.endswith(';'):
            sql += ';' # Terminate SQL statements with semicolon
        r.env.sql = sql
        r.env.dbname_arg = '' if no_db else f'--dbname {r.env.db_name}'
        r.env.pager_arg = '-P pager=off' if int(no_pager) else ''

        if as_db_root_user and r.env.db_host in {'localhost', '127.0.0.1'}:
            # Run locally as db root user with sudo -U, relying on pg_hba.conf or other Postgres auth
            ret = r.sudo(
                'psql --user={db_root_username} --no-password --host={db_host} {dbname_arg} {pager_arg} --command="{sql}"',
                user=r.env.postgres_user, ignore_errors=ignore_errors, timeout=timeout)
        elif as_db_root_user:
            # Run on remote database as db root user, relying on .pgpass or other Postgres auth
            ret = r.run(
                'psql --user={db_root_username} --no-password --host={db_host} {dbname_arg} {pager_arg} --command="{sql}"',
                ignore_errors=ignore_errors, timeout=timeout)
        else:
            # Run as normal db user, relying on .pgpass or other Postgres auth
            ret = r.run(
                'psql --user={db_user} --no-password --host={db_host} {dbname_arg} {pager_arg} --command="{sql}"',
                ignore_errors=ignore_errors, timeout=timeout)

        return ret

    @task
    def execute_file(self, filename, name='default', site=None, **kwargs):
        """
        Run SQL file with psql.
        """
        r = self.database_renderer(name=name, site=site)
        r.env.filename = filename
        #r.run('psql --user={postgres_user} --no-password -d {db_name} -a -f {filename}')
        r.run('psql --user={db_user} --no-password --host={db_host} -d {db_name} -a -f {filename}')

    @task
    def create(self, name='default', site=None, **kwargs):
        r = self.database_renderer(name=name, site=site)

        # Load site-specific satchel settings.
        site = site or self.genv.SITE
        self.set_site_specifics(site)

        # Create role/user.
        r.pc('Creating user...')
        self.execute(
            "CREATE USER {db_user} WITH PASSWORD '{db_password}';",
            name=name, site=site, as_db_root_user=True, ignore_errors=True, no_db=True)
        # Grant user role to root role (prevents "must be member of role <db_user>" errors in RDS)
        self.execute("GRANT {db_user} TO {db_root_username};", name=name, site=site, as_db_root_user=True, no_db=True)

        # Create db
        r.pc('Creating database...')
        ret = self.execute(
            "CREATE DATABASE {db_name} WITH OWNER={db_user} ENCODING='{encoding}' LC_CTYPE='{locale}' LC_COLLATE='{locale}';",
            name=name, site=site, as_db_root_user=True, ignore_errors=True, no_db=True)
        if isinstance(ret, six.string_types) and 'ERROR:' in ret and 'already exists' not in ret:
            raise Exception('Error creating database: %s' % ret)

        if r.env.schema_mt:
            # Create schema
            # This assumes each schema is associated with a unique user.
            r.pc('Creating schema...')
            self.execute(
                "CREATE SCHEMA IF NOT EXISTS {db_schema}; "
                "GRANT ALL PRIVILEGES ON SCHEMA {db_schema} to {db_user}; "
                "ALTER ROLE {db_user} SET search_path TO {db_schema};", name=name, site=site, as_db_root_user=True)

        r.pc('Enabling plpgsql on database...')
        r.run('createlang -U postgres plpgsql {db_name} || true', ignore_errors=True)

    @task
    def drop_connections(self, name=None, site=None, drop_other_usenames=0):
        """
        Drop non-root connections to the target site database.

        Useful for quickly killing deadlocks, or preventing interference with a db snapshot load.
        Uses pg_terminate_backend() to send SIGTERM to all running non-shell (psql) query processes.
        Times out after 10 seconds, since terminating connections is expected to be a very fast operation.

        Args:
            name (str): db name
            site (str): site slug
            drop_other_usenames (int): If 1, also drop connections from other non-root usenames (sites).
        """
        site = site or self.genv.SITE
        drop_other_usenames = int(drop_other_usenames)

        print('Dropping database connections...')

        r = self.database_renderer(name=name, site=site)
        external_ip = (r.run('wget http://ipecho.net/plain -O - -q ; echo') or '').strip()
        if r.env.db_root_username == 'postgres' and r.env.db_host == external_ip:
            r.env.db_host = '127.0.0.1'

        if drop_other_usenames:
            r.env.usename_condition = "usename != '{db_root_username}'"
        else:
            r.env.usename_condition = "usename = '{SITE}'"

        self.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' "
            "AND {usename_condition} AND application_name != 'psql';",
            name=name, site=site, as_db_root_user=True, ignore_errors=True, timeout=10)

    @task
    #@runs_once Interferes with global methods that want to load multiple databases.
    def load(self, dump_fn='', prep_only=0, force_upload=0, from_local=0, name=None, site=None, dest_dir=None, force_host=None):
        """
        Restore a database snapshot onto the target database server.

        Args:
            prep_only (int): If 1, commands for preparing the load will be generated, but not the command to finally load
                the snapshot.
            force_host (str): Force loading on the given host.
        """

        site = site or self.genv.SITE

        r = self.database_renderer(name=name, site=site)

        # Load site-specific satchel settings.
        try:
            self.set_site_specifics(site)
        except KeyError:
            # Sometimes databases have a logical site associated with them but no explicit site settings.
            pass

        # Render the snapshot filename.
        r.env.dump_fn = self.get_default_db_fn(fn_template=dump_fn, dest_dir=dest_dir)

        prep_only = int(prep_only)

        missing_local_dump_error = r.format("Database dump file {dump_fn} does not exist.")

        # Copy snapshot file to target.
        if self.is_local:
            r.env.remote_dump_fn = dump_fn
        else:
            r.env.remote_dump_fn = '/tmp/' + os.path.split(r.env.dump_fn)[-1]

        if not prep_only and not self.is_local:
            if not self.dryrun:
                assert os.path.isfile(r.env.dump_fn), missing_local_dump_error
            self.upload_snapshot(name=name, site=site, local_dump_fn=r.env.dump_fn, remote_dump_fn=r.env.remote_dump_fn)

        if self.is_local and not prep_only and not self.dryrun:
            assert os.path.isfile(r.env.dump_fn), missing_local_dump_error

        if force_host:
            r.env.db_host = force_host

        # Drop/create schema/db
        if r.env.schema_mt:
            # db may already exist on multitenant sites.
            # Use ignore_errors in place of missing "IF EXISTS" syntax for CREATE DATABASE.
            self.execute("CREATE DATABASE {db_name};", name=name, site=site, as_db_root_user=True, ignore_errors=True, no_db=True)
            # Disconnect all other users so we can drop the schema if it exists.
            self.drop_connections(name=name, site=site)
            self.execute("DROP SCHEMA IF EXISTS {db_schema} CASCADE;", name=name, site=site, as_db_root_user=True)
        else:
            # Disconnect all other users so we can drop the database if it exists.
            self.drop_connections(name=name, site=site, drop_other_usenames=1)
            self.execute("DROP DATABASE IF EXISTS {db_name};", name=name, site=site, as_db_root_user=True, no_db=True)
            self.execute("CREATE DATABASE {db_name};", name=name, site=site, as_db_root_user=True, no_db=True)

        # Create PostGIS extensions
        if r.env.engine == POSTGIS:
            self.execute("CREATE EXTENSION postgis;", name=name, site=site, as_db_root_user=True, ignore_errors=True)
            self.execute("CREATE EXTENSION postgis_topology;", name=name, site=site, as_db_root_user=True, ignore_errors=True)

        # Reassign user-owned objects to root user and drop user schemas
        # (user may not exist yet, so ignore errors)
        if not r.env.schema_mt:
            self.execute(
                "REASSIGN OWNED BY {db_user} TO {db_root_username}; "
                "DROP OWNED BY {db_user} CASCADE;", name=name, site=site, as_db_root_user=True, ignore_errors=True)

        # Create db user and assign privileges as appropriate
        self.execute(
            "DROP USER IF EXISTS {db_user}; "
            "CREATE USER {db_user} WITH PASSWORD '{db_password}';", name=name, site=site, as_db_root_user=True)
        if not r.env.schema_mt:
            self.execute("GRANT ALL PRIVILEGES ON DATABASE {db_name} to {db_user};", name=name, site=site, as_db_root_user=True)
            for createlang in r.env.createlangs:
                r.env.createlang = createlang
                r.sudo('createlang -U {db_root_username} --host={db_host} {createlang} {db_name} || true', user=r.env.postgres_user)

        if r.env.schema_mt:
            # Create schema and assign to user. This assumes each schema is associated with a unique user.
            self.execute(
                "CREATE SCHEMA IF NOT EXISTS {db_schema}; "
                "GRANT ALL PRIVILEGES ON SCHEMA {db_schema} to {db_user}; "
                "ALTER ROLE {db_user} SET search_path TO {db_schema};", name=name, site=site, as_db_root_user=True)

        if not prep_only:
            # Run load command (as postgres user, if database is hosted locally)
            if r.env.db_host in {'localhost', '127.0.0.1'}:
                r.sudo(r.env.load_command, user=r.env.postgres_user)
            else:
                r.run(r.env.load_command)

    @task
    def shell(self, name='default', site=None, **kwargs):
        """
        Open a SQL shell to the given database, assuming the configured database and user support this feature.
        """
        r = self.database_renderer(name=name, site=site)
        self.write_pgpass(name=name, site=site, root=True)

        db_name = kwargs.get('db_name')
        if db_name:
            r.env.db_name = db_name
            r.run('/bin/bash -i -c "psql --username={db_root_username} --host={db_host} --dbname={db_name}"')
        else:
            r.run('/bin/bash -i -c "psql --username={db_root_username} --host={db_host}"')

    @task
    def configure_apt_repository(self):
        r = self.local_renderer
        r.sudo("add-apt-repository '{apt_repo}'")
        r.sudo('wget --quiet -O - {apt_key} | apt-key add -')
        r.sudo('apt-get update')

    @task
    def drop_database(self, name):
        """
        Delete a PostgreSQL database.

        Example::

            import burlap

            # Remove DB if it exists
            if burlap.postgres.database_exists('myapp'):
                burlap.postgres.drop_database('myapp')

        """
        self.sudo('dropdb %s' % (name,), user='postgres', ignore_errors=True)

    @task
    def version(self):
        r = self.local_renderer
        if self.dryrun:
            v = r.env.version_command
        else:
            v = (r.run('echo {version_command}') or '').strip()
        self.vprint('postgresql version:', v)

        # Postgres 10+ doesn't use minor version in /etc/postgresql/ subdirectory names
        if isinstance(v, str) and not v.startswith('9'):
            v = v.split('.')[0]

        self.vprint('postgresql subdirectory version:', v)
        return v

    @task
    def load_table(self, table_name, src, dst='localhost', name=None, site=None):
        """
        Directly transfers a table between two databases.
        """
        #TODO: incomplete
        r = self.database_renderer(name=name, site=site)
        r.env.table_name = table_name
        r.run('psql --user={dst_db_user} --host={dst_db_host} --command="DROP TABLE IF EXISTS {table_name} CASCADE;"')
        r.run('pg_dump -t {table_name} --user={dst_db_user} --host={dst_db_host} | psql --user={src_db_user} --host={src_db_host}')

    @task
    def write_pg_hba_conf(self):
        r = self.local_renderer
        if 'pg_version' not in r.env:
            r.env.pg_version = self.version()# or r.env.default_version
        r.pc('Writing pg_hba.conf...')
        r.sudo('cp /etc/postgresql/{pg_version}/main/pg_hba.conf /etc/postgresql/{pg_version}/main/pg_hba.conf.$(date +%Y%m%d%H%M).bak')
        fn = self.render_to_file('postgresql/pg_hba.template.conf')
        r.put(
            local_path=fn,
            remote_path='/etc/postgresql/{pg_version}/main/pg_hba.conf',
            use_sudo=True,
        )

    @task(precursors=['packager', 'user', 'locales'])
    def configure(self, *args, **kwargs):
        #TODO:set postgres user password?
        #https://help.ubuntu.com/community/PostgreSQL
        #set postgres ident in pg_hba.conf
        #sudo -u postgres psql postgres
        #sudo service postgresql restart
        #sudo -u postgres psql
        #\password postgres
        r = self.local_renderer

        #self.install_packages()

        if r.env.apt_repo_enabled:
            self.configure_apt_repository()

        r.env.pg_version = self.version()# or r.env.default_version

        self.write_pg_hba_conf()

#         r.pc('Backing up PostgreSQL configuration files...')
        r.sudo('cp /etc/postgresql/{pg_version}/main/postgresql.conf /etc/postgresql/{pg_version}/main/postgresql.conf.$(date +%Y%m%d%H%M).bak')
        r.pc('Enabling auto-vacuuming...')
        r.sed(
            filename='/etc/postgresql/{pg_version}/main/postgresql.conf',
            before='#autovacuum = on',
            after='autovacuum = on',
            backup='',
            use_sudo=True,
        )
        r.sed(
            filename='/etc/postgresql/{pg_version}/main/postgresql.conf',
            before='#track_counts = on',
            after='track_counts = on',
            backup='',
            use_sudo=True,
        )

        r.sudo('service postgresql restart')


class PostgreSQLClientSatchel(Satchel):

    name = 'postgresqlclient'

    def set_defaults(self):
        self.env.force_version = None

    @property
    def packager_system_packages(self):
        return {
            FEDORA: ['postgresql-client'],
            UBUNTU: ['postgresql-client-11'],
            (UBUNTU, '12.04'): ['postgresql-client-9.1'],
            (UBUNTU, '14.04'): ['postgresql-client-9.3'],
            (UBUNTU, '16.04'): ['postgresql-client-10'],
            (UBUNTU, '18.04'): ['postgresql-client-11'],
            (UBUNTU, '20.04'): ['postgresql-client-13'],
        }

    #https://askubuntu.com/questions/831292/how-to-install-postgresql-9-6-on-any-ubuntu-version
    @property
    def packager_repositories(self):
        ver = self.os_version
        if ver.type == LINUX:
            if ver.distro == UBUNTU:
                if ver.release == '16.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
                if ver.release == '18.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
                if ver.release == '20.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ focal-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
        raise NotImplementedError

    @task(precursors=['packager'])
    def configure(self, *args, **kwargs):
        pass

postgresql = PostgreSQLSatchel()
PostgreSQLClientSatchel()

write_postgres_pgpass = postgresql.write_pgpass
