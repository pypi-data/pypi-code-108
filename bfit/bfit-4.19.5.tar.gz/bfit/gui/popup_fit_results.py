# Model the fit results with a function
# Derek Fujimoto
# August 2019

from tkinter import *
from tkinter import ttk, messagebox
from functools import partial
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bfit import logger_name
from bfit.gui.template_fit_popup import template_fit_popup
from bfit.backend.raise_window import raise_window
from bfit.fitting.minuit import minuit

# ========================================================================== #
class popup_fit_results(template_fit_popup):
    """
        Popup window for modelling the fit results with a function
        
        chi_label:      Label, chisquared output
        fittab:         notebook tab
        new_par:        dataframe, index: parnames, columns: p0, blo, bhi, res, err
        
        output_par_text_val string, contents of output_par_text
        output_text_val     dict of strings, contents of output_text
       
        par:            list, fit results
        reserved_pars:  dict, keys: x, y vals: strings of parameter names
        
        text:           string, model text
        
        xaxis:          StringVar, x axis drawing/fitting parameter
        yaxis:          StringVar, y axis drawing/fitting parameter
        
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}

    window_title = 'Fit the results with a model'
    reserved_pars = ['x', 'y']

    # ====================================================================== #
    def __init__(self, bfit, input_fn_text='', output_par_text='', output_text='', 
                 chi=np.nan, x='', y=''):
        
        super().__init__(bfit, input_fn_text)
        super().show()
        
        self.fittab = bfit.fit_files
        self.output_par_text_val = output_par_text
        
        if not output_text:
            self.output_text_val = {}
        else:
            self.output_text_val = output_text
        
        # text for output
        output_frame = ttk.Frame(self.right_frame, relief='sunken', pad=5)
        output_head1_label = ttk.Label(output_frame, text='Par Name')
        output_head2_label = ttk.Label(output_frame, text='p0')
        output_head3_label = ttk.Label(output_frame, text='Bounds')
        output_head4_label = ttk.Label(output_frame, text='Result')
        output_head5_label = ttk.Label(output_frame, text='Error (-)')
        output_head6_label = ttk.Label(output_frame, text='Error (+)')
        self.output_par_text = Text(output_frame, width=8, height=8)
        self.output_text = {k:Text(output_frame, width=8, height=8, wrap='none')\
                            for k in ('p0', 'blo', 'bhi', 'res', 'err-', 'err+')}
        
        # default starter strings
        if self.output_par_text_val: 
            self.output_par_text.insert('1.0', self.output_par_text_val)
        self.output_par_text.config(state='disabled')
    
        if self.output_text_val: 
            for k in self.output_text_val:
                self.output_text[k].insert('1.0', self.output_text_val[k])

        # disable results
        for k in ('res', 'err-', 'err+'):
            self.output_text[k].config(state='disabled', width=12)

        # key bindings and scrollbar
        scrollb_out = Scrollbar(output_frame, command=self.yview)
        self.output_par_text['yscrollcommand'] = scrollb_out.set
        for k in self.output_text:
            self.output_text[k].bind('<KeyRelease>', self.get_result_input)
            self.output_text[k]['yscrollcommand'] = scrollb_out.set
                
        c = 0; r = 0;
        output_head1_label.grid(column=c, row=r);        c+=1;
        output_head2_label.grid(column=c, row=r);        c+=1;
        output_head3_label.grid(column=c, row=r, 
                                columnspan=2);          c+=2;
        output_head4_label.grid(column=c, row=r);        c+=1;
        output_head5_label.grid(column=c, row=r);        c+=1;
        output_head6_label.grid(column=c, row=r);        c+=1;
        
        c = 0; r += 1;
        self.output_par_text.grid(column=c, row=r, sticky=N); c+=1;
        for k in ('p0', 'blo', 'bhi', 'res', 'err-', 'err+'):
            self.output_text[k].grid(column=c, row=r, sticky=N); c+=1;
        
        # fitting button 
        fit_button = ttk.Button(self.right_frame, text='Fit', command=self.do_fit)
        
        
        # initialize
        self.new_par = pd.DataFrame(columns=['name', 'p0', 'blo', 'bhi', 'res', 'err-', 'err+']) 
        self.fittab = self.bfit.fit_files
        self.chi = chi
        
        # menus for x and y values
        axis_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        
        ttk.Label(  axis_frame, 
                    text='Variable definitions:\n', 
                    justify=LEFT).grid(column=0, row=0, columnspan=2, sticky=W)
        ttk.Label(axis_frame, text="x axis:").grid(column=0, row=1)
        ttk.Label(axis_frame, text="y axis:").grid(column=0, row=2)
        ttk.Label(axis_frame, text=' ').grid(column=0, row=3)
        
        self.xaxis = StringVar()
        self.yaxis = StringVar()
        
        if x:   self.xaxis.set(x)
        else:   self.xaxis.set(self.fittab.xaxis.get())
        
        if y:   self.yaxis.set(y)
        else:   self.yaxis.set(self.fittab.yaxis.get())
        
        self.xaxis_combobox = ttk.Combobox(axis_frame, textvariable=self.xaxis, 
                                      state='readonly', width=19)
        self.yaxis_combobox = ttk.Combobox(axis_frame, textvariable=self.yaxis, 
                                      state='readonly', width=19)
        
        self.xaxis_combobox['values'] = self.fittab.xaxis_combobox['values']
        self.yaxis_combobox['values'] = self.fittab.yaxis_combobox['values']
        
        # module names 
        module_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved module names:\n\n'
        
        maxk = max(list(map(len, list(self.modules.keys()))))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk), d) for k, d in self.modules.items()])
        s += '\n'
        modules_label = ttk.Label(module_frame, text=s, justify=LEFT)
        
        # chisquared output
        chi_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        self.chi_label = ttk.Label(chi_frame, 
                                    text='ChiSq: %.2f' % np.around(chi, 2), 
                                    justify=LEFT)
        
        # Text entry
        self.entry_label['text'] = 'Enter a one line equation using "x"'+\
                                 ' to model y(x)'+\
                                 '\nEx: "y = a*x+b"'
             
        # draw button
        button_draw = ttk.Button(self.right_frame, text='Draw', 
                                 command=self.draw_model, pad=1)
                
        # gridding
        modules_label.grid(column=0, row=0)
        self.chi_label.grid(column=0, row=0)
        self.xaxis_combobox.grid(column=1, row=1)
        self.yaxis_combobox.grid(column=1, row=2)
        
        axis_frame.grid(column=0, row=0, rowspan=1, sticky=(E, W), padx=1, pady=1)
        module_frame.grid(column=0, row=1, sticky=(E, W), padx=1, pady=1)
        chi_frame.grid(column=0, row=2, sticky=(E, W), padx=1, pady=1, rowspan=2)
        
        button_draw.grid(column=0, row=3, sticky=(E, W))
        
        # gridding
        scrollb_out.grid(row=r, column=c, sticky='nsew')
        output_frame.grid(column=0, row=1, sticky=(N, E, W, S), padx=1, pady=1)
        fit_button.grid(column=0, row=2, sticky=(N, E, W), padx=1, pady=1)
        
    # ====================================================================== #
    def _do_fit(self, text):
        
        # save model text
        self.text= text[-1]
        
        # get fit data
        xstr = self.xaxis.get()
        ystr = self.yaxis.get()
        
        # Make model
        parnames = self.output_par_text.get('1.0', END).split('\n')[:-1]
        parstr = ', '.join(parnames)
        eqn = text[-1].split('=')[-1]
        model = 'lambda x, %s : %s' % (parstr, eqn)
        
        self.logger.info('Fitting model %s for x="%s", y="%s"', model, xstr, ystr)
        self.model_fn = eval(model)
        npar = len(parnames)
        
        # set up p0, bounds
        p0 = self.new_par['p0'].values
        blo = self.new_par['blo'].values
        bhi = self.new_par['bhi'].values
        
        p0 = list(map(float, p0))
        blo = list(map(float, blo))
        bhi = list(map(float, bhi))
                    
        # get data to fit
        xvals, xerrs_l, xerrs_h = self._get_data(xstr)
        yvals, yerrs_l, yerrs_h = self._get_data(ystr)
        
        # minimize
        m = minuit(self.model_fn, xvals, yvals, 
                  dy = yerrs_h, 
                  dx = xerrs_h, 
                  dy_low = yerrs_l, 
                  dx_low = xerrs_l,
                  name = parnames,
                  print_level = 0,
                  limit = np.array([blo, bhi]).T,
                  start = p0,
                  )
        
        m.migrad()
        m.hesse()
        m.minos()
        
        # print fitting quality
        try:
            print(m.fmin)
            print(m.params)
            print(m.merrors)
        except UnicodeEncodeError:
            pass
        
        # get results
        par = m.values
        self.par = par
        n = len(m.merrors)
        
        if npar == 1:
            std_l = np.array([m.merrors[i].lower for i in range(n)])
            std_h = np.array([std_l])
        else:
            std_l = np.array([m.merrors[i].lower for i in range(n)])
            std_h = np.array([m.merrors[i].upper for i in range(n)])
            
        # chi2
        chi = m.chi2
        self.chi_label['text'] = 'ChiSq: %.2f' % np.around(chi, 2)
        self.chi = chi
        
        self.logger.info('Fit model results: %s, Errors-: %s, Errors+: %s', 
                        str(par), str(std_l), str(std_h))
        
        self.bfit.plt.figure('param')
        self.draw_data()
        self.draw_model()    
        
        return (par, std_l, std_h)
        
    # ====================================================================== #
    def _get_data(self, xstr):
        """
            Get data and clean
            
            xstr: label for data to fetch
        """
        
        # get data
        try:
            xvals, xerrs = self.fittab.get_values(xstr)
        except UnboundLocalError as err:
            self.logger.error('Bad input parameter')
            messagebox.showerror("Error", 'Bad input parameter')
            raise err
        except (KeyError, AttributeError) as err:
            self.logger.error('Parameter "%s not found for fitting', xstr)
            messagebox.showerror("Error", 'Parameter "%s" not found' % xstr)
            raise err
        
        # split errors    
        if type(xerrs) is tuple: 
            xerrs_l = xerrs[0]
            xerrs_h = xerrs[1]
        else:
            xerrs_l = xerrs
            xerrs_h = xerrs
        
        xvals = np.asarray(xvals)
        xerrs_l = np.asarray(xerrs_l)
        xerrs_h = np.asarray(xerrs_h)
                        
        # check errors 
        if all(np.isnan(xerrs_l)): xerrs_l = None
        if all(np.isnan(xerrs_h)): xerrs_h = None
        
        return (xvals, xerrs_l, xerrs_h)
    
    # ====================================================================== #
    def do_after_parse(self, defined, eqn, new_par):
        
        # add result
        try:
            new_par = np.unique(np.concatenate(new_par))
        except TypeError:
            return 
            
        for k in new_par:
            
            # bad input
            if not k: continue
            
            # set defaults
            if k not in self.new_par['name'].values:
                self.new_par = self.new_par.append({'name':k, **self.default_parvals}, 
                                                   ignore_index=True)
        
        # drop results 
        for i, k in zip(self.new_par.index, self.new_par['name']):
            if k not in new_par:
                self.new_par.drop(i, inplace=True)
        
        # set fields
        self.new_par.sort_values('name', inplace=True)
        self.set_par_text()
    
    # ====================================================================== #
    def do_fit(self, *args):
        """
            Set up the fit functions and do the fit. 
            Then map the outputs to the proper displays. 
        """
        
        # parse text
        self.do_parse()
        
        # clean input
        text = self.input_fn_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
        # check for no input
        if not text:    return
        
        try:
            # do the fit
            out = self._do_fit(text)
        except Exception as errmsg:
            raise errmsg from None
        
        # check if fit was success
        if out is None: 
            return 
        else:
            par, std_l, std_h  = out
    
        # display output for global parameters
        for i, j in enumerate(self.new_par.index):
            self.new_par.loc[j, 'res'] = par[i]
            self.new_par.loc[j, 'err-'] = std_l[i]
            self.new_par.loc[j, 'err+'] = std_h[i]
        self.set_par_text()
        
    # ======================================================================= #
    def draw_data(self):
        figstyle = 'param'
        
        # get draw components
        xstr = self.xaxis.get()
        ystr = self.yaxis.get()
        id = self.fittab.par_label.get()
        
        self.logger.info('Draw model fit data "%s" vs "%s"', ystr, xstr)

        # get data
        xvals, xerrs_l, xerrs_h = self._get_data(xstr)
        yvals, yerrs_l, yerrs_h = self._get_data(ystr)

        # sort by x values, check for empty arrays
        idx = np.argsort(xvals)
        xvals = np.asarray(xvals)[idx]
        yvals = np.asarray(yvals)[idx]
        
        if xerrs_h is not None:     xerrs_h = np.asarray(xerrs_h)[idx]
        if xerrs_l is not None:     xerrs_l = np.asarray(xerrs_l)[idx]
        if yerrs_h is not None:     yerrs_h = np.asarray(yerrs_h)[idx]
        if yerrs_l is not None:     yerrs_l = np.asarray(yerrs_l)[idx]
        
        if xerrs_h is None and xerrs_l is None:     xerrs = None
        else:                                       xerrs = (xerrs_l, xerrs_h)
        if yerrs_h is None and yerrs_l is None:     yerrs = None
        else:                                       yerrs = (yerrs_l, yerrs_h)
        
        # get mouseover annotation labels
        mouse_label, _ = self.fittab.get_values('Unique Id')
        mouse_label = np.asarray(mouse_label)[idx]

        #draw data
        self.bfit.plt.errorbar(figstyle, id, xvals, yvals, 
                                 yerr=yerrs, 
                                 xerr=xerrs, 
                                 fmt='.', 
                                 annot_label=mouse_label)

        # pretty labels
        xstr = self.fittab.fitter.pretty_param.get(xstr, xstr)
        ystr = self.fittab.fitter.pretty_param.get(ystr, ystr)
        
        # plot elements
        self.bfit.plt.xlabel(figstyle, xstr)
        self.bfit.plt.ylabel(figstyle, ystr)
        self.bfit.plt.tight_layout(figstyle)

        raise_window()

    # ======================================================================= #
    def draw_model(self):
        """Draw model line as stacked"""
        figstyle = 'param'
        
        self.logger.info('Draw model "%s"', self.text)
        
        # get fit function and label id
        fn = self.model_fn
        draw_id = self.fittab.par_label.get()
        
        # get default data_id
        if not draw_id and self.bfit.draw_style.get() == 'stack':
            ax = self.bfit.plt.gca(figstyle)
        
        # get x data
        xstr = self.xaxis.get()
        xvals, _, _ = self._get_data(xstr)
        
        # draw fit
        self.bfit.plt.gca('param')
        fitx = np.linspace(min(xvals), max(xvals), self.fittab.n_fitx_pts)
        f = self.bfit.plt.plot(figstyle, draw_id, fitx, fn(fitx, *self.par), 
                               color='k', label=self.text, unique=False)
        plt.show()
        raise_window()

    # ====================================================================== #
    def get_result_input(self, *args):
        """
            Set new_par row to match changes made by user
        """
    
        # get text
        try:
            text = {k : list(map(float, self.output_text[k].get('1.0', END).split('\n')[:-1])) \
                for k in self.output_text}
        # no update if blank
        except ValueError:
            return 
        
        # dataframe it
        try:
            text = pd.DataFrame(text)   
        # bad input
        except ValueError:
            return
        
        # get names of the parameters
        parnames = self.output_par_text.get('1.0', END).split('\n')[:-1]
        
        # update
        par = self.new_par.set_index('name')
        for i, name in enumerate(parnames):
            par.loc[name] = text.iloc[i]
        par.reset_index(inplace=True)
        self.new_par = par
        self.logger.debug('get_result_input: updated new_par')
    
    # ====================================================================== #
    def set_par_text(self):
        """
            Set the textboxes based on stored results in self.newpar
        """
        
        # get strings
        set_par = self.new_par.astype(str)
        
        # round
        numstr = '%'+('.%df' % self.bfit.rounding)
        for k in ('res', 'err-', 'err+'):
            set_par[k] = set_par.loc[:, k].apply(\
                    lambda x : numstr % np.around(float(x), self.bfit.rounding))
        
        # enable setting
        for k in ('res', 'err-', 'err+'):
            self.output_text[k].config(state='normal')
        self.output_par_text.config(state='normal')
        
        self.output_par_text.delete('1.0', END)
        self.output_par_text.insert(1.0, '\n'.join(set_par['name']))
        self.output_par_text_val = '\n'.join(set_par['name'])
        
        for k in self.output_text:
            self.output_text[k].delete('1.0', END)
            self.output_text[k].insert(1.0, '\n'.join(set_par[k]))
            self.output_text_val[k] = '\n'.join(set_par[k])
                
        # disable setting
        for k in ('res', 'err-', 'err+'):
            self.output_text[k].config(state='disabled')
        self.output_par_text.config(state='disabled')
        
    
