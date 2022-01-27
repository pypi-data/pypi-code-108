# Put a function on the active plot and adjust it's parameters with mouse buttons
# Derek Fujimoto
# April 2019

import bdata as bd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from bfit.fitting.functions import lorentzian # freq, peak, fwhm, amp
from bfit.fitting.functions import gaussian # freq, peak, fwhm, amp
from bfit.fitting.functions import bilorentzian # freq, peak, fwhm, amp
from bfit.fitting.functions import quadlorentzian # freq, nu_0, nu_q, eta, theta, 
                                                  # phi, amp0, amp1, amp2, amp3, 
                                                  #  fwhm0, fwhm1, fwhm2, fwhm3, I
from bfit.fitting.functions import pulsed_exp # time, lambda_s, amp
from bfit.fitting.functions import pulsed_strexp # time, lambda_s, beta, amp
from bfit.fitting.functions import qp_nu # nu_0, nu_q, eta, theta, phi, I, m

from functools import partial

class FunctionPlacer(object):
    
    npts = 1000  # number of points used to draw line
    
    # ======================================================================= #
    def __init__(self, fig, data, fn_single, ncomp, p0, fnname, endfn, asym_mode, 
                base=0, spin=2):
        """
            fig:    pointer to matplotlib figure object to draw in
            data:   bdata object 
            fn:     function to draw and get the parameters for
            p0:     dictionary of StringVar corresponding to input parameters
            endfn:  function pointer to function to call at end of sequence. 
                        Called with no inputs
            asym_mode: asymmetry calcuation type (c, sl_c, or dif_c)
            base:   value of the baseline when we're not altering it
            spin:   nuclear spin of probe I
        
            fn needs input parameters with keys: 
            
                1F/2E/1W
                    peak, fwhm, amp, base OR 
                    
                20/2H
                    amp, lam, beta (optional)
        """
        # save input
        self.fig = fig
        self.ncomp = ncomp
        self.base = base
        self.fn = lambda x, **kwargs : fn_single(x, **kwargs)+self.base
        self.fname = fnname
        self.endfn = endfn
        x = data.asym(asym_mode)[0]
        self.x = np.linspace(min(x), max(x), self.npts)
        self.spin = spin
        
        # get axes for drawing
        self.ax = fig.axes
        if len(self.ax) == 0:
            self.ax = fig.add_subplot(111)
        else:
            self.ax = self.ax[0]
        
        # get ylims
        ylims = self.ax.get_ylim()
    
        # make list of initial paramters 
        self.p0 = [{k:float(p[k].get()) for k in p.keys() if 'base' not in k} for p in p0]
    
        # baseline 
        if self.fname in ('Lorentzian', 'Gaussian', 'BiLorentzian', 'QuadLorentz'):
            self.base = float(p0[0]['base'].get())
            y = np.ones(len(self.x))*self.base
            self.baseline = self.ax.plot(self.x, y, zorder=20, ls='--', label='Baseline')[0]
        else:
            self.base = 0
            self.baseline = dummybaseline()
    
        # draw each line with initial parameters
        self.lines = [self.ax.plot(self.x, 
                                   fn_single(self.x, **self.p0[i])+self.base, 
                                   zorder=20, ls='--', 
                                   label='Component %d' % i)[0] for i in range(ncomp)]
        
        # make and draw function for the sum 
        self.sumfn = lambda x: np.sum([fn_single(x, **p) for p in self.p0], axis=0)+self.base
        self.sumline = self.ax.plot(self.x, self.sumfn(self.x), zorder=21, ls='-',
                                    label='Sum')[0]
        
        # reset ylims
        self.ax.set_ylim(ylims)
        
        # make title 
        self.ax.set_title('Press enter to save parameters', fontsize='small')
        self.ax.legend(fontsize='x-small')
        self.fig.tight_layout()
        
        # connect enter key
        self.fig.canvas.mpl_connect('key_release_event', self.do_end)
        
        # resonance measurements ----------------------------------------------
        if self.fname in ('Lorentzian', 'Gaussian'):
            
            # if points are not saved they are garbage collected
            self.list_points = {'peak':[], 'fwhm':[]}
            
            # make points
            for i, (p, line) in enumerate(zip(self.p0, self.lines)):
                peakpt, widthpt = self.run_1f_single(p, line, 'C%d'%(i+1))
                self.list_points['peak'].append(peakpt)
                self.list_points['fwhm'].append(widthpt)
        
            self.list_points['base'] = self.run_1f_base(self.list_points['fwhm'], 'C0')
        
        elif self.fname == 'BiLorentzian':
            
            # if points are not saved they are garbage collected
            self.list_points = {'peak':[], 'fwhm':[]}
            
            # make points
            for i, (p, line) in enumerate(zip(self.p0, self.lines)):
                peakpt, widthpt = self.run_1f_bi_single(p, line, 'C%d'%(i+1))
                self.list_points['peak'].append(peakpt)
                self.list_points['fwhm'].append(widthpt)
        
            self.list_points['base'] = self.run_1f_base(self.list_points['fwhm'], 'C0')
        
        elif self.fname == 'QuadLorentz':
            
            # if points are not saved they are garbage collected
            self.list_points = {'peak0':[], 'peak1':[], 'peak2':[], 'peak3':[], 'fwhm':[], }
            
            # make points
            for i, (p, line) in enumerate(zip(self.p0, self.lines)):
                ppt0, ppt1, ppt2, ppt3, widthpt = self.run_1f_quad_single(p, line, 'C%d'%(i+1))
                self.list_points['peak0'].append(ppt0)
                self.list_points['peak1'].append(ppt1)
                self.list_points['peak2'].append(ppt2)
                self.list_points['peak3'].append(ppt3)
                self.list_points['fwhm'].append(widthpt)
            self.list_points['base'] = self.run_1f_quad_base(self.p0[0], self.list_points['fwhm'], 'C0')
            
        # SLR measurements ----------------------------------------------------
        elif self.fname in ('Exp', 'Str Exp'):
            
            # if points are not saved they are garbage collected
            self.list_points = {'amp':[], 'lam':[]}
            
            if self.fname == 'Str Exp':
                self.list_points['beta'] = []
            
            # make points
            for i, (p, line) in enumerate(zip(self.p0, self.lines)):
                self.list_points['amp'].append(self.run_20_initial(p, line, 'C%d'%i))
                self.list_points['lam'].append(self.run_20_lambda(p, line, 'C%d'%i))
                
                if self.fname == 'Str Exp':
                    self.list_points['beta'].append(self.run_20_beta(p, line, 'C%d'%i))
            
            # connect point shifter
            self.fig.canvas.mpl_connect('button_release_event', self.shift_20_pts_resize)
            
    # ======================================================================= #
    def run_1f_base(self, widths, color):
        """
            widths: list of points for widths, need to update y values
        """
        
        def update_base(x, y):
            
            # base point
            oldbase = self.base
            self.base = y
            for i in range(len(self.p0)):
                self.p0[i]['amp'] -= oldbase-y
            
            # update width points
            for p0, wpoint, line in zip(self.p0, widths, self.lines): 
                wpoint.point.set_ydata(self.fn(p0['peak']+p0['fwhm']/2, **p0))
                
                # update other lines
                line.set_ydata(self.fn(self.x, **p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            
            # update baseline line
            self.baseline.set_ydata(np.ones(self.npts)*self.base)    
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        xpt = self.ax.get_xticks()[-1]
        return DraggablePoint(self, update_base, xpt, 
                                 self.base, 
                                 color=color, setx=False)
    
    # ======================================================================= #
    def run_1f_single(self, p0, line, color):
        
        # make point for width
        def update_width(x, y):
            
            # width point
            p0['fwhm'] = abs(p0['peak']-x)*2
            
            # update line
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        x = p0['peak']+p0['fwhm']/2
        widthpt = DraggablePoint(self, update_width, x, self.fn(x, **p0), 
                                 color=color, sety=False)
        
        # make point for peak
        def update_peak(x, y):
        
            # peak point
            p0['amp'] = self.base-y
            p0['peak'] = x
        
            # width point
            x2 = x+p0['fwhm']/2
            widthpt.point.set_xdata(x2)
            widthpt.point.set_ydata(self.fn(x2, **p0))
            
            # update line
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
        
        peakpt = DraggablePoint(self, update_peak, p0['peak'], 
                                self.base-p0['amp'], color=color)
        
        return (peakpt, widthpt)
    
    # ======================================================================= #
    def run_1f_bi_single(self, p0, line, color):
        
        # make point for width
        def update_width(x, y):
            
            # width point
            p0['fwhm'] = abs(p0['peak']-x)*2
            
            # update line
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        x = p0['peak']+p0['fwhm']/2
        widthpt = DraggablePoint(self, update_width, x, self.fn(x, **p0), 
                                 color=color, sety=False)
        
        # make point for peak
        def update_peak(x, y):
        
            # peak point
            p0['amp'] = self.base-y
            p0['peak'] = x
        
            # width point
            x2 = x+p0['fwhm']/2
            widthpt.point.set_xdata(x2)
            widthpt.point.set_ydata(self.fn(x2, **p0))
            
            # update line
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
        
        peakpt = DraggablePoint(self, update_peak, p0['peak'], 
                                self.base-p0['amp'], color=color)
        
        return (peakpt, widthpt)
     
    # ======================================================================= #
    def run_1f_quad_base(self, p0, widths, color):
        """
            widths: list of points for widths, need to update y values
        """
        peak0 = qp_nu(p0['nu_0'], p0['nu_q'], p0['eta'], p0['theta'], p0['phi'], \
                          self.spin, -1)
        
        def update_base(x, y):
            
            # base point
            oldbase = self.base
            self.base = y
        
            for i in range(len(self.p0)):
                self.p0[i]['amp0'] -= oldbase-y
                self.p0[i]['amp1'] -= oldbase-y
                self.p0[i]['amp2'] -= oldbase-y
                self.p0[i]['amp3'] -= oldbase-y
            
            # update width points
            for p0, wpoint, line in zip(self.p0, widths, self.lines): 
                wpoint.point.set_ydata(self.fn(peak0+p0['fwhm']/2, **p0))
                
                # update other lines
                line.set_ydata(self.fn(self.x, **p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            
            # update baseline line
            self.baseline.set_ydata(np.ones(self.npts)*self.base)    
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        xpt = self.ax.get_xticks()[-1]
        
        return DraggablePoint(self, update_base, xpt, 
                                 self.base, 
                                 color=color, setx=False)
        
    # ======================================================================= #
    def run_1f_quad_single(self, p0, line, color):
        """
            p0 keys: 'amp0', 'amp1', 'amp2', 'amp3', 'eta', 'phi', 'theta', 'fwhm', 'nu_0', 'nu_q'
        """
        
        # lorentzian fn: lorentzian # freq, peak, width, amp
        s = self.spin
        
        # peak locations from right to left
        peak = lambda i: qp_nu(p0['nu_0'], p0['nu_q'], p0['eta'], p0['theta'], \
                               p0['phi'], s, i-s+1)
        
        # set width
        x = peak(0)+p0['fwhm']/2
        widthpt = DraggablePoint(self, None, x, self.fn(x, **p0), 
                                 color=color, sety=False)
        
        # set peak and amplitudes
        peakpts = []
        for n in range(2*s):
            x = p0['nu_0'] + peak(n) - (peak(s+1-n)+peak(n))/2
            
            y = self.base - \
                p0['amp%d'%n] + \
                sum([lorentzian(peak(n), 
                                peak(i%(2*s)), 
                                p0['fwhm'], 
                                p0['amp%d'%(i%(2*s))]) for i in range(n+1, 2*s+n)])                    
            
            if n in (0, 2*s-1):
                peakpts.append(DraggablePoint(self, None, x, y, color=color, marker='s'))
            else:
                peakpts.append(DraggablePoint(self, None, x, y, color=color, marker='^', setx=False))
            
        # make point for width
        def update_width(x, y):
                        
            # width point
            p0['fwhm'] = abs(peak(0)-x)*2
            
            # update line
            line.set_ydata(self.fn(self.x, **p0))
            
            # update peak heights
            for i in range(2*s):
                peakpts[i].point.set_ydata(self.fn(peak(i), **p0))
            
            # update width y 
            widthpt.point.set_ydata(self.fn(x, **p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    

        # make point for peak, updating nu_0
        def update_peak_center(x, y, n):
            
            # peak point
            p0['amp%d'%n] = self.base - y + \
                        sum([lorentzian(peak(n), 
                                        peak(i%(2*s)), 
                                        p0['fwhm'], 
                                        p0['amp%d'%(i%(2*s))]) for i in range(n+1, 2*s+n)])
            
            # width point        
            x2 = peak(0)+p0['fwhm']/2
            widthpt.point.set_ydata(self.fn(x2, **p0))
        
            # update the other peak points
            for i in range(n+1, 2*s+n):
                peakpts[i%(2*s)].point.set_ydata(self.fn(peak(i%(2*s)), **p0))
            
            # update line
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
        
        # make point for peak, updating nu_q 
        def update_peak_edge(x, y, n):
            
            # amplitude
            p0['amp%d'%n] = self.base - y + \
                        sum([lorentzian(peak(n), 
                                        peak(i%(2*s)), 
                                        p0['fwhm'], 
                                        p0['amp%d'%(i%(2*s))]) for i in range(n+1, 2*s+n)])
            
            # get x and n of the other edge peak position
            other_n = 2*s-n-1
            other_x = float(peakpts[other_n].point.get_xdata())
            
            # set nu_0
            p0['nu_0'] = (other_x+x)/2
            
            # set nu_q
            # Equation (28)
            V_0 = np.sqrt(1.5) * 0.5 * (3 * np.square(np.cos(p0['theta'])) \
                        - 1 + p0['eta'] * np.square(np.sin(p0['theta'])) * \
                        np.cos(2 * p0['phi']))
                        
            # Equation (23)
            p0['nu_q'] = (x-p0['nu_0']) / ((np.sqrt(6) / 3) * (1 - 2 * (n-s+1)) * V_0)  
            
            # width point        
            x2 = peak(0)+p0['fwhm']/2
            widthpt.point.set_xdata(x2)
            widthpt.point.set_ydata(self.fn(x2, **p0))
        
            # update the other peak points
            for i in range(1, 2*s-1):
                peakpts[i].point.set_xdata(peak(i))
                peakpts[i].point.set_ydata(self.fn(peak(i), **p0))
            peakpts[other_n].point.set_ydata(self.fn(other_x, **p0))
            
            # update line
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sum line
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
        
        widthpt.updatefn = update_width
        peakpts[0].updatefn = partial(update_peak_edge, n=0)
        peakpts[2*s-1].updatefn = partial(update_peak_edge, n=2*s-1)
        for i in range(1, 2*s-1):
            peakpts[i].updatefn = partial(update_peak_center, n=i)
        
        return (*peakpts, widthpt)
        
    # ======================================================================= #
    def run_20_initial(self, p0, line, color):
        def update(x, y):
            # initial asymmetry
            p0['amp'] = max(0, y)
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        return DraggablePoint(self, update, 0, p0['amp'], 
                              color=color, setx=False)
    
    # ======================================================================= #
    def run_20_lambda(self, p0, line, color):
        def update(x, y):
            # 1/T1
            p0['lam'] = max(0, 1/x)
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        x = np.ones(1)/p0['lam']
        ylim = self.ax.get_ylim()[0]
        y = min([i for i in self.ax.get_yticks() if i>ylim])
        return DraggablePoint(self, update, x, y, 
                              color=color, sety=False)
    
    # ======================================================================= #
    def run_20_beta(self, p0, line, color):
        def update(x, y):
    
            # beta - put y axis on a range of 0 to 1
            ylo, yhi = self.ax.get_ylim()
            y = (y-ylo)/(yhi-ylo)
            p0['beta'] = y
            line.set_ydata(self.fn(self.x, **p0))
            
            # update sumline
            self.sumline.set_ydata(self.sumfn(self.x))
            self.fig.canvas.draw()    
             
        # return so matplotlib doesn't garbage collect
        ylo, yhi = self.ax.get_ylim()
        xlo, xhi = self.ax.get_xlim()
        x = max([i for i in self.ax.get_xticks() if i < xhi])
        return DraggablePoint(self, update, x, p0['beta']*(yhi-ylo)+ylo, 
                              color=color, setx=False)
    
    # ======================================================================= #
    def shift_20_pts_resize(self, event):
        """Move the points so they fit in the screen"""
        
        xlo, xhi = self.ax.get_xlim()
        ylo, yhi = self.ax.get_ylim()
        
        for lam in self.list_points['lam']:
            ypos = lam.point.get_ydata()
            lam.point.set_ydata(min([i for i in self.ax.get_yticks() if i>ylo]))
        
        if 'beta' in self.list_points.keys():
            for beta in self.list_points['beta']:
                xpos = beta.point.get_xdata()
                beta.point.set_xdata(max([i for i in self.ax.get_xticks() if i<xhi])) 
    
    # ======================================================================= #
    def do_end(self, event):
        if event.key == 'enter':
            plt.close(self.fig.number)
            self.endfn(self.p0, self.base)
        
class dummybaseline(object):
    def __init__(self):pass
    def set_ydata(self, y) : pass
                
class DraggablePoint:

    # http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
    # https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points
    
    lock = None #  only one can be animated at a time
    size=0.01

    # ======================================================================= #
    def __init__(self, parent, updatefn, x, y, setx=True, sety=True, color=None, marker='s'):
        """
            parent: parent object
            updatefn: funtion which updates the line in the correct way
                updatefn(xdata, ydata)
            x, y: initial point position
            setx, sety: if true, allow setting this parameter
            color: point color
        """
        self.parent = parent
        self.point = parent.ax.plot(x, y, zorder=25, color=color, alpha=0.5, 
                                 marker=marker, markersize=8)[0]
        
        self.point.set_pickradius(8)
        self.updatefn = updatefn
        self.setx = setx
        self.sety = sety
        self.press = None
        self.background = None
        self.connect()
        
    # ======================================================================= #
    def connect(self):
        """connect to all the events we need"""
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    # ======================================================================= #
    def on_press(self, event):
        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        DraggablePoint.lock = self
        
    # ======================================================================= #
    def on_motion(self, event):

        if DraggablePoint.lock is not self: return
        if event.inaxes != self.point.axes: return
        
        # get data
        x = event.xdata
        y = event.ydata
        
        # move the point
        if self.setx:   self.point.set_xdata(x)
        if self.sety:   self.point.set_ydata(y)

        # update the line
        self.updatefn(x, y)        

    # ======================================================================= #
    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self: return
        DraggablePoint.lock = None
        
    # ======================================================================= #
    def disconnect(self):

        'disconnect all the stored connection ids'

        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
