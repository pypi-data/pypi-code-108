import click

from redbeard_cli.commands.generate import (
    crm as crm_data_generator
)


@click.group()
def data_generator():
    pass


@data_generator.command()
@click.option('-a', '--attributes-file', required=True, help='CRM Attributes Schema in JSON format')
@click.option('-i', '--id-file', required=True, help='File path for list of IDs for which to generate CRM data')
@click.option('-o', '--output-file', required=True, help='Full path of output file name')
def crm(attributes_file: str, id_file:str, output_file: str):
    crm_data_generator.generate(attributes_file, id_file, output_file)

