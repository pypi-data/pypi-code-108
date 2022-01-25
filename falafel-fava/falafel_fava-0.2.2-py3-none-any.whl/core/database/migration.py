from textwrap import dedent
from os import listdir, remove
from fnmatch import fnmatch
from sqlalchemy import create_engine, \
    MetaData, \
    orm, \
    exc, \
    inspect, \
    Table, \
    insert, \
    Column, \
    Integer, \
    TIMESTAMP, \
    Text
from datetime import datetime
import inflect
import toml
from importlib import import_module
from fava.core.utils import variables
from . import model

"""
Set database configuration
"""
migrations_dir = variables.get_app_dir() + "/" + variables.get("MIGRATIONS_DIR")
models_dir = variables.get_app_dir() + "/" + variables.get("MODELS_DIR")
engine = create_engine(variables.get_database_uri())
metadata = MetaData(bind=engine)
create_session = orm.sessionmaker(bind=engine)
session = create_session()


def create_new_migration(name):
    """
    Create new migration file if doesn't exists.
    :param name: string
    :return: void
    """
    name = name.lower()
    p = inflect.engine()

    for file in listdir(migrations_dir):
        if (fnmatch(file, "*.toml")) and fnmatch(file, name + "*"):
            print("#######")
            print("-> Error!")
            print("-> Migration " + name + " exists!")
            print("#######")
            raise SystemExit()

    if "create" in name:
        with open(migrations_dir
                  + '/' + datetime.now().strftime("%Y%m%d%H%M%S") + '_' + name
                  + '.toml', 'w') as migration:

            table_name = name.replace('create_', '')
            content = dedent("""\
                table_name = '""" + p.plural(table_name) + """'
                action = 'create'
                [create]
                [create.id]
                primary_key = "True"
                type = "Integer"

                [create.created_at]
                default = "datetime.utcnow"
                nullable = "False"
                type = "TIMESTAMP"

                [create.updated_at]
                nullable = "False"
                onupdate = "datetime.utcnow"
                type = "TIMESTAMP"
            """)

            migration.write(content)

            print("#######")
            print("-> Migration " + name + " created!")
            print("-> Check the file in: " +
                  migrations_dir + '/' + datetime.now().strftime("%Y%m%d%H%M%S") + '_' + name + '.toml')
            print("#######")

    elif "update" in name:
        with open(migrations_dir
                  + '/' + datetime.now().strftime("%Y%m%d%H%M%S") + '_' + name
                  + '.toml', 'w') as migration:
            table_name = name.replace('update_', '')
            content = dedent("""\
                table_name = '""" + p.plural(table_name) + """'
                action = 'update'
                [update]
                [update.example]
                item = "String"
            """)

            migration.write(content)

            print("#######")
            print("-> Migration " + name + " created!")
            print("-> Check the file in " + migrations_dir +
                  '/' + name + '_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.toml')
            print("#######")
    else:
        print("-> Migration doesn't created. Wrong command arguments, check: ")
        print("-> create: fava -mkmigration create_name_table")
        print("-> update: fava -mkmigration update_name_table")
        print("-> Remember! The name of the table always on singular!")


def run_migrate(name):
    """
    Run all migrations
    :param name: string
    :return: void
    """

    """ 
    Migration table exists?
    """
    if check_table_exists('migrations') is False:
        create_migrations_table()

    tables = []
    if name == 'all' or name == '':
        print('############################')
        print('-> Running migrations...')
        print('############################\n')

        migration_files = sorted(listdir(migrations_dir))
        for file in migration_files:
            if (fnmatch(file, "*.toml")) and (file != "__init__.py"):
                run_migrate_with_file_name(file)
                tables.append(file.replace('.toml', ''))
    else:
        try:
            run_migrate_with_file_name(name + ".toml")
            tables.append(name)

        except OSError:
            print("->Migration file doesn't exists!", OSError)

    if tables:
        save_migration_state(str(tables))

    print('############################')
    print('-> All migrations processed')


def run_migrate_with_file_name(file_name):
    """
    :param file_name:
    :return:
    """
    try:
        migration = toml.load(migrations_dir + '/' + file_name)
        if check_table_exists(migration.get('table_name')) is False:
            return save_migrate_on_database(migration, migration.get("create")
                                            or migration.get("update")
                                            or migration.get("delete")
                                            or "create")
        else:
            return "The column " + migration.get("") + " already exists on database!"
    except BaseException as err:
        print("-> An error occurring on running migration file " + file_name, err)


def save_migrate_on_database(migration, method="create"):
    """
    :param migration:
    :param method:
    :return:
    """
    if method == "delete":
        pass
    elif method == "update":
        pass
    else:
        model_data = model.create_model_file_with_not_exists(migration)
        class_name = model_data.get("class_name")
        is_new = model_data.get("is_new")
        model_path = model.get_model_import_path(class_name)
        try:
            db_module = getattr(import_module(model_path), class_name)
        except BaseException as err:
            if is_new:
                remove(model_path + ".py")
            print("-> An internal error occurring!")
            raise SystemExit(err)
        try:
            db_module.metadata.create_all(engine)
            return "-> Success when running the Model Import for " + class_name
        except Exception as err:
            if is_new:
                remove(model_path + ".py")
            raise SystemExit(err)


def check_table_exists(table_name):
    """
    Check if table exists on database
    :param table_name: string
    :return: boolean
    """
    if table_name in inspect(engine).get_table_names():
        return True
    else:
        return False


def create_migrations_table():
    """
    :return: void
    """
    try:
        migration_table = Table('migrations', metadata,
                                Column('id', Integer, primary_key=True),
                                Column('table', Text, nullable=False),
                                Column('created_at', TIMESTAMP, nullable=False, default=datetime.utcnow))
        metadata.create_all(engine)
    except exc.SQLAlchemyError as err:
        print('#########################')
        print('Error in migration task!')
        print('#########################\n')
        raise SystemExit(err)


def save_migration_state(name):
    """
    :param name:
    :return:
    """
    try:
        migration_table = Table('migrations', metadata, autoload=True)
        insert_migration = insert(migration_table)
        insert_migration = insert_migration.values(
            {"table": name, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        )
        session.execute(insert_migration)
        session.commit()
    except Exception as err:
        session.rollback()
        raise SystemExit(err)
