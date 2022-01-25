import os
import json
import click

@click.command(name='run_pulls')
@click.option('-i', '--input_file', required=True, 
              help='Path to the input workspace file')
@click.option('-x', '--poi', required=True,
              help='POIs to measure')
@click.option('-o', '--outdir', default="pulls", show_default=True,
              help='Output directory')
@click.option('-w', '--workspace', default=None, 
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', default=None, 
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', default='combData', show_default=True,
              help='Name of dataset')
@click.option('-p', '--parameter', default='', show_default=True,
              help='Nuisance parameter(s) to run pulls on.'+\
                   'Multiple parameters are separated by commas.'+\
                   'Wildcards are accepted. All NPs are run by default.')
@click.option('-r', '--profile', default=None, show_default=True,
              help='Parameters to profile')
@click.option('-f', '--fix', default=None, show_default=True,
              help='Parameters to fix')
@click.option('-s', '--snapshot', default="nominalNuis", show_default=True,
              help='Name of initial snapshot')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('--binned/--unbinned', default=True, show_default=True,
              help='Binned likelihood')
@click.option('-q', '--precision', type=float, default=0.001, show_default=True,
              help='Precision for scan')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('-l', '--log_level', default="INFO", show_default=True,
              help='Log level')
@click.option('--print_level', type=int, default=1, show_default=True,
              help='Minimizer print level')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default strategy')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-multi', default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin centre')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b Parallelize job across the N workers.'
                   '\b Case  0: Jobs are run sequentially (for debugging).\n'
                   '\b Case -1: Jobs are run across N_CPU workers.\n')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache existing result')
@click.option('--exclude', default="", show_default=True,
              help='Exclude NPs (wildcard is accepted)')
def run_pulls(**kwargs):
    """
    Tool for computing NP pulls and impacts
    """
    from quickstats.components import NuisanceParameterPull
    NuisanceParameterPull().run_pulls(**kwargs)
    
@click.command(name='plot_pulls')
@click.option('-i', '--inputdir', required=True, help='Path to directory containing pull results')
@click.option('-p', '--poi', default=None, help='Parameter of interest for plotting impact')
@click.option('-n', '--n_rank', type=int, default=None, help='Total number of NP to rank')
@click.option('-m', '--rank_per_plot', type=int, default=20, show_default=True,
              help='Number of NP to show in a single plot')
@click.option('--ranking/--no_ranking', default=True, show_default=True,
              help='Rank NP by impact')
@click.option('--threshold', type=float, default=0., show_default=True,
              help='Filter NP by postfit impact threshold')
@click.option('--show_sigma/--hide_sigma', default=True, show_default=True,
              help='Show one standard deviation pull')
@click.option('--show_prefit/--hide_prefit', default=True, show_default=True,
              help='Show prefit impact')
@click.option('--show_postfit/--hide_postfit', default=True, show_default=True,
              help='Show postfit impact')
@click.option('--sigma_bands/--no_sigma_bands', default=False, show_default=True,
              help='Draw +-1, +-2 sigma bands')
@click.option('--sigma_lines/--no_sigma_lines', default=True, show_default=True,
              help='Draw +-1 sigma lines')
@click.option('--shade/--no_shade', default=True, show_default=True,
              help='Draw shade')
@click.option('--correlation/--no_correlation', default=True, show_default=True,
              help='Show correlation impact')
@click.option('--onesided/--overlap', default=True, show_default=True,
              help='Show onesided impact')
@click.option('--relative/--absolute', default=False, show_default=True,
              help='Show relative variation')
@click.option('--theta_max', type=float, default=2, show_default=True,
              help='Pull range')
@click.option('-y', '--padding', type=int, default=7, show_default=True,
              help='Padding below plot for texts and legends. NP column height is 1 unit.')
@click.option('-h', '--height', type=float, default=1.0, show_default=True,
              help='NP column height')
@click.option('-s', '--spacing', type=float, default=0., show_default=True,
              help='Spacing between impact box')
@click.option('-d', '--display_poi', default=r"$\mu$", show_default=True,
              help='POI name to be shown in the plot')
@click.option('-t', '--extra_text', default=None, help='Extra texts below the ATLAS label. '+\
                                                       'Use "//" as newline delimiter')
@click.option('--elumi_label/--no_elumi_label', default=True, show_default=True,
              help='Show energy and luminosity labels')
@click.option('--ranking_label/--no_ranking_label', default=True, show_default=True,
              help='Show ranking label')
@click.option('--energy', default="13 TeV", show_default=True, 
              help='Beam energy')
@click.option('--lumi', default="139 fb$^{-1}$", show_default=True, 
              help='Luminosity')
@click.option('--status', default="int", show_default=True, 
              help='\b Analysis status. Choose from'
                   '\b            int : Internal\n'
                   '\b            wip : Work in Progress\n'
                   '\b         prelim : Preliminary\n'
                   '\b          final : *no status label*\n'
                   '\b *custom input* : *custom input*\n')
@click.option('--combine_pdf/--split_pdf', default=True, show_default=True,
              help='Combine all ranking plots into a single pdf')
@click.option('--outdir', default='ranking_plots', show_default=True,
              help='Output directory')
@click.option('-o', '--outname', default='ranking', show_default=True,
              help='Output file name prefix')
@click.option('--style', default='default', show_default=True,
              help='Plotting style. Built-in styles are "default" and "trex".'+\
                   'Specify path to yaml file to set custom plotting style.')
@click.option('--fix_axis_scale/--free_axis_scale', default=True, show_default=True,
              help='Fix the axis scale across all ranking plots')
def plot_pulls(**kwargs):
    """
    Tool for plotting NP pulls and impact rankings
    """    
    from quickstats.plots.np_ranking_plot import NPRankingPlot
    inputdir, poi = kwargs.pop('inputdir'), kwargs.pop('poi')
    ranking_plot = NPRankingPlot(inputdir, poi)
    ranking_plot.plot(**kwargs)
    
    
@click.command(name='likelihood_scan')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('--min', 'poi_min', type=float, required=True, 
              help='Minimum POI value to scan.')
@click.option('--max', 'poi_max', type=float, required=True, 
              help='Maximum POI value to scan.')
@click.option('--step', 'poi_step', type=float, required=True, 
              help='Scan interval.')
@click.option('-p', '--poi', 'poi_name', default=None, show_default=True,
              help='POI to scan. If not specified, the first POI from the workspace is used.')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache existing result')
@click.option('-o', '--outname', default='{poi_name}', show_default=True,
              help='Name of output.')
@click.option('--outdir', default='likelihood_scan', show_default=True,
              help='Output directory.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics)')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Binned likelihood')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--print_level', type=int, default=0, show_default=True,
              help='Minimizer print level')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b Parallelize job across the N workers.'
                   '\b Case  0: Jobs are run sequentially (for debugging).\n'
                   '\b Case -1: Jobs are run across N_CPU workers.\n')
def likelihood_scan(**kwargs):
    """
    Tool for likelihood scan
    """
    from quickstats.components.likelihood import scan_nll
    scan_nll(**kwargs)

@click.command(name='cls_limit')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file')
@click.option('-p', '--poi', 'poi_name', default=None, show_default=True,
              help='POI to scan. If not specified, the first POI from the workspace is used.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset')
@click.option('-o', '--outname', default='limits.json', show_default=True,
              help='Name of output')
@click.option('--blind/--unblind', 'do_blind', default=True, show_default=True,
              help='Blind/unblind analysis')
@click.option('--CL', 'CL', type=float, default=0.95, show_default=True,
              help='CL value to use')
@click.option('--precision', default=0.005, show_default=True,
              help='precision in mu that defines iterative cutoff')
@click.option('--do_tilde/--no_tilde', default=True, show_default=True,
              help='bound mu at zero if true and do the \tilde{q}_{mu} asymptotics')
@click.option('--predictive_fit/--no_predictive_fit', default=True, show_default=True,
              help='extrapolate best fit nuisance parameters based on previous fit results')
@click.option('--do_better_bands/--skip_better_bands', default=True, show_default=True,
              help='evaluate asymptotic CLs limit for various sigma bands')
@click.option('--better_negative_bands/--skip_better_negative_bands', default=False, show_default=True,
              help='evaluate asymptotic CLs limit for negative sigma bands')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Binned likelihood')
@click.option('--save_summary/--skip_summary', default=True, show_default=True,
              help='Save summary information')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('--timer/--no_timer', default=False, show_default=True,
              help='Enable minimizer timer')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin centre')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def cls_limit(**kwargs):
    """
    Tool for evaluating Asymptotic CLs limit
    """
    from quickstats.components import AsymptoticCLs
    outname = kwargs.pop('outname')
    save_summary = kwargs.pop('save_summary')
    asymptotic_cls = AsymptoticCLs(**kwargs)
    asymptotic_cls.evaluate_limits()
    asymptotic_cls.save(outname, summary=save_summary)

@click.command(name='compile')
@click.option('-m', '--macros', default=None, show_default=True,
              help='Macros to compile (separated by commas). By default all macros are compiled.')
def compile_macros(macros):
    """
    Compile ROOT macros
    """
    import quickstats
    quickstats.compile_macros(macros)

@click.command(name='harmonize_np')
@click.argument('ws_files', nargs=-1)
@click.option('-r', '--reference', required=True, help='Path to reference json file containing renaming scheme')
@click.option('-i', '--input_config_path', default=None, show_default=True,
              help='Path to json file containing input workspace paths')
@click.option('-b', '--base_path', default='./', show_default=True,
              help='Base path for input config')
@click.option('-o', '--outfile', default='renamed_np.json', show_default=True,
              help='Output filename')
def harmonize_np(ws_files, reference, input_config_path, base_path, outfile):
    """
    Harmonize NP names across different workspaces
    """
    from quickstats.components import NuisanceParameterHarmonizer
    harmonizer = NuisanceParameterHarmonizer(reference)
    if (len(ws_files) > 0) and input_config_path is not None:
        raise RuntimeError('either workspace paths or json file containing workspace paths should be given')
    if len(ws_files) > 0:
        harmonizer.harmonize(ws_files, outfile=outfile)
    elif (input_config_path is not None):
        harmonizer.harmonize_multi_input(input_config_path, base_path, outfile=outfile)
        
        
@click.command(name='generate_asimov')
@click.option('-i', '--input_file', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', required=True, 
              help='Name of the output workspace containing the '
                   'generated asimov dataset.')
@click.option('-p', '--poi', required=True, 
              help='Name of the parameter of interest (POI).')
@click.option('--poi_val', type=float, default=None, show_default=True,
              help='Generate asimov data with POI set at the specified value. '
                   'If None, POI will be kept at the post-fit value if a fitting '
                   'is performed or the pre-fit value if no fitting is performed.')
@click.option('--poi_profile', type=float, default=None, show_default=True,
              help='Perform nuisance parameter profiling with POI set at the specified value. '
                   'This option is only effective if do_fit is set to True. If None, POI is '
                   'set floating (i.e. unconditional maximum likelihood estimate).')
@click.option('--modify-globs/--keep-globs', default=True, show_default=True,
              help='Match the values of nuisance parameters and the corresponding global '
                   'observables when generating the asimov data. This is important for making '
                   'sure the asimov data has the (conditional) minimal NLL.')
@click.option('--do-fit/--no-fit', default=True, show_default=True,
              help='Perform nuisance parameter profiling with a fit to the given dataset.')
@click.option('--asimov_name', default="asimovData_{mu}", show_default=True,
              help='Name of the generated asimov dataset.')
@click.option('-d', '--data', default='combData', show_default=True,
              help='Name of the dataset used in NP profiling.')
@click.option('--constraint_option', default=0, show_default=True,
              help='Customize the target of nuisance paramaters involved in the profiling.'
                   'Case 0: All nuisance parameters are allowed to float;'
                   'Case 1: Constrained nuisance parameters are fixed to 0. Unconstrained '
                   'nuisrance parameters are allowed to float.')
@click.option('-c', '--configuration', default=None,
              help='Path to the json configuration file containing'
                   ' the minimizer options for NP profiling.')
def generate_asimov(**kwargs):
    """
    Generate Asimov dataset
    """
    input_filename = kwargs.pop("input_file")
    output_filename = kwargs.pop("output_file")
    if os.path.abspath(input_filename) == os.path.abspath(output_filename):
        raise ValueError("output workspace file name cannnot be the same as the input workspace file name")
    from quickstats.components import AnalysisObject
    config_file = kwargs.pop("configuration")
    if config_file is not None:
        config = json.load(open(config_file, 'r'))
    else:
        config = {}
    data_name = kwargs.pop("data")
    kwargs['poi_name'] = kwargs.pop("poi")
    task = AnalysisObject(filename=input_filename, data_name=data_name, **config)
    task.model.generate_asimov(**kwargs)
    task.model.save(output_filename)


@click.command(name='generate_standard_asimov')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', required=True, 
              help='Name of the output workspace containing the '
                   'generated asimov dataset.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of the dataset used in NP profiling.')
@click.option('-p', '--poi', 'poi_name', required=True, 
              help='Name of the parameter of interest (POI).')
@click.option('-s', '--poi_scale', type=float, default=1.0, show_default=True,
              help='Scale factor applied to the poi value')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-t', '--asimov_types', default="0,1,2", show_default=True,
              help='\b Types of asimov dataset to generate separated by commas.\n'
                   '\b 0: fit with POI fixed to 0\n'
                   '\b 1: fit with POI fixed to 1\n'
                   '\b 2: fit with POI free and set POI to 1 after fit\n'
                   '\b 3: fit with POI and constrained NP fixed to 0\n'
                   '\b 4: fit with POI fixed to 1 and constrained NP fixed to 0\n'
                   '\b 5: fit with POI free and constrained NP fixed to 0 and set POI to 1 after fit\n'
                   '\b -1: nominal NP with POI set to 0\n'
                   '\b -2: nominal NP with POI set to 1\n')
def generate_standard_asimov(**kwargs):
    """
    Generate standard Asimov dataset
    """
    from quickstats.components import AsimovGenerator
    outname = kwargs.pop('outname')
    asimov_types = kwargs.pop('asimov_types')
    asimov_types = [int(t) for t in asimov_types.split(',')]
    fix_param = kwargs.pop('fix_param')
    profile_param = kwargs.pop('profile_param')
    snapshot_name = kwargs.pop('snapshot_name')
    poi_scale = kwargs.pop("poi_scale")
    config = {
        'fix_param': fix_param,
        'profile_param': profile_param,
        'snapshot_name': snapshot_name
    }
    generator = AsimovGenerator(**kwargs, config=config)
    generator.generate_standard_asimov(asimov_types, poi_scale=poi_scale)
    generator.save(outname)
    

@click.command(name='toy_significance')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', default="toy_study/results.json", 
              help='Name of the output file containing toy results.')
@click.option('-n', '--n_toys', type=int,
              help='Number of the toys to use.')
@click.option('-b', '--batchsize', type=int, default=100, show_default=True,
              help='Divide the task into batches each containing this number of toys. '
                   'Result from each batch is saved for caching and different batches '
                   'are run in parallel if needed')
@click.option('-s', '--seed', type=int, default=0,  show_default=True,
              help='Random seed used for generating toy datasets.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('-v', '--poi_val', type=float, default=0,  show_default=True,
              help='POI value when generating the toy dataset.')
@click.option('--binned/--unbinned', default=True, show_default=True,
              help='Generate binned toy dataset.')
@click.option('--cache/--no-cache', default=True,  show_default=True,
              help='Cache existing batch results.')
@click.option('--fit_options', default=None, help='A json file specifying the fit options.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b Parallelize job across the N workers.'
                   '\b Case  0: Jobs are run sequentially (for debugging).\n'
                   '\b Case -1: Jobs are run across N_CPU workers.\n')
def toy_significance(**kwargs):
    """
    Generate toys and evaluate significance
    """
    from quickstats.components import PValueToys
    n_toys = kwargs.pop("n_toys")
    batchsize = kwargs.pop("batchsize")
    seed = kwargs.pop("seed")
    cache = kwargs.pop("cache")
    outname = kwargs.pop("outname")
    parallel = kwargs.pop("parallel")
    pvalue_toys = PValueToys(**kwargs)
    pvalue_toys.get_toy_results(n_toys=n_toys, batchsize=batchsize, seed=seed,
                                cache=cache, save_as=outname, parallel=parallel)
    
    
    
@click.command(name='toy_limit')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of the dataset used for computing observed limit.')
@click.option('-o', '--output_file', 'outname', 
              default="toy_study/toy_result_seed_{seed}_batch_{batch}.root",
              show_default=True,
              help='Name of the output file containing toy results.')
@click.option('--poi_max', type=float, default=None,
              help='Maximum range of POI.')
@click.option('--poi_min', type=float, default=None,
              help='Minimum range of POI.')
@click.option('--scan_max', type=float, default=None,
              help='Maximum scan value of POI.')
@click.option('--scan_min', type=float, default=None,
              help='Minimum scan value of POI.')
@click.option('--steps', type=int, default=10, show_default=True,
              help='Number of scan steps.')
@click.option('--mu_val', type=float, default=None,
              help='Value of POI for running a single point')
@click.option('-n', '--n_toys', type=int,
              help='Number of the toys to use.')
@click.option('-b', '--batchsize', type=int, default=50, show_default=True,
              help='Divide the task into batches each containing this number of toys. '
                   'Result from each batch is saved for caching and different batches '
                   'are run in parallel if needed')
@click.option('-s', '--seed', type=int, default=2021,  show_default=True,
              help='Random seed used for generating toy datasets.')
@click.option('-t', '--tolerance', type=float, default=1.,  show_default=True,
              help='Tolerance for minimization.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Use NLL offset.')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('--snapshot', 'snapshot_name', default=None, help='Name of initial snapshot')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b Parallelize job across the N workers.'
                   '\b Case  0: Jobs are run sequentially (for debugging).\n'
                   '\b Case -1: Jobs are run across N_CPU workers.\n')
def toy_limit(**kwargs):
    """
    Generate toys and evaluate limits
    """
    from quickstats.components.toy_limit_calculator import evaluate_batched_toy_limits
    if not (((kwargs['scan_min'] is None) and (kwargs['scan_max'] is None) and (kwargs['mu_val'] is not None)) or \
           ((kwargs['scan_min'] is not None) and (kwargs['scan_max'] is not None) and (kwargs['mu_val'] is None))):
        raise ValueError("please provide either (scan_min, scan_max, steps) for running a scan or (mu_val)"
                         " for running a single point")        
    evaluate_batched_toy_limits(**kwargs)