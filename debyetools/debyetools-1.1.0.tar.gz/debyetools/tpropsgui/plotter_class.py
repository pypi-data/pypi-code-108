import debyetools.tpropsgui.functions0 as fn
import PySimpleGUI as sg
sg.set_options(element_padding=(0, 0))

from matplotlib import pyplot as plt
plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"

class lines:
    def __init__(self,values):
        self.keys_list=[]
        for k in range(len(values['from_tab'])):
            self.keys_list.append('l'+str(k))
            setattr(self,'l'+str(k),{'from_tab':values['from_tab'][k], 'x':values['xs'][k], 'y':values['ys'][k], 'label':values['labels'][k]})

    def keys(self):
        return self.keys_list

class tabs:
    def __init__(self, tabs_multilinetxt):
        for tm in tabs_multilinetxt:
            setattr(self, tm, tabs_multilinetxt[tm])
    def keys(self):
        return list(self.__dict__.keys())

class dataplot:
    def __init__(self):
        pass
    def load_tab_data(self,tabs):
        self.tabs = tabs

        values=fn.values_from_tabs(self.tabs)
        self.lines=lines(values)

    def load_lines_settings(self,line_settings):
        self.lines_settings = line_settings
        for k in self.lines.keys():
            try:
                getattr(self.lines,k)['settings'] =line_settings[k]
            except:
                getattr(self.lines,k)['settings'] = {'plot':True,'label':0,'linestyle':'-','color':'gray','marker':'x','markerfacecolor':'gray','markeredgecolor':'cornflowerblue','linewidth':4,'markersize':8}

    def create_window(self,simple=False):
        if simple == True:
            print('simple_layout')
            layout = fn.simple_layout(self.lines)
        else:
            layout = fn.general_layout(self.lines)
        window = sg.Window('Plotting stuff...', layout, finalize=True)
        self.window=window

    def create_popupwindow(self):
        layout = fn.popup_layout(self.tabs)
        window = sg.Window('Edit data...', layout, finalize=True)
        self.popup_window=window

    def update_window(self, fig_settings):
        self.fig_settings=fig_settings
        for k in fig_settings.keys():
            self.window[k].update(fig_settings[k])

    def create_canvas(self,show=False):
        print('create_canvas show',show)

        self.fig = fn.plot_fig(self.fig_settings,self.lines,show=show)
        self.figure_canvas_agg = fn.draw_figure(self.window['--CANVAS2-'].TKCanvas, self.fig)

    def delete_fig_agg(self):
        self.figure_canvas_agg.get_tk_widget().forget()
        plt.close('all')

    def update_canvas(self,show=False):
        print('update_canvas show',show)

        self.delete_fig_agg()
        self.create_canvas(show=show)

    def increment_b_updn(self,event, values, incr, rdval):
        udstr = '_'+event.replace('_',' ').split()[-1]
        if udstr=='_UP':posneg=1
        elif udstr=='_DN':posneg=-1
        keywd = event.replace('--B_','').replace(udstr,'')
        counter = float(values[keywd])
        counter += posneg*incr
        self.window[keywd].update(round(counter,rdval))

    def update_formats(self):
        for k in self.fig_settings.keys():
            self.fig_settings[k]=self.window[k].get()

    def update_lines_settings(self):
        for l in list(self.window.key_dict.keys()):
            if l[:2]=='++':
                prp = l.replace('++',' ').split()
                li = getattr(self.lines,prp[-1])['settings']
                li[prp[0]]=self.window[l].get()

    def copy_multiline2dic(self,add=False):
        for l in list(self.popup_window.key_dict.keys()):
            if l[:2]=='||':
                prp = l.replace('||',' ').split()
                try:
                    getattr(self.tabs,prp[-1])['multiline'] = self.popup_window[l].get()
                except:
                    pass
        if add:
            setattr(self.tabs,'t'+str(int(prp[-1].replace('t',''))+1),{'multiline':'#new$~$Y(X)\n'})

    def update_lines(self):
        keys = self.lines.keys()
