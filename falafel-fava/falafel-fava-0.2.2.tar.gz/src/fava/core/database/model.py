from textwrap import dedent
from os import listdir, path, environ
from fnmatch import fnmatch
import inflect
import black
from fava.core.utils import variables

models_dir = variables.get_app_dir() + "/" + variables.get("MODELS_DIR")


def create_new_model(name):
    """
    Create new model file
    :param name: string
    :return: void
    """
    name: name.lower()
    p = inflect.engine()
    class_name = ""
    class_name_array = name.split('-')
    for item in class_name_array:
        class_name = class_name + item.capitalize()

    for file in listdir(models_dir):
        if (fnmatch(file, "*.py")) and fnmatch(file, class_name.lower() + "_model.py"):
            print("#######")
            print("Error!")
            print("Model " + models_dir + "/" + class_name.lower() + "_model.py exists!")
            print("#######")
            raise SystemExit()

    with open(models_dir + "/" + class_name.lower() + "_model.py", "w") as model:
        table_name = p.plural(name)

        content = dedent("""\
        from app.core.database import db
        from sqlalchemy_serializer import SerializerMixin
        from datetime import datetime


        class """ + class_name + """(db.Model, SerializerMixin):
            __tablename__ = '""" + table_name + """'
            id = db.Column(db.Integer, primary_key=True)
            created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow, server_default=db.text('0'))
            updated_at = db.Column(db.TIMESTAMP, onupdate=datetime.utcnow, nullable=True)

        """)

        mode = black.FileMode()
        formatted = black.format_file_contents(content, fast=False, mode=mode)

        model.write(formatted)

        print("#######")
        print("-> Model " + models_dir + "/" + class_name.lower() + "_model.py created!")
        print("#######")


def create_model_file_with_not_exists(migration):
    """
    :param migration:
    :return: {
    "class_name": str,
    "is_new": boolean
    }
    """
    p = inflect.engine()
    table_name = migration.get("table_name")
    class_name = p.singular_noun(table_name.title().replace("_", ""))

    if check_model_exists(class_name) is False:
        return {
            "class_name": create_new_model_by_migration(migration, class_name, table_name),
            "is_new": True
        }
    else:
        return {
            "class_name": class_name,
            "is_new": False
        }


def get_model_import_path(class_name):
    return models_dir.replace("/", ".") + "." + class_name


def create_new_model_by_migration(migration, class_name, table_name):
    create_columns = []
    relationship_columns = []
    relationship_imports = []
    mk_column = ""
    columns_names = []
    try:
        for column in migration.get("create"):
            mk_column = '{} = db.Column('.format(column)
            if migration.get("create").get(column).get("type"):
                if migration.get("create").get(column).get('type') == 'String':
                    if migration.get("create").get(column).get('length'):
                        mk_column = mk_column + "db.String({})".format(
                            migration.get("create").get(column).get('length'))
                    else:
                        mk_column = mk_column + "db.String(255)"
                elif migration.get("create").get(column).get('type') == 'Text':
                    if migration.get("create").get(column).get('length'):
                        mk_column = mk_column + "db.Text({})".format(migration.get("create").get(column).get('length'))
                    else:
                        mk_column = mk_column + "db.Text()"
                else:
                    mk_column = mk_column + "db.{}".format(migration.get("create").get(column).get('type'))
                if migration.get("create").get(column).get('unique'):
                    mk_column = mk_column + ", unique={}".format(migration.get("create").get(column).get('unique'))
                if migration.get("create").get(column).get('primary_key'):
                    mk_column = mk_column + ", primary_key={}".format(
                        migration.get("create").get(column).get('primary_key'))
                if migration.get("create").get(column).get('nullable'):
                    mk_column = mk_column + ", nullable={}".format(migration.get("create").get(column).get('nullable'))
                if migration.get("create").get(column).get('default'):
                    mk_column = mk_column + ", default={}".format(migration.get("create").get(column).get('default'))
                if migration.get("create").get(column).get('onupdate'):
                    mk_column = mk_column + ", onupdate={}".format(migration.get("create").get(column).get('onupdate'))

            create_columns.append(mk_column + ")")
            if column != 'created_at' and column != 'updated_at' and column != 'id':
                columns_names.append(column)

        if migration.get("relationship"):
            rel_column = ''
            extern_table = ''
            for relation in migration.get("relationship"):
                rel_column = '{} = orm.relationship('.format(relation)
                if migration.get("relationship").get(relation).get('mode') == 'OneToOne':
                    extern_table = migration.get("relationship").get(relation).get('table')
                    extern_table = p.singular_noun(extern_table.title().replace('_', ''))
                    rel_column = rel_column + '{}, remote_side=id'.format(
                        extern_table) + ', back_populates="{}"'.format(table_name) + ')'
                    mk_column = "{column} = db.Column(db.Integer, db.ForeignKey('{extern_table}.id'), index=True)".format(
                        column=migration.get("relationship").get(relation).get('column'),
                        extern_table=migration.get("relationship").get(relation).get('table')
                    )
                relationship_imports.append("from app.database.models." + extern_table.lower() + "_model import " + extern_table)
                relationship_columns.append(mk_column + "\n\t" + rel_column)

        content = "from app.core.database import db\n" \
                  "from sqlalchemy.ext.declarative import declarative_base\n" \
                  "from sqlalchemy import orm\n" \
                  "from sqlalchemy_serializer import SerializerMixin\n" \
                  "from datetime import datetime\n" + \
                  "\n".join(relationship_imports) + \
                  "\n\nBase = declarative_base()\n\n\n" \
                  "class " + class_name + " (db.Model, Base, SerializerMixin):\n" \
                                          "\t__tablename__ = '" + table_name + "'" \
                                                                               "\n\t" + \
                  "\n\t".join(create_columns) + \
                  "\n\t" + \
                  "\n\t".join(relationship_columns) + \
                  "\n\n\tdef __init__(self, " + ", ".join(columns_names) + "): \n\t\t" + \
                  "\n\t\t".join('self.{name} = {name}'.format(name=name) for name in columns_names) + \
                  "\n\n"

        return write_model_file(class_name, content)

    except BaseException as err:
        print("-> An error occurring!")
        raise SystemExit(err)


def write_model_file(class_name, content):
    """
    Create new Model file for migration action
    """
    mode = black.FileMode()
    formatted = black.format_file_contents(content, fast=False, mode=mode)

    try:
        with open(models_dir + '/' + class_name.lower() + '_model.py', 'w') as model:
            model.write(formatted)
            return class_name
    except OSError:
        print("An error occurring!")
        raise SystemExit(OSError)


def check_model_exists(class_name):
    """
    Model file exists?
    """
    if path.exists(models_dir + '/' + class_name.lower() + '_model.py'):
        return True
    else:
        return False
