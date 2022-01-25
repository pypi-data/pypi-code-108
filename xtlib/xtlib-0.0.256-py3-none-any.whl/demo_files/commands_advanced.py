#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# commands_advanced.py: commands used in the advanced mode xt_demo

def get_command_dicts(prev_exper, curr_exper, browse_flag, browse_opt, timeout_opt, templ, archives_dir, 
    monitor_opt, big_job, readonly_ws):

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

	    # STATUS    
	    {"title": "display STATUS of jobs on AZURE BATCH", "cmd": "xt view status --target=batch"}, 

        # turn this off until "view status" for local/pool has been updated for pool service manager API (psm client)
        #{"title": "display all active jobs on any of my compute targets", "cmd": "xt view status --target=all --active"},

	    # INITIAL SYNC LOCAL RUN (this will create MNIST data and model)
	    {"title": "run script without XT and generate data/model", "cmd": "!python code\\miniMnist.py --data=data --save-model"},

	    # upload DATA/MODELS (depends on miniMnist generated data and model)
	    {"title": "upload MNIST dataset", "cmd": "xt upload ./data/MNIST/processed/** MNIST/processed --share=data"},
	    {"title": "upload previously trained MNIST model", "cmd": "xt upload .\models\miniMnist\** miniMnist --share=models"},

	    # RUNS
	    {"title": "run script on LOCAL MACHINE", "cmd": "xt run {}--target=local --exper={} code\miniMnist.py".format(monitor_opt, curr_exper)},
	    {"title": "run script on ITP-US", "cmd": "xt run {}--target=itp-us --exper={} code\miniMnist.py".format(monitor_opt, curr_exper)},
	    {"title": "run script on AZURE BATCH", "cmd": "xt run {}--target=batch --exper={} code\miniMnist.py".format(monitor_opt, curr_exper)},
	    {"title": "run script on AZURE ML", "cmd": "xt run {}--target=aml --exper={} code\miniMnist.py".format(monitor_opt, curr_exper)},

	    # REPORTS
	    {"title": "OVERVIEW: status of jobs", "cmd": "xt list jobs --last=4"},
	    {"title": "ZOOM in on CURRENT experiment", "cmd": "xt list runs --exper={}".format(curr_exper)},

	    # TAGGING
	    {"title": "add tag 'good_run' to run1, run2", "cmd": "xt set tags run1, run2 good_run"},
	    {"title": "list runs with the 'good_run' tag", "cmd": "xt list runs --tags-any=good_run"},

	    # CMD LINE PIPING
	    {
            "title": "the 'list runs' and 'list jobs' have powerful filtering and sorting options", 
            "cmd": "xt list runs --exper=search10 --sort=metrics.test-acc --last=5 --workspace={}".format(readonly_ws)
        },

	    {
		    "title": "you can leverage the 'list runs' cmd to feed runs into another cmd, using XT command piping", \
		    "cmd": "!xt list runs --exper=search10 --sort=metrics.test-acc --last=5 --workspace={} ".format(readonly_ws) + 
                "| xt set tags $ top5 --workspace={}".format(readonly_ws)
		},

	    {
            "title": "let's see which runs are now tagged with 'top5", 
            "cmd": "xt list runs --tags-any=top5 --workspace={}".format(readonly_ws)
        },

	    # VIEW PORTAL
	    {"title": "Browse the portal for the 'itp' target", "cmd": "xt view portal itp {}".format(browse_flag)},

	    {"title": "Browse the portal for the 'aml' target", "cmd": "xt view portal aml {}".format(browse_flag)},

	    # TENSORBOARD
        {
	        "title": "view LIVE tensorboard of cross-service experiments with custom path template",
	        "cmd": 'xt view tensorboard --exper=search10 {} --template="{}" --workspace={}'. \
                format(browse_flag, templ, readonly_ws),
	        "needs_gui": True
	    },

	    # LOG, CONSOLE, ARTIFACTS
	    #{"title": "view log for run5751", "cmd": "xt view log run5751"}
	    {"title": "view console output of run2", "cmd": "xt view console run2"},

	    {"title": "download all source code, output, and logs for run4", "cmd": "xt extract run4 {} {}".format(archives_dir, browse_opt)},

        # TODO: replace imported runs with new ones; rerun cmd is failing due to trying to use out of date CONFIG file
	    # RERUN (monitor_opt is harder to apply here)
	    #{"title": "rerun run2, with original source code and hyperparameter settings", "cmd": "xt rerun run2"},

	    # MOUNT data and DOWNLOAD model
	    {
            "title": "run script on itp-us, mounting data and downloading model for eval", 
            "cmd": "xt run {}--target=itp-us --data-action=mount --model-action=download code\miniMnist.py --auto-download=0 --eval-model=1". \
                format(monitor_opt)
        },

	    # DOCKER RUNS
	    # {"title": "log in to azure docker registry", "cmd": "xt docker login  --environment=pytorch-xtlib "}
	    # {"title": "log out from docker registry", "cmd": "xt docker logout  --environment=pytorch-xtlib "}
	    # {"title": "run script in DOCKER container on LOCAL MACHINE", "cmd": "xt --target=local --environment=pytorch-xtlib-local run code\miniMnist.py --no-cuda"}
	    # {"title": "run script in DOCKER container on BATCH", "cmd": "xt --target=batch --environment=pytorch-xtlib run code\miniMnist.py"}

	    # PARALLEL TRAINING
	    {
		    "title": "run parallel training on Azure ML using 4 GPUs", 
	        "cmd": "xt run {}--target=aml4x code\miniMnist.py --train-percent=1 --test-percent=1 --epochs=100 --parallel=1". \
                format(monitor_opt)
	    },

	    # DISTRIBUTED TRAINING
	    {
		    "title": "run distributed training on Azure ML using 8 boxes", 
	        "cmd": "xt run {}--target=aml --direct-run=true --nodes=8 --distributed code\miniMnist.py --train-percent=1 --test-percent=1  " \
                "--epochs=100  --distributed=1".format(monitor_opt)
	    },

	    # HPARAM SEARCH
	    {
		    "title": "start a hyperparmeter search of 50 runs (5 boxes, 10 runs each) using Azure Batch", 
	        "cmd": "xt run {}--target=batch --runs=50 --nodes=5 --search-type=dgd --hp-config=code\miniSweeps.yaml code\miniMnist.py". \
                format(monitor_opt)
	    },

	    {
            "title": "view a report of previously completed HP search, ordered by test accuracy", 
            "cmd": "xt list runs --job={} --sort=metrics.test-acc --workspace={}".format(big_job, readonly_ws)
        },

        # HPARAM EXPLORER
        # NOTE: turn back ON as soon as we merge in PR's #139, #143 
	    # {
		#     "title": "open Hyperparameter Explorer to compare the effect of hyperparameter settings on test accuracy, using a previously completed HP search", 
	    #     "cmd": "xt explore {} {}".format(big_job, timeout_opt),
        #     "needs_gui": True
	    # },

	    # AD-HOC PLOTTING (run as external cmd due to problem closing 2nd matplotlib window)
        # SINGLE PLOT of 10 RUNS
        {
	        "title": "display a plot of 10 runs",
	        "cmd": '!xt plot {} test-acc {} --workspace={}'.format(big_job, timeout_opt, readonly_ws),
			"needs_gui": True
	    },

        # # APPLY SMOOTHING FACTOR
        # cmd = '!xt plot job9554 ' + \
        #     "test-acc --smooth=.85  {}".format(timeout_opt)
        # {"title": "apply a smoothing factor", cmd)

        # # AGGREGATE over runs
        # cmd = '!xt plot job9554 ' + \
        #     "test-acc --smooth=.85 --aggregate=mean --range-type=std {}".format(timeout_opt)
        # {"title": "plot the average the runs, using std as the range area", cmd)

        # 2 METRICS, 2x5 MATRIX (break on run)
        {
	        "title": "alternatively, let's add a 2nd metric, train-acc, and show each run in its own plot",
	        "cmd": '!xt plot {} train-acc, test-acc --break=run --layout=2x5 {} --workspace={}'.\
                format(big_job, timeout_opt, readonly_ws),
	        "needs_gui": True
	    },

        # 2 METRICS, 2x1 MATRIX (break on col)
        {
	        "title": "finally, we can easily break on the col, instead of the run",
	        "cmd": '!xt plot {} train-acc, test-acc --break=col --layout=2x1 {} --workspace={}'.\
                format(big_job, timeout_opt, readonly_ws),
	        "needs_gui": True
	    }

        # TODO: add plot summary cmd here
	]