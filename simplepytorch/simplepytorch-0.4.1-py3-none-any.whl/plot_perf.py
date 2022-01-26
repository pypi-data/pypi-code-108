#!/usr/bin/env -S ipython --no-banner -i --
"""
Quick performance plots used as a script to visualize results.

This is wonderfully useful for analyzing csv files of models!

  - Expects a csv header with "epoch" as a column (customizable via --index-col)
  - Requires a directory structure:
      ./results/
                run_id/perf.csv  # for mode 1 and 4
                      /log/perf*.csv  # for other modes
      where: 
          - ./results/ can be changed via  --data-dir
          - "run_id" is any directory name
          - "perf.csv" and "perf*.csv" can be changed  via --data-fp-regex
          - the "log" directory is hardcoded...

Usage:
    $ python -m simplepytorch.plot_perf  -h

    # or if simplepytorch is installed:
    $ simplepytorch_plot -h

    # or alias it in a bash shell:
    $ alias sdp='python -m simplepytorch.perf_plot -- '
"""
import argparse as ap
import datetime as dt
import IPython
import sys
import re
import glob
import os
from os.path import join, exists, basename, dirname
#  from os import exists
import pandas as pd
import numpy as np
import seaborn as sns
from textwrap import dedent
from matplotlib import pyplot as plt
#  import mpld3
#  import mpld3.plugins


def get_run_ids(ns):
    dirs = glob.glob(join(ns.data_dir, '*'))
    for dir in dirs:
        run_id = basename(dir)
        if not re.search(ns.runid_regex, basename(dir)):
            continue
        yield run_id


def load_df_from_fp(fp, ns):
    print('found data', fp)
    try:
        if fp.endswith('.csv'):
            df = pd.read_csv(fp).set_index(ns.index_col)
        elif fp.endswith('.h5'):
            df = pd.read_hdf(fp, ns.hdf_table)
        else:
            print('bug: file does not exist:', fp)
    except:
        print(f"   WARNING: failed to load {fp}")
        df = pd.DataFrame()
    return df


def _mode1_get_frames(ns):
    for run_id in get_run_ids(ns):
        #  if not exists(join(dir, 'lock.finished')):
            #  continue
        dirp = f'{ns.data_dir}/{run_id}'
        gen = (
            ((run_id, fname), load_df_from_fp(join(dirp, fname), ns))
            for fname in os.listdir(dirp)
            if re.match(ns.data_fp_regex, fname))
        yield from (x for x in gen if not x[-1].empty)


def _get_all_data(ns):
    cdfs_data = {}
    timestamp = dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S')  # date plot was created.  nothing to do with timestamp column.
    for run_id in get_run_ids(ns):
        dirp = f'{ns.data_dir}/{run_id}/log'
        if not os.path.exists(dirp):
            print('skip', run_id, 'contains no log data')
            continue

        cdfs = pd.concat({
            (run_id, fname): load_df_from_fp(join(dirp, fname), ns)
            for fname in os.listdir(dirp)
            if re.search(f'{ns.data_fp_regex}', fname)},
            sort=False, names=['run_id', 'filename']
        )
        cdfs_data[run_id] = cdfs
    cdfs = pd.concat(cdfs_data.values())
    return cdfs


def make_plots(ns, cdfs):
    cols = [col for col in cdfs.columns if re.search(ns.col_regex, col)]
    if ns.avg_cols:
        colname = 'Mean(%s)' % ns.col_regex
        cdfs[colname] = cdfs[cols].mean(axis=1)
        cols = [colname]

    plot_cols = [prettify(col) for col in cols]
    cdfs = cdfs.copy()
    cdfs.columns = [prettify(x) for x in cdfs.columns]
    cdfs.index.names = [prettify(x) for x in cdfs.index.names]
    for col in plot_cols:
        fig, ax = plt.subplots(1,1)
        df = cdfs[col].unstack(level=0)
        if ns.rolling_mean:
            df = df.rolling(ns.rolling_mean).mean()
        if (df.dtypes.values == np.dtype('O')).all():
            print('WARNING: skip col with no numeric data:', col)
            ax.set_title(f'{col}, SKIPPED because no numeric data')
            continue
        _plot_lines = df.plot(ax=ax, title=col, legend=ns.legend, alpha=.9)
        #  _legend = mpld3.plugins.InteractiveLegendPlugin(
            #  *_plot_lines.get_legend_handles_labels())
        #  mpld3.plugins.connect(fig, _legend)

        yield (fig, ax, col)


def savefig_with_symlink(fig, fp, symlink_fp):
    os.makedirs(dirname(fp), exist_ok=True)
    fig.savefig(fp, bbox_inches='tight')
    if os.path.islink(symlink_fp):
        os.remove(symlink_fp)
    prefix = os.path.dirname(os.path.commonprefix([fp, symlink_fp]))
    os.symlink(fp[len(prefix)+1:], symlink_fp)
    print('save fig', symlink_fp)


def main(ns):
    print(ns)
    # mode 1: compare each column across all files
    if ns.mode == 0:
        cdfs = mode_0(ns)
    elif ns.mode == 1:
        cdfs = mode_1_plots(ns)
    elif ns.mode == 2:
        cdfs = mode_2_plots(ns)
    elif ns.mode == 3:
        cdfs = mode_3_plots(ns)
    elif ns.mode == 4:
        cdfs = mode_4_plots(ns)
    else:
        raise Exception(f'not implemented mode: {ns.mode}')
    if ns.no_plot:
        print("type 'plt.show()' in IPython terminal to see result")
        ipython_start_cmd = []
    else:
        ipython_start_cmd = ['-c', 'plt.ion() ; plt.show(block=False)', '-i']
        #  plt.show(block=False)
    if ns.shell:
        dct = dict(locals())
        dct.update(globals())
        print("\n==== Global Namespace: ====\n{1}\n\n==== Local Namespace: ====\n{0}\n".format(
            '\n'.join([x for x in locals().keys() if not x.startswith('__')]),
            ', '.join(globals().keys())))
        IPython.start_ipython(['--no-banner'] + ipython_start_cmd, user_ns=dct)


def mode_0(ns):
    cdfs = _get_all_data(ns)
    return cdfs


def _mode_1_and_4_get_perf_data_as_df(ns):
    dfs = dict(_mode1_get_frames(ns))
    cdfs = pd.concat(dfs, sort=False, names=['run_id', 'filename'])
    return cdfs


def mode_1_plots(ns):
    """Compare experiments.  
    One plot for each metric, comparing the most recent result of each experiment
    """
    cdfs = _mode_1_and_4_get_perf_data_as_df(ns).reset_index('filename', drop=True)

    timestamp = dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S.%f')  # date plot was created.  nothing to do with timestamp column.
    os.makedirs(join(ns.mode1_savefig_dir, 'archive'), exist_ok=True)
    for fig, ax, col in make_plots(ns, cdfs):
        if not ns.savefig: continue
        savefig_with_symlink(
            fig,
            f'{ns.mode1_savefig_dir}/archive/{col}_{timestamp}.png',
            f'{ns.mode1_savefig_dir}/{col}_latest.png')
    return cdfs


def mode_2_plots(ns):
    """Analyze an experiment's historical performance across many runs.
    One plot for each experiment and metric, to analyze history of runs for
    that experiment"""
    # mode 2: compare train to val performance
    cdfs_mode2 = {}
    timestamp = dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S.%f')  # date plot was created.  nothing to do with timestamp column.
    for run_id in get_run_ids(ns):
        dirp = f'{ns.data_dir}/{run_id}/log'
        if not os.path.exists(dirp):
            print('skip', run_id, 'contains no log data')
            continue

        cdfs = pd.concat({
            (run_id, fname): load_df_from_fp(join(dirp, fname), ns)
            for fname in os.listdir(dirp)
            if re.search(f'{ns.data_fp_regex}', fname)},
            sort=False, names=['run_id', 'filename']
        )
        cdfs_mode2[run_id] = cdfs

        os.makedirs(f'{ns.mode2_savefig_dir}/archive'.format(run_id=run_id), exist_ok=True)
        for fig, ax, col in make_plots(ns, cdfs.reset_index('run_id', drop=True)):
            fig.suptitle(run_id)
            if not ns.savefig: continue
            # save to file
            savefig_with_symlink(
                fig,
                f'{ns.mode2_savefig_dir}/archive/{col}_{timestamp}.png'.format(run_id=run_id),
                f'{ns.mode2_savefig_dir}/{col}_latest.png'.format(run_id=run_id))
    return cdfs_mode2


def prettify(x:str):
    if x is None:
        return x
    x = x.replace('_', ' ').split(' ')
    for i,xx in enumerate(x):
        if not any(y.isupper() for y in xx):
            x[i] = xx.title()
    return ' '.join(x)


def mode_3_plots(ns):
    """Compare across experiments, considering their history of runs.
    Basically combines mode 1 and mode 2. """
    cdfs = _get_all_data(ns)
    cols = [col for col in cdfs.columns if re.search(ns.col_regex, col)]
    if ns.avg_cols:
        colname = 'Mean(%s)' % ns.col_regex
        cdfs[colname] = cdfs[cols].mean(axis=1)
        cols = [colname]

    #  cdfs.groupby(['run_id', 'epoch']).agg(ns.mode3_agg_method)
    cdfs_unmodified = cdfs.copy()
    if ns.rolling_mean:
        cdfs = cdfs.rolling(ns.rolling_mean).mean()
    cdfs.columns = [prettify(col) for col in cdfs.columns]
    cdfs.index.names = [prettify(x) for x in cdfs.index.names]

    timestamp = dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S.%f')  # date plot was created.  nothing to do with timestamp column.
    plot_cols = [prettify(col) for col in cols]
    for col in plot_cols:
        fig, ax = plt.subplots(1,1, figsize=(12,10))
        kws = dict(x=prettify(ns.index_col), y=col, hue='Run Id', ax=ax, data=cdfs)
        sns.lineplot(**kws, ci=ns.mode3_ci or None, lw=2 if ns.mode3_ci == 0 else 1, legend=ns.legend)
        if ns.mode3_ci == 0:
            sns.lineplot(**kws, units="Filename", estimator=None, lw=1, alpha=.5)#, legend=False)
        ax.set_title(col)
        if not ns.savefig: continue
        savefig_with_symlink(
            fig,
            f'{ns.mode3_savefig_dir}/archive/{col}_mode3_{timestamp}.png',
            f'{ns.mode3_savefig_dir}/{col}_mode3_latest.png')
    return cdfs_unmodified


def _mode4_make_subplots(grp:pd.DataFrame, ns):
    regex, grp_num = ns.mode4_groupby.rsplit(':', 1)
    run_id = grp.index.to_frame()['Run Id'].unique()
    assert len(run_id) == 1, 'code bug'
    run_id = run_id[0]
    if ns.mode4_groupby is None:
        colgrps = [run_id] * len(grp.columns)
    else:
        colgrps = []
        match_error = False
        for col,filename in grp.columns:
            match = re.search(regex, col)
            if match is None:
                colgrps.append(None)
                print(f'--mode4-groupby: No match found for "{col}" given regex: "{regex}"')
                match_error = True
                continue
            try:
                cg = match.group(int(grp_num))
            except IndexError as e:
                msg = (
                    f'    match object: {match} '
                    f'\n    regex: "{regex}" '
                    f'\n    matched groups: {match.groups()} '
                    f'\n    col: {col}')
                raise Exception(
                    '--mode4-groupby had wrong group number :N. '
                    ' Helpful detail: \n' + msg)
            colgrps.append(match.group(int(grp_num)))
        if match_error:
            raise Exception(
                '--mode4-groupby regex did not match one or'
                ' more columns (see previously printed msgs)')
    assert len(colgrps) > 0, 'code bug'
    # choose nrows, ncols for the figure
    N = len(set(colgrps))
    if N < 5:
        M = 1
    else:
        M = int(np.sqrt(N))
        N = int(np.ceil(N/M))
    fig, axs = plt.subplots(N, M, figsize=(12,10), squeeze=False)
    colgrps = np.array(colgrps)
    for ax, subplot_title in zip(axs.ravel(), sorted(set(colgrps))):
        cols = grp.columns[colgrps == subplot_title]
        z = grp[cols].reset_index('Run Id', drop=True)
        assert z.columns.names[1] == 'Filename', 'code bug'
        z.columns.set_names([subplot_title, 'Filename'], inplace=True)
        z = z.copy()  # necessary to fix legend
        if ns.mode4_allruns == -1:
            # actually don't use filename, but keep it here in case want to extend
            # mode 4 to support a mode 2 or 3 style of lookback.
            z.columns = z.columns.droplevel('Filename')
        elif ns.mode4_allruns is not None:  # consider a subset of previous runs
            filenames = set(sorted(z.columns.levels[1])[-1*ns.mode4_allruns:])
            cols = [x for x in z.columns if x[1] in filenames]
            z = z[cols]
        if (z.dtypes.values == np.dtype('O')).all():
            print('WARNING: skip col with no numeric data:', col)
            ax.set_title(f'{col}, SKIPPED because no numeric data')
            continue
        z.plot(ax=ax, title=subplot_title)
        print(ns)
        if not ns.legend:
            ax.get_legend().remove()
    fig.suptitle(f'Experiment: {run_id}')
    fig.tight_layout()


def mode_4_plots(ns):
    """For each experiment, compare across columns. One plot per experiment"""
    print(ns.mode4_allruns)
    if ns.mode4_allruns == -1:
        cdfs = _mode_1_and_4_get_perf_data_as_df(ns)
    else:
        cdfs = _get_all_data(ns)
    cols = [col for col in cdfs.columns if re.search(ns.col_regex, col)]
    if ns.avg_cols:
        colname = 'Mean(%s)' % ns.col_regex
        cdfs[colname] = cdfs[cols].mean(axis=1)
        cols = [colname]
    cdfs_unmodified = cdfs.copy()
    cdfs = cdfs[cols]
    if ns.rolling_mean:
        cdfs = cdfs.rolling(ns.rolling_mean).mean()
    cdfs.columns = [prettify(col) for col in cdfs.columns]
    cdfs.index.names = [prettify(x) for x in cdfs.index.names]

    cdfs.unstack('Filename').groupby('Run Id').apply(
        lambda grp: _mode4_make_subplots(grp, ns))
    return cdfs_unmodified


def bap():
    class F(ap.ArgumentDefaultsHelpFormatter, ap.RawTextHelpFormatter): pass
    par = ap.ArgumentParser(formatter_class=F)
    A = par.add_argument
    A('runid_regex', help='find the run_ids that match the regular expression.')
    A('--data-dir', default='./results', help=' ')
    A('--data-fp-regex', default=r'perf.*\.csv$', help=' ')
    #  A('--', nargs='?', default='one', const='two')
    A('--rolling-mean', '--rm', type=int, help='smoothing')
    A('--hdf-table-name', help='required if searching .h5 files')
    A('-c', '--col-regex', default='^(?!epoch|batch_idx|timestamp)', help='plot only columns matching regex.  By default, plot all except epoch and batch_idx.')
    A('--index-col', default='epoch', help=' ')
    A('--mode', default=1, type=int, choices=[0,1,2,3,4], help=dedent('''\
        `--mode 0` Don't plot anything, just collect data and drop into a shell.
        `--mode 1` Compare across experiments, with one plot per column (i.e. performance metric)
        `--mode 2` Within one experiment and column, visualize the history of all runs.
        `--mode 3` Combine 1 and 2.  compare across run_ids, with
                   confidence interval to consider history of runs for each run_id.
        `--mode 4` Compare across columns, one plot per experiment.
                   '''))
    A('--mode1-savefig-dir', default='./results/plots/mode1', help=' ')
    A('--mode2-savefig-dir', default='./results/plots/mode2', help=' ')
    A('--mode3-savefig-dir', default='./results/plots/mode3', help=' ')
    A('--mode3-ci', type=float,
      help='confidence interval for error bars.  If 0, also shows all lines individually')
    A('--mode4-groupby', default="(Train|Val|Test) (.*):2", help=dedent('''\
        Optionally, make one sub-plot for each group of columns. To use, pass a
        regular expression extracting a string that we can group related
        columns followed by a ":N" where N is the one-indexed N-th capturing
        group to use.
        Example:  `--mode4-subplots "(Train|Val|Test) (.*):2"
          - this would place "train_loss" and "val_loss" into a subplot, and
            "train_acc" and "val_acc" in a different subplot.
        Note: This regex applies to the prettified text. The error messages
        will help you figure out what that means.
    '''))
    A('--mode4-allruns', nargs='?', type=int, default=-1, help=dedent('''\
        If supplied, give data on N 'most recent' runs for the given experiment,
        where 'most recent' means sort the csv filenames A-Z and take the last N.
        Example:  `--mode4-allruns 2` just shows the last two runs.'''))
    A('--best-effort', action='store_true',
      help=" Try to load a csv file, but don't raise error if cannot read a file.")
    A('--savefig', action='store_true', help="save plots to file")
    A('--no-plot', action='store_true', help="if supplied, don't show the plots")
    A('--no-shell', action='store_false', dest='shell',
      help='do not drop into an IPython shell when finished')
    A('--no-legend', action='store_false', dest='legend', help='do not show legend')
    A('--avg-cols', action='store_true', help=(
        'if supplied, average the columns of the input csv file,'
        ' where columns are defined by -c parameter'))
    return par


if __name__ == "__main__":
    main(bap().parse_args())
