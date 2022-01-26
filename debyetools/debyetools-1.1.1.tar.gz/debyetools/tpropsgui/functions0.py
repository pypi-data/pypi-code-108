import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#
import numpy as np
# import addcopyfighandler
#
legend_loc_list = ['best','upper right','upper left','lower left','lower right','right','center left','center right','lower center','upper center','center']
line_styles_list = ['-','--','-.',':','None']
colors_list = ['mediumpurple','purple','gray','orchid','deepskyblue', 'pink', 'darkkhaki', 'aqua','cornflowerblue','blue','green','red','C0','C1','C2','C3','C4']
markers_list=['.','o','+','x','1', '2', '3', '4','s','h','^', 'v','>', '<','*', '8', 'd', 'P', 'p', 'H','None']
#
def NewSpinner(init_val=None,width=None,key=None,tooltip=None):
    return [sg.Input(init_val, size=(width, 1), font='Any 10', justification='l', key=key,tooltip=tooltip),
    sg.Column([[sg.Button('▲', size=(1, 1), font='Any 7', border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key='--B_'+key+'_UP')],
               [sg.Button('▼', size=(1, 1), font='Any 7', border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key='--B_'+key+'_DN')]])]
#
def textSpinner(txt=None,init_val=None,width=None,key=None,tooltip=None):
    spinner = NewSpinner(init_val=init_val,width=width,key=key,tooltip=tooltip)
    return sg.Text(txt,key='--T_'+key), spinner[0], spinner[1]
#
def general_layout(lines):
    figwidth_spin = textSpinner(txt='  w: ',init_val='6',width=3,key='figwidth')
    figheight_spin = textSpinner(txt='  h: ',init_val='4',width=3,key='figheight')
    layout_figure = [[sg.Text('  Figure size: ',key='--T_figure_size'),
                      figwidth_spin[0],figwidth_spin[1],figwidth_spin[2], figheight_spin[0],figheight_spin[1],figheight_spin[2]]]

    titlesize_spin = textSpinner(txt='  font size: ',init_val='10',width=3,key='titlesize')
    titlexpos_spin = textSpinner(txt='  x: ',init_val='0.5',width=4,key='titlexpos')
    titleypos_spin = textSpinner(txt='  y: ',init_val='0.98',width=4,key='titleypos')
    layout_title = [[sg.Checkbox('use title', enable_events=True, key='use_title')],
                    [sg.Text('  title: ',key='--T_title'),sg.Input(size=(14, 1), justification='right', key='title'),
                     titlesize_spin[0],titlesize_spin[1],titlesize_spin[2]],
                    [sg.Text('  Position: ',key='--T_pos_title'),
                     titlexpos_spin[0],titlexpos_spin[1],titlexpos_spin[2], titleypos_spin[0],titleypos_spin[1],titleypos_spin[2]]]

    labelxsize_spin = textSpinner(txt='  font size: ',init_val='10',width=3,key='labelxsize')
    labelysize_spin = textSpinner(txt='  font size: ',init_val='10',width=3,key='labelysize')

    limxmin_spin = textSpinner(txt='  min: ',init_val='0',width=4,key='limxmin')
    limymin_spin = textSpinner(txt='  min: ',init_val='0',width=4,key='limymin')
    limxmax_spin = textSpinner(txt='  max: ',init_val='0',width=4,key='limxmax')
    limymax_spin = textSpinner(txt='  max: ',init_val='0',width=4,key='limymax')

    layout_axis = [[sg.Checkbox('use xlabel ', enable_events=True, key='use_xlabel'),sg.Checkbox('use ylabel ', enable_events=True, key='use_ylabel')],
                   [sg.Text('  xlabel: ',key='--T_x_label'),sg.Input(size=(14, 1), justification='right', key='xlabel'),
                   labelxsize_spin[0],labelxsize_spin[1],labelxsize_spin[2]],
                   [sg.Text('  ylabel: ',key='--T_y_label'),sg.Input(size=(14, 1), justification='right', key='ylabel'),
                   labelysize_spin[0],labelysize_spin[1],labelysize_spin[2]],
                   [sg.Checkbox('auto xlim ', enable_events=True, key='auto_xlim')],
                   [sg.Text('  xlim: ',key='--T_xlim'),
                    limxmin_spin[0],limxmin_spin[1],limxmin_spin[2], limxmax_spin[0],limxmax_spin[1],limxmax_spin[2]],
                   [sg.Checkbox('auto ylim ', enable_events=True, key='auto_ylim')],[
                    sg.Text('  ylim: ',key='--T_ylim'),
                    limymin_spin[0],limymin_spin[1],limymin_spin[2], limymax_spin[0],limymax_spin[1],limymax_spin[2]]]

    legendncol_spin     = textSpinner(txt='  columns: ',init_val='2',width=3,key='legendncol')
    legendfontsize_spin = textSpinner(txt='  font size: ',init_val='10',width=3,key='legendfontsize')
    layout_legend = [[sg.Checkbox('use legend ', enable_events=True, key='use_legend'),sg.Text('  location: ',key='--T_legend_loc'),
                      sg.InputCombo(values=legend_loc_list, size=(12,1), key='legend_loc')],
                     [legendncol_spin[0],legendncol_spin[1],legendncol_spin[2], legendfontsize_spin[0],legendfontsize_spin[1],legendfontsize_spin[2]]]
    layout_grid = [[sg.Checkbox('use grid ', enable_events=True, key='use_grid')]]

    lmargin_spin = textSpinner(txt='  left: ',init_val='0.18',width=4,key='lmargin')
    rmargin_spin = textSpinner(txt='  riht: ',init_val='0.98',width=4,key='rmargin')
    bmargin_spin = textSpinner(txt='  bottom: ',init_val='0.12',width=4,key='bmargin')
    tmargin_spin = textSpinner(txt='  top: ',init_val='0.95',width=4,key='tmargin')
    layout_margins = [[lmargin_spin[0],lmargin_spin[1],lmargin_spin[2], rmargin_spin[0],rmargin_spin[1],rmargin_spin[2],
                       bmargin_spin[0],bmargin_spin[1],bmargin_spin[2], tmargin_spin[0],tmargin_spin[1],tmargin_spin[2]]]

    layout_left = [[sg.Frame(title='Figure',layout=layout_figure,key='--Frame_figure')],
                   [sg.Frame(title='Title',layout=layout_title,key='--Frame_title')],
                   [sg.Frame(title='Axis',layout=layout_axis,key='--Frame_axis')],
                   [sg.Frame(title='Legend',layout=layout_legend,key='--Frame_legend')],
                   [sg.Frame(title='Grid',layout=layout_grid,key='--Frame_grid')],
                   [sg.Frame(title='Margins',layout=layout_margins,key='--Frame_margins')]]

    width_spin = {k:textSpinner(txt=' ',init_val=getattr(lines,k)['settings']['linewidth'],width=2,key='++linewidth++'+k,tooltip='line width') for k in lines.keys()}
    markersize_spin = {k: textSpinner(txt=' ', init_val=getattr(lines,k)['settings']['markersize'],width=2,key='++markersize++'+k,tooltip='marker size') for k in lines.keys()}
    layout_list_lines = [[sg.Checkbox(k, enable_events=True,key='++plot++'+k,default=getattr(lines,k)['settings']['plot']),\
                          sg.Text(' line: ',key='--T_lstyle_'+k),sg.InputCombo(values=line_styles_list, size=(2,1), key='++linestyle++'+k,tooltip='line style',default_value=getattr(lines,k)['settings']['linestyle']),\
                          sg.Text(' ',key='--T_color_'+k),sg.InputCombo(default_value=getattr(lines,k)['settings']['color'],values=colors_list, size=(12,1), key='++color++'+k,tooltip='line color'),\
                          width_spin[k][0],width_spin[k][1],width_spin[k][2],\
                          sg.Text(' marker: ',key='--T_marker_'+k),sg.InputCombo(values=markers_list, size=(2,1), key='++marker++'+k,tooltip='marker style',default_value=getattr(lines,k)['settings']['marker']),\
                          sg.Text(' ',key='--T_facecolor_'+k),sg.InputCombo(default_value=getattr(lines,k)['settings']['markerfacecolor'],values=colors_list, size=(12,1), key='++markerfacecolor++'+k,tooltip='marker face color'),\
                          sg.Text(' ',key='--T_edgecolor_'+k),sg.InputCombo(default_value=getattr(lines,k)['settings']['markeredgecolor'],values=colors_list, size=(12,1), key='++markeredgecolor++'+k,tooltip='marker edge color'),\
                          markersize_spin[k][0],markersize_spin[k][1],markersize_spin[k][2],\
                          ] for k in lines.keys()]
    layout_right = [[sg.Canvas(key='--CANVAS2-')],
                    [sg.Button('Refresh figure',key='--B_refresh'),sg.Button('Edit data',key='--B_editdata'),sg.Button('Save figure..',key='--B_savefig'),sg.Button('Load data...',key='--B_loaddata')],
                     [sg.Column(layout_list_lines,size=(600,150), scrollable=True,key='--Col_list_lines')],
                    ]

    layout = [[sg.Column(layout_left),sg.Text('    ',key='--T_sep_cols'),sg.Column(layout_right,element_justification='center')],
              [sg.Button('Close',key='--B_close')]]
    return layout

def simple_layout(lines):
    print('simple_layout')
    layout = [[sg.Canvas(key='--CANVAS2-')],
              [sg.Button('Edit Figure...',key='--B_edit_fig')]]
    return layout

def popup_layout(tabs):
    tabs_layout={'Data '+k: [[sg.Multiline(default_text=getattr(tabs,k)['multiline'], size=(30,10),key='||xy||'+k)],[sg.Button('Remove tab',key='--B_remove_'+k+'_w2')]] for k in tabs.keys()}
    tab_lst_layout = [sg.Tab('Data '+k, tabs_layout['Data '+k],key='--Tab_data_'+k) for k in tabs.keys()]
    return [[sg.TabGroup([tab_lst_layout],key='--TabGroup_xy')],
             [sg.Button('Add a tab',key='--B_addtab_w2'),sg.Button('OK',key='--B_ok_w2')]]
#
def plot_fig(saved_ins,lines,show=False):
    print('plt_fig show',show)

    fig = plt.figure()

    fig.set_figwidth(float(saved_ins['figwidth']))
    fig.set_figheight(float(saved_ins['figheight']))

    ax=fig.add_subplot(111)
    for key in lines.keys():
        linei = getattr(lines,key)
        if linei['settings']['plot']:
            ls=linei['settings']
            ax.plot(linei['x'],linei['y'],label =linei['label'], linestyle=ls['linestyle'],color=ls['color'],marker=ls['marker'],markerfacecolor=ls['markerfacecolor'],
                    markeredgecolor=ls['markeredgecolor'],linewidth=ls['linewidth'],markersize=ls['markersize'])

    if saved_ins['use_title']:
        ax.set_title(saved_ins['title'],x=float(saved_ins['titlexpos']),y=float(saved_ins['titleypos']),fontsize=saved_ins['titlesize'])

    if saved_ins['use_xlabel']:
        ax.set_xlabel(saved_ins['xlabel'],fontsize=saved_ins['labelxsize'])
    if saved_ins['use_ylabel']:
        ax.set_ylabel(saved_ins['ylabel'],fontsize=saved_ins['labelysize'])
    if not saved_ins['auto_xlim']:
        ax.set_xlim(left=float(saved_ins['limxmin']),right=float(saved_ins['limxmax']),auto=not saved_ins['auto_xlim'])
    if not saved_ins['auto_ylim']:
        ax.set_ylim(bottom=float(saved_ins['limymin']),top=float(saved_ins['limymax']),auto=not saved_ins['auto_ylim'])
    if saved_ins['use_legend']:
        ax.legend(loc=saved_ins['legend_loc'],ncol=int(saved_ins['legendncol']),fontsize=float(saved_ins['legendfontsize']))
    if saved_ins['use_grid']:
        ax.grid()
    fig.subplots_adjust(left=float(saved_ins['lmargin']), bottom=float(saved_ins['bmargin']), right=float(saved_ins['rmargin']), top=float(saved_ins['tmargin']), wspace=0, hspace=0)

    if show:
        plt.show()
    return fig
#
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
#
def multiline2arr(xy_values):
    lst = []
    vals_lst = (xy_values+'\n').replace('\n\n\n','\n').replace('\n\n','\n').split('\n')
    vals_lst = np.array(vals_lst)[np.where(''!=np.array(vals_lst))]
    ixi,ixf=0,-1
    label=''
    if '#' in vals_lst[0]:
        ixi=1
        label=vals_lst[0].replace('\t',' ').split()[1:]
        remove_rec(label,'')
    if '' == vals_lst[-1]:
        ixf=-1
    else:
        ixf=len(vals_lst)
    for li in vals_lst[ixi:ixf]:
        newli = li.replace('\t',' ').split()
        remove_rec(newli,'')
        lst.append([float(lii) for lii in newli])
    return np.array(lst), label
#
def remove_rec(list4removal,elmnt_2_remove):
    try:
        list4removal.remove(elmnt_2_remove)
    except:
        return
    remove_rec(list4removal,elmnt_2_remove)
#
def values_from_tabs(tabs):
    tabsids = list(tabs.keys())
    labels = [np.array(multiline2arr(getattr(tabs,k)['multiline'])[1]) for k in tabsids]
    values = [np.array(multiline2arr(getattr(tabs,k)['multiline'])[0]) for k in tabsids]
    xs=[]
    ys=[]
    ls=[]
    fromtabix=[]
    i,j=-1,-1
    for l,v,t in zip(labels,values,tabsids):
        i+=1
        if 0==np.size(v):
            v=np.array([v])
        #print(l,v)
        for li,vi in zip(l,v[:,1:].T):
            j+=1
            xs.append(v[:,0])
            ys.append(vi)
            ls.append(li)
            fromtabix.append(t)
    values = {'from_tab':fromtabix, 'labels':ls,'xs': xs, 'ys':ys}
    return values

def increment_b_updn(window,event,values,incr,rdval):
    udstr = '_'+event.replace('_',' ').split()[-1]
    if udstr=='_UP':posneg=1
    elif udstr=='_DN':posneg=-1
    keywd = event.replace('--B_','').replace(udstr,'')
    counter = float(values[keywd])
    counter += posneg*incr
    window[keywd].update(round(counter,rdval))
