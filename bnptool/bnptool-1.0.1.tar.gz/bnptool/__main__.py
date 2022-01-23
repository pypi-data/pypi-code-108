import argparse
import os
import typing
from base64 import urlsafe_b64encode

from bcml.dev import create_bnp_mod
from bcml.util import TempModContext
from bcml.install import install_mod, export
from pathlib import Path


def bnp_create(args):
    """Takes a graphics pack or switch mod and creates a BNP mod."""
    print(args)
    target_dir: typing.Optional[str] = args.output
    mod_name: typing.Optional[str] = args.name
    mod_version: typing.Optional[str] = args.version
    options = {"disable": [], "options": {"rstb": {}, "text:": {}, "general": {}}}
    if args.disablepacks:
        options["disable"].append('packs')
    if args.disableaamp:
        options["disable"].append('aamp')
    if args.disabledrops:
        options["disable"].append('drops')
    if args.disabletext:
        options["disable"].append('texts')
    if args.disableactorinfo:
        options["disable"].append('actors')
    if args.disableshrineent:
        options["disable"].append('dungeonstatic')
    if args.disablemaps:
        options["disable"].append('maps')
    if args.disablegamedata:
        options["disable"].append('gamedata')
    if args.disablesavedata:
        options["disable"].append('savedata')
    if args.disableeventinfo:
        options["disable"].append('eventinfo')
    if args.disablestatuseff:
        options["disable"].append('effects')
    if args.disableresactors:
        options["disable"].append('residents')
    if args.disablequests:
        options["disable"].append('quests')
    if args.disablerstb:
        options["disable"].append('rstb')
    if args.norstbest:
        options["options"]["rstb"] = {"no_guess": True}
    if args.mergetextalllang:
        options["options"]["texts"] = {"all_langs": True}
    if args.lowestpriority:
        options["options"]["general"] = {"base_priority": True}
    meta = {'version': args.version, 'name': args.name}
    if not mod_name:
        meta['name'] = 'Unnamed'
    if not target_dir:
        target_dir = os.getcwd() + '\\' + mod_name + '.bnp'
    if not mod_version:
        meta['version'] = '1.0.0'
    if args.description:
        meta['desc'] = args.description
    else:
        meta['desc'] = ''
    if args.image:
        meta['image'] = args.image
    else:
        meta['image'] = ''
    if args.url:
        meta['url'] = args.url
    else:
        meta['url'] = ''

    # Place Holder Args required to create a functional BNP
    meta['depends'] = {}
    meta['options'] = {}
    meta['showCompare'] = False
    meta['showConvert'] = False

    create_bnp_mod(mod=Path(args.mod), output=Path(target_dir), meta=meta, options=options)


def convert_bnp(args):
    """Converts a BNP to a standalone zip"""
    target_dir: typing.Optional[str] = args.output
    if not target_dir:
        target_dir = os.getcwd() + '\\StandAlone.zip'
    with TempModContext():
        install_mod(Path(args.bnp), merge_now=True, options={"options": {"texts": {"all_langs": True}}, "disable": []})
        export(Path(target_dir))


def get_version_hash(args):
    """Takes the name and version and returns the BNP's mod hash"""
    depend_string = f'{args.name}=={args.version}'
    hashed_id = urlsafe_b64encode(depend_string.encode('utf-8')).decode('utf-8')
    print('The mod hash ID is: ', hashed_id)


def main():
    parser = argparse.ArgumentParser(description='Tool to create and manage BNPs via command line using BCML')

    subparses = parser.add_subparsers(dest='command', help='Command')
    subparses.required = True

    c_parser = subparses.add_parser('create', description='Create a BNP', aliases=['c'])
    c_parser.add_argument('mod', help='Path of the mod\'s directory or zip')
    c_parser.add_argument('--output', '-o', help='The path to the BNP file to create')
    c_parser.add_argument('--name', '-n', help='Name of the mod')
    c_parser.add_argument('--version', help='Version of the mod')
    c_parser.add_argument('--description', '-d', help='Description of the mod')
    c_parser.add_argument('--depends', '-d', help='Dependencies of the mod')
    c_parser.add_argument('--image', '-i', help='Url of the mod\'s image')
    c_parser.add_argument('--url', '-u', help='Url of the mod')
    c_parser.add_argument('--lowestpriority', action='store_true', help='Defautls to false')
    c_parser.add_argument('--disablepacks', action='store_true', help='Defaults to false')
    c_parser.add_argument('--disableaamp', action='store_true', help='Disables the AAMP merger. Defaults to false')
    c_parser.add_argument('--disabledrops', action='store_true', help='Disables the Drop merger. Defaults to false')
    c_parser.add_argument('--disabletext', action='store_true', help='Disables the Text merger. Defaults to false')
    c_parser.add_argument('--disableactorinfo', action='store_true',
                          help='Disables the Actor Info merge. Defaults to false')
    c_parser.add_argument('--disableshrineent', action='store_true',
                          help='Disables the Shrine entrance merger. Defaults to false')
    c_parser.add_argument('--disablemaps', action='store_true', help='Disables the Map merger. Defaults to false')
    c_parser.add_argument('--disablegamedata', action='store_true',
                          help='Disables the Game Data merger. Defaults to false')
    c_parser.add_argument('--disablesavedata', action='store_true',
                          help='Disables the Save data merger. Defaults to false')
    c_parser.add_argument('--disableeventinfo', action='store_true',
                          help='Disables the Event Info merger. Defaults to false')
    c_parser.add_argument('--disablestatuseff', action='store_true',
                          help='Disables the Status Effect merger. Defaults to false')
    c_parser.add_argument('--disableresactors', action='store_true',
                          help='Disables the Resident Actors merger. Defaults to false')
    c_parser.add_argument('--disablequests', action='store_true', help='Disables the Quest merger. Defaults to false')
    c_parser.add_argument('--disablerstb', action='store_true',
                          help='Disables the editing of the RSTB. Defaults to false')
    c_parser.add_argument('--norstbest', action='store_true',
                          help='Disables estimation for AAMP and BFRES files on RSTB entries. Defaults to false')
    c_parser.add_argument('--mergetextalllang', action='store_true',
                          help='Merges text changes to all languages. the Defaults to false')
    c_parser.set_defaults(func=bnp_create)

    t_parser = subparses.add_parser('convert', description='Convert a BNP to a standalone mod', aliases=['cv'])
    t_parser.add_argument('bnp', help='Path of the BNP file')
    t_parser.add_argument('--output', '-o', help="Where to ouput the exported BNP")
    t_parser.set_defaults(func=convert_bnp)

    h_parser = subparses.add_parser('hash', description='Get a mod\'s hash ID for dependencies', aliases=['h'])
    h_parser.add_argument('name', help='Name of the mod')
    h_parser.add_argument('version', help='Version of the mod')
    h_parser.set_defaults(func=get_version_hash)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
