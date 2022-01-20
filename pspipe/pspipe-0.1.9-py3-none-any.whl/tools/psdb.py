#!/usr/bin/env python

import os
import sys
import textwrap

import toml
import click
from tabulate import tabulate
from click import confirm, style

from libpipe import futils
from pspipe import __version__
from pspipe import settings, database


t_file = click.Path(exists=True, dir_okay=False)
t_dir = click.Path(exists=True, file_okay=False)


@click.group()
@click.version_option(__version__)
def main():
    ''' Add/list/remove obs_ids from a pspipe database'''


def load_settings(settings_file, config_modifiers=None, **additional_modifiers):
    try:
        s = settings.Settings.load_with_defaults(settings_file)
        if config_modifiers:
            mod = settings.Settings.load_from_string(config_modifiers)
            s = s + mod
    except toml.TomlDecodeError as e:
        print(f'Error parsing configuration: {e}')
        sys.exit(1)
    return s + additional_modifiers


@main.command('init')
@click.argument('template_name', type=str)
@click.argument('data_dir', type=str)
@click.argument('rev_name', type=str)
@click.argument('config_modifier', nargs=-1, required=False)
def init(template_name, data_dir, rev_name, config_modifier):
    ''' Initialize new configuration

    \b
    TEMPLATE_NAME: Template name (nenufar, hba or a12)
    DATA_DIR: Data directory
    REV_NAME: Image revision name
    CONFIG_MODIFIER: Optional configuration modifiers, of the form key=value
    '''
    if os.listdir(os.getcwd()):
        print('Current working directory is not empty, configuration file can not be created.')
        return

    settings_file = settings.get_template_path(template_name)
    print(f'Initializing configuration from {settings_file}')

    rev_name = rev_name.replace('.toml', '')
    conf_file = rev_name + '.toml'

    s = load_settings(settings_file, config_modifier, **{'data_dir': futils.abspath(data_dir),
                                                         'image': {'name': rev_name}})
    s.duplicate(conf_file, copy_parset_files=True)

    print(f'New configuration saved to {conf_file}')


@main.command('clone')
@click.argument('settings_file', type=t_file)
@click.argument('data_dir', type=str)
@click.argument('config_modifier', nargs=-1, required=False)
def clone(settings_file, data_dir, config_modifier):
    ''' Clone configuration and Obs IDs from an other pspipe config file

        \b
        CONFIG_MODIFIERS: Optional configuration modifiers, of the form key=value
    '''
    print(f'Cloning configuration from {settings_file}')
    s_in = load_settings(settings_file, config_modifier)
    s_out = s_in.duplicate(os.path.basename(settings_file), copy_parset_files=True, data_dir=futils.abspath(data_dir))

    db_in = database.Database(s_in)
    db_out = database.Database(s_out)
    for obs_id in db_out.list_obs_ids():
        db_out.new_obs_id_from_other(obs_id, db_in.get_obs_id_meta(obs_id))
        print(f'Adding obs_sd {obs_id}')


@main.command('new_rev')
@click.argument('settings_file', type=t_file)
@click.argument('rev_name', type=str)
@click.argument('config_modifier', nargs=-1, required=False)
def new_rev(settings_file, rev_name, config_modifier):
    ''' Create a new image revision

        \b
        CONFIG_MODIFIERS: Optional configuration modifiers, of the form key=value
    '''
    rev_name = rev_name.replace('.toml', '')
    conf_file = rev_name + '.toml'
    s = load_settings(settings_file, config_modifier)
    root_settings_file = s.get_root_settings_file()
    s.duplicate(conf_file, strip_parents_keys=True, default_settings=root_settings_file, image={'name': rev_name})
    print(f'New configuration saved to {conf_file}')


@main.command('list_revs')
@click.argument('settings_file', type=t_file)
@click.option('--obs_id', '-o', type=str, help='Obs ID')
@click.option('--img_rev', '-i', type=str, help='Image revision')
def list_revs(settings_file, obs_id, img_rev):
    ''' List all image and visibilities revisions
    '''
    s = load_settings(settings_file)
    db = database.Database(s)

    print(f"Image revisions in {s.data_dir}:")
    w_i = textwrap.TextWrapper(width=100, initial_indent='Obs: ', break_long_words=False)
    w_v = textwrap.TextWrapper(width=100, initial_indent='   Obs: ', subsequent_indent='   ',
                               break_long_words=False)

    for db_img_rev in db.list_image_revisions():
        if img_rev is not None and db_img_rev.name != img_rev:
            continue
        if obs_id and not db_img_rev.has_obs_id(obs_id):
            continue

        print(f'\n{style(db_img_rev.name, bold=True)}: {db_img_rev.get_path()}')
        print(w_i.fill(" ".join(db_img_rev.list_obs_ids())))
        for db_vis_rev in db_img_rev.list_vis_revisions():
            if obs_id is not None and not db_vis_rev.has_obs_id(obs_id):
                continue

            print(f' * {style(os.path.basename(db_vis_rev.get_path()), bold=True)}')
            print(w_v.fill(" ".join(db_vis_rev.list_obs_ids())))


def print_obs_ids(db, obs_ids):
    obs_metas = list(map(db.get_obs_id_meta, obs_ids))
    if not obs_metas:
        print('No obs_ids in database')
        return

    data = [obs_ids]

    for k in database.obs_id_info_keys:
        data.append([meta[k] for meta in obs_metas])

    data = list(map(list, zip(*data)))
    header = ['Obs_id'] + database.obs_id_info_keys

    print(tabulate(data, header))


@main.command('list_obs')
@click.argument('settings_file', type=t_file)
def list_obs(settings_file):
    ''' List obs_ids for the given image_rev/vis_rev
    '''
    s = load_settings(settings_file)
    vis_rev = database.VisRevision(s)
    if not os.path.exists(vis_rev.get_path()):
        print(f'Error: visibilities revision does not exist.')
        return

    print_obs_ids(database.Database(s), vis_rev.list_obs_ids())


@main.command('list_all_obs')
@click.argument('settings_file', type=t_file)
def list_all_obs(settings_file):
    ''' List obs_ids in the pspipe database
    '''
    db = database.Database(load_settings(settings_file))
    print_obs_ids(db, db.list_obs_ids())


def add(db, obs_id, ms_file_list, **kargs):
    if db.has_obs_id(obs_id):
        print(f'Error: obs_id {obs_id} already exist.')
        return

    if ms_file_list:
        ms_files = [k.strip().split() for k in open(ms_file_list).readlines() if k.strip()]
        db.new_obs_id(obs_id, ms_files)
    else:
        db.new_obs_id(obs_id, **kargs)

    print(f'{obs_id} successfully created.')


@main.command('add_obs')
@click.argument('settings_file', type=t_file)
@click.argument('obs_id', type=str)
@click.option('--ms_file_list', '-m', type=t_file, help='MS file list')
@click.option('--int_time', '-i', type=float, help='Integration time', default=0)
@click.option('--total_time', '-t', type=float, help='Total time', default=0)
@click.option('--chan_width', '-w', type=float, help='Channel width in Hz', default=0)
def add_obs(settings_file, obs_id, ms_file_list, int_time, total_time, chan_width):
    ''' Add obs_ids to the given pspipe database
    '''
    db = database.Database(load_settings(settings_file))
    add(db, obs_id, ms_file_list, int_time=int_time, total_time=total_time, chan_width=chan_width)


@main.command('add_all_obs')
@click.argument('settings_file', type=t_file)
@click.argument('ms_file_lists', nargs=-1, type=t_file)
def add_all_obs(settings_file, ms_file_lists):
    ''' Add obs_ids from MSs list files
    '''
    db = database.Database(load_settings(settings_file))
    for ms_list in ms_file_lists:
        obs_id = os.path.basename(ms_list)
        add(db, obs_id, ms_list)


@main.command('set_obs_info')
@click.argument('settings_file', type=t_file)
@click.argument('obs_ids', type=str)
@click.option('--ms_file_list', '-m', type=str, help='MS file list')
@click.option('--int_time', '-i', type=float, help='Integration time')
@click.option('--total_time', '-t', type=float, help='Total time')
@click.option('--chan_width', '-w', type=float, help='Channel width in Hz',)
def set_obs_info(settings_file, obs_ids, ms_file_list, int_time, total_time, chan_width):
    ''' Set meta data info

    \b
    OBS_IDS: Obs ID(s), comma separated with bash-type wildcards support
    '''
    db = database.Database(load_settings(settings_file))
    obs_id_set = db.filter_obs_ids(obs_ids)

    if not obs_id_set:
        print(f'Error: No obs_ids matching {obs_ids} in database.')
        return

    for obs_id in obs_id_set:
        meta = db.get_obs_id_meta(obs_id)

        if ms_file_list:
            assert os.path.exists(ms_file_list)

            ms_files = [k.strip().split() for k in open(ms_file_list).readlines()]
            meta.set_ms_files(ms_files)
        else:
            d = {'int_time': int_time, 'total_time': total_time, 'chan_width': chan_width}
            for k, v in d.copy().items():
                if v is None:
                    del d[k]
            meta.update(d)

        meta.save()

        print(f'{obs_id} successfully modified.')


@main.command('add_rev_img')
@click.argument('settings_file', type=t_file)
@click.argument('obs_id', type=str)
@click.argument('fits_images', nargs=-1, type=t_file)
@click.option('--even', '-e', help='Fits images are even set', is_flag=True)
@click.option('--odd', '-o', help='Fits images are odd set', is_flag=True)
def add_rev_img(settings_file, obs_id, fits_images, even, odd):
    ''' Add FITS_IMAGES to the given pspipe database
    '''
    db = database.Database(load_settings(settings_file))
    if not db.has_obs_id(obs_id):
        print(f'Error: obs_id {obs_id} does not exist. Create with psdb add {obs_id}')
        return

    if db.has_image_revisions(db.settings.image.name):
        img_rev = db.get_image_revision()
        if img_rev is None:
            img_rev = db.new_image_revision(db.settings.image.name)
    else:
        img_rev = db.new_image_revision(db.settings.image.name)

    if not img_rev.has_obs_id(obs_id):
        img_meta = img_rev.new_obs_id(obs_id)
    else:
        img_meta = img_rev.get_meta(obs_id)

    files = list(map(futils.abspath, fits_images))
    img_meta.add_fits(files, even=even, odd=odd, verbose=True)
    img_meta.save()


@main.command('list_rev_img')
@click.argument('settings_file', type=t_file)
@click.option('--obs_ids', '-o', type=str, help='Only for given obs ID(s)')
def list_rev_img(settings_file, obs_ids):
    ''' Retrieve FITS images statistics
    '''
    db = database.Database(load_settings(settings_file))
    if not db.has_image_revisions(db.settings.image.name):
        print(f'Error: image revision does not exist.')
        return

    if obs_ids is not None:
        obs_id_set = db.filter_obs_ids(obs_ids)
        if not obs_id_set:
            print(f'Error: No obs_ids matching {obs_ids} in database.')
            return

    img_rev = db.get_image_revision()
    stats = {}

    for obs_id in img_rev.list_obs_ids():
        if obs_ids is not None and obs_id not in obs_id_set:
            continue
        meta = img_rev.get_meta(obs_id)
        if meta is None:
            continue
        stats[obs_id] = meta.get_fits_stat()

    if len(stats) == 0:
        return

    all_types = sorted(set(t for k in stats.values() for t in k.keys()))

    data = []
    for obs_id, stat in stats.items():
        data.append([obs_id] + [stat.get(k, 0) for k in all_types])

    header = ['Obs_id'] + all_types

    print(tabulate(data, header))


@main.command('remove_rev')
@click.argument('settings_file', type=t_file)
@click.option('--obs_ids', '-o', type=str, help='Only for given obs ID(s)')
def remove_rev(settings_file, obs_ids):
    ''' Remove an image revision from the given pspipe database
    '''
    db = database.Database(load_settings(settings_file))

    if obs_ids is not None:
        obs_id_set = db.filter_obs_ids(obs_ids)
        if not obs_id_set:
            print(f'Error: No obs_ids matching {obs_ids} in database.')
            return

    img_rev = db.get_image_revision()

    if img_rev is None:
        print(f'Error: image revision {db.settings.image.name} does not exist.')
        return

    if obs_ids is not None:
        for obs_id in img_rev.list_obs_ids():
            if obs_id in obs_id_set and confirm(style(f'Removing ObsID {obs_id} in revision {img_rev.name} ?',
                                                      fg='yellow')):
                img_rev.remove(obs_id=obs_id)
    else:
        if confirm(style(f'Removing {img_rev.name} ?', fg='yellow')):
            img_rev.remove()
            print(f'Image revision {db.settings.image.name} successfully removed.')
        else:
            print('No changes made.')


@main.command('remove_obs')
@click.argument('settings_file', type=t_file)
@click.argument('obs_ids', type=str)
def remove_obs(settings_file, obs_ids):
    ''' Remove an Obs ID from the given pspipe database
    '''
    db = database.Database(load_settings(settings_file))
    obs_id_set = db.filter_obs_ids(obs_ids)

    if not obs_id_set:
        print(f'Error: No obs_ids matching {obs_ids} in database.')
        return

    if confirm(style(f'Removing obs_ids: {",".join(obs_id_set)} ?', fg='yellow')):
        for obs_id in obs_id_set:
            db.remove_obs_id(obs_id)
            print(f'{obs_id} successfully removed.')
    else:
        print('No changes made.')


if __name__ == '__main__':
    main()
