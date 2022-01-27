from tkinter import *
from tkinter import ttk, messagebox
from bfit import logger_name
from bdata import bdata, bmerged
from bfit.gui.InputLine import InputLine

import bfit.backend.colors as colors
import numpy as np
import bdata as bd

import logging, textwrap


# =========================================================================== #
class fitline(object):
    """
        Instance variables

            bfit            pointer to top class
            data            fitdata object in bfit.data dictionary
            disable_entry_callback  disables copy of entry strings to
                                    dataline.bdfit parameter values
            gui_param_button ttk.Button, set initial parameters 
            lines           list of InputLine objects
            parent          pointer to parent object (frame)
            run_label       label for showing which run is selected
            run_label_title label for showing which run is selected
            fitframe        mainframe for this tab.
    """

    collist = ['p0', 'blo', 'bhi', 'res', 'dres-', 'dres+', 'chi', 'fixed', 'shared']

    # ======================================================================= #
    def __init__(self, bfit, parent, data, row):
        """
            Inputs:
                bfit:       top level pointer
                parent:     pointer to parent frame object
                dataline:   fetch_files.dataline object corresponding to the
                                data we want to fit
                row:        grid position
        """

        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing fit line for run %d in row %d',
                          data.run, row)

        # initialize
        self.bfit = bfit
        self.parent = parent
        self.data = data
        self.row = row
        self.disable_entry_callback = False
        self.lines = []

        data.fitline = self

        # get parent frame
        fitframe = ttk.Frame(self.parent, pad=(5, 0))

        frame_title = ttk.Frame(fitframe)

        # label for displyaing run number
        if type(self.data.bd) is bdata:
            self.run_label = Label(frame_title,
                            text='[ %d - %d ]' % (self.data.run,
                                                  self.data.year),
                           bg=colors.foreground, fg=colors.background)

        elif type(self.data.bd) is bmerged:
            runs = textwrap.wrap(str(self.data.run), 5)

            self.run_label = Label(frame_title,
                                text='[ %s ]' % ' + '.join(runs),
                                bg=colors.foreground, fg=colors.background)

        # title of run
        self.run_label_title = Label(frame_title,
                            text=self.data.title,
                            justify='right', fg=colors.red)

        # Parameter input labels
        gui_param_button = ttk.Button(fitframe, text='Initial Value',
                        command=lambda : self.bfit.fit_files.do_gui_param(id=self.data.id),
                        pad=0)
        result_comp_button = ttk.Button(fitframe, text='Result',
                        command=self.draw_fn_composition, pad=0)

        c = 0
        ttk.Label(fitframe, text='Parameter').grid(     column=c, row=1, padx=5); c+=1
        gui_param_button.grid(                          column=c, row=1, padx=5, pady=2); c+=1
        ttk.Label(fitframe, text='Low Bound').grid(     column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='High Bound').grid(    column=c, row=1, padx=5); c+=1
        result_comp_button.grid(                        column=c, row=1, padx=5, pady=2, sticky=(E, W)); c+=1
        ttk.Label(fitframe, text='Error (-)').grid(     column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='Error (+)').grid(     column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='ChiSq').grid(         column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='Fixed').grid(         column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='Shared').grid(        column=c, row=1, padx=5); c+=1
        
        self.run_label.grid(column=0, row=0, padx=5, pady=5, sticky=W)
        self.run_label_title.grid(column=2, row=0, padx=5, pady=5, sticky=E)
        frame_title.grid(column=0, row=0, columnspan=c, sticky=(E, W))
        frame_title.columnconfigure(1, weight=1)

        # save frame
        self.fitframe = fitframe
        self.gui_param_button = gui_param_button

        # resizing
        for i in range(c):
            self.fitframe.grid_columnconfigure(i, weight=1)

    # ======================================================================= #
    def __del__(self):

        # kill buttons and frame
        try:
            for child in self.parent.winfo_children():
                child.destroy()
        except Exception:
            pass

        if hasattr(self, 'parentry'):    del self.parentry
        
    # ======================================================================= #
    def get_new_parameters(self, force_modify=False):
        """
            Fetch initial parameters from fitter, set to data.

            plist: Dictionary of initial parameters {par_name:par_value}
        """
        
        # get pointer to fit files object
        fit_files = self.bfit.fit_files
        fitter = fit_files.fitter
        ncomp = fit_files.n_component.get()
        fn_title = fit_files.fit_function_title.get()

        # check if we are using the fit results of the prior fit
        values_res = None
        res = self.data.fitpar['res']
        
        isfitted = not all(res.isna()) # is this run fitted?
        
        if fit_files.set_prior_p0.get() and not isfitted:
            
            r = 0
            for data in self.bfit.data.values():
                isfitted = not all(data.fitpar['res'].isna()) # is the latest run fitted?
                if isfitted and data.run > r:
                    r = data.run
                    values_res = data.fitpar.copy()
        
        # get calcuated initial values
        try:
            values = fitter.gen_init_par(fn_title, ncomp, self.data.bd,
                                    self.bfit.get_asym_mode(fit_files))
        except Exception as err:
            print(err)
            self.logger.exception(err)
            return
                
        # set p0 from old
        if values_res is not None:
            for idx in values_res.index:
                if idx not in values.index:
                    values = values.append(values_res.loc[idx])
                    values.loc[idx, ['res', 'dres+', 'dres-', 'chi']] = np.nan
            values.loc[:, 'p0'] = values_res.loc[:, 'res']
        
        # set to data
        self.data.set_fitpar(values)
        
    # ======================================================================= #
    def grid(self, row):
        """Re-grid a dataline object so that it is in order by run number"""
        self.row = row
        self.fitframe.grid(column=0, row=row, sticky=(W, N))
        self.fitframe.update_idletasks()

    # ======================================================================= #
    def degrid(self):
        """Remove displayed dataline object from file selection. """

        self.logger.debug('Degridding fitline for run %s', self.data.id)
        self.fitframe.grid_forget()
        self.fitframe.update_idletasks()

    # ======================================================================= #
    def draw_fn_composition(self):
        """
            Draw window with function components and total
        """

        self.logger.info('Drawing fit composition for run %s', self.data.id)

        # get top objects
        fit_files = self.bfit.fit_files
        bfit = self.bfit

        # get fit object
        bdfit = self.data

        # get base function
        fn_name = fit_files.fit_function_title.get()

        # get number of components and parameter names
        ncomp = fit_files.n_component.get()
        pnames_single = fit_files.fitter.gen_param_names(fn_name, 1)
        pnames_combined = fit_files.fitter.gen_param_names(fn_name, ncomp)

        if '2' in bdfit.mode:
            fn_single = fit_files.fitter.get_fn(fn_name=fn_name, 
                            ncomp=1,
                            pulse_len=bdfit.pulse_s,
                            lifetime=bd.life[bfit.probe_species.get()])
            fn_combined = fit_files.fitter.get_fn(fn_name=fn_name, 
                            ncomp=ncomp,
                            pulse_len=bdfit.pulse_s,
                            lifetime=bd.life[bfit.probe_species.get()])
        else:
            fn_single = fit_files.fitter.get_fn(fn_name=fn_name, ncomp=1)
            fn_combined = fit_files.fitter.get_fn(fn_name=fn_name, ncomp=ncomp)

        # draw in redraw mode
        draw_mode = bfit.draw_style.get()
        bfit.draw_style.set('redraw')

        # draw the data
        bdfit.draw(bfit.get_asym_mode(fit_files), figstyle='fit', color='k')

        # get the fit results
        results = {par:bdfit.fitpar.loc[par, 'res'] for par in pnames_combined}

        # draw if ncomp is 1
        if ncomp == 1:
            bfit.draw_style.set('stack')
            bdfit.draw_fit('fit', unique=False, 
                           asym_mode=bfit.get_asym_mode(self.bfit.fit_files), 
                           label=fn_name)
            self.bfit.draw_style.set(draw_mode)
            return

        # draw baseline
        if 'baseline' in pnames_single:
            bfit.plt.axhline('fit', bdfit.id+'_base', results['baseline'], ls='--', zorder=6)

        # get x pts
        t, a, da = bdfit.asym(bfit.get_asym_mode(fit_files))
        fitx = np.linspace(min(t), max(t), fit_files.n_fitx_pts)

        # get x axis scaling
        if bdfit.mode in bfit.units:
            unit = bfit.units[bdfit.mode]
        else:
            fitxx = fitx

        # draw relative to peak 0
        if self.bfit.draw_rel_peak0.get():
            
            # get reference
            par = data.fitpar
            
            if 'peak_0' in par.index:   index = 'peak_0'
            elif 'mean_0' in par.index: index = 'mean_0'
            elif 'peak' in par.index:   index = 'peak'
            elif 'mean' in par.index:   index = 'mean'
            else:
                msg = "No 'peak' or 'mean' fit parameter found. Fit with" +\
                     " an appropriate function."
                self.logger.exception(msg)
                messagebox.error(msg)
                raise RuntimeError(msg)
            
            ref = par.loc[index, 'res']
            
            # do the shift
            fitxx = fitx-ref                    
            fitxx *= unit[0]
            xlabel = 'Frequency Shift (%s)' % unit[1]
            self.logger.info('Drawing as freq shift from peak_0')
        
        # ppm shift
        elif self.bfit.draw_ppm.get():
            
            # check div zero
            try:
                fitxx = 1e6*(fitx-self.bfit.ppm_reference)/self.bfit.ppm_reference
            except ZeroDivisionError as err:
                self.logger.exception(str(msg))
                messagebox.error(str(msg))
                raise err
            
            self.logger.info('Drawing as PPM shift with reference %s Hz', 
                             self.bfit.ppm_reference)
            xlabel = 'Frequency Shift (PPM)'
            
        else: 
            fitxx = fitx*unit[0]

        # draw the combined
        params = [results[name] for name in pnames_combined]

        bfit.plt.plot('fit', bdfit.id+'_comb', fitxx, fn_combined(fitx, *params),
                            unique=False, label='Combined', zorder=5)

        # draw each component
        for i in range(ncomp):

            # get parameters
            params = [results[single+'_%d'%i] \
                        for single in pnames_single if single != 'baseline']

            if 'baseline' in pnames_single:
                params.append(results['baseline'])

            # draw
            bfit.plt.plot('fit', bdfit.id+'_%d'%i, fitxx, fn_single(fitx, *params),
                            unique=False, ls='--', label='%s %d'%(fn_name, i), zorder=6)

        # plot legend
        bfit.plt.legend('fit')

        # reset to old draw mode
        bfit.draw_style.set(draw_mode)

    # ======================================================================= #
    def populate(self, force_modify=False):
        """
            Fill and grid new parameters. Reuse old fields if possible

            force_modify: if true, clear and reset parameter inputs.
        """

        # get data and frame
        fitframe = self.fitframe
        fitdat = self.data
        fit_files = self.bfit.fit_files
        pop_constr = fit_files.pop_fitconstr

        if force_modify:
            fitdat.reset_fitpar()
            
        # check if new data
        new_data = len(fitdat.fitpar.index) == 0
        
        # disable init button if constrained
        pop_constr.set_init_button_state(self)
                    
        # add constrained parameter and function
        pop_constr.add_new_par(fitdat)    
        pop_constr.add_fn(fitdat)
        
        # drop parameters which are no longer needed
        pop_constr.drop_unused_param(fitdat)
                
        # set new p0
        if force_modify or new_data:
            
            # make a new parameter dataframe
            try:
                self.get_new_parameters(force_modify)
            except KeyError as err:
                return          # returns if no parameters found
            except RuntimeError as err:
                messagebox.showerror('RuntimeError', err)
                raise err from None
        
        # get list of parameters and initial values
        fitdat.fitpar.sort_index(inplace=True)
        fitpar = fitdat.fitpar
        plist = tuple(fitpar.index.values)
        self.logger.debug('Populating parameter list with %s', plist)
        
        # get needed number of lines
        n_lines_total = len(plist)
        n_lines_current = len(self.lines)
        n_lines_needed = n_lines_total - n_lines_current
        
        # drop unneeded lines
        if n_lines_needed < 0:
            
            unused = self.lines[n_lines_total:]
            for rem in unused:
                rem.degrid()
                del rem
            self.lines = self.lines[:n_lines_total]

        # add new lines
        elif n_lines_needed > 0:
            self.lines.extend([InputLine(fitframe, self.bfit, fitdat) \
                                                for i in range(n_lines_needed)])

        # reassign and regrid lines
        for i, line in enumerate(self.lines):
            line.grid(i+2)
            
        # drop old parameters
        fitdat.drop_unused_param(plist)
        fitdat.fitpar.sort_index(inplace=True)
        fitpar = fitdat.fitpar
        
        # set parameters
        for i, k in enumerate(fitpar.index):
            self.lines[i].set(k, **fitpar.loc[k].to_dict())
                                     
    # ======================================================================= #
    def set(self, pname, **kwargs):
        """
            Set line columns
        """
        for line in self.lines:
            if line.pname == pname:
                line.set(**kwargs)
        
    # ======================================================================= #
    def show_fit_result(self):
        self.logger.debug('Showing fit result for run %s', self.data.id)

        try:
            data = self.data
        except KeyError:
            return
        
        try:
            chi = data.chi
        except AttributeError:
            return

        # show fit results
        for line in self.lines:
            values = {r: data.fitpar.loc[line.pname, r] for r in ('res', 'dres-', 'dres+')}
            values['chi'] = chi
            line.set(**values)

