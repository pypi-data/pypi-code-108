from . import version
import argparse


# ---- functions used by the argparser
# names starts with 'p_' (so I can distinguish they from other objects)
def p_version(args):
    print('version ' + version)


def p_create_task(args):
    from .cli_create import create_task
    result = create_task(args.name)

    if result:
        print('Задача не была создана!')
    else:
        print('Задача ' + args.name + ' создана.')


def p_addtest(args):
    from .cli_test import addtest
    addtest(args.amount)


def p_cleartests(args):
    from .cli_test import cleartests
    cleartests()


def p_build(args):
    from .cli_build import build
    build(args.tasks)


# ---- arguments definition
def parser():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(help='commands')

    version_parser = s.add_parser('version', help='print package version')
    version_parser.set_defaults(func=p_version)

    create_parser = s.add_parser('create', help='создание новой задачи в текущем каталоге')
    create_parser.add_argument('name', help='название задачи')
    create_parser.set_defaults(func=p_create_task)

    addtest_parser = s.add_parser('addtests', help='добавление тестов')
    addtest_parser.add_argument('amount', help='количество добавляемых тестов', type=int)
    addtest_parser.set_defaults(func=p_addtest)

    cleartest_parser = s.add_parser('deltests', help='удалить все тесты')
    cleartest_parser.set_defaults(func=p_cleartests)

    build_parser = s.add_parser('build', help='собрать zip-архив задачи')
    build_parser.add_argument('tasks', nargs='+', help='названия задач; \'*\' - собрать все задачи в текущем каталоге')
    build_parser.set_defaults(func=p_build)

    '''
    PARAMETERS EXAMPLES
    
    # ---- parameter with alias (without value)
    example_parser.add_argument('--long', '-l', default=False, action='store_true')
    
    # ---- parameter with value (without alias)
    example_parser.add_argument('value', default='.')
    
    '''

    return p


# ---- entry point
def run():
    p = parser()
    args = p.parse_args()

    if not hasattr(args, 'func'):
        p.print_help()
    else:
        args.func(args)
        return 0

    return 1
