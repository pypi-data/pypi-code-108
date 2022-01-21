
from pycldf import Dataset
from .maker import Record


def load_cldf(cldf, table='ValueTable', column='Cognacy'):
    dataset = Dataset.from_metadata(cldf)

    if table not in dataset:  # pragma: no cover
        raise ValueError("Required table %s not in dataset" % table)

    if (table, column) not in dataset:  # pragma: no cover
        raise ValueError("Required column %s is not in table %s" % (column, table))

    languages = {r['ID']: r for r in dataset['LanguageTable']}
    parameters = {r['ID']: r for r in dataset['ParameterTable']}

    for row in dataset[table]:
        for e in ('Language_ID', 'Parameter_ID', column):
            assert e in row, 'Missing expected column %s in table %s' % (e, table)

        yield Record(
            ID=row['ID'],
            Language_ID=row['Language_ID'],
            Language=languages[row['Language_ID']]['Name'],
            Parameter_ID=row['Parameter_ID'],
            Parameter=parameters[row['Parameter_ID']]['Name'],
            Item=row['Value'],
            Loan=row.get('Loan', None),
            Cognacy=row[column]
       )
