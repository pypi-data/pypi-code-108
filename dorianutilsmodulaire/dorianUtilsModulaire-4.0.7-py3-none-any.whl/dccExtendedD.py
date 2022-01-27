import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash
import dash_daq as daq
from dash.dependencies import Input, Output, State

from dateutil import parser
import re,datetime as dt, numpy as np
from dorianUtils.utilsD import Utils

class DccExtended:
    def __init__(self):
        self.utils=Utils()
        self.line_styles = ['default','lines+markers','stairs','markers','lines']
        self.graphTypes = ['scatter','area','area %']
        self.stdStyle = {'fontsize':'12 px','width':'120px','height': '40px','min-height': '1px',}
        self.smallStyle = {'fontsize':'12 px','width':'180px','height': '40px','min-height': '1px',}
        self.verysmallStyle = {'fontsize':'12 px','width':'60px','height': '40px','min-height': '1px',}
        self.blockGreen = {"border":"0.25em green solid","padding":"0.25em","margin":"0.25em"}
        self.blockRed = {"border":"0.25em red solid","padding":"0.25em","margin":"0.25em"}
        self.blockBlue = {"border":"0.25em blue solid","padding":"0.25em","margin":"0.25em"}
        self.id_modalLog='log_modal'


    ''' dropdown with a list or dictionnary. Dictionnary doesn"t work for the moment '''
    def dropDownFromList(self,idName,listdd,pddPhrase = None,defaultIdx=None,labelsPattern=None,**kwargs):
        if not pddPhrase :
            pddPhrase = 'Select your ... : ' + idName
        p = html.P(pddPhrase)
        if labelsPattern :
            ddOpt= [{'label': re.findall(labelsPattern,t)[0], 'value': t} for t in listdd]
        else :
            ddOpt =[{'label': t, 'value': t} for t in listdd]

        if 'value' in list(kwargs.keys()):
            dd = dcc.Dropdown(id=idName,options=ddOpt,clearable=False,**kwargs)
        else :
            if not defaultIdx:
                defaultIdx = 0
            if 'value' in list(kwargs.keys()):
                del kwargs['value']
            dd = dcc.Dropdown(id=idName,options=ddOpt,value=listdd[defaultIdx],clearable=False,**kwargs)
        return [p,dd]

    def dropDownFromDict(self,idName,listdd,pddPhrase = None,valIdx=None,**kwargs):
        if not pddPhrase :
            pddPhrase = 'Select your ... : ' + idName
        p = html.P(pddPhrase)
        if isinstance(listdd,dict):
            keysDict= list(listdd.keys())
            valDict = list(listdd.values())
            ddOpt =[{'label': k, 'value': v} for k,v in listdd.items()]

        if 'value' in list(kwargs.keys()):
            dd = dcc.Dropdown(id=idName,options=ddOpt,clearable=False,**kwargs)
        elif valIdx:
            valSel = [list(listdd.values())[k] for k in valIdx]
            # print(valSel)
            dd = dcc.Dropdown(id=idName,options=ddOpt,value=valSel,clearable=False,**kwargs)
        else :
            dd = dcc.Dropdown(id=idName,options=ddOpt,clearable=False,**kwargs)
        return [p,dd]

    def quickInput(self,idName,typeIn='text',pddPhrase = 'input',dftVal=0,**kwargs):
        p = html.P(pddPhrase),
        inp = dcc.Input(id=idName,placeholder=pddPhrase,type=typeIn,value=dftVal,**kwargs)
        return [p,inp]

    def timeRangeSlider(self,id,t0=None,t1=None,**kwargs):
        if not t0 :
            t0 = parser.parse('00:00')
        if not t1 :
            t1 = t0+dt.timedelta(seconds=3600*24)
        maxSecs=int((t1-t0).total_seconds())
        rs = dcc.RangeSlider(id=id,
        min=0,max=maxSecs,
        # step=None,
        marks = self.utils.buildTimeMarks(t0,t1,**kwargs)[0],
        value=[0,maxSecs]
        )
        return rs

    def dDoubleRangeSliderLayout(self,baseId='',t0=None,t1=None,formatTime = '%d - %H:%M',styleDBRS='small'):
        if styleDBRS=='large':
            style2 = {'padding-bottom' : 50,'padding-top' : 50,'border': '13px solid green'}
        elif styleDBRS=='small':
            style2 = {'padding-bottom' : 10,'padding-top' : 10,'border': '3px solid green'}
        elif styleDBRS=='centered':
            style2 = {'text-align': 'center','border': '3px solid green','font-size':'18'}

        if not t0:
            t0 = parser.parse('00:00')
        if not t1:
            t1 = t0 + dt.timedelta(seconds=3600*24*2-1)
        p0      = html.H5('fixe time t0')
        in_t0   = dcc.Input(id=baseId + 'in_t0',type='text',value=t0.strftime(formatTime),size='75')
        in_t1   = dcc.Input(id=baseId + 'in_t1',type='text',value=t1.strftime(formatTime),size='75')
        p       = html.H5('select the time window :',style={'font-size' : 40})
        ine     = dcc.Input(id=baseId + 'ine',type='text',value=t0.strftime(formatTime))
        rs      = self.timeRangeSlider(id=baseId + 'rs',t0=t0,t1=t1,nbMarks=5)
        ins     = dcc.Input(id=baseId + 'ins',type='text',value=t1.strftime(formatTime))
        pf      = html.H5('timeselect start and end time ', id = 'pf',style={'font-size' : 60})
        dbrsLayout = html.Div([
                            dbc.Row([dbc.Col(p0),
                                    dbc.Col(in_t0),
                                    dbc.Col(in_t1)],style=style2,no_gutters=True),
                            dbc.Row(dbc.Col(p),style=style2,no_gutters=True),
                            dbc.Row([dbc.Col(ine),
                                    dbc.Col(rs,width=9),
                                    dbc.Col(ins)],
                                    style=style2,
                                    no_gutters=True),
                            ])
        return dbrsLayout

    def parseLayoutIds(self,obj,debug=False):
        c = True
        objs,queueList,k = {},[],0
        while c:
            if debug : k=k+1;print(k)
            if isinstance(obj,list):
                if debug : print('listfound')
                if len(obj)>1 : queueList.append(obj[1:])
                obj = obj[0]
            elif hasattr(obj,'id'):
                if debug : print('id prop found')
                objs[obj.id]=obj
                obj='idfound'
            elif hasattr(obj,'children'):
                if debug : print('children found')
                obj=obj.children
            elif not queueList:
                if debug : print('queue list empty')
                c=False
            else :
                if debug : print('iterate over queue list')
                obj = queueList.pop()
        print('\n'.join(list(objs.keys())))
        return objs

    def autoDictOptions(self,listWidgets):
        dictOpts = {}
        d1 = {k : 'value' for k in listWidgets if bool(re.search('(in_)|(dd_)', k))}
        d2 = {k : 'n_clicks' for k in listWidgets if bool(re.search('btn_', k))}
        d3 = {k : 'figure' for k in listWidgets if bool(re.search('graph', k))}
        d4 = {k : 'children' for k in listWidgets if bool(re.search('fileInCache', k))}
        for d in [d1,d2,d3,d4] :
            if not not d : dictOpts.update(d)
        return dictOpts

    def build_dbcBasicBlock(self,widgets,rows,cols,ws=None):
        dbc_rows,k = [],0
        if not ws : ws = [12/cols]*cols
        for r in range(rows):
            curRow=[]
            for c,w in zip(range(cols),ws) :
                # print(k,'******',widgets[k])
                curRow.append(dbc.Col(widgets[k],width=w))
                k+=1
            dbc_rows.append(curRow)
        return html.Div([dbc.Row(r) for r in dbc_rows])

    def basicComponents(self,dicWidgets,baseId=''):
        widgetLayout,dicLayouts = [],{}
        for wid_key,wid_val in dicWidgets.items():
            if 'dd_cmap'==wid_key:
                widgetObj = self.dropDownFromList(
                    baseId+wid_key,self.utils.cmapNames[0],'colormap : ',value=wid_val)

            elif 'dd_resampleMethod'==wid_key:
                widgetObj = self.dropDownFromList(baseId+wid_key,wid_val['methods'],
                    'resampling method: ',value=wid_val['value'],multi=False)

            elif 'dd_style'==wid_key:
                widgetObj = self.dropDownFromList(baseId+wid_key,self.line_styles,'style : ',value = wid_val)

            elif 'dd_typeGraph'==wid_key:
                widgetObj = self.dropDownFromList(baseId+wid_key,self.graphTypes,
                            'type graph : ',value=wid_val,
                            style=self.stdStyle,optionHeight=20)

            elif 'btn_export'==wid_key:
                widgetObj = [html.Button('export .csv',id=baseId+wid_key, n_clicks=wid_val),
                            dcc.Download(id=baseId + "dl")]

            elif 'btn_update'==wid_key:
                widgetObj = [html.Button('update',id=baseId+wid_key, n_clicks=wid_val)]

            elif 'check_button'==wid_key:
                widgetObj = [dcc.Checklist(id=baseId+wid_key,options=[{'label': wid_val, 'value': wid_val}])]

            elif 'btns_refresh'==wid_key:
                btnstyle = {'font-size':'30px','padding':'0px 16px','margin':'10px','display':'inline-block'}
                btnstyle2 = {'font-size':'18px','padding':'10px 25px','display':'inline-block'}
                instyle = btnstyle.copy()
                for k,v in zip(['font-size','padding','width'],['20px','0px 0px','120px']):instyle[k]=v
                widgetObj = [
                dbc.Row([
                    dbc.Col(html.Button('update',id=baseId+'btn_update', n_clicks=0,style=btnstyle2)),
                    # dbc.Col(html.Button('refresh',id=baseId+'btn_freeze', n_clicks=0,style=btnstyle2))
                    dbc.Col(daq.ToggleSwitch(id=baseId+'ts_freeze',value=False,label='Refresh mode',color='blue')),
                    ]),
                dbc.Row([
                    dbc.Col([
                        html.Button('-',id=baseId+'btn_freeze'+'-', n_clicks=0,style=btnstyle),
                        dcc.Input(id=baseId+'in_addtime',value=60,max=60*60,min=0,type='number',style=instyle),
                        html.Button('+',id=baseId+'btn_freeze'+'+', n_clicks=0,style=btnstyle),
                        dcc.Store(id=baseId+'st_freeze'),
                        ])
                    ])
                ]

            elif 'in_timeRes'==wid_key:
                widgetObj = [html.P('time resolution : '),
                dcc.Input(id=baseId+wid_key,placeholder='time resolution : ',type='text',value=wid_val)]
                widgetObj = [self.build_dbcBasicBlock(widgetObj,2,1)]

            elif 'in_heightGraph'==wid_key:
                widgetObj = [html.P('heigth of graph: '),
                dcc.Input(id=baseId+wid_key,type='number',value=wid_val,max=3000,min=400,step=5,style=self.stdStyle)]
                widgetObj = [self.build_dbcBasicBlock(widgetObj,2,1)]

            elif 'in_axisSp'==wid_key :
                widgetObj = [html.P('space between axis: '),
                dcc.Input(id=baseId+wid_key,type='number',value=wid_val,max=1,min=0,step=0.01,style=self.stdStyle)]
                widgetObj = [self.build_dbcBasicBlock(widgetObj,2,1)]

            elif 'in_hspace'==wid_key :
                widgetObj = [html.P('horizontal space: '),
                dcc.Input(id=baseId+wid_key,type='number',value=wid_val,max=1,min=0,step=0.01,style=self.stdStyle)]
                widgetObj = [self.build_dbcBasicBlock(widgetObj,2,1)]

            elif 'in_vspace'==wid_key :
                widgetObj = [html.P('vertical space: '),
                dcc.Input(id=baseId+wid_key,type='number',value=wid_val,max=1,min=0,step=0.01,style=self.stdStyle)]
                widgetObj = [self.build_dbcBasicBlock(widgetObj,2,1)]

            elif 'interval'==wid_key :
                widgetObj = [dcc.Interval(id=baseId + wid_key,interval=wid_val*1000,n_intervals=0)]

            elif 'pdr_time'==wid_key :
                if not wid_val :
                    wid_val={}
                    tmax = dt.datetime.now()
                    tmin = tmax-dt.timedelta(days=2*30)
                else :
                    tmax = self.utils.findDateInFilename(wid_val['tmax'])-dt.timedelta(seconds=1)
                    tmin = self.utils.findDateInFilename(wid_val['tmin'])
                t1 = tmax
                t0 = t1
                timeFormat='%Y-%m-%d'
                t0 = t0.strftime(timeFormat)
                t1 = t1.strftime(timeFormat)
                widgetObj = [
                html.Div([
                    dbc.Row([dbc.Col(html.P('select start and end time : ')),
                        dbc.Col(html.Button(id  = baseId + wid_key + 'Btn',children='update'))]),

                    dbc.Row([dbc.Col(dcc.DatePickerRange(id = baseId + 'pdr_date',
                                # max_date_allowed = t1,
                                initial_visible_month = t0,
                                display_format = 'D-MMM-YY',minimum_nights=0,persistence=False,
                                start_date = t0, end_date = t1))]),

                    dbc.Row([dbc.Col(dcc.Input(id = baseId + wid_key + 'Start',type='text',value = '09:00',size='13',style={'font-size' : 13})),
                            dbc.Col(dcc.Input(id = baseId + wid_key + 'End',type='text',value = '18:00',size='13',style={'font-size' : 13}))
                        ]),
                    dcc.Interval(id=baseId + wid_key + 'Interval',n_intervals=0,interval=60*60*1000)
                ])]

            elif 'block_refresh'==wid_key:
                inStyle = {'fontsize':'1em','width':'5em','display':'inline-block','float':'right'}
                txtStyle = {'fontsize':'1em','width':'10em','display':'inline-block'}
                interval = dcc.Interval(id=baseId + 'interval',interval=wid_val['val_refresh']*1000,n_intervals=0)

                timeWindow=[
                    html.P('time window (in min): ',style=txtStyle),
                    dcc.Input(id=baseId+'in_timeWindow',placeholder='refresh Time in seconds: ',type='number',
                        max=10000000,min=wid_val['min_window'],step=1,value=wid_val['val_window'],style=inStyle)
                            ]

                refreshTime = [
                    html.P('refresh time (in s): ',style=txtStyle),
                    dcc.Input(id=baseId+'in_refreshTime',placeholder='refresh Time in seconds: ',type='number',
                        max=10000000,min=wid_val['min_refresh'],step=1,value=wid_val['val_refresh'],style=inStyle)
                            ]

                timeBlock = html.Div([
                                dbc.Row([dbc.Col(refreshTime)]),
                                dbc.Row([dbc.Col(timeWindow)])],
                                style=self.blockGreen)
                widgetObj = [interval,timeBlock]

            elif wid_key =='block_graphSettings':
                blockSettings = self.basicComponents({
                                            'dd_cmap':wid_val['colmap'],
                                            'dd_style':wid_val['style'],
                                            'dd_typeGraph':wid_val['type'],
                                            },baseId)
                widgetObj = [html.Div([self.build_dbcBasicBlock(blockSettings,3,2)],style=self.blockRed)]

            elif wid_key =='block_colstyle':
                cmStyle = {'fontsize':'1em','width':'5em','display':'inline-block','float':'right'}
                stStyle = {'fontsize':'1em','width':'9em','display':'inline-block','float':'right'}
                txtStyle = {'fontsize':'1em','width':'6em','display':'inline-block'}

                coldd =[
                    html.P('colormap : ',style=txtStyle),
                    dcc.Dropdown(id=baseId+'dd_cmap',
                            options=[{'label':t,'value':t} for t in self.utils.cmapNames[0]],
                            value=wid_val['colmap'],style=cmStyle)
                            ]
                styledd =[
                    html.P('style : ',style=txtStyle),
                    dcc.Dropdown(id=baseId+'dd_style',
                            options=[{'label':t,'value':t} for t in self.line_styles],
                            value=wid_val['style'],style=stStyle)
                            ]

                widgetObj = [html.Div([
                                dbc.Row([dbc.Col(coldd)]),
                                dbc.Row([dbc.Col(styledd)])
                                ],style=self.blockRed)]

            elif wid_key == 'block_resample':
                ddStyle = {'fontsize':'1em','width':'5em','display':'inline-block','float':'right'}
                ddStyleMethods = {'fontsize':'1em','width':'15em'}
                inStyle = {'fontsize':'1em','width':'3em','display':'inline-block','float':'right'}
                txtStyle = {'fontsize':'1em','width':'10em','display':'inline-block'}

                timeRes = [
                    html.P('time resolution: ',style=txtStyle),
                    dcc.Input(id=baseId+'in_timeRes',placeholder='time resolution : ',type='text',
                            value=wid_val['val_res'],style=inStyle)
                        ]
                resampleMethod = [
                    html.P('resampling method: ',style=txtStyle),
                    dcc.Dropdown(id=baseId+'dd_resampleMethod',options=[{'value':t,'label':t} for t in wid_val['methods']],
                        value=wid_val['val_method'],clearable=False,style=ddStyleMethods)
                        ]

                widgetObj = [html.Div([
                                dbc.Row([dbc.Col(timeRes)]),
                                dbc.Row([dbc.Col(resampleMethod)])
                                ],style=self.blockBlue)]

            elif wid_key == 'block_multiAxisSettings':
                blockSettings = self.basicComponents({
                                            'in_heightGraph':900,
                                            'in_axisSp':0.02,
                                            'in_hspace':0.05,
                                            'in_vspace':0.05,
                                            },baseId)
                widgetObj = [self.build_dbcBasicBlock(blockSettings,2,2)]

            else :
                print('component ',wid_key,' is not available')
                return

            for widObj in widgetObj:widgetLayout.append(widObj)
        return widgetLayout

    def buildGraphLayout(self,widgetLayout,baseId,widthG=85):
        import plotly.graph_objects as go
        config={
                'displaylogo': False
                }
        fig = self.utils.addLogo(go.Figure())
        graphObj = dcc.Graph(id=baseId+'graph',config = config,figure=fig)
        graphLayout=[html.Div(graphObj,style={"width": str(widthG)+"%", "display": "inline-block"})]
        return [html.Div(widgetLayout,style={"width": str(100-widthG) + "%", "float": "left"})]+graphLayout

    def createTabs(self,tabs):
        return [dbc.Tabs([dbc.Tab(t.tabLayout,label=t.tabname) for t in tabs])]

    def addModalLog(self,app,titleBtn,mdFile):
        f = open(mdFile)
        t = dcc.Markdown(f.readlines())
        f.close()
        logModal = html.Div([
                dbc.Button(titleBtn, id=self.id_modalLog + "_btn", n_clicks=0),
                dbc.Modal([
                    dbc.ModalHeader("Log versionning"),
                    dbc.ModalBody(t),
                    dbc.ModalFooter(dbc.Button("Close", id=self.id_modalLog + "_close", className="ml-auto", n_clicks=0)),
                    ],
                    id=self.id_modalLog,
                    is_open=False,
                    size='xl',
                ),
            ]
        )
        @app.callback(
            Output(self.id_modalLog, "is_open"),
            Input(self.id_modalLog + "_btn", "n_clicks"),
            Input(self.id_modalLog + "_close", "n_clicks"),
            State(self.id_modalLog, "is_open")
        )
        def showLog(n1, n2, is_open):
            if n1 or n2:
                return not is_open
            return is_open

        return logModal

    def addModalError(self,app,cfg,baseid=''):
        baseid = baseid+'error_modal'
        errorHeader = dbc.ModalHeader(id=baseid +'_header',children='')
        errorBody   = dbc.ModalBody(id=baseid +'_body',children='')
        errorStore  = dcc.Store(id = baseid  + '_store',data=0)
        errorFooter = dbc.ModalFooter(dbc.Button("Close",id = baseid  + "_close",
                                                className="ml-auto", n_clicks=0))
        errorModal  = html.Div([
            dbc.Modal([
                errorHeader,
                errorBody,
                errorFooter
                ],
            id = baseid,
            is_open=False,
            # size='xl',
            ),
            errorStore
        ])
        @app.callback(
            Output(baseid, "is_open"),
            Output(baseid + "_header", "children"),
            Output(baseid + "_body", "children"),
            Input(baseid + "_store", "data"),
            Input(baseid + "_close", "n_clicks"),
        )
        def showError(d,n):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            if d>0 and not trigId=='error_modal_close':
                if d==1:
                    errorHeader = 'NO DATA COULD BE LOADED'
                    errorBody = html.Div([
                        html.P('''no available data for that time range,
                            please select among the available dates : ''')]+
                        [html.P(k) for k in cfg.parkedDays[::-1]]
                            )
                elif d==2:
                    errorHeader = 'NO TAGS'
                    errorBody = 'No tags found for this comibnation/category. Please select another category.'
                return True,errorHeader,errorBody
            else:
                return False,'',''

        return errorModal


    ''' dropdown with a list'''
    class DropdownFromList(dcc.Dropdown):
        def __init__(self,listdd,**kwargs):
            dcc.Dropdown.__init__(self,**kwargs)
            self.options = [{'label': t, 'value': t} for t in listdd]
