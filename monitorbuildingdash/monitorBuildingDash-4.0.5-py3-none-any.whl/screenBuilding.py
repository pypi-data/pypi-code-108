#!/bin/python
# #######################
# #   GLOBAL VARIABLES  #
# # COMPUTER DEPENDENT  #
# #######################
import sys, glob, re, os, time, datetime as dt,importlib,pickle,glob
import pandas as pd,numpy as np
from dorianUtils.utilsD import Utils
import dorianUtils.comUtils as comUtils
importlib.reload(comUtils)
import socket
namePC = socket.gethostname()
# ==============================================================================
#                           CONFIGURATION

DATABASE_SIZE_SECONDS = 1*3600
PARKING_TIME          = 1*3600
METEO_FREQ            = 60
# VMUC_FREQ             = 5
# SMARTLOGGER_FREQ      = 5
DB_PARAMETERS = {
    'host'     : "localhost",
    # 'host'     : "192.168.7.2",
    'port'     : "5432",
    'dbname'   : "bigbrother",
    'user'     : "postgres",
    'password' : "sylfenbdd"
    }

if 'sylfen' in os.getenv('HOME'):
    # baseFolder   = '/home/sylfen/share/dataScientismProd/MonitoringBatiment/'
    baseFolder   = '/home/sylfen/data_ext/'
else:
    # baseFolder   = '/home/dorian/sylfen/AS6204R/dataScientism/MonitoringBatiment/'
    baseFolder = '/home/dorian/data/sylfenData/'

FOLDERPKL = baseFolder + 'monitoring_daily/'

fs = comUtils.FileSystem()
appdir = os.path.dirname(os.path.realpath(__file__))
parentdir = fs.getParentDir(appdir)
CONFFOLDER = parentdir+'monitorBuildingDash/confFiles/'

# ==============================================================================
#           PREPARE DEVICES INFOS(should be instead generate plc files)
listFiles = glob.glob(CONFFOLDER + '*devices*.ods')
file_devices = listFiles[0]
v_devices  = re.findall('_v\d+',file_devices)[0]
df_devices = pd.read_excel(file_devices,index_col=0,sheet_name='devices')
variables = pd.read_excel(file_devices,index_col=0,sheet_name='variables')
compteurs = pd.read_excel(file_devices,index_col=0,sheet_name='compteurs')
dictCat = df_devices.category.to_dict()
compteurs['fullname']=list(compteurs.reset_index().apply(lambda x:dictCat[x['device']]+'-'+ x['pointComptage']+'-',axis=1))
for device in [d for  d in df_devices.index if not d=='meteo']:
    catCompteur = compteurs.loc[compteurs.device==device].reset_index()
    fullnames   = dictCat[device] + catCompteur.index.to_series().apply(lambda x:'{:x}'.format(x+1).zfill(8))+'-'+catCompteur['pointComptage']
    compteurs.loc[compteurs.device==device,'fullname'] =list(fullnames)

DEVICE_INFOS={}
for device_name in df_devices.index[df_devices.statut=='actif']:
    DEVICE_INFOS[device_name]={
        'variables':variables[variables.device==device_name],
        'compteurs':compteurs[compteurs.device==device_name],
        'version':v_devices
    }
DEVICE_INFOS['meteo']['freq']=METEO_FREQ

# [print(k,v,'\n') for k,v in DEVICE_INFOS['meteo'].items()]
# sys.exit()
# ==============================================================================
#                           INSTANCIATIONS
VisualisationMaster_daily = comUtils.VisualisationMaster_daily
Configurator = comUtils.Configurator
SuperDumper_daily = comUtils.SuperDumper_daily
VersionManager_daily = comUtils.VersionManager_daily

class Config_extender():
    def __init__(self):
        cfg = Configurator(FOLDERPKL,CONFFOLDER,DB_PARAMETERS,
            dbTimeWindow=DATABASE_SIZE_SECONDS,parkingTime=PARKING_TIME,
            device_infos=DEVICE_INFOS,
            generateConfFiles=False
            )
        tag_cats={}
        for cat in cfg.usefulTags.index:
            tag_cats[cat] = cfg.getUsefulTags(cat)
        tag_cats['SLS niveau0 puissances']=[k for k in tag_cats['SLS puissances'] if k not in tag_cats['SLS niveau1 puissances']]
        tag_cats['SLS niveau0 compteurs']=[k for k in tag_cats['SLS compteurs'] if k not in tag_cats['SLS niveau1 compteurs']]
        self.tag_categories=tag_cats
        self.compteurs=cfg.compteurs

class ScreeningBuilding_dumper(SuperDumper_daily,Config_extender):
    def __init__(self,**kwargs):
        Config_extender.__init__(self)
        SuperDumper_daily.__init__(self,FOLDERPKL,CONFFOLDER,DB_PARAMETERS,
                    dbTimeWindow=DATABASE_SIZE_SECONDS,parkingTime=PARKING_TIME,
                    device_infos=DEVICE_INFOS,
            **kwargs)

import plotly.express as px
import plotly.graph_objects as go
import textwrap
import locale, calendar, datetime as dt,textwrap
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')   ## first I set locale
class ScreenBuildingComputer(VisualisationMaster_daily,Config_extender):
    def __init__(self,**kwargs):
        Config_extender.__init__(self)
        VisualisationMaster_daily.__init__(self,FOLDERPKL,CONFFOLDER,DB_PARAMETERS,
                        dbTimeWindow=DATABASE_SIZE_SECONDS,parkingTime=PARKING_TIME,
                        device_infos=DEVICE_INFOS,
                        **kwargs)
        self.listComputation    = ['power enveloppe','consumed energy','energyPeriodBarPlot']
        self.utils = Utils()

    def get_description_tags_compteurs(self,tags):
        counts=[k.split('-')[1] for k in tags]
        return [self.compteurs.loc[k,'description'] for k in counts]

    def exportToxcel(self,df):
        df.index = [t.astimezone(pytz.timezone('Etc/GMT-2')).replace(tzinfo=None) for t in df.index]
        df.to_excel(dt.date.today().strftime('%Y-%m-%d')+'.xlsx')

    # ==========================================================================
    #                       REPORTING SLS FUNCTIONS
    # ==========================================================================
    def get_highPV(self,t1):
        t0 = pd.Timestamp('2021-08-05 00:00')
        pv = localGetTags('*PV*JTW-00*')[0]
        df  = self.load_parkedtags_daily([pv],t0,t1,folderPkl)
        dfmax=df[df.value>60]
        return dfmax

    def get_nearest_available_day(self,t):
        listdays_diff=pd.DataFrame([[k,k-t] for k in self.daysnotempty]).set_index(0)
        return listdays_diff.abs().idxmin().squeeze()

    def get_last_days_month_since_start(self,t1):
        first_day=self.daysnotempty.min()
        first_day=pd.Timestamp('2021-08-07',tz='CET')
        last_day_month=lambda t1: t1-pd.DateOffset(days=t1.day)
        list_lastDays=[]
        t=t1-pd.DateOffset(hours=t1.hour,minutes=t1.minute)
        while t>first_day:
            list_lastDays.append(t)
            t = last_day_month(t)
        list_lastDays.append(first_day)
        return pd.Series(list_lastDays).sort_values().to_list()

    def getTags_sls_conso(self,t0,t1,rs,units,formula='g+f-e+pv'):
        folderday = self.folderPkl + self.streamer.to_folderday(t1)
        if units=='kW':
            zones   = self.tag_categories['SLS niveau1 puissances']
            pv = self.tag_categories['Pv puissance']
        elif units=='kWh':
            zones   = self.tag_categories['SLS niveau1 compteurs']
            pv = self.tag_categories['Pv compteur']
        tags = zones+pv
        # print(tags)
        g,e,f = zones
        pv = pv[0]
        df = self.loadtags_period(t0,t1,tags,rsMethod='forwardfill',rs=rs)
        if df.empty:
            print('')
            print('NO DATA FOR PERIOD : ',[t0,t1])
            return df
        df.columns=['e','f','g','pv']
        if formula == 'g+f-e+pv':
            df['total site'] = df['g'] + df['f'] - df['e'] + df['pv']
        elif formula =='g-pv':
            df['total site'] = df['g']-df['pv']
        return df

    def get_conso_prod_sls_lastValue(self,formula='g+f-e+pv'):
        t1 = pd.Timestamp.now(tz='CET')
        t0 = t1-pd.Timedelta(minutes=1)
        return self.getTags_sls_conso(t0,t1,rs='10s',units='kWh',formula=formula).iloc[-1,-2:]

    def conso2days_sls(self,t1,**kwargs):
        t0 = t1-dt.timedelta(days=2,hours=0,minutes=0)
        df = self.getTags_sls_conso(t0,t1,units='kW',rs='600s',**kwargs)
        if df.empty:
            print('conso2days not possible df empty')
            return df
        df['diffPV']=df['pv']-df['total site']
        dfAutoConso = pd.DataFrame()
        df['zero'] = 0
        dfAutoConso['part Grid']     = -df[['diffPV','zero']].min(axis=1)
        dfAutoConso['Consommation du site'] = df['total site']
        dfAutoConso['surplus PV']    = df[['diffPV','zero']].max(axis=1)
        dfAutoConso['part PV']       = df['pv']-dfAutoConso['surplus PV']
        dfAutoConso['part rSoc']     = 0
        dfAutoConso['part batterie'] = 0
        # dfAutoConso['Autoconsommation'] = df[pv]-dfAutoConso['PV surplus']
        return dfAutoConso

    def consoweek_sls(self,t1,**kwargs):
        t0 = t1-dt.timedelta(days=7,hours=0,minutes=0)
        df = self.getTags_sls_conso(t0,t1,units='kW',rs='1H',**kwargs)
        if df.empty:
            print('conso2week not possible df empty')
            return df
        df = df[['total site','pv']]
        df.columns = ['consommation bâtiment','production PV']
        return df

    def consomonth_sls(self,t1,**kwargs):
        t0 = t1-pd.Timedelta(days=32,hours=t1.hour,minutes=t1.minute,seconds=t1.second)
        df = self.getTags_sls_conso(t0,t1,rs='10s',units='kWh',**kwargs)
        df = df[['total site','pv']].bfill()
        df.columns = ['consommation bâtiment','production PV']
        df = df.resample('1D',closed='right').ffill()
        df=df.diff().shift(periods=-1).iloc[:-1,:]
        return df

    def conso_sls_compteurs(self,compteurs,t1,t0=None,**kwargs):
        if t0 is None:t0 = t1-pd.Timedelta(days=32,hours=t1.hour,minutes=t1.minute,seconds=t1.second)
        tags = [self.getTagsTU(k+'.*kWh-JTWH') for k in compteurs]
        tags = self.fs.flatten(tags)
        # print(tags)
        df = self.loadtags_period(t0,t1,tags,rsMethod='forwardfill',rs='5s')
        df = df.resample('1D',closed='right').ffill()
        df=df.diff().shift(periods=-1).iloc[:-1,:]
        return df

    def get_compteurs_sls_since_start(self,t1,level='all'):
        listdays = self.get_last_days_month_since_start(t1)
        compteurs = self.tag_categories['SLS compteurs']
        pv = self.tag_categories['Pv compteur']
        tags=compteurs+pv
        # print(tags)
        dfs=[]
        for t in listdays:
            t0,t1=t,t+pd.Timedelta(hours=23,minutes=58,seconds=0)
            # print(t0,t1)
            df = self.loadtags_period(t0,t1,tags,rs='10s',rsMethod='forwardfill')
            if df.empty:
                t0 = self.get_nearest_available_day(t)
                t1 = t0 + pd.Timedelta(hours=23,minutes=58,seconds=0)
                df = self.loadtags_period(t0,t1,tags,rs='10s',rsMethod='forwardfill')
            df=df.iloc[[-1],:]
            dfs.append(df)
        df = pd.concat(dfs)
        return df
        # return dfs

    def track_energy_compteurs_months(self,t1):
        df_compteurs = self.get_compteurs_sls_since_start(t1)
        # return df_compteurs
        get_tag = lambda x: [k for k in df_compteurs.columns if x in k][0]
        # abcd,e,f,pv = [get_tag(x) for x in ['GENERAL','E001','F001','PV']]
        abcd,e,f,pv = [get_tag(x) for x in ['A007','E001','F001','PV']]
        total_sls = df_compteurs[abcd]-df_compteurs[e]+df_compteurs[f]+df_compteurs[pv]

        df_conso = df_compteurs.diff()
        compteursNames = self.get_description_tags_compteurs(df_compteurs.columns)
        df_conso.columns = [(c,'consommation') for c in compteursNames]
        df_compteurs.columns = [(c,'compteur') for c in compteursNames]
        df_compteurs[('total sls','compteur')]=total_sls
        df_conso[('total sls','consommation')]=total_sls.diff()

        df_final=pd.concat([df_compteurs,df_conso],axis=1)
        df_final=df_final[df_final.columns.sort_values()]
        df_final.columns=pd.MultiIndex.from_tuples(df_final.columns)
        df_final.index=[k.strftime('%d-%B-%Y') for k in df_final.index]
        nameFile = 'conso_elec_' + t1.strftime('%B_%Y') + '.xlsx'
        df_final.to_excel(nameFile)
        return df_final

    def conso_repartition_sls(self,t1):
        t0 = t1-dt.timedelta(days=7,hours=0,minutes=0)
        folderday = self.folderPkl+ self.streamer.to_folderday(t0)
        sls_power = [k.split('/')[-1].split('.pkl')[0] for k in glob.glob(folderday+'*sys-JTW*')]
        sls_power = [k for k in sls_power if 'GENERAL' not in k]
        sls_power = [k for k in sls_power if 'EM_VIRTUAL' not in k]
        sls_power = [k for k in sls_power if 'F001' not in k]
        sls_power = [k for k in sls_power if 'E001' not in k]
        sls_power = [k for k in sls_power if 'A007' not in k]

        t0 = t1-dt.timedelta(days=7,hours=0,minutes=0)
        df = self.loadtags_period(t0,t1,sls_power,rsMethod='forwardfill',rs='3600s')
        df.columns = self.get_description_tags_compteurs(df.columns)
        return df

    ###### graphics
    def updateLegend(self,fig,w=30):
        for n in fig.data:
            t = textwrap.wrap(n.name,width=w)
            t = [k.ljust(w) for k in t]
            n.name='<br>'.join(t)
        return fig

    def fig_conso2days_sls(self,t1,tfsize=17,**kwargs):
        df = self.conso2days_sls(t1,**kwargs)
        colPV='rgba(32,56,100,255)'
        colgrid='rgba(132,151,176,255)'
        ti = df.resample('2H').mean().index
        fig=px.area()
        fig.add_trace(go.Scatter(x=df.index,y=df['part PV'],name='Electricité solaire',
                        line_color='black',stackgroup='1',fillcolor=colPV))
        df['part Grid']=df['part Grid']-df['part PV']
        fig.add_trace(go.Scatter(x=df.index,y=df['part Grid']+df['part PV'],name='Electricité du réseau',
                        line_color='black',stackgroup='1',fillcolor=colgrid))
        fig.add_trace(go.Scatter(x=df.index,y=df['surplus PV'],name='surplus PV',
                        line_color='black',stackgroup='1',line_dash='dot',fillcolor='rgb(232,236,244)'))

        fig.add_trace(go.Scatter(x=df.index,y=df['Consommation du site'],name='Consommation du site',line_color='black'))

        for l in [k for k in df.index if k.hour==0 and k.minute==0]:
            fig.add_vline(x=l,xref='x', line_width=3, line_dash="solid", line_color="rgba(0,0,0,90)")
        ticks =  list(ti.strftime('%Hh'))
        days=[k for k,l in enumerate(ti) if l.hour==0 and l.minute==0]
        lims=[0] + days + [len(ti)]
        middles = [(k+l)//2 for k,l in zip(lims[1:],lims[:-1])]

        for k in middles:
            ticks[k]=ti[k].strftime('%Hh <br>%A <br> %d/%m/%Y ')
        fig.update_layout(xaxis = dict(tickangle=0,tickmode='array',tickvals = ti,ticktext =ticks))
        fig.update_layout(hovermode= 'closest',xaxis_title_text = '')
        fig.update_layout(legend_title_text = '')
        fig.update_layout(title={'text': 'Le Mix électrique du site SLS Actiparc en temps réel',
                            'x':0.5,'xanchor': 'center','yanchor': 'top'})
        fig.update_layout(yaxis_title_text = 'Puissance éléctrique active (en kW)')
        fig.update_traces(hovertemplate='%{y:.1f}<br>%{x}')

        lgdtxt='Suivi des puissances consommées et de la puissance solaire produite au pas de 10 minutes/10 minutes'
        lgdtxt = textwrap.wrap(lgdtxt,width=20)
        lgdtxt = ' <br> '.join(lgdtxt)
        # fig.add_annotation(x=1.08,y=-0.05,xref="paper",yref="paper",text=lgdtxt,showarrow=False,
        #     font=dict(family="Courier New, monospace",size=10,color="black"),align="left")
        fig.update_xaxes(tickfont_size=tfsize)
        fig = self.updateLegend(fig)
        return fig

    def fig_consoweek_sls(self,t1,tfsize=17,**kwargs):
        df = self.consoweek_sls(t1,**kwargs)
        ti=df.resample('1d').mean().index
        df.columns = ['Consommation électrique du site','Production solaire du site']
        fig = px.scatter(df)
        fig.update_traces(mode='lines+markers')
        for l in ti :
            fig.add_vline(x=l,xref='x', line_width=3, line_dash="solid", line_color="black")
        fig.update_layout(xaxis = dict(tickmode='array',tickvals = ti,ticktext = ti.strftime('%A %d %b %Y')))
        fig.update_xaxes({'range':[df.index[0],df.index[-1]]})
        fig.data[0].line.color = 'rgba(32,56,100,255)'# grid
        fig.data[1].line.color = 'rgba(147,164,188,255)'# grid
        fig.data[0].marker.color = 'rgba(32,56,100,255)'# grid
        fig.data[1].marker.color = 'rgba(147,164,188,255)'# grid
        fig.update_layout(yaxis_title_text = 'Puissance éléctrique active (en kW)')
        fig.update_layout(legend_title_text = '',xaxis_title_text = '')
        fig.update_traces(hovertemplate='%{y:.1f}<br>%{x}')

        fig.update_layout(title={'text': 'Suivi de la consommation et de la production électrique du site SLS Actiparc sur 1 semaine', 'x':0.5,'xanchor': 'center','yanchor': 'top'})
        lgdtxt = 'Données de puissance moyennées au pas horaire'
        lgdtxt = textwrap.wrap(lgdtxt,width=20)
        lgdtxt = ' <br> '.join(lgdtxt)
        # fig.add_annotation(x=1.1,y=0.05,xref="paper",yref="paper",text=lgdtxt,
        #     showarrow=False,font=dict(family="Courier New, monospace",size=10,color="black"),align="left")
        fig.update_xaxes(tickfont_size=tfsize)
        fig=self.updateLegend(fig)
        return fig

    def fig_consomonth_sls(self,t1,tfsize=17,**kwargs):
        df = self.consomonth_sls(t1,**kwargs)

        fig = px.bar(df,barmode="group")
        mondays = [k for k in df.index.strftime('%Y-%m-%d %H:%M:%S') if pd.to_datetime(k).weekday()==0]
        for l in mondays :
            fig.add_vline(x=l,xref='x', line_width=3, line_dash="solid", line_color="black")

        fig.data[0].marker.color = 'rgba(32,56,100,255)'# grid
        fig.data[1].marker.color = 'rgba(147,164,188,255)'# PV
        ti = df.index
        fig.update_layout(xaxis = dict(tickmode='array',tickvals = ti,ticktext = ti.strftime('%d/%m/%Y')))
        fig.update_layout(legend_title_text = '',xaxis_title_text = '')
        fig.update_layout(yaxis_title_text = 'Cumul d’énergie par jour (kWh)')
        titletxt='Suivi des bilans quotidiens de consommation et production électrique du site SLS Actiparc sur un mois'
        # fig.update_layout(title={'text': titletxt ,'y':1.05,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        fig.update_layout(title={'text': titletxt})
        lgdtxt = "Données d'énergies cumulées au pas journalier"
        lgdtxt = textwrap.wrap(lgdtxt,width=20)
        lgdtxt = ' <br> '.join(lgdtxt)
        # fig.add_annotation(x=1.08,y=0.05,xref="paper",yref="paper",text=lgdtxt,
        #     showarrow=False,font=dict(family="Courier New, monospace",size=10,color="black"),align="left")
        fig.update_xaxes(tickfont_size=tfsize)
        return self.updateLegend(fig)

    def fig_consoyear(self,t1,tfsize=17,mode='repartition'):
        if mode=='repartition':
            df = self.get_compteurs_sls_since_start(t1,level='singles')
            df.columns = self.get_description_tags_compteurs(df.columns)
            colors=self.utils.getColorHexSeq(len(df.columns),'tab20')
            barmode='relative'
        elif mode=='global':
            barmode='group'
            df = self.get_compteurs_sls_since_start(t1)
            keeptags = lambda x:[k for k in df.columns if x in k][0]
            abcd,e,f,pv = [keeptags(k) for k in ['A007','E001','F001','PV']]
            dffig=pd.DataFrame()
            dffig['consommation sls'] = df[abcd]-df[e]+df[f]+df[pv]
            dffig['production sls']   = df[pv]
            colors= [
            'rgba(147,164,188,255)',
            'rgba(32,56,100,255)'
            ]
            df=dffig
        df=df.diff().iloc[1:,:].fillna(0)
        df.index=[k.strftime('%b-%Y') for k in df.index]
        fig=px.bar(df.melt(ignore_index=False),y='value',color='variable',color_discrete_sequence=colors,barmode=barmode)
        fig.update_layout(legend_title_text = '',xaxis_title_text = '')
        fig.update_layout(yaxis_title_text = 'Cumul d’énergie par mois (kWh)')
        titletxt='Suivi des bilans mensuel de consommation et production électrique du site SLS Actiparc sur un mois'
        fig.update_layout(title={'text': titletxt})
        fig.update_xaxes(tickfont_size=tfsize)
        return self.updateLegend(fig)

    def fig_repartitioncompteurs_sls(self,t1,tfsize=17,**kwargs):
        df = self.conso_repartition_sls(t1)
        df.index = pd.to_datetime(df.index,utc=True).tz_convert('Europe/Paris')# convert datetime to utc

        ti=df.resample('1d').mean().index
        fig = px.area(df)
        fig.update_traces(mode='lines+markers')
        fig.update_layout(xaxis = dict(tickmode='array',tickvals = ti,ticktext = ti.strftime('%A %d %b %Y')))
        fig = px.area(df)
        fig = self.utils.updateColorMap(fig,'gist_ncar')
        for l in ti[1:] :
            fig.add_vline(x=l,xref='x', line_width=3, line_dash="solid", line_color="black")

        # fig.add_trace(go.Scatter(x=dfTotal.index,y=dfTotal['Consommation Totale du site du Cheylas']))
        # ,name='Consommation du site',line_color='black'))
        fig.update_layout(yaxis_title_text = 'Puissance éléctrique active (en kW)')
        fig.update_layout(legend_title_text = '',xaxis_title_text = '')

        fig.update_layout(title={'text': 'Répartition des puissances du site du Cheylas(semaine)'
                            ,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        # fig.add_annotation(x=1,y=-0.15,xref="paper",yref="paper",text='Données de puissance moyennées au pas horaire',
            # showarrow=False,font=dict(family="Courier New, monospace",size=10,color="black"),align="right")
        fig.update_xaxes(tickfont_size=tfsize)
        fig.update_traces(hovertemplate='%{y:.1f}<br>%{x}')

        return self.updateLegend(fig)
    # ==========================================================================
    #                       COMPUTATIONS FUNCTIONS
    # ==========================================================================
    def computePowerEnveloppe(self,timeRange,compteur = 'EM_VIRTUAL',rs='auto'):
        listTags = self.getTagsTU(compteur+'.+[0-9]-JTW','kW')
        df = self.df_loadTimeRangeTags(timeRange,listTags,rs='5s')
        L123min = df.min(axis=1)
        L123max = df.max(axis=1)
        L123moy = df.mean(axis=1)
        L123sum = df.sum(axis=1)
        df = pd.concat([df,L123min,L123max,L123moy,L123sum],axis=1)

        from dateutil import parser
        ts=[parser.parse(t) for t in timeRange]
        deltaseconds=(ts[1]-ts[0]).total_seconds()
        if rs=='auto':rs = '{:.0f}'.format(max(1,deltaseconds/1000)) + 's'
        df = df.resample(rs).apply(np.mean)
        dfmin = L123min.resample(rs).apply(np.min)
        dfmax = L123max.resample(rs).apply(np.max)
        df = pd.concat([df,dfmin,dfmax],axis=1)
        df.columns=['L1_mean','L2_mean','L3_mean','PminL123_mean','PmaxL123_mean',
                    'PmoyL123_mean','PsumL123_mean','PminL123_min','PmaxL123_max']
        return df

    def compute_kWhFromPower(self,timeRange,compteurs=['B001'],rs='raw'):
        generalPat='('+'|'.join(['(' + c + ')' for c in compteurs])+')'
        listTags = self.getTagsTU(generalPat+'.*sys-JTW')

        df = self.df_loadTimeRangeTags(timeRange,listTags,rs=rs,applyMethod='mean',pool=True)
        dfs=[]
        for tag in listTags:
            dftmp = self._integratePowerCol(df,tag,True)
            if not dftmp.empty:dfs.append(dftmp)

        try : df=pd.concat(dfs,axis=1)
        except : df = pd.DataFrame()
        return df.ffill().bfill()

    def compute_kWhFromCompteur(self,timeRange,compteurs=['B001']):
        generalPat='('+'|'.join(['(' + c + ')' for c in compteurs])+')'
        listTags = self.getTagsTU(generalPat+'.+kWh-JTWH')
        df = self.df_loadTimeRangeTags(timeRange,listTags,rs='raw',applyMethod='mean')
        df = df.drop_duplicates()
        dfs=[]
        for tag in listTags:
            x1=df[df.tag==tag]
            dfs.append(x1['value'].diff().cumsum()[1:])
        try :
            df = pd.concat(dfs,axis=1)
            df.columns = listTags
        except : df = pd.DataFrame()
        return df.ffill().bfill()

    def plot_compare_kwhCompteurvsPower(self,timeRange,compteurs=['B001'],rs='600s'):
        dfCompteur = self.compute_kWhFromCompteur(timeRange,compteurs)
        dfPower = self.compute_kWhFromPower(timeRange,compteurs)
        df = self.utils.prepareDFsforComparison([dfCompteur,dfPower],
                            ['energy from compteur','enery from Power'],
                            group1='groupPower',group2='compteur',
                            regexpVar='\w+-\w+',rs=rs)

        fig=px.line(df,x='timestamp',y='value',color='compteur',line_dash='groupPower',)
        fig=self.utils.quickLayout(fig,'energy consumed from integrated power and from energy counter',ylab='kWh')
        fig.update_layout(yaxis_title='energy consommée en kWh')
        return fig

    def energyPeriodBarPlot(self,timeRange,period='1d',compteurs = ['A003','B001']):
        dfCompteur   = self.compute_kWhFromCompteur(timeRange,compteurs)
        df = dfCompteur.resample(period).first().diff()[1:]
        fig = px.bar(df,title='répartition des énergies consommées par compteur')
        fig.update_layout(yaxis_title='énergie en kWh')
        fig.update_layout(bargap=0.5)
        return fig
    # ==========================================================================
    #                       for website monitoring
    # ==========================================================================
    # def getListTagsAutoConso(self,compteurs):
    #     pTotal = [self.getTagsTU(k + '.*sys-JTW')[0] for k in compteurs]
    #     pvPower = self.getTagsTU('PV.*-JTW-00')[0]
    #     listTagsPower = pTotal + [pvPower]
    #     energieTotale = [self.getTagsTU(k + '.*kWh-JTWH')[0] for k in compteurs]
    #     pvEnergie = self.getTagsTU('PV.*-JTWH-00')[0]
    #     listTagsEnergy = energieTotale + [pvEnergie]
    #     return pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy
    #
    # def computeAutoConso(self,timeRange,compteurs,formula='g+f-e+pv'):
    #     pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
    #     # df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'600s','mean')
    #     df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'600s','mean')
    #     if formula=='g+f-e+pv':
    #         g,e,f = [self.getTagsTU(k+'.*sys-JTW')[0] for k in ['GENERAL','E001','F001',]]
    #         df['puissance totale'] = df[g] + df[f] - df[e] + df[pvPower]
    #     elif formula=='sum-pv':
    #         df['puissance totale'] = df[pTotal].sum(axis=1) - df[pvPower]
    #     elif formula=='sum':
    #         df['puissance totale'] = df[pTotal].sum(axis=1)
    #
    #     df['diffPV']=df[pvPower]-df['puissance totale']
    #     dfAutoConso = pd.DataFrame()
    #     df['zero'] = 0
    #     dfAutoConso['part rSoc']     = 0
    #     dfAutoConso['part batterie'] = 0
    #     dfAutoConso['part Grid']     = -df[['diffPV','zero']].min(axis=1)
    #     dfAutoConso['Consommation du site']      = df['puissance totale']
    #     dfAutoConso['surplus PV']    = df[['diffPV','zero']].max(axis=1)
    #     dfAutoConso['part PV']       = df[pvPower]-dfAutoConso['surplus PV']
    #     # dfAutoConso['Autoconsommation'] = df[pvPower]-dfAutoConso['PV surplus']
    #     return dfAutoConso
    #
    # def consoPowerWeek(self,timeRange,compteurs,formula='g+f-e+pv'):
    #     pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
    #     # df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'1H','mean')
    #     df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'1H','mean')
    #
    #     if formula=='g+f-e+pv':
    #         g,e,f = [self.getTagsTU(k+'.*sys-JTW')[0] for k in ['GENERAL','E001','F001',]]
    #         df['puissance totale'] = df[g] + df[f] - df[e] + df[pvPower]
    #     elif formula=='sum-pv':
    #         df['puissance totale'] = df[pTotal].sum(axis=1) - df[pvPower]
    #     elif formula=='sum':
    #         df['puissance totale'] = df[pTotal].sum(axis=1)
    #
    #     df = df[['puissance totale',pvPower]]
    #     df.columns = ['consommation bâtiment','production PV']
    #     return df
    #
    # def compute_EnergieMonth(self,timeRange,compteurs,formula='g+f-e+pv'):
    #     pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
    #     # df = self.df_loadTimeRangeTags(timeRange,listTagsEnergy,rs='raw',applyMethod='mean')
    #     df = self.df_loadTimeRangeTags(timeRange,listTagsEnergy,rs='raw',applyMethod='mean')
    #     df = df.drop_duplicates()
    #
    #     df=df.pivot(columns='tag',values='value').resample('1d').first().ffill().bfill()
    #     newdf=df.diff().iloc[1:,:]
    #     newdf.index = df.index[:-1]
    #     if formula=='g+f-e+pv':
    #         g,e,f = [self.getTagsTU(k + '.*kWh-JTWH')[0] for k in ['GENERAL','E001','F001',]]
    #         newdf['energie totale'] = newdf[g] + newdf[f] - newdf[e] + newdf[pvEnergie]
    #     elif formula=='sum-pv':
    #         newdf['energie totale'] = newdf[pTotal].sum(axis=1) - newdf[pvEnergie]
    #     elif formula=='sum':
    #         newdf['energie totale'] = newdf[energieTotale].sum(axis=1)
    #
    #     newdf = newdf[['energie totale',pvEnergie]]
    #     newdf.columns = ['kWh consommés','kWh produits']
    #     return newdf
    #
    # def get_compteur(self,timeDate,compteurs,formula='g+f-e+pv'):
        timeRange = [k.isoformat() for k in [timeDate - dt.timedelta(seconds=600),timeDate]]
        pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
        df = self.df_loadTimeRangeTags(timeRange,listTagsEnergy,rs='20s',applyMethod='mean')
        g,e,f = [self.getTagsTU(k + '.*kWh-JTWH')[0] for k in ['GENERAL','E001','F001',]]
        if formula=='g+f-e+pv':
            df['energie totale'] = df[g] + df[f] - df[e] + df[pvEnergie]
        elif formula=='sum':
            df['energie totale'] = df[energieTotale].sum(axis=1)
        return df.iloc[-1,:]
    # ==============================================================================
    #                   GRAPHICAL FUNCTIONS
    # ==============================================================================
    def update_lineshape_fig(self,fig,style='default'):
        if style=='default':
            fig.update_traces(line_shape="linear",mode='lines+markers')
        elif style in ['markers','lines','lines+markers']:
            fig.update_traces(line_shape="linear",mode=style)
        elif style =='stairs':
            fig.update_traces(line_shape="hv",mode='lines')

    def multiUnitGraphSB(self,df,tagMapping=None,**kwargs):
        if not tagMapping:tagMapping = {t:self.getUnitofTag(t) for t in df.columns}
        fig = self.utils.multiUnitGraph(df,tagMapping,**kwargs)
        return fig

class ScreeningBuilding_VM(VersionManager_daily,Config_extender):
    def __init__(self,*args,**kwargs):
        Config_extender.__init__(self)
        VersionManager_daily.__init__(self,FOLDERPKL,CONFFOLDER + "/PLC_config/",*args,**kwargs)
        self.count_ids_0_0_to_O_1 = {
            '8-A004-':'9-A004-',
            'b-A005-':'c-A005-',
            '0f-A006-':'11-A006-',
            'd-B002-':'e-B002-',
            '7-B003-':'8-B003-',
            'e-B004-':'f-B004-',
            'a-D001-':'b-D001-',
            '9-D002-':'a-D002-',
            '10-E001-':'12-E001-',
            '11-E002-':'13-E002-',
            '12-F001-':'14-F001-',
            '13-F002-':'15-F002-',
            'c-F003-':'d-F003-'
        }

    def mergeTags_on_2022_01_07(self):
        '''on that day tags with 2 different count ids where dumped. Data look like :
        C000000c-F003-... and C00000d-F003. Need to be merged.
        -WORKS ONLY IF DATA OF 2022-01-07 ARE PRESENT
        '''
        folderday = self.folderData + '2022-01-07/'
        for oldcount,newcount in self.count_ids_0_0_to_O_1.items():
            ltags = pd.Series(self.fs.listfiles_pattern_folder(folderday,oldcount))
            # print(ltags)
            for tagold in ltags:
                tagnew = tagold.replace(oldcount,newcount)
                df1 = pickle.load(open(folderday + tagold,'rb'))
                df2 = pickle.load(open(folderday + tagnew,'rb'))
                # print(df1,df2)
                df = pd.concat([df1,df2]).sort_index()
                # print(df)
                df.to_pickle(folderday + tagnew)
                os.remove(folderday + tagold)
                print(tagold,' and ',tagnew,' were merged and ', tagold,' was removed.')

    def mergeTags_B008_F003_on_2022_01_04(self):
        '''on that day B008 and F003 were dumped. Data look like :
        -WORKS ONLY IF DATA OF 2022-01-04 ARE PRESENT
        '''
        folderday = self.folderData + '2022-01-04/'
        ltags = pd.Series(self.fs.listfiles_pattern_folder(folderday,'-B008'))
        # print(ltags)
        for tagold in ltags:
            tagnew = tagold.replace('-B008','-F003')
            df1 = pickle.load(open(folderday + tagold,'rb'))
            df2 = pickle.load(open(folderday + tagnew,'rb'))
            # print(df1,df2)
            df = pd.concat([df1,df2]).sort_index()
            # print(df)
            df.to_pickle(folderday + tagnew)
            os.remove(folderday + tagold)
            print(tagold,' and ',tagnew,' were merged and ', tagold,' was removed.')

    def get_renameTag_map_v0_0_to_v0_1(self):
        '''some counts had their ids temporarily decremented in december 2021
            correctly reincremented on the 2022-01-07.
            -WORKS ONLY IF DATA OF 2022-01-06 ARE PRESENT'''
        folderday = self.folderData + '2022-01-06/'
        count_ids=self.count_ids_0_0_to_O_1.copy()
        count_ids['14-GENE']='16-GENE'
        df_renametagsmap = {}
        for oldcount,newcount in count_ids.items():
            ltags = pd.Series(self.fs.listfiles_pattern_folder(folderday,oldcount))
            # print(ltags)
            ltags = [k.replace('.pkl','') for k in ltags]
            for oldtag in ltags:
                df_renametagsmap[oldtag] = oldtag.replace(oldcount,newcount)
        df_renametagsmap=pd.DataFrame({'oldtag':df_renametagsmap.keys(),'newtag':df_renametagsmap.values()})
        return df_renametagsmap

    def get_renameTag_map_v0_1_to_v0_2(self):
        '''
            - GENERAL-ADMINISTRATIF renamed in A007(on the 2022-01-07)
            - B008 was renamed in F003 (rename on the 2022-01-04)
            - E003, F004 counts were added (on the 2022-01-07)
            - B005,SIS,EM_VIRTUAL suppressed (on the 2022-01-07)
        '''
        df_renametagsmap = {}
        oldtags = list(self.df_plcs['0.1'].index)
        for oldtag in oldtags:
            newtag   = oldtag
            newtag   = newtag.replace('GENERAL_ADMINISTRATIF','A007')
            newtag   = newtag.replace('-B008','-F003')
            if len([k for k in ['-B005-','-EM_VIRTUAL-','SIS-'] if k in oldtag])>0:
                newtag=None
            df_renametagsmap[oldtag] = newtag
        df_renametagsmap = pd.DataFrame({'oldtag':df_renametagsmap.keys(),'newtag':df_renametagsmap.values()})

        newtags = list(self.df_plcs['0.2'].index)
        brand_newtags = [t for t in newtags if t not in list(df_renametagsmap['newtag'])]
        brand_newtags = pd.DataFrame([(None,k) for k in brand_newtags],columns=['oldtag','newtag'])
        df_renametagsmap=pd.concat([df_renametagsmap,brand_newtags])
        return df_renametagsmap[~df_renametagsmap.apply(lambda x: x['oldtag']==x['newtag'],axis=1)]

    def get_renameTag_map_v0_2_to_v1_0(self):
        '''
            - point de comptage are removed in tag names :
                ex : C0000000d-F003-13-kWh-JTWH ====> C0000000d-F003-kWh-JTWH
            - 00 at the end of PV00000001 removed.
            - XM meteo data for le cheylas added
        '''
        df_renametagsmap = {}
        oldtags=list(self.df_plcs['0.2'].index)
        for oldtag in oldtags:
            tagsplit = oldtag.split('-')
            newtag   = oldtag
            if not re.match('C[0-9a-f]{8}',oldtag) is None:
                newtag = '-'.join(tagsplit[0:2]+tagsplit[3:])

            newtag= newtag.replace('PV00000001-centrale SLS 80kWc-JTW-00','PV00000001-centrale SLS 80kWc-kW-JTW')
            newtag= newtag.replace('PV00000001-centrale SLS 80kWc-JTWH-00','PV00000001-centrale SLS 80kWc-kWh-JTWH')
            df_renametagsmap[oldtag] = newtag
        df_renametagsmap=pd.DataFrame({'oldtag':df_renametagsmap.keys(),'newtag':df_renametagsmap.values()})

        newtags=list(self.df_plcs['1.0'].index)
        brand_newtags = [t for t in newtags if t not in list(df_renametagsmap['newtag'])]
        brand_newtags = pd.DataFrame([(None,k) for k in brand_newtags],columns=['oldtag','newtag'])
        df_renametagsmap=pd.concat([df_renametagsmap,brand_newtags])
        return df_renametagsmap
