#!/usr/bin/env python

import re
import logging
import traceback
import queue
import threading
import time

import tkinter as tk
import tkinter.ttk

import marlowe_ui.tktool.askfilename
import marlowe_ui.tktool.codedoptionmenu
import marlowe_ui.logconsole

import marlowe_ui.postprocess.dumper as old_dumper
import marlowe_ui.postprocess_lark.dumper as dumper

logger = logging.getLogger(__name__)

class OldDumpWorker(threading.Thread):
    def __init__(self,
            input_,
            outputdir):
        super().__init__()

        self.input_ = input_
        self.outputdir = outputdir

    def run(self):
        try:
            p = old_dumper.Parser(outputdir=self.outputdir)
            p.parse(self.input_)
        except Exception as e:
            logger.error(str(e), exc_info=True)

class DumpWorker(threading.Thread):
    def __init__(self,
            input_,
            outputdir,
            config_dump_text_blocks=True,
            config_cascade_table_output='BOTH',
            config_ignore_block_parse_error=False):
        super().__init__()

        self.input_ = input_
        self.outputdir = outputdir
        self.config_dump_text_blocks = config_dump_text_blocks
        self.config_cascade_table_output = config_cascade_table_output
        self.config_ignore_block_parse_error=config_ignore_block_parse_error

    def run(self):
        try:
            dumper.run(
                    self.input_,
                    self.outputdir,
                    config_dump_text_blocks=self.config_dump_text_blocks,
                    config_cascade_table_output=self.config_cascade_table_output,
                    config_ignore_block_parse_error=self.config_ignore_block_parse_error)
        except Exception as e:
            logger.error(str(e), exc_info=True)



if __name__ == '__main__':
    app = tk.Tk()

    # input file chooser
    labelframe = tk.LabelFrame(app, text='Input Filename')
    labelframe.pack(fill=tk.X)

    filepath = marlowe_ui.tktool.askfilename.OpenFileName(
        labelframe,
        diagfiletypes=[('Marlowe output', '*.lst'), ('All', '*')])
    filepath.pack(fill=tk.X)

    dumpworker = None
    dumpstartepoch = None

    def watch_dumpworker():
        global dumpworker
        global dumpstartepoch
        
        if dumpworker and dumpworker.is_alive():
            # keep watch thread
            timediff = int(time.time() - dumpstartepoch)
            hdiff, rest = divmod(timediff, 60*60)
            mdiff, sdiff = divmod(rest, 60)
            button.config(text=f'Expanding {hdiff:02d}:{mdiff:02d}:{sdiff:02d}')
            button.after(1, watch_dumpworker)
        else:
            # dumpworker stopped
            dumpworker = None
            dumpstarttime = None
            button.config(text='Expand Data')
            logger.info('**** Expansion finished ****')
    

    def runbutton():
        global dumpworker
        global dumpstartepoch

        if dumpworker and dumpworker.is_alive():
            # dumpworker is running
            logger.warning('Expansion thread is already running')
            return

        # invoke dumpworker thread
        try:
            inputf = filepath.get()
            logger.info('input file: {}'.format(inputf))
            if not inputf:
                raise Exception('input file is Null')

            # generate output dirname
            output = re.sub('\.lst$', '.post', inputf)
            logger.info('output directory: {}'.format(output))

            if inputf == output:
                raise Exception('input and output have same name,'
                                'input file should have ".lst" suffix, currently')
            if use_old_parser_var.get():
                logger.info('Expand using old inline parser')
                dumpworker = OldDumpWorker(open(inputf, 'rt'), output)

            else:
                logger.info('Expand options')
                logger.info(f'--skip-verbose-textblock-output: {skip_verbose_textblockout_var.get()}')
                logger.info(f'--cascade-table-output: {cascade_table_output.get()}')
                logger.info(f'--abort-on-block-parse-error: {ignore_block_parse_error_var.get()}')
                logger.info('start expansion')

                dumpworker = DumpWorker(
                        open(inputf, 'rt'),
                        output,
                        config_dump_text_blocks = not skip_verbose_textblockout_var.get(),
                        config_cascade_table_output = cascade_table_output.get(),
                        config_ignore_block_parse_error=ignore_block_parse_error_var.get())
            # start thread and change text on the button
            dumpstartepoch = time.time()
            dumpworker.start()
            button.after(1, watch_dumpworker)

        except Exception as e:
            logger.error(str(e), exc_info=True)

    # run button
    button = tk.Button(app, text='Expand Data', command=runbutton)
    button.pack()

    # tab frame
    tab = tkinter.ttk.Notebook(app)
    tab.pack(expand=True, fill=tk.BOTH)

    # tab 1 - msgbox
    logtext = tk.scrolledtext.ScrolledText(app)
    logtext.pack(expand=True, fill=tk.BOTH)
    tab.add(logtext, text='Message')

    # tab 2 - options
    option = tk.Frame(app, padx=10, pady=10)
    tab.add(option, text='Options')

    # logging level
    logging_frame = tk.LabelFrame(option, text='Logging')
    logging_level_label = tk.Label(logging_frame, text='logging level')
    logging_level_var = tk.StringVar(logging_frame, 'WARNING')

    def on_logging_level(v):
        # dumper.logger.setLevel(logging.getLevelName(v))
        # old_dumper.logger.setLevel(logging.getLevelName(v))

        # set default logging level (affects on NOSET loggers)
        logging.getLogger().setLevel(v)

        logger.info(f'default logging level is {v}')

        # print all loggers
        # for name in logging.root.manager.loggerDict:
        #     lo = logging.getLogger(name)
        #     print(name, lo.getEffectiveLevel(), lo.propagate)

    logging_level = tk.OptionMenu(logging_frame, logging_level_var,
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', command=on_logging_level)
    logging_level_label.pack(side=tk.LEFT)
    logging_level.pack(side=tk.LEFT)

    logging_frame.pack(anchor=tk.W)

    # control option
    output_ctrl_frame = tk.LabelFrame(option, text='Output control')

    # --skip-verbose-textblock-output
    skip_verbose_textblockout_var = tk.BooleanVar(output_ctrl_frame, False)
    skip_verbose_textblockout = tk.Checkbutton(output_ctrl_frame,
            variable=skip_verbose_textblockout_var,
            text='Skip output of verbose text block')
    # --cascade-table-output
    cascade_table_label = tk.Label(output_ctrl_frame, text='Output form for large cascade data tables:')
    cascade_table_output = marlowe_ui.tktool.codedoptionmenu.CodedOptionMenu(
            output_ctrl_frame,
            options = [
                ('BUNDLE', 'BUNDLE: output as <root>/xxx_all.csv'),
                ('SEPARATE', 'SEPARATE: output as <root>/<each cascade>/xxx.csv'), 
                ('BOTH', 'BOTH: BUNDLE and SEPARATE')])
    cascade_table_output.set('BUNDLE')

    # --abort-on-block-parse-error
    ignore_block_parse_error_var = tk.BooleanVar(output_ctrl_frame, False)
    ignore_block_parse_error = tk.Checkbutton(output_ctrl_frame,
            variable=ignore_block_parse_error_var,
            text='Ignore errors during parsing each text block')

    # layout widgets
    skip_verbose_textblockout.pack(anchor=tk.W) 
    cascade_table_label.pack(anchor=tk.W)
    cascade_table_output.pack(anchor=tk.E) 
    ignore_block_parse_error.pack(anchor=tk.W)

    output_ctrl_frame.pack(anchor=tk.W, pady=5)

    # use old parser
    def on_use_old_parser():
        v = use_old_parser_var.get()
        if v:
            state = tk.DISABLED
        else:
            state = tk.NORMAL

        for c in output_ctrl_frame.winfo_children():
            c.config(state=state)

    use_old_parser_var = tk.BooleanVar(option, False)
    use_old_parser = tk.Checkbutton(option,
            variable=use_old_parser_var,
            text='Use old inline parser',
            command=on_use_old_parser)

    use_old_parser.pack(anchor=tk.W, pady=5)


    # bind logging handler
    logqueue = queue.Queue()
    h = marlowe_ui.logconsole.QueueHandler(logqueue)
    h.setFormatter(logging.Formatter('%(levelname)s %(name)s: %(message)s'))
    logging.getLogger().addHandler(h)
    # set WARING level as default logging level
    logging.getLogger().setLevel('WARNING')
    marlowe_ui.logconsole.LogConsoleBinder(logtext, logqueue)

    # set INFO level on this module only, which is not affected by logging.getLogger().setLevel()
    logger.setLevel(logging.INFO)
    logger.info('ml_post_ui is ready. Select input file to be expanded')

    app.mainloop()
