#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# commands_basic.py: commands used in the basic mode xt_demo

def get_command_dicts(prev_exper, curr_exper, browse_flag, browse_opt, timeout_opt, templ, archives_dir, 
    monitor_opt, readonly_ws):

	return [
	    # OVERVIEW
	    {"title": "show the XT about page", "cmd": "xt help --about"},
	    
        {"title": "show the help topic on the miniMnist app", "cmd": "xt help topic mini_mnist"},

	    # CONFIG FILES
	    {"title": "view the XT FACTORY config file", "cmd": "xt config factory"},
	    
        {"title": "view your XT GLOBAL config file", "cmd": "xt config global"},

	    # HELP
	    {"title": "display XT commands", "cmd": "xt help"},
	    
        {"title": "display help for LIST JOBS command", "cmd": "xt help list jobs"},

	    {"title": "browse the XT HTML docs", "cmd": "xt help --browse", "needs_gui": True},

	    # VERSION / RESTART
	    {"title": "display XT version", "cmd": "xt help --version"},

	    # INITIAL SYNC LOCAL RUN (this will create MNIST data and model)
	    {"title": "run script without XT and generate data/model", "cmd": "!python code/miniMnist.py --data=data --save-model"},

	    # upload DATA/MODELS (depends on miniMnist generated data and model)
	    {"title": "upload MNIST dataset", "cmd": "xt upload ./data/MNIST/processed/** MNIST/processed"},
	    
        {"title": "upload MNIST models", "cmd": "xt upload ./models/miniMnist/** miniMnist"},

	    # RUNS
	    {"title": "run script on LOCAL_MACHINE", "cmd": "xt run {}--target=local code/miniMnist.py".format(monitor_opt)},
	    
        {"title": "run script on AZURE BAtCH", "cmd": "xt run {}--target=batch code/miniMnist.py".format(monitor_opt)},

	    # REPORTS
	    {"title": "OVERVIEW: status of jobs", "cmd": "xt list jobs --last=4 --workspace={}".format(readonly_ws)},

	    {"title": "List runs", "cmd": "xt list runs --workspace={}".format(readonly_ws)},
	    
        {"title": "List runs and sort by metrics", "cmd": "xt list runs --sort=metrics.test-acc --last=5 --workspace={}".format(readonly_ws)},

	    {
            "title": "run script on Batch", 
            "cmd": "xt run {}--runs=50 --nodes=5 --search-type=dgd --hp-config=code/miniSweeps.yaml --target=batch  " \
                "code/miniMnist.py ".format(monitor_opt)
        },

	    {
            "title": "run script on ITP-US", 
            "cmd": "xt run {} --target=itp-us --data-action=mount --model-action=download code/miniMnist.py --auto-download=0 --eval-model=1". \
                format(monitor_opt)
        },
	]