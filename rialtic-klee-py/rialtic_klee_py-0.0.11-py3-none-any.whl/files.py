import csv, json, pickle, os, sys

from klee.internal import log
from fhir.resources import domainresource
from fhir.resources.claim import Claim
from typing import Dict, Any

def save_json(data, target):
    log.debug('saving json: %s', os.path.relpath(target, os.getcwd()))
    os.makedirs(os.path.dirname(target), exist_ok = True)
    with open(target, 'w', encoding = 'utf-8') as file:
        json.dump(data, file, indent = 2)

def read_claim(target) -> Claim:
    return Claim.parse_obj(read_json(target))

def read_json(target) -> Dict[Any, Any]:
    log.debug('reading json: %s', os.path.relpath(target, os.getcwd()))
    with open(target) as file:
        return json.load(file)

def read_str(target) -> str:
    log.debug('reading str: %s', os.path.relpath(target, os.getcwd()))
    with open(target) as file:
        return file.read()

def read_csv(target, normalize = False, **kwargs):
    log.debug('reading csv: %s', os.path.relpath(target, os.getcwd()))
    with open(target) as file:
        reader = csv.DictReader(file, **kwargs)
        new_list = []
        if normalize:
            for row in reader:
                new_row = {}
                for col in row:
                    new_col = col.lower()
                    new_col = new_col.replace(" ", "")
                    new_col = new_col.replace("-", "")
                    new_col = new_col.replace("_", "")
                    new_row[new_col] = row[col]
                new_list.append(new_row)
        else:
            new_list.extend(reader)
        return new_list

class KleeFile:
    def __init__(self, filename, mode, **kwargs):
        self.path = os.path.join(os.getcwd(), filename)
        self.file = open(self.path, mode, **kwargs)
        self.mode = mode

    def read_data(self):
        if self.mode == 'rb':
            return pickle.load(self.file)
        else:
            return json.load(self.file)

    def write_and_flush(self, data):
        if self.mode == 'wb':
            pickle.dump(data, self.file)
        else:
            json.dump(data, self.file)

        self.file.flush()

    def delete_file(self):
        self.file.close()
        if os.path.exists(self.file.name):
            os.remove(self.file.name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete_file()

    def __del__(self):
        self.delete_file()

class Inspection:
    def __enter__(self):
        sys.path.append(os.getcwd())

    def __exit__(self, type, value, traceback):
        sys.path.pop()

def fhir_to_json(obj: domainresource.DomainResource) -> Dict:
    return json.loads(obj.json())
