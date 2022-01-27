"""
18/12/18
Convert the XML annotations to csv
"""

from pathlib import Path
import pandas as pd
from vpv.annotations.impc_xml import load_xml
import yaml

from collections import defaultdict


xml_dir = Path('/home/neil/Desktop/xml_to_csv')
outfile = '/home/neil/Desktop/181218_xml_annotations_to_csv.csv'


term_mapping_file = '/vpv_viewer/annotations/options/e15_5/ucd_terms.yaml'
with open(term_mapping_file) as fh:
    terms = yaml.load(fh)

map_ = {}
for _, p in terms['parameters'].items():
    param_id = p['impc_id']
    name = p['name']
    map_[param_id] = name


all_spec = []

for xml_file in xml_dir.iterdir():
    r = load_xml(str(xml_file))
    print(r)

    spec_records = {}

    spec_id = r[5]

    for param_id, options in r[7].items():
        option = options['option']
        param_name = map_[param_id]
        spec_records[param_name] = option

    df = pd.DataFrame.from_dict(spec_records, orient='index', columns=['option'])
    df.rename(columns={'option': spec_id}, inplace=True)

    all_spec.append(df)

o = pd.concat(all_spec, axis=1)

o.to_csv(outfile)