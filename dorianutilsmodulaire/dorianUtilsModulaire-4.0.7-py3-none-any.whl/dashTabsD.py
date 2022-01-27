import datetime as dt, pickle, time
import os,re,sys
import pandas as pd,numpy as np
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px, plotly.graph_objects as go
from dorianUtils.dccExtendedD import DccExtended
from dorianUtils.utilsD import Utils

class TabMaster():
    '''
    - cfg: ConfigFiles object
    - loadData,plotgraph and updateLayoutGraph are functions
    '''
    def __init__(self,app,cfg,loadData,plotData,tabname,update_fig=None,baseId='tab_'):
        self.utils = Utils()
        self.dccE = DccExtended()
        self.initialDateMethod = 'parkedData'
        self.app = app
        self.cfg = cfg
        self.loadData   = loadData
        self.plotData   = plotData
        if not update_fig==None:
            self.update_fig = update_fig
        self.tabname    = tabname
        self.baseId     = baseId
        self.modalError = self.dccE.addModalError(app,cfg,baseid=self.baseId)

    def _define_basicCallbacks(self,categories=[]):
        #update freeze button
        if 'ts_freeze' in categories:
            @self.app.callback(
                Output(self.baseId + 'ts_freeze', 'label'),
                Output(self.baseId + 'st_freeze', 'data'),
                Output(self.baseId + 'interval', 'disabled'),
                Input(self.baseId + 'ts_freeze','value'),
                Input(self.baseId + 'btn_freeze+','n_clicks'),
                Input(self.baseId + 'btn_freeze-','n_clicks'),
                State(self.baseId + 'in_addtime','value'),
                State(self.baseId + 'st_freeze','data'),
                State(self.baseId + 'graph','figure'),
                prevent_initial_call=True)
            def updateTimeRangeFrozen(valueFreeze,tp,tm,tadd,timeRange,fig):
                if valueFreeze:
                    mode_ts='mode : freeze'
                    freeze=True
                    ctx = dash.callback_context
                    trigId = ctx.triggered[0]['prop_id'].split('.')[0]
                    if trigId==self.baseId + 'ts_freeze':
                        fig = go.Figure(fig)
                        timeRange = [min([min(k['x']) for k in fig.data]),max([max(k['x']) for k in fig.data])]
                    elif trigId==self.baseId + 'btn_freeze+':
                        timeRange[1] = (pd.to_datetime(timeRange[1]) + dt.timedelta(seconds=tadd)).isoformat()
                    elif trigId==self.baseId + 'btn_freeze-':
                        timeRange[0] = (pd.to_datetime(timeRange[0]) - dt.timedelta(seconds=tadd)).isoformat()
                else:
                    mode_ts='mode : refresh'
                    freeze = False

                return mode_ts, timeRange, freeze

        #update freeze button
        if 'refreshWindow' in categories:
            @self.app.callback(Output(self.baseId + 'interval', 'interval'),
                                Input(self.baseId + 'in_refreshTime','value'))
            def updateRefreshTime(refreshTime):
                return refreshTime*1000

        #update legend toogle button
        if 'legendtoogle' in categories:
            @self.app.callback(Output(self.baseId + 'btn_legend', 'children'),
                                Input(self.baseId + 'btn_legend','n_clicks'))
            def updateLgdBtn(legendType):
                    if legendType%3==0 :
                        buttonMessage = 'tag'
                    elif legendType%3==1 :
                        buttonMessage = 'description'
                    elif legendType%3==2:
                        buttonMessage = 'unvisible'
                    return buttonMessage

        # call the export button
        if 'export' in categories:
            @self.app.callback(
                    Output(self.baseId + 'dl','data'),
                    Input(self.baseId + 'btn_export', 'n_clicks'),
                    State(self.baseId + 'graph','figure'),
                    prevent_initial_call=True
                    )
            def exportonclick(btn,fig):
                df,filename =  self.utils.exportDataOnClick(fig)
                return dcc.send_data_frame(df.to_csv, filename+'.csv')

        if 'datePickerRange' in categories:
            # initial visible month tuned to selection
            @self.app.callback(
            Output(self.baseId + 'pdr_date','initial_visible_month'),
            Input(self.baseId + 'pdr_date','start_date'),
            Input(self.baseId + 'pdr_date','end_date'),
            )
            def updateInitialVisibleMonth(startdate,enddate):
                ctx = dash.callback_context
                trigId = ctx.triggered[0]['prop_id']
                if 'start_date' in trigId:
                    return startdate
                else :
                    return enddate

            # update inital datetime regularly
            @self.app.callback(
            Output(self.baseId + 'pdr_date','start_date'),
            Output(self.baseId + 'pdr_timeStart','value'),
            Output(self.baseId + 'pdr_date','end_date'),
            Output(self.baseId + 'pdr_timeEnd','value'),
            Input(self.baseId + 'pdr_timeInterval','n_intervals'),
            )
            def updateInitialDateTime(n):
                if self.initialDateMethod == 'time':
                    now = dt.datetime.now().astimezone()
                    t0 = now- dt.timedelta(hours=8)
                    return t0.strftime('%Y-%m-%d'),t0.strftime('%H:%M'),now.strftime('%Y-%m-%d'),now.strftime('%H:%M')
                if self.initialDateMethod == 'parkedData':
                    # dangerous => better use localtimezone
                    listDates = [pd.Timestamp(k,tz='CET') for k in self.cfg.parkedDays]
                    lastDate = max(listDates)
                    t0=t1=lastDate
                    # if hours/minute parked take the last 8 hours:
                    # folderLastDay = self.cfg.folderPkl+'parkedData/'+lastDate.strftime('%Y-%m-%d')+'/*'
                    # listHours=glob.glob(folderLastDay)
                    # lastHour = max([float(k) for k in listHours])
                    # t1 = lastDate+dt.timedelta(hours=lastHour)
                    # t0 = t1-dt.timedelta(hours=8)
                    # return t0,t0.strftime('%H:%M'),t1,t1.strftime('%H:%M')
                    return t0.strftime('%Y-%m-%d'),t0.strftime('9:00'),t1.strftime('%Y-%m-%d'),t1.strftime('18:00')
                    # return t0,t0.strftime('9:00'),t1,t1.strftime('18:00')

        if 'modalTagsTxt' in categories:
            @self.app.callback(
                Output(self.baseId + "modalListTags", "is_open"),
                [Input(self.baseId + "btn_omlt", "n_clicks"), Input(self.baseId + "close_omlt", "n_clicks")],
                [State(self.baseId + "modalListTags", "is_open")],
            )
            def popupModalListTags(n1,n2, is_open):
                if n1:
                    return not is_open
                return is_open

            @self.app.callback(
                Output(self.baseId + "dd_tag", "value"),
                [Input(self.baseId + "close_omlt", "n_clicks")],
                [State(self.baseId + "txtListTags", "value")],
                prevent_initial_call=True
            )
            def getListTagsModal(close,txt):
                listTags = [k.strip().upper() for k in txt.split('\n')]
                return listTags

    def _buildLayout(self,specialWidDic,realTime=False,widthG=85,*args):
        if not realTime:
            dicWidgets = {
                'pdr_time' : {'tmin':self.cfg.parkedDays[0],'tmax':self.cfg.parkedDays[-1]},
                'in_timeRes':'5s','dd_resampleMethod' : {'value':'forwardfill','methods':list(self.cfg.methods.keys())},
                'dd_style':'default',
                'btn_export':0,
                    }
        else :
            dicWidgets = {
                'block_refresh':{'val_window':120,'val_refresh':50,
                                    'min_refresh':1,'min_window':2},
                'btns_refresh':None,
                'block_resample':{'val_res':'5s','val_method' : 'forwardfill','methods':list(self.cfg.methods.keys())},
                'dd_style':'default',
                'btn_export':0,
                }

        basicWidgets = self.dccE.basicComponents(dicWidgets,self.baseId)

        config={
                'displaylogo': False,
                'modeBarButtonsToAdd':[
                    'drawline',
                    'drawopenpath',
                    'drawclosedpath',
                    'drawcircle',
                    'drawrect',
                    'eraseshape'
                ]
            }

        specialWidgets = self.addWidgets(specialWidDic)
        # add graph object
        fig = self.utils.addLogo(go.Figure())
        graphObj = dcc.Graph(id=self.baseId + 'graph',config = config,figure=fig)

        widgetLayout = html.Div(basicWidgets+specialWidgets,style={"width": str(100-widthG) + "%", "float": "left"})
        graphLayout = html.Div(graphObj, style={"width": str(widthG)+"%", "display": "inline-block"})
        self.tabLayout = [widgetLayout,graphLayout]

    def addWidgets(self,dicWidgets):
        widgetLayout,dicLayouts = [],{}
        for wid_key,wid_val in dicWidgets.items():
            if 'dd_cmap'==wid_key:
                widgetObj = self.dccE.dropDownFromList(
                    self.baseId + wid_key, self.utils.cmapNames[0], 'colormap : ',value=wid_val)

            elif 'dd_listFiles' in wid_key:
                widgetObj = self.dccE.dropDownFromList(self.baseId+wid_key,self.cfg.listFilesPkl,
                    'Select your File : ',labelsPattern='\d{4}-\d{2}-\d{2}-\d{2}',defaultIdx=wid_val)


            elif 'dd_tag' in wid_key:
                widgetObj = self.dccE.dropDownFromList(self.baseId+wid_key,self.cfg.getTagsTU(''),
                    'Select the tags : ',value=wid_val,multi=True,optionHeight=20)

            elif 'dd_Units' in wid_key :
                widgetObj = self.dccE.dropDownFromList(self.baseId+wid_key,self.cfg.listUnits,'Select units graph : ',value=wid_val)

            elif 'dd_typeTags' in wid_key:
                widgetObj = self.dccE.dropDownFromList(self.baseId+wid_key,list(self.cfg.usefulTags.index),
                            'Select categorie : ',value=wid_val,optionHeight=20)

            elif 'btn_legend' in wid_key:
                widgetObj = [html.Button('tag',id=self.baseId+wid_key, n_clicks=wid_val)]

            elif 'in_patternTag' in wid_key  :
                widgetObj = [html.P('pattern with regexp on tag : '),
                dcc.Input(id=self.baseId+wid_key,type='text',value=wid_val)]

            elif 'in_step' in wid_key:
                widgetObj = [html.P('skip points : '),
                dcc.Input(id=self.baseId+wid_key,placeholder='skip points : ',type='number',
                            min=1,step=1,value=wid_val)]

            elif 'in_axisSp' in wid_key:
                widgetObj = [
                    html.P('select the space between axis : '),
                    dcc.Input(id=self.baseId+wid_key,type='number',value=wid_val,max=1,min=0,step=0.01)]

            elif wid_key == 'modalListTags':
                # print()
                widgetObj = [
                    dbc.Button("enter your list of tags!", id=self.baseId + "btn_omlt", n_clicks=0),
                    dbc.Modal([
                            dbc.ModalHeader("list of tags to load"),
                            dbc.ModalBody([
                                html.P('please enter your list of tags. Tags are written as rows ==> a line for each tag:'),
                                dcc.Textarea(id=self.baseId + 'txtListTags',value='',
                                                style={
                                    'width':'50em',
                                    'min-height': '50vh'
                                    }),
                            ]),
                            dbc.ModalFooter(dbc.Button("Apply changes", id=self.baseId + "close_omlt", className="ml-auto", n_clicks=0)),
                        ],
                        id=self.baseId + "modalListTags",
                        is_open=False,
                        size='xl',
                    )
                ]
            else:
                print('component :' + wid_key +' not found')
                sys.exit()

            for widObj in widgetObj:widgetLayout.append(widObj)

        return widgetLayout

    def updateLegendBtnState(self,legendType):
        if legendType%3==0 :
            buttonMessage = 'tag'
        elif legendType%3==1 :
            buttonMessage = 'description'
        elif legendType%3==2:
            buttonMessage = 'unvisible'
        return buttonMessage

    def updateLegend(self,fig,lgd):
        fig.update_layout(showlegend=True)
        oldNames = [k['name'] for k in fig['data']]
        if lgd=='description':
            newNames = [self.cfg.dfPLC.loc[k,'DESCRIPTION'] for k in oldNames]
            dictNames   = dict(zip(oldNames,newNames))
            fig         = self.utils.customLegend(fig,dictNames)

        elif lgd=='unvisible': fig.update_layout(showlegend=False)
        elif lgd=='tag': # get tags
            if not oldNames[0] in list(self.cfg.dfPLC.index):# for initialization mainly
                newNames = [self.cfg.dfPLC[self.cfg.dfPLC.DESCRIPTION==k].index[0] for k in oldNames]
                dictNames   = dict(zip(oldNames,newNames))
                fig         = self.utils.customLegend(fig,dictNames)
        return fig

    def updateGraph(self,previousFig,listTrigs,argsLoad,argsPlot,argsUpdateGraph):
        ctx = dash.callback_context
        trigId = ctx.triggered[0]['prop_id'].split('.')[0]
        fig = go.Figure(previousFig)
        ## load data in that case
        if trigId in [self.baseId+k for k in listTrigs]:
            # print('*argsLoad:')
            # print(*argsLoad)
            start=time.time()
            df_tuple = self.loadData(*argsLoad)
            print()
            print('full loading of  data in {:.2f} ms'.format((time.time()-start)*1000))
            if not isinstance(df_tuple,tuple):
                df_tuple = df_tuple,
            start=time.time()
            if isinstance(df_tuple[0],pd.DataFrame) and df_tuple[0].empty:
                ## get error code loading data ==> 1
                return go.Figure(),1
            else :
                fig = self.plotData(*df_tuple,*argsPlot)
        ###### update style of graph
        start=time.time()
        self.update_fig(fig,*argsUpdateGraph)
        print('figure generated in {:.2f} ms'.format((time.time()-start)*1000))
        print("====================================")

        # keep traces visibility
        try :
            fig = self.utils.legendPersistant(previousFig,fig)
        except:
            print('problem to make traces visibility persistant.')
        return self.utils.addLogo(fig),0

    def _defineCallbackGraph(self,realTime,inputTuples,prepareTags,argsPrepare,argsPlotGraph=[],argsUpdateGraph=[],outputTuples={},stateTuples={}):
        '''
        inputTuples:dictionnary of inputs
        '''
        d_outputs = [
            ('graph','figure'),
            ('error_modal_store','data')
        ]
        d_outputs+=outputTuples

        if realTime:
            d_inputs = [
                ('interval','n_intervals'),
                ('btn_update','n_clicks'),
                ('st_freeze','data'),
                ('dd_resampleMethod','value'),
                ('dd_style','value')
            ]
            d_states = [
                ('graph','figure'),
                ('in_timeWindow','value'),
                ('in_timeRes','value'),
                ('ts_freeze','value'),
            ]
        else:
            d_inputs = [
                ('pdr_timeBtn','n_clicks'),
                ('dd_resampleMethod','value'),
                ('dd_style','value')
            ]
            d_states = [
                ('graph','figure'),
                ('in_timeRes','value'),
                ('pdr_date','start_date'),
                ('pdr_date','end_date'),
                ('pdr_timeStart','value'),
                ('pdr_timeEnd','value'),
            ]
        d_inputs+=inputTuples
        d_states+=stateTuples

        # print(d_inputs)
        listArgsInputs = [k+'_' + v for k,v in d_inputs]
        listArgsStates = [k+'_' + v for k,v in d_states]
        allArgsName = listArgsInputs + listArgsStates
        # print(allArgsName)
        @self.app.callback(
            [Output(self.baseId + k,v) for k,v in d_outputs],
            [Input(self.baseId + k,v) for k,v in d_inputs],
            [State(self.baseId + k,v) for k,v in d_states])
        def updateGraph(*argsCallback):
            la = {k : v for k,v in zip(allArgsName,argsCallback)}
            # print(timeRange)
            # for k in la.keys() : print(k)

            previousFig = la['graph_figure']
            corrArgsPrepare=[ la[k+'_value'] for k in argsPrepare]
            # print(corrArgsPrepare)
            tags = prepareTags(*corrArgsPrepare)
            if len(tags)==0:
                return previousFig,2
            if realTime:
                t1 = pd.Timestamp.now()
                t0 = t1 - dt.timedelta(seconds=la['in_timeWindow_value']*60)
                if la['ts_freeze_value']:
                    timeRange = la['st_freeze_data']
                else:
                    timeRange = [t0.isoformat(),t1.isoformat()]
                triggerloadData_ids = ['interval','btn_update','st_freeze','dd_resampleMethod'] + argsPrepare
            else:
                t0 = la['pdr_date_start_date'] + ' ' + la['pdr_timeStart_value']
                t1 = la['pdr_date_end_date'] + ' ' + la['pdr_timeEnd_value']
                timeRange=[t0,t1]
                triggerloadData_ids=['dd_tag','pdr_timeBtn','dd_resampleMethod'] + argsPrepare

            fig,errCode = self.updateGraph(previousFig,triggerloadData_ids,
                [tags,timeRange,False,la['dd_resampleMethod_value'],la['in_timeRes_value']],
                [la[k + '_value'] for k in argsPlotGraph],
                [la[k + '_value'] for k in argsUpdateGraph]
            )
            return fig,errCode

    def update_fig(self,fig,style,colmap=None,lgd=None):
        self.cfg.update_lineshape_fig(fig,style)
        self.cfg.standardLayout(fig)
        if not colmap==None:
            fig = self.utils.updateColorMap(fig,colmap)
        if not lgd==None:
            # print(lgd)
            fig = self.updateLegend(fig,lgd)
        return fig

# ==============================================================================
#                              TEMPLATE TABS
# ==============================================================================
class TabSelectedTags(TabMaster):
    def __init__(self,*args,realtime=False,defaultCat=[],baseId='ts0_',**kwargs):
        TabMaster.__init__(self,*args,**kwargs,tabname='pre-selected tags',baseId=baseId)
        dicSpecialWidgets = {'dd_typeTags':defaultCat,'dd_cmap':'jet','btn_legend':0}

        self._buildLayout(dicSpecialWidgets,realTime=realtime)
        if realtime:
            self._define_basicCallbacks(['export','ts_freeze','refreshWindow'])
        else:
            self._define_basicCallbacks(['legendtoogle','export','datePickerRange'])
        inputTuples = [
            ('dd_typeTags','value'),
            ('dd_cmap','value')
            #('btn_legend','children')
            ]
        def prepareTags(tagCat):return self.cfg.getUsefulTags(tagCat)
        self._defineCallbackGraph(realtime,inputTuples,prepareTags,['dd_typeTags'],[],['dd_style','dd_cmap'])

class TabMultiUnits(TabMaster):
    def __init__(self,*args,realtime=False,defaultTags=[],baseId='tmu0_',**kwargs):
        # for k in args:print(k)
        TabMaster.__init__(self,*args,**kwargs,tabname='multi unit',baseId=baseId)
        dicSpecialWidgets = {'dd_tag':defaultTags,'modalListTags':None,'btn_legend':0}
        self._buildLayout(dicSpecialWidgets,realTime=realtime)
        if realtime:
            self._define_basicCallbacks(['legendtoogle','export','modalTagsTxt','refreshWindow','ts_freeze'])
        else:
            self._define_basicCallbacks(['legendtoogle','export','datePickerRange','modalTagsTxt'])
        inputTuples = [
            ('dd_tag','value'),
            ('btn_legend','children'),
        ]
        def prepareTags(tags):return tags
        self._defineCallbackGraph(realtime,inputTuples,prepareTags,['dd_tag'],[],['dd_style'])

class TabMultiUnitSelectedTags(TabMaster):
    def __init__(self,*args,realtime=False,defaultCat=[],baseId='muts0_',**kwargs):
        TabMaster.__init__(self,*args,**kwargs,
                    update_fig = self.update_fig,
                    tabname='multi-unit +',baseId=baseId)
        dicSpecialWidgets = {'dd_typeTags':defaultCat,'dd_tag':[],'btn_legend':0}
        self._buildLayout(dicSpecialWidgets,realTime=realtime)
        if realtime:
            self._define_basicCallbacks(['legendtoogle','export','ts_freeze','refreshWindow'])
        else:
            self._define_basicCallbacks(['legendtoogle','export','datePickerRange'])
        inputTuples = [
            ('dd_typeTags','value'),
            ('dd_tag','value'),
        ]
        def prepareTags(tagCat,tags):
            return self.cfg.getUsefulTags(tagCat) + tags
        self._defineCallbackGraph(realtime,inputTuples,prepareTags,['dd_typeTags','dd_tag'],[],['dd_style'])

class TabDoubleMultiUnits(TabMaster):
    def __init__(self,*args,realtime=False,defaultTags1=[],defaultTags2=[],baseId='rtdmu0_',**kwargs):
        TabMaster.__init__(self,*args,**kwargs,
                plotData   = self.plotData,
                update_fig = self.update_fig,
                tabname    = 'double multi units',baseId=baseId)
        dicSpecialWidgets = {
            'dd_tag1':defaultTags1,
            'dd_tag2':defaultTags2,
            # 'dd_cmap':'jet',
            'btn_legend':0,'in_axisSp':0.05}
        self._buildLayout(dicSpecialWidgets,realTime=realtime)
        inputTuples = [
            ('dd_tag1','value'),
            ('dd_tag2','value')
            # 'dd_cmap','value'
        ]
        def prepareTags(tags1,tags2):
            return tags1 + tags2
        self._defineCallbackGraph(realtime,inputTuples,prepareTags,
                    ['dd_tag1','dd_tag2'],
                    ['dd_tag1','dd_tag2'],
                    ['dd_style'])

    def plotData(self,*args,**kwargs):
        return self.cfg.doubleMultiUnitGraph(*args,**kwargs)

class TabUnitSelector(TabMaster):
    def __init__(self,*args,realtime=False,unitInit='mbarg',patTagInit='GFC',baseId='tu0_',**kwargs):
        TabMaster.__init__(self,*args,**kwargs,tabname='select Units',baseId=baseId)

        dicSpecialWidgets = {'dd_Units':unitInit,'in_patternTag':patTagInit,'dd_cmap':'jet','btn_legend':0}
        inputTuples = [
            ('dd_Units','value'),
            ('in_patternTag','value'),
        ]
        self._buildLayout(dicSpecialWidgets,realTime=realtime)
        if realtime:
            self._define_basicCallbacks(['legendtoogle','export','ts_freeze','refreshWindow'])
        else:
            self._define_basicCallbacks(['legendtoogle','export','datePickerRange'])
        def prepareTags(patTag,unit):
            tags=self.cfg.getTagsTU(patTag,unit)
            return tags
        self._defineCallbackGraph(realtime,inputTuples,prepareTags,['in_patternTag','dd_Units'],[],['dd_style'])


class AnalysisTab(TabMaster):
    def __init__(self,app,cfg):
        TabMaster.__init__(self,app,cfg,
                    self.loadDF,self.plotdf,cfg.update_lineshape,
                    baseId='formu_',tabname = 'Analysis'
                    )
        self.df = px.data.stocks()
        dicSpecialWidgets = {}
        self._buildLayout(dicSpecialWidgets)
        xwid  = self.dccE.DropdownFromList(self.cfg.getTagsTU('')+['timestamp'],
                    id=self.baseId+'dd_x',value='timestamp',clearable=False)
        ywid  = self.dccE.DropdownFromList(self.cfg.getTagsTU(''),
                    id=self.baseId+'dd_y',value=self.cfg.getTagsTU('GFC')[0],multi=True)
        self.tabLayout[0].children+=[html.P('   x variable :'),xwid,html.P('   y variables :'),ywid]
        self.tabLayout.append(html.Div(self.newWidgets()))
        self.tabLayout.append(dcc.Store(id=self.baseId + '_newListTags',data={}))
        self._define_callbacks()

    def computeNewTag(self,timeRange,formulas,**kwargs):
        if len(formulas)==0:
            return pd.DataFrame()
        listTags = [re.findall('[a-zA-Z][a-zA-Z\._\d]*',f) for f in formulas]
        listTags = list(pd.Series(self.cfg.utils.flattenList(listTags)).unique())

        df = self.cfg.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
        newdf=pd.DataFrame()
        for formula in formulas:
            realFormula = formula
            for t in listTags:realFormula = realFormula.replace(t,"df['"+t+"']")
            newdf[realFormula] = eval(realFormula)
        return newdf

    def loadDF(self,timeRange,x,ys,rs,rsMethod):
        if not isinstance(ys,list):ys=[ys]
        #search and compute formulas
        formulas = [t for t in ys + [x] if re.search('[-\*\+\/]',t)]
        dfFormulas = self.computeNewTag(timeRange,formulas,rs=rs,applyMethod=rsMethod)
        #search and compute not formulas
        tags = [t for t in ys+[x] if t not in formulas]
        if not x=='timestamp':
            df = self.cfg.DF_loadTimeRangeTags(timeRange,tags,rs=rs,applyMethod=rsMethod)
            dft = pd.concat([dfFormulas,df],axis=1)
            dft = dft.set_index(x)
        else :
            tags = [t for t in tags if not t=='timestamp']
            df = self.cfg.DF_loadTimeRangeTags(timeRange,tags,rs=rs,applyMethod=rsMethod)
            dft = pd.concat([dfFormulas,df],axis=1)
        return dft

    def plotdf(self,df):
        return px.scatter(df)

    def newWidgets(self):
        self.egalstyle = {'fontsize':'20 px','width':'10px','height': '40px','min-height': '1px',}
        self.newtagstyle = {'fontsize':'15 px','width':'300px','height': '40px','min-height': '1px',}
        self.tagstyle = {'fontsize':'15 px','width':'400px','height': '40px','min-height': '1px',}
        self.formulastyle = {'fontsize':'15 px','width':'800px','height': '40px','min-height': '1px',}
        self.buttonstyle = {'fontsize':'15 px','width':'90px','height': '40px','min-height': '1px',}

        tagwid = self.dccE.DropdownFromList(self.cfg.getTagsTU(''),
                        id=self.baseId+'dd_tag',placeholder='liste tags:',style=self.tagstyle)
        newTagIn = dcc.Input(id=self.baseId+'in_newtag',placeholder='tagname:',
                        type='text',style=self.newtagstyle)
        egalwid     = html.P(id=self.baseId+'egal',children=' : ',style=self.egalstyle)
        formulawid  = dcc.Input(id=self.baseId+'in_formula',placeholder='formula : ',
                        type='text',style=self.formulastyle,value='')
        btn_create  = html.Button(id=self.baseId+'btn_create',children='create',
                        style=self.buttonstyle)

        createFormulaWidget = [
                dbc.Row([
                    dbc.Col(tagwid),
                    dbc.Col(newTagIn),
                    dbc.Col(egalwid),
                    dbc.Col(formulawid),
                    dbc.Col(btn_create)
                ]),
                ]
        return createFormulaWidget

    def _define_callbacks(self):
        @self.app.callback(
            Output(self.baseId + 'in_formula', 'value'),
            Output(self.baseId + 'in_newtag', 'value'),
            Output(self.baseId + 'dd_tag', 'value'),
            Output(self.baseId + 'dd_x', 'options'),
            Output(self.baseId + 'dd_y', 'options'),

            Input(self.baseId + 'btn_create', 'n_clicks'),
            Input(self.baseId + 'dd_tag', 'value'),
            State(self.baseId + 'in_newtag','value'),
            State(self.baseId + 'in_formula','value'),
            State(self.baseId + 'dd_x','options'),
            State(self.baseId + 'dd_y','options'),
            prevent_initial_call=True
        )
        def addNewTag(n,tag,newtag,formula,ddx,ddy):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            # print(trigId)
            if trigId==self.baseId + 'dd_tag':
                return formula + tag,newtag,'',ddx,ddy

            if trigId==self.baseId + 'btn_create':
                ## check if formula is correct
                ## add the new formula
                newentry = [{'label':newtag,'value':formula}]
                newddx = ddx + newentry
                newddy = ddy + newentry
                return '','','',newddx,newddy

        self._define_basicCallbacks(['export','datePickerRange'])
        @self.app.callback(
            Output(self.baseId + 'graph', 'figure'),
            Output(self.baseId + 'error_modal_store', 'data'),
            Input(self.baseId + 'pdr_timeBtn','n_clicks'),
            Input(self.baseId + 'dd_resampleMethod','value'),
            Input(self.baseId + 'dd_style','value'),
            Input(self.baseId + 'dd_x','value'),
            Input(self.baseId + 'dd_y','value'),
            State(self.baseId + 'graph','figure'),
            State(self.baseId + 'in_timeRes','value'),
            State(self.baseId + 'pdr_date','start_date'),
            State(self.baseId + 'pdr_date','end_date'),
            State(self.baseId + 'pdr_timeStart','value'),
            State(self.baseId + 'pdr_timeEnd','value'),
            )
        def updateGraph(timeBtn,rsMethod,style,x,y,previousFig,rs,date0,date1,t0,t1):
            triggerList=['pdr_timeBtn','dd_resampleMethod','dd_x','dd_y']
            timeRange = [date0+' '+t0,date1+' '+t1]

            fig,errCode = self.updateGraph(previousFig,triggerList,style,
                [timeRange,x,y,rs,rsMethod],[]
                )
            return fig,errCode

# ==============================================================================
#                               template tabs
# ==============================================================================
class TabExploreDF(TabMaster):
    def __init__(self,app,df,baseId='ted0_'):
        TabMaster.__init__(self,app,baseId)
        self.tabname = 'explore df'
        self.df = df
        self.tabLayout = self._buildLayout()
        self._define_callbacks()

    def _buildLayout(self,widthG=85):
        dicWidgets = {  'btn_update':0,
                        'dd_resampleMethod' : 'mean',
                        'dd_style':'lines+markers','dd_typeGraph':'scatter',
                        'dd_cmap':'jet'}
        basicWidgets = self.dccE.basicComponents(dicWidgets,self.baseId)
        listCols = list(self.df.columns)
        specialWidgets = self.dccE.dropDownFromList(self.baseId + 'dd_x',listCols,'x : ',defaultIdx=0)
        specialWidgets = specialWidgets + self.dccE.dropDownFromList(self.baseId + 'dd_y',listCols,'y : ',defaultIdx=1,multi=True)
        specialWidgets = specialWidgets + [html.P('nb pts :'),dcc.Input(self.baseId + 'in_pts',type='number',step=1,min=0,value=1000)]
        specialWidgets = specialWidgets + [html.P('slider x :'),dcc.RangeSlider(self.baseId + 'rs_x')]
        # reodrer widgets
        widgetLayout = specialWidgets + basicWidgets
        return self.dccE.buildGraphLayout(widgetLayout,self.baseId,widthG=widthG)

    def _define_callbacks(self):
        @self.app.callback(
        Output(self.baseId + 'rs_x', 'marks'),
        Output(self.baseId + 'rs_x', 'value'),
        Output(self.baseId + 'rs_x', 'max'),
        Output(self.baseId + 'rs_x', 'min'),
        Input(self.baseId +'dd_x','value'))
        def update_slider(x):
            x = self.df[x].sort_values()
            min,max = x.iloc[0],x.iloc[-1]
            listx = [int(np.floor(k)) for k in np.linspace(0,len(x)-1,5)]
            marks = {k:{'label':str(k),'style': {'color': '#77b0b1'}} for k in x[listx]}
            return marks,[min,max],max,min

        listInputsGraph = {
                        'dd_x':'value',
                        'dd_y':'value',
                        'btn_update':'n_clicks',
                        'dd_resampleMethod':'value',
                        'dd_typeGraph':'value',
                        'dd_cmap':'value',
                        'dd_style':'value'
                        }
        listStatesGraph = {
                            'graph':'figure',
                            'in_pts':'value',
                            'rs_x': 'value',
                            }
        @self.app.callback(
        Output(self.baseId + 'graph', 'figure'),
        [Input(self.baseId + k,v) for k,v in listInputsGraph.items()],
        [State(self.baseId + k,v) for k,v in listStatesGraph.items()],
        )
        def updateGraph(x,y,upBtn,rsMethod,typeGraph,cmap,style,fig,pts,rsx):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            if not upBtn or trigId in [self.baseId+k for k in ['btn_update','dd_x','dd_y']]:
                df = self.df.set_index(x)
                if not isinstance(y,list):y=[y]
                if x in y : df[x]=df.index
                # print(df)
                df = df[df.index>rsx[0]]
                df = df[df.index<rsx[1]]
                if pts==0 : inc=1
                else :
                    l = np.linspace(0,len(df),pts)
                    inc = np.median(np.diff(l))
                df = df[::int(np.ceil(inc))]
                df  = df.loc[:,y]
                fig = self.utils.multiUnitGraph(df)
            else :fig = go.Figure(fig)
            fig.update_yaxes(showgrid=False)
            fig.update_xaxes(title=x)
            fig = self.utils.quickLayout(fig,title='',xlab='',ylab='',style='latex')
            fig = self.utils.updateStyleGraph(fig,style,cmap)
            return fig
