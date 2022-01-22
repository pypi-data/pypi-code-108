from random import random
from typing import Dict, Tuple, List
import os
import csv

from .field_generators.base import *
from .config import loadConfig


def main(file: str, outdir: str):
    """The main entry point for the generate command

        Params:
            file (str): the validated file path
            outdir (str): the path to the 'out'-directory, where data should be stored
    """
    config = loadConfig(file)
    data = generateByConfig(config)

    file_count = 0

    # write data to disk
    for key in data.keys():
        path = os.path.join(outdir, f"{key}.csv")
        file_count += 1

        with open(path, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file, dialect='excel')
            schema = data.get(key)
            headers = schema[0]

            # write header
            writer.writerow(map(lambda header: header[0], headers))
            # write content
            writer.writerows([[(None if entry is None else headers[index][1](entry)) for (
                index, entry) in enumerate(row)] for row in schema[1]])

    return f"Successfully generated {file_count} files!"


def generateByConfig(config: Dict) -> Dict[str, Tuple[Tuple[Tuple], List]]:
    """Generates the data based on the configuration file

        Params:
            config (Dict): the validated configuration file

        Returns:
            data (Dict): the generated data by name and rows
    """

    res: Dict[str, Tuple[Tuple[Tuple], List]] = {}

    generateBaseData(config, res)
    generateFromSteps(config, res)

    return res


def generateBaseData(config: Dict, res: Dict):
    base: Dict[str, int] | None = config.get("base")
    if base is None:
        return

    for (schema_name, amount) in base.items():
        generate_schema(schema_name, config, {}, res, amount=amount)


def generateFromSteps(config: Dict, res: Dict):
    steps: Dict[str, Dict] = config.get("steps")
    if steps is None:
        return

    initial_step = config["initial"]
    amount = config["amount"]

    for _ in range(amount):
        step: Dict = steps.get(initial_step)
        iter_res = {}

        while step is not None:
            generate: str | Dict = step.get("generate")

            # choose what schema to generate
            if type(generate) is str:
                schema_name = generate
            else:
                rand = random()
                total = 0
                schema_name = None

                for (key, value) in generate.items():
                    if (value + total) >= rand:
                        schema_name = key
                        break
                    total += value

            if schema_name is None:
                step = None
                continue

            generate_schema(schema_name, config, res, iter_res)

            step = steps.get(step.get("next"))

        # add generated step data to complete result
        for key, value in iter_res.items():
            if res.get(key) is None:
                res[key] = (value[0], [*value[1]])
            else:
                res[key][1].extend(value[1])


def generate_schema(schema_name: str, config: Dict, res: Dict, iter_res: Dict = {}, amount: int = 1):
    schema: Dict = config["schemas"][schema_name]

    # initialize schema entry if it is not present in result yet
    if iter_res.get(schema_name) is None:
        def map_schema_key(key: str) -> str | Tuple:
            return (key, schema[key].val_to_str)

        iter_res[schema_name] = (
            ((f"{schema_name.lower()}_id", str), *map(map_schema_key, schema.keys())), [])

    id = 1 if res.get(schema_name) is None else len(
        res[schema_name][1]) + 1

    for _ in range(amount):
        # initialize schema values with id
        schema_entries = iter_res[schema_name][1]
        schema_entries.append([id])

        # generate schema_values
        for field in schema.values():
            if isinstance(field, FieldGenerator):
                value = field.generate(
                    schema_name=schema_name, res=res, iter_res=iter_res)
            else:
                raise Exception(f"Unknown field:\n{field}")

            schema_entries[-1].append(value)

        id += 1
