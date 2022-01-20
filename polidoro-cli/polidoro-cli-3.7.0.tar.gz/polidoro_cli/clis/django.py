from polidoro_argument import Command
from polidoro_cli import CLI


class Django(object):
    @Command(help='Unapply last migration. Accepts APPLICATION and the number of rollbacks.')
    def rollback(*args):
        app = None
        migrations_to_rollback = 1
        if args:
            if len(args) == 1:
                if args[0].isnumeric():
                    migrations_to_rollback = int(args[0])
                else:
                    app = args[0]
            else:
                if args[0].isnumeric():
                    app = args[1]
                    migrations_to_rollback = int(args[0])
                else:
                    app = args[0]
                    migrations_to_rollback = int(args[1])

        if app is None:
            print('Getting last migration app...')
            migrations = Django._get_last_migrations()
            app = migrations[0][0]

        query_filter = f'.filter(app=\'{app}\')' if app else ''

        print(f'Rollbacking last {migrations_to_rollback} {app} migrations..')
        migrations = Django._get_last_migrations(migrations_to_rollback, query_filter)
        if migrations:
            last_app, last_name = migrations[-1]
            CLI.execute(f'./manage.py migrate {last_app} {last_name}')
        else:
            print(f'There is no {app} migration')

    @staticmethod
    def _get_last_migrations(migrations=0, query_filter=''):
        out, err = CLI.execute("echo \"from django.db.migrations.recorder import MigrationRecorder;print(list("
                               f"MigrationRecorder.Migration.objects{query_filter}.values_list('app', "
                               f"'name').order_by('-applied')[ :{migrations + 1}]))\" | ./manage.py shell",
                               capture_output=True, show_cmd=False)
        return eval(out)
