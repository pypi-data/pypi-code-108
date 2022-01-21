from tabulate import tabulate

def output_table(obj, sort_by=None, reverse=False):
    if sort_by:
        obj = sorted(obj, key = lambda x: x[sort_by], reverse=reverse)
    table = tabulate(obj, headers="keys")
    print(table)
    return table

def yaml_multiline_string_pipe(dumper, data):
    text_list = [line.rstrip() for line in data.splitlines()]
    fixed_data = "\n".join(text_list)
    if len(text_list) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data, style="|")
    return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data)

