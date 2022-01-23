#!/usr/bin/env python
def main():
    import sys
    from omfit_classes import unix_os as os
    import re

    def omfit_version_info():
        """
        Return tuple with OMFIT (major, year, month) version

        :return: tuple with OMFIT (major, year, month) version
        """
        with open(os.path.dirname(os.path.abspath(__file__)) + '/omfit_classes/version') as f:
            return tuple(map(int, f.read().split('.')))

    python_version_str = '.'.join([str(i) for i in sys.version_info[0:2]])
    omfit_version_str = '.'.join([str(i) for i in omfit_version_info()])
    if sys.version_info < (3, 5):
        print(
            f'''
OMFIT v{omfit_version_str} only runs with Python 3.6+ and you are running Python {python_version_str}
Consider running a more recent version of Python or using OMFIT v2.x
'''
        )
        sys.exit(64)
    print(f"OMFIT v{omfit_version_str} running on Python {python_version_str}")

    # handle display of omfit_launch.sh options in omfit_parse_args help
    show_omfit_launch_options = False
    if 'show_omfit_launch_options' in sys.argv:
        sys.argv = list([x for x in sys.argv if x != 'show_omfit_launch_options'])
        show_omfit_launch_options = True
    # remove -P option (this is processed by the shell script that launches OMFIT)
    sys.argv = list([x for x in sys.argv if not re.match(r'^\-P[0-9\.]+', x)])
    # remove --cwd option (this is processed by the shell script that launches OMFIT)
    sys.argv = list([x for x in sys.argv if not re.match(r'^\-+cwd', x)])

    from omfit_parse_args import omfit_parse_args, nice_script_args

    args = omfit_parse_args(show_omfit_launch_options=show_omfit_launch_options)
    if len(args.scriptArgs):
        print(f'Calling `{os.path.splitext(os.path.basename(args.scriptFile))[0]}` with arguments:\n')
        tmp = nice_script_args(args)
        for k, v in tmp.items():
            print(f'   {k.rjust(max(map(len, tmp.keys())))} : {v}')
        print('')

    OMFITstartDir = os.getcwd()
    # setup
    if args.setup:
        os.environ['OMFIT_NO_GUI'] = "1"
        import omfit_setup

    # purge temporary files
    elif args.purge or args.reset or args.packages:
        os.environ['OMFIT_NO_GUI'] = "1"

        if args.reset:
            from omfit_classes.utils_base import quiet_environment

            with quiet_environment() as qe:
                from omfit_tree import OMFIT

                timing = qe.stdout.strip().split('\n')[-1]
            print(timing)
            OMFIT.reset_connections()

        if args.packages:
            from omfit_classes.utils_base import summarize_installed_packages

            exit(summarize_installed_packages()[0])

        if args.purge:
            from omfit_classes.utils_base import purge_omfit_temporary_files

            purge_omfit_temporary_files()

    # run a script not inside of OMFIT
    elif args.scriptFile and args.bare:
        _tmp = nice_script_args(args)

        from pprint import pformat

        print('Running script outside of framework: %s' % args.scriptFile)
        print('with arguments: ' + ('\n' + ' ' * 16).join(pformat(_tmp, depth=1).split('\n')))

        def defaultVars(**kw):
            for item in kw:
                if item not in _tmp:
                    _tmp[item] = kw[item]
            return _tmp

        _tmp['defaultVars'] = defaultVars
        with open(args.scriptFile, 'r') as f:
            exec(f.read(), _tmp)

    # run a script in the framework but without GUI
    elif args.scriptFile and not args.scriptGui:
        os.environ['OMFIT_NO_GUI'] = "1"
        from omfit_tree import OMFIT, OMFITpythonTask

        print('Running script: %s' % args.scriptFile)
        _tmp = nice_script_args(args)

        OMFIT['__userScript__'] = OMFITpythonTask(args.scriptFile, modifyOriginal=True)
        import time

        t0 = time.time()
        OMFIT['__userScript__'].runNoGUI(**_tmp)
        print('Running %s took %g seconds' % (args.scriptFile, time.time() - t0))
        return OMFIT

    # run the OMFIT framework with GUI
    # omfit_gui handles the opening of scripts in GUI, projects, modules, and commands
    else:
        os.environ['OMFIT_NO_GUI'] = '0'
        import omfit_gui


# =======================
if __name__ == '__main__':
    OMFIT = main()
