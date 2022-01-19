from tabulate import tabulate

def output_table(obj, sort_by=None):
    if sort_by:
        obj = sorted(obj, key = lambda x: x[sort_by], reverse=True)
    table = tabulate(obj, headers="keys")
    print(table)
    return table

    
