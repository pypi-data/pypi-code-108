import csv
import json
from random import randrange
from typing import Dict, List


# CRM Dataset generator


def generate(attributes_file: str, id_file: str, output_file: str):
    attributes = read_crm_attributes(attributes_file)
    attribute_keys = ['id', 'id_type']
    for a in attributes.keys():
        attribute_keys.append(a)
    crm_data = []
    with open(id_file) as idfo:
        reader = csv.DictReader(idfo)
        for row in reader:
            crm_record = {
                'id': row['id'],
                'id_type': row['id_type']
            }
            for attribute in attribute_keys:
                if attribute in ['id', 'id_type']:
                    continue
                crm_record[attribute] = select_attribute_value(attributes[attribute])
            crm_data.append(crm_record)

    with open(output_file, 'w') as ofo:
        writer = csv.DictWriter(ofo, fieldnames=attribute_keys)
        writer.writeheader()
        for record in crm_data:
            writer.writerow(record)


def read_crm_attributes(attributes_file: str) -> Dict[str, List[str]]:
    attributes = {}
    with open(attributes_file) as afo:
        attr_records = json.load(afo)
        for ar in attr_records:
            attribute = ar.get('attribute', None)
            if attribute is not None:
                attribute_values = ar.get('attribute_values', None)
                attributes[attribute] = attribute_values
    return attributes


def select_attribute_value(attribute_values: List[str]) -> str:
    return attribute_values[randrange(len(attribute_values))]

