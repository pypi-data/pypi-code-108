# Track which plots are active, which to draw in. 
# Derek Fujimoto
# June 2019

import matplotlib as mpl
import matplotlib.pyplot as plt

# =========================================================================== #
class PltTracker(object):
    """
        active:         dictionary, id number of active plot
        plots:          dictionary, list of plots drawn for type
    """
    
    # ======================================================================= #
    def __init__(self):
        
        # lists for tracking all plots 
        self.plots = {'inspect':[], 'data':[], 'fit':[], 'param':[], 'periodic':[]}
        
        # track the active plot 
        self.active = {'inspect':0, 'data':0, 'fit':0, 'param':0, 'periodic':0}
    
    # ======================================================================= #
    def _close_figure(self, event):
        """Remove figure from list"""
        
        # get number and style
        number = event.canvas.figure.number
        style = event.canvas.style
        
        # disconnect events
        event.canvas.mpl_disconnect(event.canvas.user_close)
        event.canvas.mpl_disconnect(event.canvas.user_active)
        
        # close the winow
        plt.figure(number).clf()
        plt.close(number)
        
        # remove from list 
        self.plots[style].remove(number)
        
        # reset active
        try:
            self.active[style] = self.plots[style][-1]
        except IndexError:
            self.active[style] = 0
                        
    # ======================================================================= #
    def _decorator(self, style, fn, *args, id=None, unique=True, **kwargs):
        """
            Function wrapper
            
            style: one of "data", "fit", "param"
            fn: matplotlib function to operate on 
            args: passed to fn
            kwargs: passed to fn
        """
        
        # switch 
        fig = plt.figure(self.active[style])
        
        if len(fig.axes) == 0:
            ax = fig.add_subplot()
        else:
            ax = fig.axes[0]
            
        # clear old objects
        if unique and id is not None:
            self._remove_drawn_object(ax, id)
        
        # run function 
        output = fn(*args, **kwargs)
        
        # track the drawn object
        if id is not None:
            ax.draw_objs.setdefault(id, []).append(output) 
        
        return output
    
    # ======================================================================= #
    def _remove_drawn_object(self, ax, draw_id):
        """
            Remove an object labelled by draw_id from the figure, based on draw 
            style.
        """
        color=None
        
        # check that objects exist
        if not hasattr(ax, 'draw_objs'):
            ax.draw_objs = {}
            return
        
        # check if id is present in drawn data
        if draw_id in ax.draw_objs.keys():

            # get item
            for item in ax.draw_objs[draw_id]:
            
                # remove line
                try:
                    item[0].remove()
                except TypeError:
                    item.remove()
                else: 
                    # remove errorbars
                    if type(item) == mpl.container.ErrorbarContainer:    
                        for i in item[1]:   i.remove()
                        for i in item[2]:   i.remove()
                        del ax.containers[ax.containers.index(item)]
                        
                    # remove lines
                    else:
                        try:
                            del ax.lines[ax.lines.index(item)]
                        except ValueError:
                            pass
                del item 
            
            # clear labels
            del ax.draw_objs[draw_id]
        
    # ======================================================================= #
    def _set_hover_annotation(self, fig, ax):
        """
            Setup the annotate object for mouse hover drawing
        """
        if not hasattr(ax, 'hover_annot'):
            ax.hover_annot = ax.annotate('', 
                             xy=(0, 0), 
                             xytext=(-3, 20), 
                             textcoords='offset points', 
                             ha='right', 
                             va='bottom', 
                             bbox=dict(boxstyle='round, pad=0.1', 
                                       fc='white', 
                                       alpha=0.1), 
                             arrowprops=dict(arrowstyle = '->', 
                                             connectionstyle='arc3, rad=0'), 
                             fontsize='xx-small', 
                            )    
        ax.hover_annot.set_visible(False)
        
        fig.canvas.mpl_connect("motion_notify_event", \
                               lambda x: self._show_annot_on_hover(x, fig, ax))
        
    # ======================================================================= #
    def _show_annot_on_hover(self, event, fig, ax):
        """
            If the cursor is near enough to the line, show the annotation. 
            
            Citation: https://stackoverflow.com/a/47166787
        """
        vis = ax.hover_annot.get_visible()
        if event.inaxes == ax:
            for line in ax.lines:        
                cont, ind = line.contains(event)
                if cont:
                    self._update_hover_annot(ind, line, ax)
                    fig.canvas.draw_idle()
                    break
                else:
                    if vis:
                        ax.hover_annot.set_visible(False)
                        fig.canvas.draw_idle()
        
    # ======================================================================= #
    def _update_active_id(self, event):
        """
            Update the active figure id based on click event.
        """
        number = event.canvas.figure.number
        style = event.canvas.style
        self.active[style] = number
    
    # ======================================================================= #
    def _update_hover_annot(self, ind, line, ax):
        """
            Update the hover annotation with that object's label.
            
            Citation: https://stackoverflow.com/a/47166787
        """
    
        i = ind["ind"][0]
        x, y = line.get_data()
        annot = ax.hover_annot
        annot.xy = (x[i], y[i])
        
        if hasattr(line, 'annot_label'):
            text = line.annot_label[i]
        else:
            text = line.get_label()
            
        annot.set_text(text)
        annot.set_backgroundcolor(line.get_color())
        annot.get_bbox_patch().set_alpha(0.4)
        annot.set_visible(True)
    
    # ======================================================================= #
    def annotate(self, style, id, *args, unique=True, **kwargs):
        return self._decorator(style, plt.annotate, *args, id=id, unique=unique, **kwargs)
    
    # ======================================================================= #
    def autoscale(self, style, enable=True, axis='both', tight=None):
        return self._decorator(style, plt.autoscale, enable=enable, axis=axis, 
                               tight=tight)
        
    # ======================================================================= #
    def axhline(self, style, id, *args, unique=True, **kwargs):
        return self._decorator(style, plt.axhline, *args, id=id, unique=unique, **kwargs)
        
    # ======================================================================= #
    def axvline(self, style, id, *args, unique=True, **kwargs):
        return self._decorator(style, plt.axvline, *args, id=id, unique=unique, **kwargs)
        
    # ======================================================================= #
    def clf(self, style):
        """Clear the figure for a given style"""
        out = self._decorator(style, plt.clf)
        ax = plt.gca()
        ax.draw_objs = {}
        
    # ======================================================================= # 
    def errorbar(self, style, id, x, y, yerr=None, xerr=None, fmt='', ecolor=None, 
                 elinewidth=None, capsize=None, barsabove=False, lolims=False, 
                 uplims=False, xlolims=False, xuplims=False, errorevery=1, 
                 capthick=None, *, data=None, unique=True, annot_label=None, 
                 **kwargs):
        """
            Plot data.
            
            style: one of "inspect", "data", "fit", or "param"
            annot_label: list of annotations for each point
            other arguments: defaults for matplotlib.pyplot.plot
        """
        
        # get active for this style
        active_style = self.active[style]
        
        # make new figure if needed 
        if active_style == 0:   
            self.figure(style)
            active_style = self.active[style]
        fig = plt.figure(active_style)
        
        try:
            ax = fig.axes[0]
        except IndexError:
            ax = fig.add_subplot()
        
        # track drawn objects    
        if not hasattr(ax, 'draw_objs'):
            ax.draw_objs = {}
        
        # redraw old objects and lines
        if unique:  self._remove_drawn_object(ax, id)
        self._remove_drawn_object(ax, 'line')
        
        # set up labelling of line objects for mouseover
        if 'label' in kwargs:
            label = kwargs.pop('label')
        else:
            label = ''
        
        # draw in active style 
        obj = ax.errorbar(x, y, yerr=yerr, xerr=xerr, fmt=fmt, ecolor=ecolor, 
                     elinewidth=elinewidth, capsize=capsize, 
                     barsabove=barsabove, lolims=lolims, uplims=uplims, 
                     xlolims=xlolims, xuplims=xuplims, errorevery=errorevery, 
                     capthick=capthick, data=data, **kwargs)

        # label the line object
        ax.lines[-1].set_label(label)
        
        # set the annotation
        if annot_label is not None: 
            ax.lines[-1].annot_label = annot_label
        elif style == 'inspect':
            annot_label = [f'({i:f}, {j:f})' for i, j in zip(x,y)]
            ax.lines[-1].annot_label = annot_label
            
            
        # save the drawn object to the file
        ax.draw_objs.setdefault(id, []).append(obj)
        
        return obj
    
    # ======================================================================= #
    def figure(self, style, **kwargs):
        """
            Make new figure.
            
            style: one of "data", "fit", or "param"
            kwargs: keyword arguments to pass to plt.figure
        """
        
        # make figure
        fig = plt.figure(**kwargs)
        
        # make events and save as canvas attribute
        fig.canvas.user_close = fig.canvas.mpl_connect('close_event', self._close_figure)
        fig.canvas.user_active = fig.canvas.mpl_connect('button_press_event', self._update_active_id)
        
        # set style
        fig.canvas.style = style
        
        # set window name 
        fig.canvas.manager.set_window_title('Figure %d (%s)' % (fig.number, style.title()))
        
        # update lists
        self.plots[style].append(fig.number)
        self.active[style] = fig.number
        
        # get axes
        if len(fig.axes) == 0:
            ax = fig.add_subplot()
        else:
            ax = fig.axes[0]
        
        # track drawn objects    
        if not hasattr(ax, 'draw_objs'):
            ax.draw_objs = {}
        
        # set up the hover annotations 
        self._set_hover_annotation(fig, ax)
        
        return fig

    # ======================================================================= #
    def gca(self, style):
        if not self.plots[style]: self.figure(style)
        return self._decorator(style, plt.gca)
    
    # ======================================================================= #
    def gcf(self, style):
        if not self.plots[style]: self.figure(style)
        return self._decorator(style, plt.gcf)
    
    # ======================================================================= #
    def legend(self, style, *args, **kwargs):
        self._decorator(style, plt.legend, *args, **kwargs)
        
    # ======================================================================= #
    def plot(self, style, id, *args, scalex=True, scaley=True, data=None, unique=True, **kwargs):
        """
            Plot data.
            
            style: one of "data", "fit", or "param"
            other arguments: defaults for matplotlib.pyplot.plot
        """
        
        # get active for this style
        active_style = self.active[style]
        
        # make new figure if needed 
        if active_style not in self.plots[style]:   
            self.figure(style)
        
        # draw in active style 
        fig = plt.figure(num=active_style)
        
        try:
            ax = fig.axes[0]
        except IndexError:
            ax = fig.add_subplot()
        
        # track drawn objects    
        if not hasattr(ax, 'draw_objs'):
            ax.draw_objs = {}
        
        # redraw old objects and lines
        if unique:  self._remove_drawn_object(ax, id)
        self._remove_drawn_object(ax, 'line')
        
        obj = ax.plot(*args, scalex=scalex, scaley=scaley, data=data, **kwargs)
        ax.draw_objs.setdefault(id, []).append(obj)
        
        return obj

    # ======================================================================= #
    def text(self, style, *args, id=None, unique=True, **kwargs):
        return self._decorator(style, plt.text, *args, id=id, unique=unique, **kwargs)

    # ======================================================================= #
    def tight_layout(self, style, *args, **kwargs):
        return self._decorator(style, plt.tight_layout, *args, **kwargs)

    # ======================================================================= #
    def xlabel(self, style, *args, **kwargs):
        return self._decorator(style, plt.xlabel, *args, **kwargs)
    
    # ======================================================================= #
    def xlim(self, style, *args, **kwargs):
        return self._decorator(style, plt.xlim, *args, **kwargs)
    
    # ======================================================================= #
    def xticks(self, style, *args, **kwargs):
        return self._decorator(style, plt.xticks, *args, **kwargs)
    
    # ======================================================================= #
    def ylabel(self, style, *args, **kwargs):
        return self._decorator(style, plt.ylabel, *args, **kwargs)
    
    # ======================================================================= #
    def ylim(self, style, *args, **kwargs):
        return self._decorator(style, plt.ylim, *args, **kwargs)
    
    # ======================================================================= #
    def yticks(self, style, *args, **kwargs):
        return self._decorator(style, plt.yticks, *args, **kwargs)
    
    # ======================================================================= #
    def zlabel(self, style, *args, **kwargs):
        return self._decorator(style, plt.zlabel, *args, **kwargs)
    
    # ======================================================================= #
    def zlim(self, style, *args, **kwargs):
        return self._decorator(style, plt.zlim, *args, **kwargs)
    
    # ======================================================================= #
    def zticks(self, style, *args, **kwargs):
        return self._decorator(style, plt.zticks, *args, **kwargs)
    
