import debyetools.tpropsgui.plotter_class as plotter
import numpy as np
import re
def find_rec_in_str(all_lines,pattrn):
    line2=str(all_lines)
    n=0
    ns=[]
    while len(all_lines)>0:
        if all_lines.find(pattrn)<0:
            break
        n = all_lines.find(pattrn)
        if len(ns)>=1:
            ns.append(ns[-1]+n+len(pattrn))
        else:
            ns.append(n)
        all_lines=all_lines[n+len(pattrn):]

    return ns

def pop_window(initial_tabs_multilinetxt,initial_lines_settings,initial_fig_settings,show=False):
    print('pop_window show',show)
    tabs = plotter.tabs(initial_tabs_multilinetxt)
    data4plot = plotter.dataplot()
    data4plot.load_tab_data(tabs)
    data4plot.load_lines_settings(initial_lines_settings)

    data4plot.create_window()
    data4plot.update_window(initial_fig_settings)
    data4plot.create_canvas(show=show)
    while True:
        event, values = data4plot.window.read()
        print('plot_event:',event)
        if event in (plotter.sg.WIN_CLOSED, '--B_close'):
            break

        elif event in ['--B_figwidth_UP','--B_figheight_UP','--B_figwidth_DN','--B_figheight_DN']:
            data4plot.increment_b_updn(event, values,0.1,1)
            data4plot.update_formats()
            data4plot.update_canvas(show=show)
        elif event in ['--B_titlesize_UP','--B_labelxsize_UP','--B_labelysize_UP','--B_titlesize_DN','--B_labelxsize_DN','--B_labelysize_DN','--B_legendncol_UP','--B_legendncol_DN','--B_legendfontsize_UP','--B_legendfontsize_DN']:
            data4plot.increment_b_updn(event, values,1,None)
            data4plot.update_formats()
            data4plot.update_canvas(show=show)
        elif event in ['--B_lmargin_UP','--B_rmargin_UP','--B_bmargin_UP','--B_tmargin_UP','--B_lmargin_DN','--B_rmargin_DN','--B_bmargin_DN','--B_tmargin_DN','--B_titlexpos_UP','--B_titlexpos_DN','--B_titleypos_UP','--B_titleypos_DN']:
            data4plot.increment_b_updn(event, values,0.01,2)
            data4plot.update_formats()
            data4plot.update_canvas(show=show)
        elif event in ['--B_limxmax_UP','--B_limxmin_UP','--B_limxmax_DN','--B_limxmin_DN','--B_limymax_UP','--B_limymin_UP','--B_limymax_DN','--B_limymin_DN']:
            data4plot.increment_b_updn(event, values,.1,2)
            data4plot.update_formats()
            data4plot.update_canvas(show=show)
        elif event in ['use_grid','use_legend','use_xlabel','use_ylabel','use_title','auto_xlim','auto_ylim']:
            data4plot.update_formats()
            data4plot.update_canvas(show=show)

        elif ('++plot++' in event or '--B_refresh' in event):
            data4plot.update_lines_settings()
            data4plot.update_formats()
            data4plot.update_canvas(show=show)

        elif ('++linewidth++'in event or '++markersize++'in event) :
            data4plot.increment_b_updn(event, values,1,None)
            data4plot.update_lines_settings()
            data4plot.update_formats()
            data4plot.update_canvas(show=show)
        elif event == '--B_loaddata':
            filename = plotter.sg.popup_get_file('Load Figure...')
            print(filename)
            with open(filename,'r') as f:
                lines=f.readlines()
                setting_dict = {}
                for line in lines:
                    if '->' in line[0:2] and '<-' in line[-3:-1]:
                        setting_dict[line[2:-3]]={}
                        last_keylvl0 = line[2:-3]
                        lvl = 0
                        continue
                    elif '*>' in line[0:2] and '<*' in line[-3:-1]:
                        setting_dict[last_keylvl0][line[2:-3]]={}
                        last_keylvl1 = line[2:-3]
                        lvl = 1
                        continue
                    if '*k>' in line[0:3]:
                        if lvl == 0:
                            ix0 = line.find('*k>')
                            ix1 = line.find('<k*')
                            jx0 = line.find('>|')
                            jx1 = line.find('|<')
                            val = line[jx0+2:jx1].replace('||newline','\n')
                            if val == 'True':
                                val=True
                            if val == 'False':
                                val=False
                            setting_dict[last_keylvl0][line[ix0+3:ix1]] = val
                        if lvl == 1:
                            ix0 = line.find('*k>')
                            ix1 = line.find('<k*')
                            jx0 = line.find('>|')
                            jx1 = line.find('|<')
                            val = line[jx0+2:jx1].replace('||newline','\n')
                            if val == 'True':
                                val=True
                            if val == 'False':
                                val=False
                            setting_dict[last_keylvl0][last_keylvl1][line[ix0+3:ix1]] = val

            data4plot.window.close()
            tabs = plotter.tabs(setting_dict['tabs_multilinetxt'])
            data4plot = plotter.dataplot()
            data4plot.load_tab_data(tabs)
            data4plot.load_lines_settings(setting_dict['lines_settings'])

            data4plot.create_window()
            data4plot.fig_settings=setting_dict['figure_settings']
            data4plot.update_window(setting_dict['figure_settings'])
            data4plot.create_canvas(show=show)

        elif event == '--B_savefig':

            filename = plotter.sg.popup_get_file('Save Figure',save_as=True)
            data4plot.fig.savefig(filename+".pdf")

            with open(filename+'.ftg','w') as f:
                f.write('->figure_settings<-\n')
                for k in data4plot.fig_settings.keys():
                    f.write('*k>'+k+'<k*'+">|"+str(data4plot.window[k].get())+'|<\n')

                f.write('->lines_settings<-\n')
                for l in data4plot.lines.keys_list:
                    f.write('*>'+l+'<*\n')
                    for k in getattr(data4plot.lines,l)['settings'].keys():
                        f.write('*k>'+k+'<k*'+">|"+str(getattr(data4plot.lines,l)['settings'][k])+'|<\n')

                f.write('->tabs_multilinetxt<-\n')
                for i,l in enumerate(data4plot.lines.keys_list):
                    f.write('*>t'+str(i)+'<*\n')
                    f.write('*k>'+'multiline<k*>|')
                    f.write('#X '+getattr(data4plot.lines,l)['label']+'||newline')
                    sm_array = np.array([getattr(data4plot.lines,l)['x'],getattr(data4plot.lines,l)['y']]).T
                    for line in sm_array:
                        f.write(str(line[0])+' '+str(line[1])+'||newline')
                    f.write('|<\n')

        elif '--B_editdata' == event:
            data4plot.create_popupwindow()

            while True:
                event2, values2 = data4plot.popup_window.read()
                print(event2)
                if event2 in ('--B_ok_w2',plotter.sg.WIN_CLOSED):
                    print('ok')
                    break

                if event2 == '--B_addtab_w2':
                    data4plot.copy_multiline2dic(add=True)
                    data4plot.popup_window.close()
                    data4plot.create_popupwindow()
                    data4plot.popup_window['--Tab_data_'+data4plot.tabs.keys()[-1]].select()
                    # print(data4plot.tabs.keys())

                if '--B_remove_t' in event2:
                    #print(event2.replace('_',' ').split()[2])
                    delattr(data4plot.tabs,event2.replace('_',' ').split()[2])
                    data4plot.copy_multiline2dic()
                    data4plot.popup_window.close()
                    data4plot.create_popupwindow()

            data4plot.copy_multiline2dic()
            data4plot.load_tab_data(data4plot.tabs)

            data4plot.load_lines_settings(data4plot.lines_settings)

            data4plot.window.close()
            data4plot.create_window()
            data4plot.update_window(data4plot.fig_settings)
            data4plot.create_canvas(show=show)

            data4plot.popup_window.close()

def pop_window_simple(initial_tabs_multilinetxt,initial_lines_settings,initial_fig_settings,show=False):
    print('pop_window_simple show',show)
    tabs = plotter.tabs(initial_tabs_multilinetxt)
    data4plot = plotter.dataplot()
    data4plot.load_tab_data(tabs)
    data4plot.load_lines_settings(initial_lines_settings)

    data4plot.create_window(simple=True)
    data4plot.fig_settings=initial_fig_settings
    data4plot.create_canvas(show=show)
    while True:
        event, values = data4plot.window.read()
        print('plotssimple:',event)
        if event in (plotter.sg.WIN_CLOSED, '--B_close'):
            break
        elif event == '--B_edit_fig':
            pop_window(initial_tabs_multilinetxt,initial_lines_settings,initial_fig_settings,show=show)

class fig:
    def __init__(self,xlabel, ylabel):
        self.colors = ['mediumpurple','gray','deepskyblue', 'purple','orchid','pink','aqua','cornflowerblue', 'C0']
        self.markers = ['s','+','x','o','^','>','1','<','2']
        self.initial_lines_settings = {}
        self.initial_fig_settings = {'figwidth':6,'figheight':4.5,'use_title':False,'title':'','titlexpos':.7,'titleypos':.9,
                                'titlesize':12,'use_xlabel':True,'use_ylabel':True,'xlabel':xlabel,'ylabel':ylabel,'labelxsize':12,
                                'labelysize':12,'auto_xlim':True,'auto_ylim':True,'limxmin':-0.5,'limxmax':110,'limymin':-1,'limymax':2,'use_legend':True,'legend_loc':'best',
                                'legendncol':1,'legendfontsize':10,'use_grid':True,'lmargin':0.11,'rmargin':0.98,'tmargin':0.95,'bmargin':0.12}

        self.tabs = []
        self.types = []
        self.len = 0
    def add_set(self, X, Y, label='Y', type='line'):
        tab3_str = '#T '+label+'\n'
        for Ti, Ci in zip(X, Y):
            tab3_str = tab3_str + '%.10e   %.10e  '%(Ti,Ci)+'\n'
        self.types.append(type)
        self.tabs.append(tab3_str)
        if type == 'line':
            linestyle = '-'
            marker = 'None'
        elif type == 'dash':
            linestyle = '--'
            marker = 'None'

        else:
            linestyle = 'None'
            marker = self.markers[self.len]
        self.initial_lines_settings['l'+str(self.len)] = {'plot':True,'label':0,'linestyle':linestyle,'color':self.colors[self.len],        'marker':marker,   'markerfacecolor':'None', 'markeredgecolor':self.colors[self.len],'linewidth':2,'markersize':10}
        self.len+=1
    def plot(self,show=False):
        print('plot show',show)
        self.initial_tabs_multilinetxt = {'t'+str(i):{'multiline':self.tabs[i]} for i in range(len(self.tabs))}
        pop_window_simple(self.initial_tabs_multilinetxt,self.initial_lines_settings,self.initial_fig_settings,show=show)
