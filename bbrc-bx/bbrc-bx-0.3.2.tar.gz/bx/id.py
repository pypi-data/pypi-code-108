from bx.command import Command


class IDCommand(Command):
    """Return generic information like subject/session labels, parent project.

    Usage:
     bx id <resource_id>
    """
    nargs = 1

    def __init__(self, *args, **kwargs):
        super(IDCommand, self).__init__(*args, **kwargs)

    def parse(self):
        id = self.args[0]
        df = self.run_id(id, get_id_table, max_rows=10)

        if len(df) == 1:
            print(df.iloc[0])
        else:
            self.to_excel(df)


def get_id_table(x, experiments):
    import pandas as pd
    table = []
    from tqdm import tqdm
    columns = ['label', 'subject_label']
    for e in tqdm(experiments):
        try:
            e_id = e['ID']
            exp = x.array.experiments(experiment_id=e_id, columns=columns).data[0]
            table.append([e_id, exp['label'], exp['subject_label'], exp['project']])
        except KeyboardInterrupt:
            break

    columns = ['ID', 'label', 'subject_label', 'project']
    df = pd.DataFrame(table, columns=columns).set_index('ID').sort_index()
    return df
