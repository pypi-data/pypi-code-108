# Handle tasks
#
# Author: F. Mertens

import os
import re
import glob
import tempfile

import numpy as np
import astropy.io.fits as pf

from libpipe import worker, futils
from . import database, utils

CWD = os.getcwd()

H5_FLAG_BACKUP = 'flags_before_ssins.h5'


def get_all_tasks():
    d = {}
    for klass in AbstractTask.__subclasses__():
        if hasattr(klass, 'name'):
            d[klass.name] = klass
    return d


def get_all_tasks_descriptions():
    d = {}
    for klass in AbstractTask.__subclasses__():
        if hasattr(klass, 'name') and hasattr(klass, 'desc'):
            d[klass.name] = klass.desc
    return d


def get_target_host(in_file, worker_settings):
    host = None
    if worker_settings.run_on_file_host and worker_settings.run_on_file_host_pattern:
        r = re.search(worker_settings.run_on_file_host_pattern, in_file)
        if r is not None:
            host = r.group(1)
    return host


class AbstractSubTask(object):

    def __init__(self, settings_obj, exec_name):
        self.settings = settings_obj
        self.exec_name = exec_name

    def get_parameters(self):
        raise NotImplementedError()

    def get_log_file(self):
        return None

    def done_callback(self):
        pass

    def build_command(self):
        parameters = ' '.join(self.get_parameters())
        cmd = f'cd {CWD}; {self.exec_name} {parameters}'

        return cmd


class AbstractTask(object):

    def __init__(self, name, settings_obj, **worker_kargs):
        self.name = name
        self.settings = settings_obj.copy()
        self.settings.worker.update(worker_kargs)
        s_worker = self.settings.worker

        if not self.settings.validate('worker'):
            raise ValueError('Invalid worker settings.')

        self.worker = worker.get_worker_pool(name, nodes=s_worker.nodes, max_concurrent=s_worker.max_concurrent,
                                             env_file=s_worker.env_file)

    def init_for_new_task(self, post_task_name):
        s_worker = self.settings.worker
        self.worker = worker.get_worker_pool(post_task_name, nodes=s_worker.nodes,
                                             max_concurrent=s_worker.max_concurrent,
                                             env_file=s_worker.env_file)

    def add_sub_task(self, sub_task, run_on_host=None):
        log_file = sub_task.get_log_file()

        if log_file is not None:
            if not os.path.exists(os.path.dirname(log_file)):
                os.makedirs(os.path.dirname(log_file))

        cmd = sub_task.build_command()
        if self.settings.debug:
            print(cmd)
        self.worker.add(cmd, output_file=log_file, done_callback=sub_task.done_callback, run_on_host=run_on_host)

    def run(self, obs_ids):
        raise NotImplementedError()

    def execute(self):
        self.worker.execute()

    def execute_single_local(self, cmd, log_file):
        w = worker.WorkerPool([worker.localhost_shortname], name=self.name,
                              env_source_file=self.settings.worker.env_file)
        w.add(cmd, output_file=log_file)
        if self.settings.debug:
            print(cmd)
        w.execute()


class ImagingSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id, inp_ms_files, even=False, odd=False):
        AbstractSubTask.__init__(self, settings_obj, 'wsclean')
        self.inp_ms_files = inp_ms_files
        self.obs_id = obs_id
        self.even = even
        self.odd = odd
        self.img_rev = database.ImageRevision(self.settings)
        self.obs_meta = database.Database(self.settings).get_obs_id_meta(self.obs_id)
        self.temp_dir = None
        self.temp_protect_file = None

    def get_dir(self):
        return self.img_rev.get_image_path(self.obs_id)

    def get_sb(self):
        res = re.search(r'_SB(\d+)', os.path.basename(self.inp_ms_files[0]))
        if res is not None:
            return res.groups()[0]
        return '000'

    def get_log_file(self):
        return os.path.join(self.get_dir(), 'logs', os.path.basename(self.get_fits_prefix()) + '.log')

    def get_fits_prefix(self):
        img = self.settings.image
        eo_str = database.even_odd_str(self.even, self.odd)
        w_str = utils.alphanum(img.weight)
        s = f'{self.obs_id}{eo_str}-SB{self.get_sb()}-UV{img.umin}_{img.umax}_{w_str}'
        return os.path.join(self.get_dir(), s)

    def register_files(self, files, lst_idx=None, img_name='image'):
        meta = self.img_rev.get_meta(self.obs_id, lst_idx=lst_idx)
        meta.add_fits(files, even=self.even, odd=self.odd, img_name=img_name)
        meta.save()

    def done_callback(self):
        for file in glob.glob(f'{self.get_fits_prefix()}*-MFS-*.fits'):
            os.remove(file)

        img = self.settings.image

        if img.time_start_index != img.time_end_index:
            total_time = self.obs_meta.int_time * (img.time_end_index - img.time_start_index)
        elif img.lst_bins:
            total_time = img.lst_bins[2] * 3600
        else:
            total_time = self.obs_meta.total_time

        if img.clean_niter > 0 and img.clean_residual:
            files = glob.glob(f'{self.get_fits_prefix()}*psf.fits')
            files.extend(glob.glob(f'{self.get_fits_prefix()}*residual.fits'))
            img_name = 'residual'
        else:
            files = glob.glob(f'{self.get_fits_prefix()}*.fits')
            img_name = 'image'

        for file in files:
            pf.setval(file, 'PEINTTIM', value=int(self.obs_meta.int_time))
            pf.setval(file, 'PETOTTIM', value=int(total_time))
            pf.setval(file, 'PECHWIDT', value=int(self.obs_meta.chan_width))

        if not img.lst_bins:
            self.register_files(files, img_name=img_name)
        else:
            for i, data_lst_idx in enumerate(self.img_rev.get_lst_bins(self.obs_id, return_time_index=True)[2]):
                files = glob.glob(f'{self.get_fits_prefix()}*-t{i:04}-*.fits')
                self.register_files(files, lst_idx=data_lst_idx, img_name=img_name)

        try:
            os.remove(self.temp_protect_file)
        except (FileNotFoundError, OSError):
            # ignore
            pass

        try:
            os.rmdir(self.temp_dir)
        except (FileNotFoundError, OSError):
            # ignore
            pass

    def get_parameters(self):
        args = []
        img = self.settings.image
        # Default arguments

        channels_out = img.channels_out
        if channels_out == 'all':
            if self.obs_meta.n_channels:
                channels_out = self.obs_meta.n_channels
            else:
                channels_out = 1
        elif str(channels_out).startswith('every'):
            assert self.obs_meta.n_channels
            channels_out = self.obs_meta.n_channels // int(channels_out[5:])
        channels_out = int(channels_out)

        args.append("-oversampling 4095 -kernel-size 15 -nwlayers 32 -grid-mode kb -taper-edge 100")
        args.append("-padding 2 -visibility-weighting-mode unit -reorder -make-psf -no-dirty")

        # If MS directory is not writable, we need to define a temp directory
        if not all(os.access(ms_file, os.W_OK) for ms_file in self.inp_ms_files):
            self.temp_dir = os.path.join(self.get_dir(), 'tmp' + database.even_odd_str(self.even, self.odd))
        else:
            self.temp_dir = os.path.join(self.inp_ms_files[0], 'tmp' + database.even_odd_str(self.even, self.odd))

        if not os.path.isdir(self.temp_dir):
            os.makedirs(self.temp_dir)

        # Make sure we do not remove this directory by accident
        _, self.temp_protect_file = tempfile.mkstemp(dir=self.temp_dir)

        args.append(f'-temp-dir {self.temp_dir}')

        if self.even:
            args.append('-even-timesteps')
        elif self.odd:
            args.append('-odd-timesteps')

        args.append(f'-scale {img.scale} -size {img.size} -channels-out {channels_out}')
        args.append(f'-weight {img.weight} -minuv-l {img.umin} -maxuv-l {img.umax}')
        args.append(f'-pol {img.stokes} -data-column {img.data_col}')

        if not img.lst_bins:
            args.append(f'-interval {img.time_start_index} {img.time_end_index}')
        else:
            lst_bins, (start_idx, end_idx, _), _ = self.img_rev.get_lst_bins(self.obs_id, return_time_index=True)
            args.append(f'-interval {start_idx} {end_idx} -intervals-out {len(lst_bins)}')

        for key, value in img.wsclean_args.items():
            args.append(f'-{key} {value}')

        if img.clean_niter > 0:
            args.append(f'-niter {img.clean_niter} -auto-threshold {img.clean_auto_threshold}')
            args.append(f'-local-rms -mgain {img.clean_mgain} -stop-negative -no-update-model-required')
            args.append(f'-join-channels -fit-spectral-pol {img.clean_spectra_fit_nterms}')

            if channels_out > 1:
                args.append('-join-channels')

        args.append(f'-name {self.get_fits_prefix()} {" ".join(self.inp_ms_files)}')

        return args


class ImagingTask(AbstractTask):

    name = 'image'
    desc = 'Create images'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'Imaging', settings_obj)
        self.img_rev = database.ImageRevision(self.settings)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        if not self.settings.validate('image'):
            return []

        if not self.img_rev.exist():
            self.img_rev.create()
        else:
            if not self.settings.image == self.img_rev.get_settings().image:
                print('Error: Image revision already exist and settings are not compatible.')
                return []

        all_obs_id_out = []

        for obs_id in obs_ids:
            if not self.db.has_obs_id(obs_id):
                print(f'Error: Obs ID {obs_id} does not exist.')
                return []

            ms_files = self.db.get_obs_id_meta(obs_id).ms_files

            if not ms_files:
                print(f'Error: Obs ID {obs_id} has no MS files registered.')
                return []

            if not self.settings.image.lst_bins:
                self.img_rev.new_obs_id(obs_id)
            else:
                for i in self.img_rev.get_lst_bins(obs_id).keys():
                    self.img_rev.new_obs_id(obs_id, lst_idx=i)

            for ms_files_channel in ms_files:
                target_host = get_target_host(ms_files_channel[0], self.settings.worker)
                if self.settings.image.split_even_odd:
                    self.add_sub_task(ImagingSubTask(self.settings, obs_id, ms_files_channel, even=True),
                                      run_on_host=target_host)
                    self.add_sub_task(ImagingSubTask(self.settings, obs_id, ms_files_channel, odd=True),
                                      run_on_host=target_host)
                else:
                    self.add_sub_task(ImagingSubTask(self.settings, obs_id, ms_files_channel), run_on_host=target_host)

            all_obs_id_out.append(obs_id)

        self.execute()

        return all_obs_id_out


class GenVisCubeSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id, stokes, even=False, odd=False, lst_idx=None):
        AbstractSubTask.__init__(self, settings_obj, 'pstool gen_vis_cube')
        self.obs_id = obs_id
        self.stokes = stokes
        self.even = even
        self.odd = odd
        self.lst_idx = lst_idx
        self.vis_rev = database.VisRevision(self.settings)

    def make_img_files(self):
        img_meta = database.ImageRevision(self.settings).get_meta(self.obs_id, self.lst_idx)
        type_name = database.get_type_name(self.stokes, self.even, self.odd)
        type_psf_name = database.get_type_name('psf', self.even, self.odd)
        img_file = os.path.join(self.vis_rev.get_h5_path(self.obs_id, self.lst_idx), f'img_{type_name}_list.txt')
        psf_file = os.path.join(self.vis_rev.get_h5_path(self.obs_id, self.lst_idx), f'img_{type_psf_name}_list.txt')
        with open(img_file, 'w') as f:
            f.writelines(k + '\n' for k in img_meta[type_name])
        with open(psf_file, 'w') as f:
            f.writelines(k + '\n' for k in img_meta[type_psf_name])

        return img_file, psf_file

    def get_out_file(self):
        return self.vis_rev.get_h5_file(self.obs_id, self.stokes.upper(), self.even, self.odd, lst_idx=self.lst_idx)

    def get_log_file(self):
        return os.path.join(self.vis_rev.get_h5_path(self.obs_id, self.lst_idx), 'logs',
                            os.path.basename(self.get_out_file().replace('.h5', '.log')))

    def done_callback(self):
        meta = self.vis_rev.get_meta(self.obs_id, self.lst_idx)
        meta.add_h5(self.get_out_file(), self.stokes, self.even, self.odd)
        meta.save()

    def get_parameters(self):
        vis = self.settings.vis_cube
        img_file, psf_file = self.make_img_files()
        out_file = self.get_out_file()
        obs_meta = database.Database(self.settings).get_obs_id_meta(self.obs_id)

        args = [img_file, psf_file, f'-o {out_file} -m b -w 0', f'-i {obs_meta.int_time} -t {obs_meta.total_time}']
        args.append(f'--theta_fov={vis.fov} --umin={vis.umin} --umax={vis.umax} --win_function="{vis.win_fct}"')

        return args


class EvenOddToSumDiffSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id, stokes, lst_idx=None):
        AbstractSubTask.__init__(self, settings_obj, 'pstool even_odd_to_sum_diff')
        self.obs_id = obs_id
        self.stokes = stokes
        self.lst_idx = lst_idx
        self.vis_rev = database.VisRevision(self.settings)

    def get_parameters(self):
        h5_even = self.vis_rev.get_h5_file(self.obs_id, self.stokes.upper(), lst_idx=self.lst_idx, even=True)
        h5_odd = self.vis_rev.get_h5_file(self.obs_id, self.stokes.upper(), lst_idx=self.lst_idx, odd=True)
        h5_sum = self.vis_rev.get_h5_file(self.obs_id, self.stokes.upper(), lst_idx=self.lst_idx)
        h5_diff = self.vis_rev.get_h5_file(self.obs_id, 'dt_' + self.stokes.upper(), lst_idx=self.lst_idx)
        return [h5_even, h5_odd, h5_sum, h5_diff]


class GenVisCubeTask(AbstractTask):

    name = 'gen_vis_cube'
    desc = 'Generate gridded visibility cubes from images'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'GenVisCube', settings_obj)
        self.img_rev = database.ImageRevision(self.settings)
        self.vis_rev = database.VisRevision(self.settings)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        if not self.settings.validate('vis_cube'):
            return []

        if not self.img_rev.exist():
            print(f'Error: Image revision {self.settings.image.name} does not exist.')
            return []

        if not self.vis_rev.exist():
            self.vis_rev.create()

        has_even = set()
        has_odd = set()
        all_obs_id_out = []

        for obs_id in obs_ids:
            if not self.db.has_obs_id(obs_id):
                print(f'Error: Obs ID {obs_id} does not exist.')
                return []

            if not self.img_rev.has_obs_id(obs_id):
                print(f'Error: Images for obs ID {obs_id} not available.')
                return []

            all_lst_idx = self.img_rev.get_lst_bins(obs_id).keys() if self.settings.image.lst_bins else [None]

            for lst_idx in all_lst_idx:
                self.vis_rev.new_obs_id(obs_id, lst_idx=lst_idx)
                meta = self.img_rev.get_meta(obs_id, lst_idx=lst_idx)

                for stokes in meta.get_all_stokes():
                    if meta.has_stokes(stokes, odd=True):
                        self.add_sub_task(GenVisCubeSubTask(self.settings, obs_id, stokes, lst_idx=lst_idx, odd=True))
                        has_odd.add(obs_id)
                    if meta.has_stokes(stokes, even=True):
                        self.add_sub_task(GenVisCubeSubTask(self.settings, obs_id, stokes, lst_idx=lst_idx, even=True))
                        has_even.add(obs_id)
                    if meta.has_stokes(stokes):
                        self.add_sub_task(GenVisCubeSubTask(self.settings, obs_id, stokes, lst_idx=lst_idx))

            all_obs_id_out.append(obs_id)

        self.execute()

        if has_even.intersection(has_odd):
            self.init_for_new_task('EvenOddToSumDiff')

            for obs_id in has_even.intersection(has_odd):
                all_lst_idx = self.img_rev.get_lst_bins(obs_id).keys() if self.settings.image.lst_bins else [None]

                for lst_idx in all_lst_idx:
                    meta = self.vis_rev.get_meta(obs_id, lst_idx=lst_idx)

                    for stokes in meta.get_all_stokes():
                        if meta.has_stokes(stokes, odd=True) and meta.has_stokes(stokes, even=True):
                            self.add_sub_task(EvenOddToSumDiffSubTask(self.settings, obs_id, stokes, lst_idx))

            self.execute()

        return all_obs_id_out


class MergeMSSubTask(AbstractSubTask):

    def __init__(self, settings_obj, ms_files, obs_id_out):
        AbstractSubTask.__init__(self, settings_obj, 'DPPP')
        self.db = database.Database(self.settings)
        self.ms_files = ms_files
        self.obs_id_out = obs_id_out

    def get_dir(self):
        return os.path.join(self.settings.get_path('data_dir'), 'merged_ms', self.obs_id_out)

    def get_out_file(self):
        return os.path.join(self.get_dir(), f'{self.obs_id_out}.MS')

    def get_log_file(self):
        return os.path.join(self.get_out_file().replace('.MS', '.log'))

    def make_link(self):
        inp_ms_dir = os.path.join(self.get_dir(), 'input_ms')
        if not os.path.exists(inp_ms_dir):
            os.makedirs(inp_ms_dir)
        else:
            for file in glob.glob(f'{inp_ms_dir}/*.MS'):
                os.remove(file)
        for ms_file in self.ms_files:
            os.symlink(ms_file[0], os.path.join(inp_ms_dir, os.path.basename(ms_file[0])))

        return inp_ms_dir

    def done_callback(self):
        if not self.db.has_obs_id(self.obs_id_out):
            meta = self.db.new_obs_id(self.obs_id_out)
        else:
            meta = self.db.get_obs_id_meta(self.obs_id_out)
        meta.set_ms_files([[self.get_out_file()]])

    def get_parameters(self):
        if not os.path.exists(self.get_dir()):
            os.makedirs(self.get_dir())
        inp_ms_dir = self.make_link()
        merge_ms = self.settings.merge_ms

        steps = ['filter']
        args = [f'msin={inp_ms_dir}/*.MS', f'msin.datacolumn={merge_ms.data_col}']
        args.append(f'msout={self.get_out_file()} msout.overwrite=true')
        args.append(f'filter.type=filter filter.blrange=[{merge_ms.blmin},{merge_ms.blmax}]')

        if merge_ms.time_start_index:
            args.append(f'msin.starttimeslot={merge_ms.time_start_index}')

        if merge_ms.time_end_index:
            args.append(f'msin.ntimes={merge_ms.time_end_index - merge_ms.time_start_index}')

        if merge_ms.apply_aoflagger:
            steps.append('flagger')
            args.append('flagger.type=aoflagger flagger.memoryperc=30')

        if merge_ms.flag_baselines:
            steps.append('preflag')
            bl_str = merge_ms.flag_baselines.strip().replace(' ', '')
            args.append(f'preflag.type=preflagger preflag.mode=set preflag.baseline="{bl_str}"')

        if merge_ms.avg_timestep > 1:
            steps.append('avg')
            args.append(f'avg.type=average avg.timestep={merge_ms.avg_timestep}')

        args.append(f'steps=[{",".join(steps)}]')

        return args


class MergeMSTask(AbstractTask):

    name = 'merge_ms'
    desc = 'Merge all MS sub-bands into one MS, create a new obs_id'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'MergeMS', settings_obj, max_concurrent=1)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        if not self.settings.validate('merge_ms'):
            return []

        all_obs_id_out = []

        for obs_id in obs_ids:
            if not self.db.has_obs_id(obs_id):
                print(f'Error: Obs ID {obs_id} does not exist.')
                return []

            ms_files = self.db.get_obs_id_meta(obs_id).ms_files

            if not ms_files:
                print(f'Error: Obs ID {obs_id} has no MS files registered.')
                return []

            if not all(len(k) == 1 for k in ms_files):
                print(f'Error: Obs ID {obs_id} has invalid ms files.')
                return []

            obs_id_out = f'{obs_id}_{self.settings.merge_ms.obs_id_out_suffix}'.replace(' ', '')
            self.add_sub_task(MergeMSSubTask(self.settings, ms_files, obs_id_out))
            all_obs_id_out.append(obs_id_out)

        self.execute()

        return all_obs_id_out


class MakePSSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id, lst_idx=None):
        AbstractSubTask.__init__(self, settings_obj, 'pstool make_ps')
        self.obs_id = obs_id
        self.lst_idx = lst_idx
        self.vis_rev = database.VisRevision(self.settings)

    def get_log_file(self):
        return os.path.join(self.vis_rev.get_h5_path(self.obs_id, self.lst_idx), 'logs', 'make_ps.log')

    def get_parameters(self):
        h5_i = self.vis_rev.get_h5_file(self.obs_id, 'I', lst_idx=self.lst_idx)
        h5_v = self.vis_rev.get_h5_file(self.obs_id, 'V', lst_idx=self.lst_idx)
        h5_dt = self.vis_rev.get_h5_file(self.obs_id, 'dt_V', lst_idx=self.lst_idx)
        psc = self.settings.power_spectra
        out_dir = os.path.join(self.vis_rev.get_h5_path(self.obs_id, self.lst_idx))
        plot_out_dir = os.path.join(self.vis_rev.get_result_path(self.obs_id, self.lst_idx))

        args = [h5_i, h5_v, h5_dt, f'-f {psc.get_path("flagger")} -e {psc.get_path("eor_bin_list")}']
        args.append(f'-c {psc.get_path("ps_config")} -o {out_dir} -po {plot_out_dir}')

        return args


class MakePSTask(AbstractTask):

    name = 'make_ps'
    desc = 'Produce power-spectra'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'MakePS', settings_obj)
        self.vis_rev = database.VisRevision(self.settings)
        self.img_rev = database.ImageRevision(self.settings)

    def run(self, obs_ids):
        if not self.settings.validate('power_spectra'):
            return []

        if not self.vis_rev.exist():
            print(f'Error: visibility revision does not exist.')
            return []

        for obs_id in obs_ids:
            if not self.vis_rev.has_obs_id(obs_id):
                print(f'Error: visibility revision for obs ID {obs_id} not available.')
                return []

            all_lst_idx = self.img_rev.get_lst_bins(obs_id).keys() if self.settings.image.lst_bins else [None]

            for lst_idx in all_lst_idx:
                self.add_sub_task(MakePSSubTask(self.settings, obs_id, lst_idx))

        self.execute()

        return obs_ids


class RunGPRSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id, lst_idx=None):
        AbstractSubTask.__init__(self, settings_obj, 'pstool run_gpr')
        self.obs_id = obs_id
        self.lst_idx = lst_idx
        self.vis_rev = database.VisRevision(self.settings)

    def get_log_file(self):
        return os.path.join(self.vis_rev.get_path(), self.obs_id, 'logs', 'run_gpr.log')

    def get_parameters(self):
        h5_i = self.vis_rev.get_h5_file(self.obs_id, 'I', lst_idx=self.lst_idx)
        h5_v = self.vis_rev.get_h5_file(self.obs_id, 'V', lst_idx=self.lst_idx)
        psc = self.settings.power_spectra
        gpr = self.settings.gpr
        out_dir = os.path.join(self.vis_rev.get_h5_path(self.obs_id, self.lst_idx), gpr.name)
        plot_out_dir = os.path.join(self.vis_rev.get_result_path(self.obs_id, self.lst_idx), gpr.name)

        args = [h5_i, h5_v, gpr.get_path("config_i"), gpr.get_path("config_v")]
        args.append(f'-f {psc.get_path("flagger")} -e {psc.get_path("eor_bin_list")}')
        args.append(f'-c {psc.get_path("ps_config")} -o {out_dir} -po {plot_out_dir}')

        if not gpr.plot_results:
            args.append('--no_plot')

        return args


class RunGPRTask(AbstractTask):

    name = 'run_gpr'
    desc = 'Run GPR and produce power-spectra'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'GPR', settings_obj)
        self.vis_rev = database.VisRevision(self.settings)
        self.img_rev = database.ImageRevision(self.settings)

    def run(self, obs_ids):
        if not (self.settings.validate('power_spectra') and self.settings.validate('gpr')):
            return []

        if not self.vis_rev.exist():
            print(f'Error: visibility revision does not exist.')
            return []

        for obs_id in obs_ids:
            if not self.vis_rev.has_obs_id(obs_id):
                print(f'Error: visibility revision for obs ID {obs_id} not available')
                return []

            all_lst_idx = self.img_rev.get_lst_bins(obs_id).keys() if self.settings.image.lst_bins else [None]

            for lst_idx in all_lst_idx:
                self.add_sub_task(RunGPRSubTask(self.settings, obs_id, lst_idx))

        self.execute()

        return obs_ids


class RunMLGPRSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id, lst_idx=None):
        AbstractSubTask.__init__(self, settings_obj, 'pstool run_ml_gpr')
        self.obs_id = obs_id
        self.lst_idx = lst_idx
        self.vis_rev = database.VisRevision(self.settings)

    def get_log_file(self):
        return os.path.join(self.vis_rev.get_path(), self.obs_id, 'logs', 'run_ml_gpr.log')

    def get_parameters(self):
        h5_i = self.vis_rev.get_h5_file(self.obs_id, 'I', lst_idx=self.lst_idx)
        h5_v = self.vis_rev.get_h5_file(self.obs_id, 'V', lst_idx=self.lst_idx)
        psc = self.settings.power_spectra
        gpr = self.settings.ml_gpr
        out_dir = os.path.join(self.vis_rev.get_h5_path(self.obs_id, self.lst_idx), gpr.name)
        plot_out_dir = os.path.join(self.vis_rev.get_result_path(self.obs_id, self.lst_idx), gpr.name)

        args = [h5_i, h5_v, gpr.get_path("config")]
        args.append(f'-f {psc.get_path("flagger")} -e {psc.get_path("eor_bin_list")}')
        args.append(f'-c {psc.get_path("ps_config")} -o {out_dir} -po {plot_out_dir}')

        if not gpr.plot_results:
            args.append('--no_plot')

        return args


class RunMLGPRTask(AbstractTask):

    name = 'run_ml_gpr'
    desc = 'Run ML-GPR and produce power-spectra'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'ML-GPR', settings_obj)
        self.vis_rev = database.VisRevision(self.settings)
        self.img_rev = database.ImageRevision(self.settings)

    def run(self, obs_ids):
        if not (self.settings.validate('power_spectra') and self.settings.validate('gpr')):
            return []

        if not self.vis_rev.exist():
            print(f'Error: visibility revision does not exist.')
            return []

        for obs_id in obs_ids:
            if not self.vis_rev.has_obs_id(obs_id):
                print(f'Error: visibility revision for obs ID {obs_id} not available')
                return []

            all_lst_idx = self.img_rev.get_lst_bins(obs_id).keys() if self.settings.image.lst_bins else [None]

            for lst_idx in all_lst_idx:
                self.add_sub_task(RunMLGPRSubTask(self.settings, obs_id, lst_idx))

        self.execute()

        return obs_ids


class CombineTask(AbstractTask):

    name = 'combine'
    desc = 'Combine several obs_id together'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'Combine', settings_obj)
        self.vis_rev = database.VisRevision(self.settings)
        self.db = database.Database(self.settings)

    def get_path(self):
        return os.path.join(self.vis_rev.get_path(), 'combined_obs_ids')

    def get_combine_file(self):
        return os.path.join(self.get_path(), f'C{self.settings.combine.obs_id_out_prefix}.list')

    def make_combine_file(self, obs_ids):
        if not os.path.exists(self.get_path()):
            os.makedirs(self.get_path())

        with open(self.get_combine_file(), 'w') as f:
            for obs_id in obs_ids:
                h5_i = self.vis_rev.get_h5_file(obs_id, 'I')
                h5_v = self.vis_rev.get_h5_file(obs_id, 'V')
                if self.settings.combine.use_v_as_dt:
                    h5_dt = h5_v
                else:
                    h5_dt = self.vis_rev.get_h5_file(obs_id, 'dt_V')

                f.write(f"{obs_id} {h5_i} {h5_v} {h5_dt}\n")

    def run(self, obs_ids):
        if not self.settings.validate('combine'):
            return []

        if not self.vis_rev.exist():
            print(f'Error: visibility revision does not exist.')
            return []

        obs_ids_meta = [self.db.get_obs_id_meta(obs_id) for obs_id in obs_ids]
        is_sph = obs_ids_meta[0].is_sph

        if not all(obs_ids_meta):
            print(f'Error: some visibility revision not available.')
            return []

        if not utils.all_same([k.is_sph for k in obs_ids_meta]):
            print(f'Error: all input obs_ids should be of the same type.')
            return []

        if any([k.is_combined for k in obs_ids_meta]):
            print(f'Error: input obs_ids should not be of the type "combined".')
            return []

        start_times = [k.start_time for k in obs_ids_meta]
        start_times, obs_ids_meta = zip(*sorted(zip(start_times, obs_ids_meta), key=lambda x: x[0]))

        obs_ids = [k.obs_id for k in obs_ids_meta]
        start_times = [k.start_time for k in obs_ids_meta]
        end_times = [k.end_time for k in obs_ids_meta]
        int_time = obs_ids_meta[0].int_time
        tot_times = [k.total_time for k in obs_ids_meta]
        n_channels = obs_ids_meta[0].n_channels
        chan_width = obs_ids_meta[0].chan_width
        cum_times = np.cumsum(tot_times)

        obs_id_out_prefix = self.settings.combine.obs_id_out_prefix

        for i in range(len(obs_ids)):
            self.db.new_obs_id(f'C{obs_id_out_prefix}{i + 1:03}', int_time=int_time, start_time=start_times[0],
                               end_time=end_times[i], n_channels=n_channels, total_time=int(cum_times[i]),
                               is_combined=1, is_sph=is_sph, chan_width=chan_width)
        self.db.new_obs_id(f'M{obs_id_out_prefix}{len(obs_ids):03}', int_time=int_time, start_time=start_times[0],
                           end_time=end_times[-1], n_channels=n_channels, total_time=int(np.mean(tot_times)),
                           is_combined=1, is_sph=is_sph, chan_width=chan_width)

        self.make_combine_file(obs_ids)

        c_id = f'C{obs_id_out_prefix}%NUM%'
        m_id = f'M{obs_id_out_prefix}%NUM%'
        output_template = os.path.join(self.vis_rev.get_h5_file(c_id, '%STOKES%'))
        output_multi_template = os.path.join(self.vis_rev.get_h5_file(m_id, '%STOKES%'))
        umin = self.settings.vis_cube.umin
        umax = self.settings.vis_cube.umax
        c = self.settings.combine

        out_log = os.path.join(self.get_path(), f'C{obs_id_out_prefix}.log')

        if is_sph:
            cmd = (f'pstool combine_sph {self.get_combine_file()} -o {output_template} '
                   f'--save_intermediate --pre_flag {c.get_path("pre_flag")}')
        else:
            cmd = (f'pstool combine {self.get_combine_file()} --umin {umin} --umax {umax} -w {c.weights_mode} '
                   f'{"-ih" * c.inhomogeneous} {"-s" * c.scale_with_noise} -o {output_template} '
                   f'-om {output_multi_template} --save_intermediate --pre_flag {c.get_path("pre_flag")}')

        self.execute_single_local(cmd, out_log)

        return [c_id]


class RunFlaggerSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id):
        AbstractSubTask.__init__(self, settings_obj, 'pstool run_flagger')
        self.vis_rev = database.VisRevision(self.settings)
        self.obs_id = obs_id

    def get_parameters(self):
        h5_i = self.vis_rev.get_h5_file(self.obs_id, 'I')
        h5_v = self.vis_rev.get_h5_file(self.obs_id, 'V')
        return [h5_i, h5_v, self.settings.vis_to_sph.get_path("pre_flag"),
                f'-o {self.vis_rev.get_h5_path(self.obs_id)}']


class VisToSphSubTask(AbstractSubTask):

    def __init__(self, settings_obj, obs_id_out, stokes, h5_input, h5_out, h5_flag):
        AbstractSubTask.__init__(self, settings_obj, 'pstool vis_to_sph')
        self.vis_rev = database.VisRevision(self.settings)
        self.obs_id_out = obs_id_out
        self.h5_input = h5_input
        self.h5_flag = h5_flag
        self.stokes = stokes
        self.h5_out = h5_out

    def done_callback(self):
        meta = self.vis_rev.get_meta(self.obs_id_out)
        meta.add_h5(self.h5_out, self.stokes)
        meta.save()

    def get_parameters(self):
        return [self.h5_input, self.h5_out, f'-f {self.h5_flag}']


class VisToSphTask(AbstractTask):

    name = 'vis_to_sph'
    desc = 'Convert gridded visibility cube to sph cube'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'VisToSph S1', settings_obj)
        self.vis_rev = database.VisRevision(self.settings)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        if not self.settings.validate('vis_to_sph'):
            return []

        if not self.vis_rev.exist():
            print(f'Error: visibility revision does not exist.')
            return []

        for obs_id in obs_ids:
            if not self.vis_rev.has_obs_id(obs_id):
                print(f'Error: visibility revision for obs ID {obs_id} not available')
                return []

            self.add_sub_task(RunFlaggerSubTask(self.settings, obs_id))

        self.execute()
        self.init_for_new_task('VisToSph S2')
        new_obs_ids = []

        for obs_id in obs_ids:
            obs_id_meta = database.Database(self.settings).get_obs_id_meta(obs_id)
            obs_id_out = f'{obs_id}_{self.settings.vis_to_sph.obs_id_out_suffix}'.replace(' ', '')

            self.db.new_obs_id_from_other(obs_id_out, obs_id_meta, is_sph=1)
            self.vis_rev.new_obs_id(obs_id_out)

            h5_flag = self.vis_rev.get_h5_file(obs_id, 'I').replace('.h5', '_flag.h5')

            for stokes in ['I', 'V', 'dt_I', 'dt_V']:
                h5_input = self.vis_rev.get_h5_file(obs_id, stokes)
                h5_output = self.vis_rev.get_h5_file(obs_id_out, stokes)
                self.add_sub_task(VisToSphSubTask(self.settings, obs_id_out, stokes, h5_input, h5_output, h5_flag))

            new_obs_ids.append(obs_id_out)

        self.execute()

        return new_obs_ids


class ApplyFlagSubTask(AbstractSubTask):

    def __init__(self, settings_obj, ms_file, h5_file):
        AbstractSubTask.__init__(self, settings_obj, 'flagtool restore')
        self.ms_file = ms_file
        self.h5_file = h5_file

    def get_parameters(self):
        return [self.ms_file, self.h5_file]


class ApplyFlagTask(AbstractTask):

    name = 'apply_flag'
    desc = 'Apply flag h5 file'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'ApplyFlag', settings_obj)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        for obs_id in obs_ids:
            if not self.db.has_obs_id(obs_id):
                print(f'Error: Obs ID {obs_id} does not exist.')
                return []

            ms_files = self.db.get_obs_id_meta(obs_id).ms_files

            if not ms_files:
                print(f'Error: Obs ID {obs_id} has no MS files registered.')
                return []

            for ms_file in np.array(ms_files).flatten():
                h5_file = os.path.join(ms_file, self.settings.apply_flag.filename)

                if not os.path.exists(h5_file):
                    print(f'Error: Flag file {h5_file} does not exist.')
                    return []

                self.add_sub_task(ApplyFlagSubTask(self.settings, ms_file, h5_file))

        self.execute()

        return obs_ids


class RestoreFlagTask(AbstractTask):

    name = 'restore_flag'
    desc = 'Restore flag h5 file'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'ApplyFlag', settings_obj)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        for obs_id in obs_ids:
            if not self.db.has_obs_id(obs_id):
                print(f'Error: Obs ID {obs_id} does not exist.')
                return []

            ms_files = self.db.get_obs_id_meta(obs_id).ms_files

            if not ms_files:
                print(f'Error: Obs ID {obs_id} has no MS files registered.')
                return []

            for ms_file in np.array(ms_files).flatten():
                h5_file = os.path.join(ms_file, H5_FLAG_BACKUP)

                if not os.path.exists(h5_file):
                    print(f'No backup to restore from for {ms_file}.')
                    continue

                self.add_sub_task(ApplyFlagSubTask(self.settings, ms_file, h5_file))

        self.execute()

        return obs_ids


class DelayFlaggerSubTask(AbstractSubTask):

    def __init__(self, settings_obj, ms_file):
        AbstractSubTask.__init__(self, settings_obj, 'flagtool delay_flagger')
        self.ms_file = ms_file

    def get_log_file(self):
        return os.path.join(self.ms_file.replace('.MS', '_delay_flagger.log'))

    def get_path(self):
        d = os.path.join(os.path.dirname(self.ms_file), 'flagger')
        futils.mkdir(d)
        return d

    def get_parameters(self):
        s = self.settings.delay_flagger
        return [self.ms_file, f'--data_col={self.settings.image.data_col}', f'--umin={s.umin}', f'--umax={s.umax}',
                f'--n_time_avg={s.n_time_avg}', f'--n_times={s.n_times}', f'--n_sigma_i={s.n_sigma_i}',
                f'--n_sigma_v={s.n_sigma_v}', '--backup', f'--backup_file={H5_FLAG_BACKUP}',
                f'--plot_dir={self.get_path()}']


class DelayFlagger(AbstractTask):

    name = 'delay_flagger'
    desc = 'Apply delay flagger on MS'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'DelayFlagger', settings_obj)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        if not self.settings.validate('delay_flagger'):
            return []

        for obs_id in obs_ids:
            if not self.db.has_obs_id(obs_id):
                print(f'Error: Obs ID {obs_id} does not exist.')
                return []

            ms_files = self.db.get_obs_id_meta(obs_id).ms_files

            if not ms_files:
                print(f'Error: Obs ID {obs_id} has no MS files registered.')
                return []

            for ms_file in np.array(ms_files).flatten():
                self.add_sub_task(DelayFlaggerSubTask(self.settings, ms_file))

        self.execute()

        return obs_ids


class SSINSSubTask(AbstractSubTask):

    def __init__(self, settings_obj, ms_file):
        AbstractSubTask.__init__(self, settings_obj, 'flagtool ssins')
        self.ms_file = ms_file

    def get_log_file(self):
        return os.path.join(self.ms_file.replace('.MS', '_ssins.log'))

    def get_path(self):
        d = os.path.join(os.path.dirname(self.ms_file), 'flagger')
        futils.mkdir(d)
        return d

    def get_config(self):
        f = os.path.join(self.ms_file, 'ssins_config.toml')
        self.settings.ssins.save(f)
        return f

    def get_parameters(self):
        return [self.ms_file, f'--data_col={self.settings.image.data_col}', f'--config={self.get_config()}',
                f'--plot_dir={self.get_path()}', '--backup', f'--backup_file={H5_FLAG_BACKUP}']


class SSINSTask(AbstractTask):

    name = 'ssins'
    desc = 'Apply SSINS flagging on MS'

    def __init__(self, settings_obj):
        AbstractTask.__init__(self, 'SSINS', settings_obj, max_concurrent=1)
        self.db = database.Database(self.settings)

    def run(self, obs_ids):
        if not self.settings.validate('ssins'):
            return []

        if not self.settings.ssins.apply_ssins:
            return obs_ids

        for obs_id in obs_ids:
            if not self.db.has_obs_id(obs_id):
                print(f'Error: Obs ID {obs_id} does not exist.')
                return []

            ms_files = self.db.get_obs_id_meta(obs_id).ms_files

            if not ms_files:
                print(f'Error: Obs ID {obs_id} has no MS files registered.')
                return []

            for ms_file in np.array(ms_files).flatten():
                self.add_sub_task(SSINSSubTask(self.settings, ms_file))

        self.execute()

        return obs_ids
