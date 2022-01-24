
import os


def get_database(database=None, path=None, user_rc_list=None):
    """Helper for handling CLI inputs.
    """
    from flinter.io import load
    from flinter.scan import scan_dir
    from flinter.scan import scan_file
    from flinter.rules import init_languages_specs

    if database is None and path is None:
        raise Exception("Database or path must be defined")

    if database:
        return load(database)

    rule_sets = init_languages_specs(user_rc_list=user_rc_list)
    if os.path.isdir(path):
        return scan_dir(path, rule_sets=rule_sets)

    else:
        rules = rule_sets.get_from_fname(path)
        return scan_file(path, rules=rules)


def dump_file(filename, db, verbose=1):
    from flinter.io import dump

    # ensure extension is json
    base_filename = '.'.join(filename.split('.')[:-1])
    filename = f'{base_filename}.json'

    dump(filename, db)

    if verbose:
        print(f'Created {filename}')


def score_cli(count_dict, max_lvl=None):
    """Show stats in terminal.
    """
    def _rec_print(data, lvl=0):

        head = "  {:<3} {:<50} {:<10} {:<10}".format(lvl, data['path'], '{:.2f}'.format(data['rate']), data['size'])

        print(head)

        for varname in ["regexp_rules", "struct_rules"]:
            for key, value in data[varname].items():
                print(f"{indent} {key} :  {value}")

        if lvl >= max_lvl:
            print(f"{indent}.")
            return
        else:
            for child in data["children"]:
                _rec_print(child, lvl=lvl + 1)

    if max_lvl == 0:
        rating = '{:.2f}'.format(count_dict['rate'])
        size = count_dict['size']
        print(f"Flinter global rating -->|{rating}|<--  ({size} statements)")
        return

    head = "  {:<3} {:<50} {:<10} {:<10}".format("lvl", "path", "rate", "size (stmt)")
    print(head)

    indent = "........"

    _rec_print(count_dict)


def _build_pretty_table_for_regexp(regexp_item):
    from prettytable import PrettyTable

    headers = ['line_no', 'column', 'span', 'line']

    table = PrettyTable(headers)
    for rule_info in regexp_item:
        table.add_row([rule_info.get(name) for name in headers])

    return table
