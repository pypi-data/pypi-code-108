import datetime as dt, pickle, time, sys
import os,re,pandas as pd
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px, plotly.graph_objects as go
from dorianUtils.dccExtendedD import DccExtended
from dorianUtils.utilsD import Utils
import dorianUtils.dashTabsD as tabsD

class ScreenBuildingTab():
    def __init__(self,cfg):
        self.cfg=cfg
        self.listCompute = ['power enveloppe','consumed energy','energyPeriodBarPlot']
    # ==========================================================================
    #                           SHARED FUNCTIONS CALLBACKS
    # ==========================================================================
    def addWidgets(self,dicWidgets):
        widgetLayout,dicLayouts = [],{}
        for wid_key,wid_val in dicWidgets.items():
            if 'dd_computation' in wid_key:
                widgetObj = self.dccE.dropDownFromList(self.baseId + wid_key,self.listCompute,
                                                        'what should be computed ?',value = wid_val)

            elif 'dd_compteur' in wid_key:
                widgetObj  = self.dccE.dropDownFromList(self.baseId + wid_key,
                                self.cfg.listCompteurs,'variables:',value=wid_val,multi=True)

            else :
                print('component ',wid_key,' is not available')
                sys.exit()

            for widObj in widgetObj:widgetLayout.append(widObj)

        return widgetLayout

    def computeGraph(self,timeRange,computation,compteurs,rs):
        if not isinstance(compteurs,list):compteurs=[compteurs]
        if computation == 'power enveloppe' :
            df = self.cfg.computePowerEnveloppe(timeRange,compteur=compteurs[0],rs=rs)
            unit = 'kW'
            fig = px.scatter(df)
            # fig.update_layout(title=compteurs)
        elif computation == 'consumed energy' :
            fig= self.cfg.plot_compare_kwhCompteurvsPower(timeRange,compteurs,rs)
        elif computation == 'energyPeriodBarPlot' :
            fig = self.cfg.energyPeriodBarPlot(timeRange,compteurs=compteurs)
        return fig

    def returnfig(self,fig):
        return fig

# ==========================================================================
#                           SHARED FUNCTIONS CALLBACKS
# ==========================================================================
class ComputationTab(ScreenBuildingTab,tabsD.TabMaster):
    def __init__(self,app,cfg,baseId='tc0_'):
        ScreenBuildingTab.__init__(self,cfg)
        tabsD.TabMaster.__init__(self,app,cfg,
                    self.computeGraph,
                    self.returnfig,
                    cfg.update_lineshape,
                    tabname='computation',baseId=baseId)

        dicSpecialWidgets = {'dd_computation':'power enveloppe','dd_compteur':'B001'}
        self._buildLayout(dicSpecialWidgets)
        self._define_callbacks()

    def _define_callbacks(self):
        self._define_basicCallbacks(['export','datePickerRange'])
        @self.app.callback(
            Output(self.baseId + 'graph', 'figure'),
            Output(self.baseId + 'error_modal_store', 'data'),
            Input(self.baseId + 'dd_computation','value'),
            Input(self.baseId + 'dd_compteur','value'),
            Input(self.baseId + 'pdr_timeBtn','n_clicks'),
            Input(self.baseId + 'dd_resampleMethod','value'),
            Input(self.baseId + 'dd_style','value'),
            State(self.baseId + 'graph','figure'),
            State(self.baseId + 'in_timeRes','value'),
            State(self.baseId + 'pdr_timePdr','start_date'),
            State(self.baseId + 'pdr_timePdr','end_date'),
            State(self.baseId + 'pdr_timeStart','value'),
            State(self.baseId + 'pdr_timeEnd','value'),
            )
        def updateComputationGraph(compute,compteur,timeBtn,rsMethod,style,previousFig,rs,date0,date1,t0,t1):
            timeRange = [date0+' '+t0,date1+' '+t1]
            print(timeRange)
            triggerList=['dd_computation','dd_compteur','pdr_timeBtn','dd_resampleMethod']
            fig,errCode = tabsD.TabMaster.updateGraph(self,previousFig,triggerList,style,
                            # [timeRange,compute,compteur,rs,rsMethod],[])
                            [timeRange,compute,compteur,rs],[])
            return fig,errCode

# ==============================================================================
#                        FROM DORIANUTILS.DASHTABSD
# ==============================================================================

class TabSelectedTags_SB(tabsD.TabSelectedTags):
    def __init__(self,app,cfg,realtime):
        tabsD.TabSelectedTags.__init__(self,app,cfg,
            cfg.loadtags_period,
            cfg.plotTabSelectedData,
            realtime=realtime,
            baseId = 'stt_sb_',
            defaultCat='SLS puissances'
        )

class TabMultiUnit_SB(tabsD.TabMultiUnits):
    def __init__(self,app,cfg,realtime):
        tabsD.TabMultiUnits.__init__(self,app,cfg,
            cfg.loadtags_period,
            cfg.utils.multiUnitGraph,
            realtime=realtime,
            baseId = 'mut_sb_',
            defaultTags = cfg.tag_categories['SLS niveau1 puissances'] + cfg.tag_categories['Pv puissance']
            )

class TabMultiUnitSelectedTags_SB(tabsD.TabMultiUnitSelectedTags):
    def __init__(self,app,cfg,realtime):
        tabsD.TabMultiUnitSelectedTags.__init__(self,app,cfg,
            cfg.loadtags_period,
            cfg.multiUnitGraphSB,
            realtime=realtime,
            defaultCat = 'SLS niveau1 puissances',
            ddtag = cfg.tag_categories['Pv puissance'],
            baseId = 'must_sb_',
        )

class TabDoubleMultiUnits_SB(tabsD.TabDoubleMultiUnits):
    def __init__(self,app,cfg,realtime):
        tabsD.TabDoubleMultiUnits.__init__(self,app,cfg,
            cfg.loadtags_period,
            realtime = realtime,
            defaultTags1 = cfg.getTagsTU('B.*sys-JTW'),
            defaultTags2 = cfg.getTagsTU('XM.*temp'),
            baseId = 'rtdmu_sb_',
        )

class TabUnitSelector_SB(tabsD.TabUnitSelector):
    def __init__(self,app,cfg,realtime):
        tabsD.TabUnitSelector.__init__(self,app,cfg,
            cfg.loadtags_period,
            cfg.plotTabSelectedData,
            realtime=realtime,
            baseId = 'ust_sb_',
        )
