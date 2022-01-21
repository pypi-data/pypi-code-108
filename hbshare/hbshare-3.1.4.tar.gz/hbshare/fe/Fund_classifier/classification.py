import datetime
import pandas as pd
import numpy as np
from hbshare.fe.XZ import db_engine
from hbshare.fe.nav_attr import nav_attribution
from hbshare.fe.Machine_learning import classifier
import joblib

class Classifier_Ml:

    def __init__(self,asofdate=None):

        self.localengine=db_engine.PrvFunDB().engine
        self.hbdb=db_engine.HBDB()
        self.theme_map={'大金融' : ['银行','券商','房地产','保险','非银金融'],
                   '消费' : ['美容护理','家用电器','酒类','制药','医疗保健','生物科技','商业服务','零售','纺织服装','食品','农业','家居用品','餐饮旅游','软饮料','医药生物','商业贸易','商贸零售','食品饮料','农林牧渔','休闲服务','纺织服饰'],
                   'TMT' : ['半导体','电子元器件','电脑硬件','软件','互联网','文化传媒','电子','计算机','传媒','通信'],
                   '周期': ['采掘','有色金属','化工原料','基本金属','贵金属','钢铁','化纤','建筑','煤炭','化肥农药','石油天然气','日用化工','建材','石油化工','石油石化','化工','基础化工','黑色金属'],
                   '制造' : ['精细化工','建筑材料','工业机械','电工电网','电力','发电设备','汽车零部件','航天军工','能源设备','航空','环保','汽车','通信设备','海运','工程机械','国防军工','电力设备','电气设备','机械设备','建筑装饰','公用事业','环保','交通运输','制造','社会服务','轻工制造'],
                   }
        if(asofdate is None):
            self.today=str(datetime.datetime.today().date())
        else:
            self.today=asofdate
        self.style_label=self.read_style_lable_fromhbdb()
        self.theme_label=self.read_theme_lable_fromloacldb()
        self.risk_label=self.read_risk_level_fromloacldb()

        sql = "select max(JYRQ) as JYRQ from funddb.JYRL where SFYM='1' and JYRQ>='{0}' and JYRQ<='{1}' "\
            .format(str(int(self.today.split('-')[0])-1)+'1201',str(int(self.today.split('-')[0])-1)+'1231')
        self.lastyearend =self.hbdb.db2df(sql,db='readonly')['JYRQ'][0]
        print('the data used for trainning the style,theme model is later than {}'.format(self.lastyearend))

        sql = """
        select max(tjrq) as tjrq from st_fund.r_st_nav_attr_df where jjdm='000001' and tjrq<='{0}' and tjrq>='{1}'
        """.format(self.today.split('-')[0]+self.today.split('-')[1]+self.today.split('-')[2],str(int(self.today.split('-')[0])-1)+'0101')
        self.exp_quater=self.hbdb.db2df(sql=sql, db='funduser')['tjrq'][0]
        print("the data used for style,theme predition is no later than {}".format(self.exp_quater))
        self.vol_term=['2101','2103','2106','2201','2999']

        sql = "select max(tjrq) as tjrq from st_hedge.t_st_sm_zqjbdl where zblb='2101' and  tjrq<='{0}' and tjrq>='{1}' " \
            .format(self.today.split('-')[0]+self.today.split('-')[1]+self.today.split('-')[2],str(int(self.today.split('-')[0])-1)+'0101')
        self.vol_week=self.hbdb.db2df(sql=sql, db='highuser')['tjrq'][0]
        print('the data used for vol lable trainnning and prediction is no later than {}'.format(self.vol_week))

        self.clbz={"1":"存量","2":"关注","3":"FOF核心","4":"FOF非核心"}

    def wind_theme_data2localdb(self,asofdate):

        fund_theme=pd.read_csv(r"E:\基金分类\wind主题分类.csv",encoding='gbk')
        fund_theme['证券代码'] = [x.split('.')[0] for x in fund_theme['证券代码']]
        fund_theme['所属主题基金类别(Wind行业)'] = [x.split('行业')[0] for x in fund_theme['所属主题基金类别(Wind行业)']]
        fund_theme['record_date']=asofdate
        fund_theme.to_sql('mutual_fund_theme',con=self.localengine,index=False,if_exists='append')

    def wind_risk_data2localdb(self,asofdate):

        fund_theme=pd.read_csv(r"E:\基金分类\windrisk.csv",encoding='gbk')
        fund_theme['证券代码'] = [x.split('.')[0] for x in fund_theme['证券代码']]
        fund_theme['基金风险等级'] = [x.split('-')[0] for x in fund_theme['基金风险等级']]
        fund_theme['record_date']=asofdate
        fund_theme.to_sql('wind_fund_risk_level',con=self.localengine,index=False,if_exists='append')

    def wind_stock_style_data2localdb(self,asofdate):

        fund_theme=pd.read_csv(r"E:\基金分类\股票风格.csv",encoding='gbk')
        fund_theme['证券代码'] = [x.split('.')[0] for x in fund_theme['证券代码']]
        fund_theme['record_date']=asofdate
        fund_theme.to_sql('wind_stock_style',con=self.localengine,index=False,if_exists='append')

    def lable_trans(self,inputdf):

        fg_dict={
                '1':'成长',
                '2': '均衡',
                '3': '价值'
        }
        sz_dict={
            '1': '小盘',
            '2': '中盘',
            '3': '大盘'
        }
        for key in fg_dict.keys():
            inputdf.loc[inputdf['wdfgsx']==key,'wdfgsx']=fg_dict[key]
        for key in sz_dict.keys():
            inputdf.loc[inputdf['wdszsx']==key,'wdszsx']=sz_dict[key]

        return  inputdf

    def theme_trans(self,fund_theme):

        for key in self.theme_map.keys():
            map_list=self.theme_map[key]
            for industry in map_list:
                fund_theme.loc[fund_theme['所属主题基金类别(Wind行业)']==industry,'所属主题基金类别(Wind行业)']=key

        return fund_theme

    def read_mu_extra_info(self):

        sql="select jjdm,jjjc from st_fund.t_st_gm_jjxx where cpfl='2'"
        jjdm=self.hbdb.db2df(sql,db='funduser')

        tempdf=self.lable_trans(self.style_label.copy())
        tempdf['style']=tempdf['wdszsx']+tempdf['wdfgsx']
        jjdm=pd.merge(jjdm,tempdf[['jjdm','style']],how='left',on='jjdm')

        tempdf= self.theme_trans(self.theme_label.copy())
        tempdf.rename(columns={'所属主题基金类别(Wind行业)':'theme'},inplace=True)
        jjdm = pd.merge(jjdm, tempdf, how='left', left_on='jjdm',right_on='证券代码').drop('证券代码',axis=1)

        jjdm = pd.merge(jjdm, self.risk_label, how='left',  left_on='jjdm',right_on='证券代码').drop('证券代码',axis=1)
        jjdm.rename(columns={'基金风险等级':'risk_level'},inplace=True)
        return jjdm

    def get_fund_basicinfo(self):

        sql="""
        select jjdm,wdfgsx,wdszsx,clrq,zzrq from st_fund.t_st_gm_jjxx 
        where wdfgsx is not null and  wdszsx is not null and cpfl='2'
        """
        fund_df=self.hbdb.db2df(sql=sql,db='funduser')

        sql= "select distinct(jjdm) from funddb.jjxx1"
        left_df=self.hbdb.db2df(sql=sql,db='readonly')
        fund_df=pd.merge(left_df,fund_df,how='inner',left_on='JJDM',right_on='jjdm').drop(['JJDM','ROW_ID'],axis=1)

        today=self.today
        today=''.join(today.split('-'))

        return fund_df.fillna(today)

    def save_exp_df2db(self):
        funddf = self.get_fund_basicinfo()
        fg_exp_df = pd.DataFrame()

        record=[]

        for i in range(len(funddf)):
            jjdm = funddf.iloc[i]['jjdm']
            start_date = str(funddf.iloc[i]['clrq'])
            end_date = str(funddf.iloc[i]['zzrq'])
            sql="select jzrq from st_fund.t_st_gm_jjjz where jjdm='{0}' and jzrq>='{1}' and jzrq<={2}"\
                .format(jjdm,str(int(end_date[0:4])-1)+"0101",end_date)
            jzrq=self.hbdb.db2df(sql=sql, db='funduser')['jzrq'].values
            gap=pd.Series(jzrq[1:]-jzrq[0:-1]).mode()[0]
            if(gap==1):
                fre='day'
            elif(gap==7):
                fre='week'
            try:
                nav_attr = nav_attribution.StyleAttribution(fund_id=jjdm, fund_type='mutual', start_date=start_date,
                                                            end_date=end_date, factor_type='style_allo',
                                                            benchmark_id='000300',
                                                            nav_frequency=fre).get_all(processed=False)['attribution_df']
            except Exception:
                record.append(i)
                continue


            fg_exp_df = pd.concat([fg_exp_df, nav_attr['factor_exposure'].to_frame().T], axis=0)
            print('the {1}th data {0} done..'.format(jjdm,str(i)))


        fg_exp_df.columns=nav_attr['style_factor']
        fg_exp_df['jjdm']=funddf['jjdm']
        fg_exp_df['wdfgsx']=funddf['wdfgsx']
        fg_exp_df['wdszsx'] = funddf['wdszsx']
        today=self.today
        today=''.join(today.split('-'))
        fg_exp_df['end_date']=today
        fg_exp_df.to_sql('style_exp', con=self.localengine)
        record_df=pd.DataFrame(data=record,columns=['wrong_i'])
        record_df.to_csv('record_i.csv')


        print('data saved in table style_exp')

    def read_style_lable_fromhbdb(self):

        sql="""
        select jjdm,wdfgsx,wdszsx from st_fund.t_st_gm_jjxx 
        where wdfgsx in ('1','2','3') and  wdszsx in ('1','2','3') and cpfl='2'
        """
        fund_df=self.hbdb.db2df(sql=sql,db='funduser')

        return fund_df

    def read_hld_ind_fromdb(self,start_date,end_date,ext_con=''):

        sql = """select distinct jsrq  from st_fund.t_st_gm_gpzhhytj where hyhfbz= 2 and jsrq>='{0}' and jsrq<='{1}'
        """.format( start_date, end_date)
        data_list=self.hbdb.db2df(sql,db='funduser')['jsrq'].tolist()[-2:]

        sql = """select jjdm,jsrq,fldm,zzjbl from st_fund.t_st_gm_gpzhhytj where hyhfbz=2 and zzjbl<200 and jsrq>='{0}' and jsrq<='{1}' {2} 
        """.format( data_list[0], data_list[1],ext_con)
        hld = self.hbdb.db2df(sql, db='funduser')
        hld['jsrq'] = hld['jsrq'].astype(str)
        fldm_list=hld['fldm'].unique().tolist()
        fldm_con="'"+"','".join(fldm_list)+"'"

        sql="select fldm,flmc from st_fund.t_st_gm_zqhyflb where fldm in ({0}) and hyhfbz=2 ".format(fldm_con)
        industry_map=self.hbdb.db2df(sql,db='funduser')
        industry_map.drop_duplicates(inplace=True)

        hld=pd.merge(hld,industry_map,how='left',on='fldm')
        #hld['flmc']=[ self.industry_name_map[x] for x in hld['flmc']]

        hld.loc[hld['zzjbl']==99999,'zzjbl']=0

        hld.rename(columns={'flmc':'所属主题基金类别(Wind行业)'},inplace=True)
        hld=self.theme_trans(hld)
        hld.drop(hld[hld['所属主题基金类别(Wind行业)']=='综合'].index,inplace=True,axis=0)

        return hld[['jsrq','jjdm','所属主题基金类别(Wind行业)','zzjbl']]

    def read_hld_fromdb(self,start_date,end_date,ext_con=''):

        sql = """select distinct(jsrq) from st_fund.t_st_gm_gpzh where jsrq>='{0}' and jsrq<='{1}' {2}
        """.format(start_date,end_date,ext_con)
        data_list=self.hbdb.db2df(sql,db='funduser')['jsrq'].tolist()[-2:]

        sql="""select jjdm,jsrq,zqdm,zjbl from st_fund.t_st_gm_gpzh where jsrq='{0}' or jsrq='{1}' {2}
        """.format(data_list[0],data_list[1],ext_con)
        hld=self.hbdb.db2df(sql,db='funduser')
        hld['jsrq']=hld['jsrq'].astype(str)

        return hld

    def read_exp_fromhbdb(self,asofdate,attr_type,if_train=True):

        if(if_train):

            sql="""
            select jjdm,style_factor,data_value from st_fund.r_st_nav_attr_df where attr_type='{1}' 
            and tjrq='{0}' and data_type='exposure'
            """.format(asofdate,attr_type)
            exp_df=self.hbdb.db2df(sql=sql,db='funduser')


        else:

            sql="select jjdm from st_hedge.t_st_jjxx where clbz in ('1','2','3','4') and jjfl='1' "
            prv_list=self.hbdb.db2df(sql=sql,db='highuser')['jjdm'].tolist()
            list_con="'"+"','".join(prv_list)+"'"

            sql="""
            select jjdm,style_factor,data_value from st_hedge.r_st_nav_attr_df where attr_type='{1}' 
            and tjrq='{0}' and data_type='exposure' and jjdm in ({2})
            """.format(asofdate,attr_type,list_con)
            exp_df_prv=self.hbdb.db2df(sql=sql,db='highuser')

            if(attr_type=='style_allo'):
                sql = """
                select jjdm from st_fund.t_st_gm_jjxx 
                where wdfgsx is null or  wdszsx is null and cpfl='2' and (jjfl='1' or jjfl='4') 
                """

                mu_list = self.hbdb.db2df(sql=sql, db='funduser')['jjdm'].tolist()

            else:
                sql = """
                select jjdm from st_fund.t_st_gm_jjxx 
                where cpfl='2' and (jjfl='1' or jjfl='4')
                """
                mu_list1 = self.hbdb.db2df(sql=sql, db='funduser')['jjdm'].tolist()

                mu_list2=self.read_theme_lable_fromloacldb()['证券代码']
                mu_list=list(set(mu_list1).difference(set(mu_list2)))

            list_con = "'" + "','".join(mu_list) + "'"

            sql="""
            select jjdm,style_factor,data_value from st_fund.r_st_nav_attr_df where attr_type='{1}' 
            and tjrq='{0}' and data_type='exposure' and jjdm in({2})
            """.format(asofdate,attr_type,list_con)
            exp_df_mu=self.hbdb.db2df(sql=sql,db='funduser')

            exp_df=pd.concat([exp_df_prv,exp_df_mu],axis=0)


        exp_df.sort_values(by='jjdm', inplace=True)
        exp_df.reset_index(drop=True, inplace=True)

        return exp_df

    def read_vol_fromhbdb(self,asofdate,if_train=True):

        term_con="'"+"','".join(self.vol_term)+"'"

        if(if_train):
            sql="select jjdm,zblb,zbnp from st_fund.t_st_gm_zqjbdl where tjrq={0} and zblb in ({1}) "\
                .format(asofdate,term_con)
            fund_vol=self.hbdb.db2df(sql,db='funduser')

        else:

            sql="select jjdm from st_hedge.t_st_jjxx where clbz in ('1','2','3','4') and jjfl='1' "
            prv_list=self.hbdb.db2df(sql=sql,db='highuser')['jjdm'].tolist()
            list_con="'"+"','".join(prv_list)+"'"

            sql="select jjdm,tjrq from st_hedge.t_st_sm_zqjbdl where jjdm in ({0}) and zblb='2999' and tjrq>={1} "\
                .format(list_con,str(int(self.today.split('-')[0])-1)+self.today[5:7]+self.today[8:10])
            tjrqdf=self.hbdb.db2df(sql,db='highuser')
            tjrqdf=tjrqdf.groupby(by='jjdm').max()

            fund_vol_prv=pd.DataFrame()
            for jjdm in tjrqdf.index:

                sql="select jjdm,zblb,zbnp from st_hedge.t_st_sm_zqjbdl where tjrq='{0}' and zblb in ({1}) and jjdm ='{2}' "\
                    .format(tjrqdf['tjrq'][jjdm],term_con,jjdm)
                fund_vol_prv=pd.concat([fund_vol_prv,self.hbdb.db2df(sql,db='highuser')],axis=0)


            sql = "select distinct record_date from  wind_fund_risk_level where record_date<='{0}' " \
                .format(self.today)
            latest_date = pd.read_sql(sql, con=self.localengine).sort_values('record_date')['record_date'].tolist()[-1]

            sql = "select 证券代码 from wind_fund_risk_level where record_date='{}'".format(latest_date)
            mu_list = pd.read_sql(sql, con=self.localengine)['证券代码'].tolist()
            list_con = "'" + "','".join(mu_list) + "'"

            sql="select jjdm,tjrq from st_fund.t_st_gm_zqjbdl where zblb='2999' and tjrq>={0} and jjdm not in ({1}) "\
                .format(str(int(self.today.split('-')[0])-1)+self.today[5:7]+self.today[8:10],list_con)
            tjrqdf=self.hbdb.db2df(sql,db='funduser')
            tjrqdf=tjrqdf.groupby(by='jjdm').max()

            fund_vol_mu=pd.DataFrame()
            for jjdm in tjrqdf.index:
                sql="select jjdm,zblb,zbnp from st_fund.t_st_gm_zqjbdl where  tjrq='{0}' and zblb in ({1}) and jjdm ='{2}'"\
                    .format(tjrqdf['tjrq'][jjdm],term_con,jjdm)
                fund_vol_mu = pd.concat([fund_vol_mu, self.hbdb.db2df(sql, db='funduser')], axis=0)

            fund_vol=pd.concat([fund_vol_prv,fund_vol_mu],axis=0)


        fund_vol.sort_values(by='jjdm', inplace=True)
        fund_vol.reset_index(drop=True, inplace=True)

        return fund_vol

    def read_exp_from_hld(self,asofdate,attr_type,if_train=True):

        start_date=str(int(asofdate.split('-')[0])-1)+asofdate.split('-')[1]+asofdate.split('-')[2]
        end_date=asofdate.split('-')[0]+asofdate.split('-')[1]+asofdate.split('-')[2]

        if(if_train):
            ext_con=''
        else:
            if (attr_type == 'style_allo'):
                sql = """
                select jjdm from st_fund.t_st_gm_jjxx 
                where (wdfgsx is null or  wdszsx is null) and cpfl='2' and (jjfl='1' or jjfl='4')
                """
                mu_list = self.hbdb.db2df(sql=sql, db='funduser')['jjdm'].tolist()

            else:
                sql = """
                select jjdm from st_fund.t_st_gm_jjxx 
                where cpfl='2' and (jjfl='1' or jjfl='4')
                """
                mu_list1 = self.hbdb.db2df(sql=sql, db='funduser')['jjdm'].tolist()

                mu_list2 = self.read_theme_lable_fromloacldb()['证券代码']
                mu_list = list(set(mu_list1).difference(set(mu_list2)))

            ext_con ="and jjdm in ("+ "'" + "','".join(mu_list) + "'"+")"

        if(attr_type=='style_allo'):

            hld = self.read_hld_fromdb(start_date, end_date,ext_con)
            ticker_list = hld['zqdm'].unique().tolist()
            ticker_con = "'" + "','".join(ticker_list) + "'"

            styledf=self.read_stock_style_fromloacldb(ticker_con)

            hld = pd.merge(hld, styledf[['证券代码', '所属规模风格类型']], how='left', left_on='zqdm', right_on='证券代码')

            # for date in hld['jsrq'].unique().tolist():
            date = hld['jsrq'].unique().tolist()[0]
            tempdf1 = hld[hld['jsrq'] == date].groupby(by=['jjdm', '所属规模风格类型'], as_index=False).sum()
            weight = hld[hld['jsrq'] == date].groupby(by=['jjdm'], as_index=False).sum()
            tempdf1 = pd.merge(tempdf1, weight, how='left', on='jjdm')
            tempdf1['data_value'] = tempdf1['zjbl_x'] / tempdf1['zjbl_y'] * 100

            date = hld['jsrq'].unique().tolist()[1]
            tempdf2 = hld[hld['jsrq'] == date].groupby(by=['jjdm', '所属规模风格类型'], as_index=False).sum()
            weight = hld[hld['jsrq'] == date].groupby(by=['jjdm'], as_index=False).sum()
            tempdf2 = pd.merge(tempdf2, weight, how='left', on='jjdm')
            tempdf2['data_value'] = tempdf2['zjbl_x'] / tempdf2['zjbl_y'] * 100

            tempdf = pd.merge(tempdf1[['jjdm', '所属规模风格类型', 'data_value']]
                              , tempdf2[['jjdm', '所属规模风格类型', 'data_value']]
                              , how='outer', on=['jjdm', '所属规模风格类型'])
            tempdf['data_value'] = tempdf[['data_value_x', 'data_value_y']].mean(axis=1)
            tempdf.rename(columns={'所属规模风格类型': 'style_factor'}, inplace=True)
            tempdf['style_factor']=[x[0:4] for x in tempdf['style_factor']]
            outputdf=tempdf.copy()

        elif(attr_type=='sector'):

            hld = self.read_hld_ind_fromdb(start_date, end_date,ext_con)
            # for date in hld['jsrq'].unique().tolist():
            date = hld['jsrq'].unique().tolist()[0]
            tempdf1 = hld[hld['jsrq']==date].groupby(by=['jjdm', '所属主题基金类别(Wind行业)'], as_index=False).sum()
            weight = hld[hld['jsrq'] == date].groupby(by=['jjdm'], as_index=False).sum()
            tempdf1 = pd.merge(tempdf1, weight, how='left', on='jjdm')
            tempdf1['data_value'] = tempdf1['zzjbl_x'] / tempdf1['zzjbl_y'] * 100

            date = hld['jsrq'].unique().tolist()[1]
            tempdf2 = hld[hld['jsrq'] == date].groupby(by=['jjdm', '所属主题基金类别(Wind行业)'], as_index=False).sum()
            weight = hld[hld['jsrq'] == date].groupby(by=['jjdm'], as_index=False).sum()
            tempdf2 = pd.merge(tempdf2, weight, how='left', on='jjdm')
            tempdf2['data_value'] = tempdf2['zzjbl_x'] / tempdf2['zzjbl_y'] * 100

            tempdf = pd.merge(tempdf1[['jjdm', '所属主题基金类别(Wind行业)', 'data_value']]
                              , tempdf2[['jjdm', '所属主题基金类别(Wind行业)', 'data_value']]
                              , how='outer', on=['jjdm', '所属主题基金类别(Wind行业)'])
            tempdf['data_value'] = tempdf[['data_value_x', 'data_value_y']].mean(axis=1)

            tempdf.rename(columns={'所属主题基金类别(Wind行业)':'style_factor'},inplace=True)

            outputdf = pd.DataFrame()
            outputdf['jjdm'] = tempdf['jjdm'].unique().tolist() * 5
            jjdm_len = len(tempdf['jjdm'].unique())
            style_list = []
            for style in tempdf['style_factor'].unique():
                style_list += [style] * jjdm_len
            outputdf['style_factor'] = style_list

            outputdf = pd.merge(outputdf, tempdf, how='left', on=['jjdm', 'style_factor'])
            outputdf.fillna(0, inplace=True)

        else:
            raise Exception

        return outputdf[['style_factor','data_value','jjdm']]

    def read_theme_lable_fromloacldb(self):

        sql="select distinct record_date from  mutual_fund_theme where record_date<='{0}' "\
            .format(self.today)
        latest_date=pd.read_sql(sql,con=self.localengine).sort_values('record_date')['record_date'].tolist()[-1]

        sql="select * from mutual_fund_theme where record_date='{0}'".format(latest_date)
        fund_theme=pd.read_sql(sql,con=self.localengine)

        return fund_theme[['证券代码','所属主题基金类别(Wind行业)']]

    def read_risk_level_fromloacldb(self):

        sql="select distinct record_date from  wind_fund_risk_level where record_date<='{0}' "\
            .format(self.today)
        latest_date=pd.read_sql(sql,con=self.localengine).sort_values('record_date')['record_date'].tolist()[-1]

        sql="select * from wind_fund_risk_level where record_date='{}'".format(latest_date)
        fund_risk=pd.read_sql(sql,con=self.localengine)

        return fund_risk[['证券代码','基金风险等级']]

    def read_stock_style_fromloacldb(self,ticker_con):

        sql="select distinct record_date from  wind_stock_style where record_date<='{0}' "\
            .format(self.today)
        latest_date=pd.read_sql(sql,con=self.localengine).sort_values('record_date')['record_date'].tolist()[-1]

        sql = "select * from wind_stock_style where 证券代码 in ({0}) and record_date='{1}'".format(ticker_con,latest_date)
        styledf = pd.read_sql(sql, con=self.localengine)
        return  styledf

    def model_selection(self,inputdf,features_col,label_col,dir):

        max_f1_score=0
        for modelname in ['xgboost','randomforest','svm']:
            model,f1_score=classifier.model_built_up(inputdf,label_col,modelname,features_col,0.2)
            if(f1_score>max_f1_score):
                max_f1_score=f1_score
                best_model=modelname

        print('The winning model is {0}'.format(best_model))
        model, f1_score = classifier.model_built_up(inputdf, label_col, best_model, features_col, 0)

        joblib.dump(model, dir)
        print("the best fited model is saved at E:\GitFolder\hbshare\fe\Fund_classifier ")

    def model_generation_style(self,value_style='nv'):

        print('Training the style label model...')

        #read the fund data with style lable
        fund_style=self.style_label.copy()

        if(value_style=='nv'):
            #read the style exposure of mutual fund from the hb data base
            style_exp=self.read_exp_fromhbdb(self.exp_quater,'style_allo')
        else:
            style_exp=self.read_exp_from_hld(self.today,'style_allo')

        inputdf=pd.DataFrame()
        inputdf['jjdm']=style_exp['jjdm'].unique()
        #reshape the exposure dataframe
        for style in ['小盘价值','小盘成长','中盘成长','中盘价值','大盘价值','大盘成长']:
            tempddf=style_exp[style_exp['style_factor']==style][['data_value','jjdm']]
            tempddf.rename(columns={'data_value':style},inplace=True)
            #inputdf[style]=style_exp[style_exp['style_factor']==style]['data_value'].values
            inputdf=pd.merge(inputdf,tempddf,how='left',on='jjdm').fillna(0)


        #join the two df
        inputdf=pd.merge(fund_style,inputdf,how='inner',left_on='jjdm',right_on='jjdm')
        del fund_style,style_exp

        #transfrom the style name from int to strings
        inputdf=self.lable_trans(inputdf)
        inputdf['Label']=inputdf['wdszsx']+inputdf['wdfgsx']
        inputdf.drop(['wdfgsx','wdszsx','jjdm'],axis=1,inplace=True)

        features_col=inputdf.columns.tolist()
        features_col.remove('Label')

        dir=r"E:\GitFolder\hbshare\fe\Fund_classifier\model_style_{1}_{0}.pkl".format(self.today,value_style)
        self.model_selection(inputdf=inputdf, features_col=features_col, label_col='Label', dir=dir)

    def model_generation_theme(self,value_style='nv'):

        print('Training the theme label model...')

        #read the fund data with theme lable
        fund_theme=self.theme_label.copy()
        if (value_style == 'nv'):
            #read the style exposure of mutual fund from the hb data base
            theme_exp=self.read_exp_fromhbdb(self.exp_quater,'sector')
        else:
            theme_exp=self.read_exp_from_hld(self.today,'sector')

        fund_theme=self.theme_trans(fund_theme)

        inputdf=pd.DataFrame()
        inputdf['jjdm']=theme_exp['jjdm'].unique()

        #reshape the exposure dataframe
        for style in self.theme_map.keys():
            inputdf[style]=theme_exp[theme_exp['style_factor']==style]['data_value'].values

        #join the two df
        inputdf=pd.merge(fund_theme,inputdf,how='inner',left_on='证券代码',right_on='jjdm').drop(['证券代码','jjdm'],axis=1)
        del fund_theme,theme_exp

        inputdf.rename(columns={'所属主题基金类别(Wind行业)':'Label'},inplace=True)

        features_col=inputdf.columns.tolist()
        features_col.remove('Label')

        dir=r"E:\GitFolder\hbshare\fe\Fund_classifier\model_theme_{1}_{0}.pkl".format(self.today,value_style)

        self.model_selection(inputdf=inputdf, features_col=features_col, label_col='Label', dir=dir)

    def model_generation_risk_level(self):

        print('Training the risk label model...')

        # read the fund data with risk lable from local db
        fund_risk=self.risk_label.copy()

        # read the vol data of mutual fund from the hb data base
        fund_vol=self.read_vol_fromhbdb(asofdate=self.vol_week,if_train=True)

        inputdf=pd.DataFrame()
        inputdf['jjdm']=fund_vol['jjdm'].unique()

        #reshape the exposure dataframe
        for risk in self.vol_term:
            inputdf[risk]=fund_vol[fund_vol['zblb']==risk]['zbnp'].values

        #join the two df
        inputdf=pd.merge(fund_risk,inputdf,how='inner',left_on='证券代码',right_on='jjdm').drop(['证券代码','jjdm'],axis=1)
        del fund_risk,fund_vol
        inputdf.rename(columns={'基金风险等级':'Label'},inplace=True)

        temp_col=self.vol_term.copy()
        temp_col.remove('2999')
        #deal with the outliers by assuming that the vol for certain term equals to its vol since established
        for col in temp_col :
            inputdf.loc[inputdf[col]==99999,col]=inputdf[inputdf[col]==99999]['2999']

        features_col=inputdf.columns.tolist()
        features_col.remove('Label')

        dir=r"E:\GitFolder\hbshare\fe\Fund_classifier\model_risk_{0}.pkl".format(self.today)

        self.model_selection(inputdf=inputdf,features_col=features_col,label_col='Label',dir=dir)

    def label_style(self,asofdate,filename,value_style='nv'):

        #load the trained style lable model
        dir=r"E:\GitFolder\hbshare\fe\Fund_classifier\{}".format(filename)
        trained_model= joblib.load(dir)

        if(value_style=='nv'):
            #read the style exposure of target priviate fund from the hb data base
            style_exp=self.read_exp_fromhbdb(asofdate,'style_allo',if_train=False)
        else:
            style_exp = self.read_exp_from_hld(self.today, 'style_allo',if_train=False)

        inputdf=pd.DataFrame()
        inputdf['jjdm']=style_exp['jjdm'].unique()
        #reshape the exposure dataframe
        for style in ['小盘价值','小盘成长','中盘成长','中盘价值','大盘价值','大盘成长']:
            tempddf=style_exp[style_exp['style_factor']==style][['data_value','jjdm']]
            tempddf.rename(columns={'data_value':style},inplace=True)
            #inputdf[style]=style_exp[style_exp['style_factor']==style]['data_value'].values
            inputdf=pd.merge(inputdf,tempddf,how='left',on='jjdm').fillna(0)
        del style_exp

        #make the prediction of the lables
        label=trained_model.predict(inputdf[['小盘价值','小盘成长','中盘成长','中盘价值','大盘价值','大盘成长']])
        inputdf['style']=label
        print('style label marked')
        return inputdf[['jjdm','style']]

    def label_theme(self,asofdate,filename,value_style='nv'):

        # load the trained style lable model
        dir = r"E:\GitFolder\hbshare\fe\Fund_classifier\{}".format(filename)
        trained_model = joblib.load(dir)
        if (value_style == 'nv'):
            # read the style exposure of target priviate fund from the hb data base
            theme_exp = self.read_exp_fromhbdb(asofdate, 'sector', if_train=False)
        else:
            theme_exp = self.read_exp_from_hld(self.today, 'sector',if_train=False)

        inputdf = pd.DataFrame()
        inputdf['jjdm'] = theme_exp['jjdm'].unique()

        # reshape the exposure dataframe
        for style in self.theme_map.keys():
            inputdf[style] = theme_exp[theme_exp['style_factor'] == style]['data_value'].values

        # make the prediction of the lables
        label = trained_model.predict(inputdf[self.theme_map.keys()])
        inputdf['theme'] = label
        print('theme label marked')
        return inputdf[['jjdm','theme']]

    def label_risk(self, asofdate, filename):

        # load the trained style lable model
        dir = r"E:\GitFolder\hbshare\fe\Fund_classifier\{}".format(filename)
        trained_model = joblib.load(dir)

        # read the vol data of priviate fund from the hb data base
        fund_vol=self.read_vol_fromhbdb(asofdate=asofdate,if_train=False)

        inputdf = pd.DataFrame()
        inputdf['jjdm'] = fund_vol['jjdm'].unique()

        #reshape the vol dataframe
        for risk in ['2101','2103','2106','2201','2999']:
            inputdf[risk]=fund_vol[fund_vol['zblb']==risk]['zbnp'].values

        #deal with the outliers by assuming that the vol for certain term equals to its vol since established
        for col in ['2101','2103','2106','2201']:
            inputdf.loc[inputdf[col]==99999,col]=inputdf[inputdf[col]==99999]['2999']

        # make the prediction of the lables
        label = trained_model.predict(inputdf[['2101','2103','2106','2201','2999']])
        inputdf['risk_level'] = label
        print('risk label marked')
        return inputdf[['jjdm','risk_level']]

    def read_fund_vol_fromdb_new(self,asofdate):

        # end_date=asofdate.replace('-','')
        # start_date=datetime.datetime.strftime(
        #     datetime.datetime.strptime(asofdate,"%Y-%m-%d")-datetime.timedelta(days=30),"%Y%m%d")

        end_date = asofdate
        start_date = datetime.datetime.strftime(
              datetime.datetime.strptime(asofdate,"%Y%m%d")-datetime.timedelta(days=30),"%Y%m%d")

        sql="select jjdm from st_fund.t_st_gm_jjxx where jjfl=1 or jjfl=3 "
        mu_stock_fund_list=self.hbdb.db2df(sql,db='funduser')['jjdm'].tolist()
        jjdmcon="'"+"','".join(mu_stock_fund_list)+"'"

        sql="select  jjdm,max(tjrq) as tjrq from st_fund.t_st_gm_zqjbdl where jjdm in ({2}) and zblb='2106' and tjrq>='{0}' and tjrq<='{1}' and zbnp!=99999 group by jjdm"\
            .format(start_date,end_date,jjdmcon)
        jjdmdf=self.hbdb.db2df(sql,db='funduser')
        tjrq_list=jjdmdf['tjrq'].unique().tolist()

        mu_vol=pd.DataFrame()
        for tjrq in tjrq_list:
            jjdm_list=jjdmdf[jjdmdf['tjrq']==tjrq]['jjdm'].to_list()
            jjdmcon="'"+"','".join(jjdm_list)+"'"
            sql="select jjdm,zbnp from st_fund.t_st_gm_zqjbdl where jjdm in ({0}) and zblb='2106' and tjrq='{1}'"\
                .format(jjdmcon,tjrq)
            mu_vol=pd.concat([mu_vol,self.hbdb.db2df(sql,db='funduser')],axis=0)

        sql = "select jjdm,max(tjrq) as tjrq from st_hedge.t_st_sm_zqjbdl where zblb='2106' and tjrq>='{0}' and tjrq<='{1}' and zbnp!=99999 group by jjdm" \
            .format(start_date,end_date)
        jjdmdf = self.hbdb.db2df(sql, db='highuser')
        tjrq_list = jjdmdf['tjrq'].unique().tolist()

        prv_vol=pd.DataFrame()
        for tjrq in tjrq_list:
            jjdm_list=jjdmdf[jjdmdf['tjrq']==tjrq]['jjdm'].to_list()
            jjdmcon="'"+"','".join(jjdm_list)+"'"
            sql="select jjdm,zbnp from st_hedge.t_st_sm_zqjbdl where jjdm in ({0}) and zblb='2106' and tjrq='{1}'"\
                .format(jjdmcon,tjrq)
            prv_vol=pd.concat([prv_vol,self.hbdb.db2df(sql,db='highuser')],axis=0)

        # sql = "select jjdm,zbnp from st_hedge.t_st_sm_zqjbdl where zblb='2106' and zbnp!=99999 and tjrq='{0}'"\
        #     .format(max(tjrq_list))
        # prv_vol=self.hbdb.db2df(sql,db='highuser')

        return mu_vol,prv_vol

    def read_fund_drawback_fromdb(self,asofdate):

        end_date=asofdate.replace('-','')
        start_date=datetime.datetime.strftime(
            datetime.datetime.strptime(asofdate,"%Y-%m-%d")-datetime.timedelta(days=30),"%Y%m%d")

        sql="select jjdm from st_fund.t_st_gm_jjxx where jjfl=1 or jjfl=3 "
        mu_stock_fund_list=self.hbdb.db2df(sql,db='funduser')['jjdm'].tolist()
        jjdmcon="'"+"','".join(mu_stock_fund_list)+"'"


        sql="select  jjdm,max(jzrq) as jzrq from st_fund.t_st_gm_rqjzdhc where jjdm in ({2}) and zblb='2106' and jzrq>='{0}' and jzrq<='{1}' and zbnp!=99999 group by jjdm"\
            .format(start_date,end_date,jjdmcon)
        jjdmdf=self.hbdb.db2df(sql,db='funduser')
        tjrq_list=jjdmdf['jzrq'].unique().tolist()

        mu_db=pd.DataFrame()
        for tjrq in tjrq_list:
            jjdm_list=jjdmdf[jjdmdf['jzrq']==tjrq]['jjdm'].to_list()
            jjdmcon="'"+"','".join(jjdm_list)+"'"
            sql="select jjdm,zbnp from st_fund.t_st_gm_rqjzdhc where jjdm in ({0}) and zblb='2106' and jzrq='{1}'"\
                .format(jjdmcon,tjrq)
            mu_db=pd.concat([mu_db,self.hbdb.db2df(sql,db='funduser')],axis=0)


        sql="select  jjdm,max(jzrq) as jzrq from st_hedge.t_st_sm_qjzdhc where zblb='2106' and jzrq>='{0}' and jzrq<='{1}' and zbnp!=99999 group by jjdm"\
            .format(start_date,end_date)
        jjdmdf=self.hbdb.db2df(sql,db='highuser')
        tjrq_list=jjdmdf['jzrq'].unique().tolist()

        prv_db=pd.DataFrame()
        for tjrq in tjrq_list:
            jjdm_list=jjdmdf[jjdmdf['jzrq']==tjrq]['jjdm'].to_list()
            jjdmcon="'"+"','".join(jjdm_list)+"'"
            sql="select jjdm,zbnp from st_hedge.t_st_sm_qjzdhc where jjdm in ({0}) and zblb='2106' and jzrq='{1}'"\
                .format(jjdmcon,tjrq)
            prv_db=pd.concat([prv_db,self.hbdb.db2df(sql,db='highuser')],axis=0)

        return mu_db,prv_db

    def label_risk_new(self,asofdate):

        mu_vol, prv_vol=self.read_fund_vol_fromdb_new(asofdate)

        temp=mu_vol.describe()
        mu_threshold=[(temp.loc['mean']-temp.loc['std'])[0],(temp.loc['mean']+temp.loc['std'])[0]]

        temp=prv_vol.describe()
        prv_threshold = [(temp.loc['mean']-temp.loc['std'])[0],(temp.loc['mean']+temp.loc['std'])[0]]

        mu_vol['risk_level']='中风险'
        mu_vol.loc[mu_vol['zbnp']<=mu_threshold[0],'risk_level']='低风险'
        mu_vol.loc[mu_vol['zbnp'] >= mu_threshold[1], 'risk_level'] = '高风险'
        prv_vol['risk_level'] = '中风险'
        prv_vol.loc[prv_vol['zbnp']<=prv_threshold[0],'risk_level']='低风险'
        prv_vol.loc[prv_vol['zbnp'] >= prv_threshold[1], 'risk_level'] = '高风险'

        mu_db, prv_db=self.read_fund_drawback_fromdb (asofdate)

        temp=mu_db.describe()
        mu_threshold=[(temp.loc['mean']-temp.loc['std'])[0],(temp.loc['mean']+temp.loc['std'])[0]]

        temp=prv_db.describe()
        prv_threshold = [(temp.loc['mean']-temp.loc['std'])[0],(temp.loc['mean']+temp.loc['std'])[0]]

        mu_db['draw_back_level']='中等回撤'
        mu_db.loc[mu_db['zbnp']<=mu_threshold[0],'draw_back_level']='低回撤'
        mu_db.loc[mu_db['zbnp'] >= mu_threshold[1], 'draw_back_level'] = '高回撤'
        prv_db['draw_back_level'] = '中等回撤'
        prv_db.loc[prv_db['zbnp']<=prv_threshold[0],'draw_back_level']='低回撤'
        prv_db.loc[prv_db['zbnp'] >= prv_threshold[1], 'draw_back_level'] = '高回撤'

        outputdf=pd.concat([mu_vol,prv_vol],axis=0)
        outputdf=pd.merge(outputdf[['jjdm','risk_level']],pd.concat([mu_db,prv_db],axis=0)[['jjdm','draw_back_level']],how='outer',on='jjdm')

        return outputdf.fillna('')

    def classify(self):

        style_label=self.label_style(asofdate=self.exp_quater,filename='model_style_2022-01-10.pkl')
        theme_label=self.label_theme(asofdate=self.exp_quater,filename='model_theme_2022-01-10.pkl')
        #risk_label=self.label_risk(asofdate=self.vol_week, filename='model_risk_2022-01-10.pkl')
        risk_label=self.label_risk_new(asofdate=self.exp_quater)

        style_label['style_source']='model'
        theme_label['theme_source'] = 'model'
        risk_label['risk_source'] = 'model'

        final_df=pd.merge(style_label,theme_label,how='outer',left_on='jjdm',right_on='jjdm')
        final_df=pd.merge(final_df,risk_label,how='outer',left_on='jjdm',right_on='jjdm')

        sql="select jjdm,jjjc,clbz from st_hedge.t_st_jjxx where jjdm in ({0}) "\
            .format("'"+"','".join(final_df['jjdm'].unique())+"'")
        extra_info_prv=self.hbdb.db2df(sql,db='highuser')
        for key in self.clbz.keys():
            extra_info_prv.loc[extra_info_prv['clbz']==key,'clbz']=self.clbz[key]

        final_df=pd.merge(final_df,extra_info_prv,how='left',on='jjdm')
        final_df.loc[final_df['clbz'].isnull(),'clbz']='公募'

        prv=final_df[final_df['clbz']!='公募']
        mu=final_df[final_df['clbz']=='公募']
        del final_df

        extra_info_mu=self.read_mu_extra_info()
        mu=pd.merge(extra_info_mu,mu,how='left',on='jjdm')

        mu.fillna('', inplace=True)

        for i in mu.index:
            if(mu.iloc[i]['style_x']=='' and mu.iloc[i]['style_y']!=''):
                mu.iloc[i]['style_x']=mu.iloc[i]['style_y']
            if((mu.iloc[i]['theme_x'] =='') and (mu.iloc[i]['theme_y'] !='')):
                mu.iloc[i]['theme_x']=mu.iloc[i]['theme_y']
            if(mu.iloc[i]['risk_level_x'] =='' and mu.iloc[i]['risk_level_y'] !=''):
                mu.iloc[i]['risk_level_x']=mu.iloc[i]['risk_level_y']

        for col in ['style_source','theme_source','risk_source']:
            mu.loc[mu[col]=='',col]='wind'
        mu['clbz']='公募'
        mu.drop(['style_y','theme_y','risk_level_y','jjjc_y'],axis=1,inplace=True)

        mu.rename(columns={'style_x':'style', 'theme_x':'theme', 'risk_level_x':'risk_level','jjjc_x':'jjjc'},inplace=True)
        mu=mu[prv.columns]

        final_df=pd.concat([prv,mu],axis=0)
        final_df['style_updated_date']=self.exp_quater
        final_df['vol_updated_date'] = self.vol_week


        #check if the same data exists already, if yes, updates them with latest data
        sql="select distinct (style_updated_date) from labled_fund"
        date_list=pd.read_sql(sql,con=self.localengine)['style_updated_date'].tolist()
        if(self.today in date_list):
            sql="delete from labled_fund where style_updated_date='{}'".format(self.today)
            self.localengine.execute(sql)

        sql="select distinct (vol_updated_date) from labled_fund"
        date_list=pd.read_sql(sql,con=self.localengine)['vol_updated_date'].tolist()
        if(self.today in date_list):
            sql="delete from labled_fund where vol_updated_date='{}'".format(self.today)
            self.localengine.execute(sql)

        final_df.fillna('',inplace=True)
        final_df[['jjjc','jjdm','clbz','style','theme','risk_level','style_updated_date','vol_updated_date','style_source', 'theme_source','risk_source']].to_sql('labled_fund',con=self.localengine,index=False,if_exists='append')

        print('Fund has benn labled and saved in labled_fund table ')

    def classify_hldbase(self):

        style_label=self.label_style(asofdate=self.exp_quater,filename='model_style_hld_2022-01-17.pkl',value_style='hld')
        theme_label=self.label_theme(asofdate=self.exp_quater,filename='model_theme_hld_2022-01-17.pkl',value_style='hld')
        risk_label=self.label_risk_new(self.today)

        style_label['style_source']='model'
        theme_label['theme_source'] = 'model'
        risk_label['risk_source'] = 'model'

        final_df=pd.merge(style_label,theme_label,how='outer',left_on='jjdm',right_on='jjdm')
        final_df=pd.merge(final_df,risk_label,how='outer',left_on='jjdm',right_on='jjdm')

        sql="select jjdm,jjjc,clbz from st_hedge.t_st_jjxx where jjdm in ({0}) "\
            .format("'"+"','".join(final_df['jjdm'].unique())+"'")
        extra_info_prv=self.hbdb.db2df(sql,db='highuser')
        for key in self.clbz.keys():
            extra_info_prv.loc[extra_info_prv['clbz']==key,'clbz']=self.clbz[key]

        final_df=pd.merge(final_df,extra_info_prv,how='left',on='jjdm')
        final_df.loc[final_df['clbz'].isnull(),'clbz']='公募'

        prv=final_df[final_df['clbz']!='公募']
        mu=final_df[final_df['clbz']=='公募']
        del final_df

        extra_info_mu=self.read_mu_extra_info()
        mu=pd.merge(extra_info_mu,mu,how='left',on='jjdm')

        mu.fillna('', inplace=True)

        for i in mu.index:
            if(mu.iloc[i]['style_x']=='' and mu.iloc[i]['style_y']!=''):
                mu.iloc[i]['style_x']=mu.iloc[i]['style_y']
            if((mu.iloc[i]['theme_x'] =='') and (mu.iloc[i]['theme_y'] !='')):
                mu.iloc[i]['theme_x']=mu.iloc[i]['theme_y']
            if(mu.iloc[i]['risk_level_x'] =='' and mu.iloc[i]['risk_level_y'] !=''):
                mu.iloc[i]['risk_level_x']=mu.iloc[i]['risk_level_y']

        for col in ['style_source','theme_source','risk_source']:
            mu.loc[mu[col]=='',col]='wind'
        mu['clbz']='公募'
        mu.drop(['style_y','theme_y','risk_level_y','jjjc_y'],axis=1,inplace=True)

        mu.rename(columns={'style_x':'style', 'theme_x':'theme', 'risk_level_x':'risk_level','jjjc_x':'jjjc'},inplace=True)
        mu=mu[prv.columns]

        final_df=pd.concat([prv,mu],axis=0)
        final_df['style_updated_date']=self.exp_quater
        final_df['vol_updated_date'] = self.vol_week


        #check if the same data exists already, if yes, updates them with latest data
        sql="select distinct (style_updated_date) from labled_fund"
        date_list=pd.read_sql(sql,con=self.localengine)['style_updated_date'].tolist()
        if(self.today in date_list):
            sql="delete from labled_fund where style_updated_date='{}'".format(self.today)
            self.localengine.execute(sql)

        sql="select distinct (vol_updated_date) from labled_fund"
        date_list=pd.read_sql(sql,con=self.localengine)['vol_updated_date'].tolist()
        if(self.today in date_list):
            sql="delete from labled_fund where vol_updated_date='{}'".format(self.today)
            self.localengine.execute(sql)

        final_df.fillna('',inplace=True)
        # final_df[['jjjc','jjdm','clbz','style','theme','risk_level','style_updated_date','vol_updated_date','style_source', 'theme_source','risk_source']].to_sql('labled_fund',con=self.localengine,index=False,if_exists='append')
        #
        # print('Fund has benn labled and saved in labled_fund table ')

class Classifier_brinson:

    def __init__(self):
        self.localengine=db_engine.PrvFunDB().engine
        self.hbdb=db_engine.HBDB()
        self.today=str(datetime.datetime.today().date())

    def rank_perc(self,ret_df):

        ret_col=ret_df.columns
        ret_df[ret_col] = ret_df[ret_col].rank(ascending=False)
        for col in ret_col:
            ret_df[col] = ret_df[col] / ret_df[col].max()

        return ret_df

    def get_brinson_data(self):

        sql="select distinct tjrq from st_fund.r_st_hold_excess_attr_df where tjrq>='{0}' "\
            .format(str(int(self.today.split('-')[0])-7)+'0101')
        tjrq_list=self.hbdb.db2df(sql,db='funduser').sort_values('tjrq',ascending=False)['tjrq'].tolist()

        fin_df=self.hbdb.db2df("select jjdm from st_fund.r_st_hold_excess_attr_df where tjrq='{}'"
                               .format(tjrq_list[0]),db='funduser')

        ret_col = ['asset_allo', 'sector_allo', 'equity_selection', 'trading']
        for tjrq in tjrq_list:
            sql="""select jjdm,asset_allo,sector_allo,equity_selection,trading 
            from st_fund.r_st_hold_excess_attr_df where tjrq='{0}'""".format(tjrq)
            ret_df=self.hbdb.db2df(sql,db='funduser')

            for col in ret_col:

                ret_df.rename(columns={col: col + "_" + tjrq}, inplace=True)

            fin_df=pd.merge(fin_df,ret_df,how='outer',on='jjdm')

        return  fin_df

    def brinson_rank(self,fin_df,threshold):

        outputdf = pd.DataFrame()
        outputdf['jjdm'] = fin_df.columns.tolist()

        for i in range(4):
            step = int(len(fin_df) / 4)
            tempdf = fin_df.iloc[i * step:(i + 1) * step]
            inputdf = pd.DataFrame()
            inputdf['jjdm'] = tempdf.columns.tolist()

            for j in range(1, 13):
                inputdf['{}month_ave_rank'.format(6 * j)] = self.rank_perc(tempdf.rolling(j).sum().T).T.mean().values

            short_term = inputdf.columns[1:7]
            long_term = inputdf.columns[7:13]

            new_col = 'short_term_{}'.format(tempdf.index[0].split('_')[0])
            inputdf[new_col] = 0
            inputdf.loc[(inputdf[short_term] <= threshold).sum(axis=1) >= 1, new_col] = 1

            new_col2 = 'long_term_{}'.format(tempdf.index[0].split('_')[0])
            inputdf[new_col2] = 0
            inputdf.loc[(inputdf[long_term] <= threshold).sum(axis=1) >= 1, new_col2] = 1

            outputdf = pd.merge(outputdf, inputdf[['jjdm', new_col, new_col2]], how='left', on='jjdm')

            return outputdf

    def target_fun_brinson(self,outputdf,iteration):

        target = outputdf[['short_term_trading', 'long_term_trading', 'short_term_sector',
                         'long_term_sector', 'short_term_equity', 'long_term_equity',
                         'short_term_asset', 'long_term_asset']].sum(axis=1)

        print('iteration {}'.format(iteration))
        print("ratio of multi label is {0}, ratio of null label is {1}".format(len(target[target > 1]) / len(target),
                                                                               len(target[target == 0]) / len(target)))
        print('sum of two ratio is {}'.format(len(target[target > 1]) / len(target) + len(target[target == 0]) / len(target)))

    def classify_threshold(self,iteration_num=100):

        fin_df=self.get_brinson_data()

        fin_df=fin_df.T.sort_index(ascending=False)
        fin_df.columns=fin_df.loc['jjdm']
        fin_df.drop('jjdm',axis=0,inplace=True)


        # for iteration in range(0,iteration_num):
        #
        #     threshold=0.01*(iteration+1)
        #
        #     outputdf=self.brinson_rank(fin_df,threshold)
        #
        #     self.target_fun_brinson(outputdf, iteration)

        inputdf=self.brinson_rank(fin_df,0.1)

        print('Done')

    def classify_socring(self):

        fin_df=self.get_brinson_data()

        asofdate=fin_df.columns[1].split('_')[-1]

        fin_df=fin_df.T.sort_index(ascending=False)
        fin_df.columns=fin_df.loc['jjdm']
        fin_df.drop('jjdm',axis=0,inplace=True)

        outputdf = pd.DataFrame()
        outputdf['jjdm'] = fin_df.columns.tolist()

        for i in range(4):
            step = int(len(fin_df) / 4)
            tempdf = fin_df.iloc[i * step:(i + 1) * step]
            inputdf = pd.DataFrame()
            inputdf['jjdm'] = tempdf.columns.tolist()

            for j in range(1, 13):
                inputdf['{}month_ave_rank'.format(6 * j)] = self.rank_perc(tempdf.rolling(j).sum().T).T.mean().values

            short_term = inputdf.columns[1:7]
            long_term = inputdf.columns[7:13]

            new_col = 'short_term_{}'.format(tempdf.index[0].split('_')[0])
            inputdf[new_col] = 10-(inputdf[short_term].mean(axis=1)*10).astype(int)

            new_col2 = 'long_term_{}'.format(tempdf.index[0].split('_')[0])
            inputdf[new_col2] =10- (inputdf[long_term].mean(axis=1)*10).fillna(0).astype(int)

            outputdf = pd.merge(outputdf, inputdf[['jjdm', new_col, new_col2]], how='left', on='jjdm')

        outputdf['asofdate']=asofdate

        #check if data already exist
        sql='select distinct asofdate from brinson_score'
        date_list=pd.read_sql(sql,con=self.localengine)['asofdate'].tolist()
        if(asofdate in date_list):
            sql="delete from brinson_score where asofdate='{}'".format(asofdate)
            self.localengine.execute(sql)

        outputdf.to_sql('brinson_score',con=self.localengine,index=False,if_exists='append')

class Classifier_barra:

    def __init__(self):
        self.localengine=db_engine.PrvFunDB().engine
        self.hbdb=db_engine.HBDB()
        self.barra_col=['size','beta','momentum','resvol','btop','sizenl','liquidity','earnyield','growth','leverage']
        self.indus_col=['aerodef','agriforest','auto','bank','builddeco','chem','conmat','commetrade','computer','conglomerates','eleceqp','electronics',
        'foodbever','health','houseapp','ironsteel','leiservice','lightindus','machiequip','media','mining','nonbankfinan','nonfermetal',
        'realestate','telecom','textile','transportation','utilities']
        chinese_name=['国防军工','农林牧渔','汽车','银行','建筑装饰','化工','建筑材料','商业贸易','计算机','综合','电气设备',
                      '电子','食品饮料','医药生物','家用电器','钢铁','休闲服务','轻工制造','机械设备','传媒','采掘','非银金融',
                      '有色金属','房地产','通信','纺织服装','交通运输','公用事业']
        self.industry_name_map=dict(zip(chinese_name,self.indus_col))

        self.style_trans_map=dict(zip(self.barra_col,['市值','市场','动量','波动率','价值','非线性市值','流动性','盈利','成长','杠杆',]))

        self.ability_trans=dict(zip(['stock_alpha_ret_adj', 'trading_ret', 'industry_ret_adj',
       'unexplained_ret', 'barra_ret_adj'],['股票配置','交易','行业配置','Alpha','风格配置']))

    def read_barra_fromdb(self,date_list,tickerlist):

        date_list=[''.join(x.split('-')) for x in date_list.astype(str)]
        # date_con="'"+"','".join(date_list)+"'"
        ticker_con="'"+"','".join(tickerlist)+"'"

        sql="""
        select ticker,trade_date,size,beta,momentum,resvol,btop,sizenl,liquidity,earnyield,growth,leverage,
        aerodef,agriforest,auto,bank,builddeco,chem,conmat,commetrade,computer,conglomerates,eleceqp,electronics,
        foodbever,health,houseapp,ironsteel,leiservice,lightindus,machiequip,media,mining,nonbankfinan,nonfermetal,
        realestate,telecom,textile,transportation,utilities 
        from st_ashare.r_st_barra_style_factor where trade_date>='{0}' and trade_date<='{1}' and ticker in ({2})
        """.format(date_list[0],date_list[-1],ticker_con)
        expdf=self.hbdb.db2df(sql,db='alluser')

        sql="select factor_name,factor_ret,trade_date from st_ashare.r_st_barra_factor_return where trade_date>='{0}' and trade_date<='{1}'"\
            .format(date_list[0],date_list[-1])
        fac_ret_df=self.hbdb.db2df(sql,db='alluser')

        return expdf,fac_ret_df

    def read_anon_fromdb(self,date_list,tickerlist):

        date_list=[''.join(x.split('-')) for x in date_list.astype(str)]
        ticker_con="'"+"','".join(tickerlist)+"'"

        sql=""" select ticker,trade_date,s_ret from st_ashare.r_st_barra_specific_return where ticker in ({0})
        and trade_date>='{1}' and trade_date<='{2}'
        """.format(ticker_con,date_list[0],date_list[-1])

        anon_ret=self.hbdb.db2df(sql,db='alluser')

        return anon_ret

    def read_hld_fromdb(self,start_date,end_date,jjdm):

        sql="""select jsrq,zqdm,zjbl from st_fund.t_st_gm_gpzh where jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}'
        """.format(jjdm,start_date,end_date)
        hld=self.hbdb.db2df(sql,db='funduser')
        hld['jsrq']=hld['jsrq'].astype(str)
        return hld

    def smooth_hld(self,hld,date_list,weight_col,date_col,code_col):

        smoothed_hld=pd.DataFrame()
        ext_zqdm=[]
        ext_date=[]
        ext_zjbl=[]

        for i in range(len(date_list)-1):
            q0=date_list[i]
            q1=date_list[i+1]

            sql = """
            select distinct(trade_date)
            from st_ashare.r_st_barra_style_factor where trade_date>'{0}' and trade_date<'{1}'
            """.format(q0, q1)
            ext_date_list = self.hbdb.db2df(sql, db='alluser')['trade_date'].tolist()

            tempdf=pd.merge(hld[hld[date_col]==q0],hld[hld[date_col]==q1],how='outer',on=code_col).fillna(0)
            tempdf['shift_rate']=(tempdf[weight_col+'_y']-tempdf[weight_col+'_x'])/(len(ext_date_list)+1)
            zqdm=tempdf[code_col].unique().tolist()
            zq_amt=len(zqdm)
            ini_zjbl=tempdf[weight_col+'_x'].tolist()

            for j  in range(len(ext_date_list)):
                ext_date+=[ext_date_list[j]]*zq_amt
                ext_zjbl+=(np.array(ini_zjbl)+np.array((tempdf['shift_rate']*(j+1)).tolist())).tolist()
                ext_zqdm+=zqdm

        smoothed_hld[weight_col]=ext_zjbl
        smoothed_hld[date_col] = ext_date
        smoothed_hld[code_col] = ext_zqdm

        hld=pd.concat([hld,smoothed_hld],axis=0)
        return hld

    def read_hld_ind_fromdb(self,start_date,end_date,jjdm):

        sql = """select jsrq,fldm,zzjbl from st_fund.t_st_gm_gpzhhytj where hyhfbz='2' and jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}'
        """.format(jjdm, start_date, end_date)
        hld = self.hbdb.db2df(sql, db='funduser')
        hld['jsrq'] = hld['jsrq'].astype(str)

        sql="select fldm,flmc from st_market.t_st_zs_hyzsdmdyb where hyhfbz='2'"
        industry_map=self.hbdb.db2df(sql,db='alluser')

        hld=pd.merge(hld,industry_map,how='left',on='fldm')
        hld['flmc']=[ self.industry_name_map[x] for x in hld['flmc']]

        hld.loc[hld['zzjbl']==99999,'zzjbl']=0
        hld['zzjbl']=hld['zzjbl']/100

        return hld

    def weight_times_exp(self,fund_exp,col_list):

        for col in col_list:
            fund_exp[col]=fund_exp[col]*fund_exp['zjbl']

        return  fund_exp

    def save_barra_ret2db(self,jjdm,start_date,end_date,add=False):

        hld=self.read_hld_fromdb(start_date,end_date,jjdm)
        tickerlist=hld['zqdm'][~hld['zqdm'].dropna().str.contains('H')].unique()
        date_list=hld['jsrq'].unique()
        hld=self.smooth_hld(hld,date_list,weight_col='zjbl',date_col='jsrq',code_col='zqdm')

        hld_industry=self.read_hld_ind_fromdb(start_date,end_date,jjdm)
        hld_industry=self.smooth_hld(hld_industry[['zzjbl','jsrq','flmc']],date_list,weight_col='zzjbl',date_col='jsrq',code_col='flmc')

        fund_allocation = self.fund_asset_allocation(jjdm, date_list)
        fund_allocation = self.smooth_hld(fund_allocation, date_list, weight_col='gptzzjb', date_col='jsrq',
                                          code_col='jjdm')

        expdf, fac_ret_df=self.read_barra_fromdb(date_list,tickerlist)

        stock_df = self.stock_price(date_list, tickerlist)

        anno_df=self.read_anon_fromdb(date_list,tickerlist)

        fund_exp=pd.merge(hld,expdf[['ticker','trade_date']+self.barra_col],how='inner',left_on=['zqdm','jsrq'],right_on=['ticker','trade_date']).drop(['ticker', 'trade_date'],axis=1)

        fund_exp=pd.merge(fund_exp, stock_df[['ZQDM', 'JYRQ', 'hld_ret']], how='inner', left_on=['zqdm', 'jsrq'],
                 right_on=['ZQDM', 'JYRQ']).drop(['ZQDM','JYRQ'],axis=1)

        fund_exp=pd.merge(fund_exp, anno_df, how='inner', left_on=['zqdm', 'jsrq'],
                 right_on=['ticker', 'trade_date']).drop(['ticker', 'trade_date'],axis=1)

        fund_exp=self.weight_times_exp(fund_exp,self.barra_col+['hld_ret','s_ret'])

        fund_exp.drop(['zqdm'],axis=1,inplace=True)

        fund_exp=fund_exp.groupby(by='jsrq').sum()/100

        hld_ret=fund_exp[['zjbl','hld_ret']]
        s_ret=fund_exp[['zjbl','s_ret']]

        fund_exp.drop(['hld_ret','s_ret'],axis=1,inplace=True)
        fund_exp=fund_exp.T

        indus_exp = pd.DataFrame()
        indus_exp['industry'] = self.indus_col

        for date in fund_exp.columns:

            tempdf=fac_ret_df[fac_ret_df['trade_date']==date][['factor_ret','factor_name']].T
            tempdf.columns = [x.lower() for x in  tempdf.loc['factor_name']]

            indus_exp=pd.merge(indus_exp,hld_industry[hld_industry['jsrq']==date][['zzjbl','flmc','jsrq']],how='left',left_on='industry',right_on='flmc').drop(['flmc','jsrq'],axis=1).fillna(0)
            indus_exp.rename(columns={'zzjbl':date},inplace=True)
            fund_exp[date+'_ret']=fund_exp[date].values*np.append([1],tempdf[self.barra_col].loc['factor_ret'].values)
            indus_exp[date+'_ret']=indus_exp[date].values*tempdf[self.indus_col].loc['factor_ret'].values

        fund_exp=fund_exp.T
        indus_exp.set_index(['industry'], inplace=True)
        indus_exp=indus_exp.T

        fund_exp['total_bar']=fund_exp[self.barra_col].sum(axis=1)
        indus_exp['total_ind'] = indus_exp[self.indus_col].sum(axis=1)

        fund_exp['index']=fund_exp.index
        indus_exp['index'] = indus_exp.index
        fund_exp['jjrq']=[x.split('_')[0] for x in fund_exp['index']]
        indus_exp['jjrq'] = [x.split('_')[0] for x in indus_exp['index']]
        hld_ret['jjrq'] = hld_ret.index
        s_ret['jjrq'] = s_ret.index
        for df in [fund_exp,indus_exp,hld_ret,s_ret]:
            df['jjdm']=jjdm

        fund_allocation=pd.merge(s_ret['jjrq'],fund_allocation,how='left',left_on='jjrq',right_on='jsrq').drop('jjrq',axis=1)

        if(not add):
            sql="select distinct jjrq from barra_style_s_ret where jjdm='{0}'".format(jjdm)
            date_list=pd.read_sql(sql,con=self.localengine)['jjrq']
            common_date=list(set(date_list).intersection(set(fund_allocation['jsrq'] )))
            date_con="'"+"','".join(common_date)+"'"

            sql="delete from barra_style_fund_exp where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con)
            self.localengine.execute(sql)
            sql="delete from barra_style_indus_exp where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con)
            self.localengine.execute(sql)
            sql="delete from barra_style_hld_ret where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con)
            self.localengine.execute(sql)
            sql="delete from barra_style_s_ret where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con)
            self.localengine.execute(sql)
            sql = "delete from barra_style_fund_allocation where jjdm='{0}' and jsrq in ({1})".format(jjdm, date_con)
            self.localengine.execute(sql)

        fund_exp.to_sql('barra_style_fund_exp',con=self.localengine,index=False,if_exists='append')
        indus_exp.to_sql('barra_style_indus_exp', con=self.localengine,index=False,if_exists='append')
        hld_ret.to_sql('barra_style_hld_ret', con=self.localengine,index=False,if_exists='append')
        s_ret.to_sql('barra_style_s_ret', con=self.localengine,index=False,if_exists='append')
        fund_allocation.to_sql('barra_style_fund_allocation', con=self.localengine,index=False,if_exists='append')

        #print('{0} data for {1} to {2} has been saved in local db'.format(jjdm,start_date,end_date))

    def read_barra_retfromdb(self,jjdm,start_date,end_date):

        sql="select * from barra_style_fund_exp where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date)
        fund_exp=pd.read_sql(sql,con=self.localengine).drop(['jjdm','jjrq'],axis=1)
        fund_exp.set_index('index',drop=True,inplace=True)

        sql="select * from barra_style_indus_exp where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date)
        indus_exp=pd.read_sql(sql,con=self.localengine).drop(['jjdm','jjrq'],axis=1)
        indus_exp.set_index('index', drop=True,inplace=True)

        sql="select * from barra_style_hld_ret where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date)
        hld_ret=pd.read_sql(sql,con=self.localengine).drop(['jjdm'],axis=1)
        hld_ret.set_index('jjrq', drop=True,inplace=True)

        sql="select * from barra_style_s_ret where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date)
        s_ret=pd.read_sql(sql,con=self.localengine).drop(['jjdm'],axis=1)
        s_ret.set_index('jjrq', drop=True,inplace=True)

        sql="select * from barra_style_fund_allocation where jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}'"\
            .format(jjdm,start_date,end_date)
        fund_allocation=pd.read_sql(sql,con=self.localengine).drop(['jjdm'],axis=1)

        sql="""select jsrq from st_fund.t_st_gm_gpzh where jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}'
        """.format(jjdm,start_date,end_date)
        hld=self.hbdb.db2df(sql,db='funduser')
        hld['jsrq']=hld['jsrq'].astype(str)

        date_list=hld['jsrq'].unique().tolist()

        return fund_exp, indus_exp, hld_ret, s_ret, date_list,fund_allocation

    def stock_price(self,date_list,tickerlist):

        date_list=[''.join(x.split('-')) for x in date_list.astype(str)]
        ticker_con="'"+"','".join(tickerlist)+"'"

        sql="""
        select ZQDM,JYRQ,QSPJ,SPJG from FUNDDB.ZGJY where ZQDM in ({0}) and JYRQ>='{1}' and JYRQ<='{2}'
         """.format(ticker_con,date_list[0],date_list[-1])

        stock_price=self.hbdb.db2df(sql,db='readonly')

        stock_price['hld_ret']=stock_price['SPJG']/stock_price['QSPJ']-1

        return stock_price

    def fund_nv(self,jjdm,date_list):

        sql="""
        select jzrq,hbdr from st_fund.t_st_gm_rhb where jjdm='{0}' 
        and jzrq>='{1}' and jzrq<='{2}' 
        """.format(jjdm,date_list[0],date_list[-1])

        fundnv=self.hbdb.db2df(sql,db='funduser')
        fundnv['jzrq']=fundnv['jzrq'].astype(str)
        fundnv['hbdr']=fundnv['hbdr']/100

        return fundnv

    def fund_asset_allocation(self,jjdm,date_list):

        sql="select jjdm,jsrq,gptzzjb from st_fund.t_st_gm_zcpz where jjdm='{2}' and jsrq>='{0}' and jsrq<='{1}'"\
            .format(date_list[0],date_list[-1],jjdm)
        fund_allocation=self.hbdb.db2df(sql,db='funduser')
        fund_allocation['gptzzjb']=fund_allocation['gptzzjb']/100
        fund_allocation['jsrq']=fund_allocation['jsrq'].astype(str)
        return fund_allocation

    def ret_div(self,jjdm,start_date,end_date):

        fund_exp,indus_exp,hld_ret,s_ret,date_list,fund_allocation=self.read_barra_retfromdb(jjdm,start_date,end_date)

        fundnv=self.fund_nv(jjdm,date_list)
        #
        # fund_allocation = self.fund_asset_allocation(jjdm, date_list)
        # fund_allocation = self.smooth_hld(fund_allocation, date_list, weight_col='gptzzjb', date_col='jsrq',
        #                                   code_col='jjdm')
        # fund_allocation.drop('jjdm',axis=1,inplace=True)

        hld_ret['jzrq']=hld_ret.index
        hld_ret=pd.merge(hld_ret,fundnv,how='left',on='jzrq')

        barra_ret=fund_exp.loc[[x+'_ret' for x in hld_ret['jzrq']]][self.barra_col+['total_bar']].reset_index(drop=True)
        barra_exp=fund_exp.loc[hld_ret['jzrq']][self.barra_col+['total_bar']].reset_index(drop=True)
        barra_exp.columns=[x+'_exp' for x in barra_exp.columns]

        ind_ret = indus_exp.loc[[x + '_ret' for x in hld_ret['jzrq']]].reset_index(
            drop=True)
        ind_exp = indus_exp.loc[hld_ret['jzrq']].reset_index(drop=True)
        ind_exp.columns = [x + '_exp' for x in ind_exp.columns]

        s_ret=s_ret['s_ret'].reset_index(drop=True)
        ouputdf=pd.concat([hld_ret,barra_ret,barra_exp,ind_ret,ind_exp,s_ret],axis=1)

        columns=['zjbl', 'hld_ret', 'jzrq', 'hbdr', 'total_bar', 'total_bar_exp', 's_ret','total_ind']

        new_names=['published_stock_weight','hld_based_ret','date','nv_ret','barra_ret','barra_exp','stock_alpha_ret','industry_ret']

        ouputdf.rename(columns=dict(zip(columns,new_names)),inplace=True)

        ouputdf=pd.merge(ouputdf,fund_allocation,how='left',left_on='date',right_on='jsrq').drop('jsrq',axis=1)

        for col in self.barra_col+self.indus_col:
            ouputdf[col+"_adj"]=ouputdf[col]/ouputdf['published_stock_weight']*ouputdf['gptzzjb']
            ouputdf[col + "_exp_adj"] = ouputdf[col+"_exp"] / ouputdf['published_stock_weight'] * ouputdf['gptzzjb']

        ouputdf.set_index('date',drop=True,inplace=True)

        return  ouputdf,date_list

    def date_trans(self,date_list,inputlist):

        missing_date=set(inputlist).difference(set(date_list))
        available_list=list(set(inputlist).difference(set(missing_date)))
        new_list = []
        if(len(missing_date)>0):
            for date in missing_date:
                diff=abs(date_list.astype(int)-int(date)).min()
                new_list.append(date_list[abs(date_list.astype(int)-int(date))==diff][0])
        available_list+=new_list
        available_list.sort()
        return  available_list

    def style_change_detect(self,df,q_list,col_list,t1,t2):

        q_list=self.date_trans(df.index,q_list)
        q_df = df.loc[q_list]
        style_change = []
        diff1=q_df.diff(1)
        diff2=q_df.rolling(3).mean().diff(2)

        for col in col_list:

            potential_date=diff2[diff2[col]<=-1*t1].index.to_list()
            last_added_date=q_list[-1]
            for date in potential_date:
                if(diff1.loc[q_df.index[q_df.index<=date][-3]][col]<=-1*t2):
                    added_date=q_df.index[q_df.index<=date][-3]
                elif(diff1.loc[q_df.index[q_df.index<=date][-2]][col]<=-1*t2):
                    added_date=q_df.index[q_df.index<=date][-2]
                elif(diff1.loc[q_df.index[q_df.index<=date][-1]][col]<=-1*t2):
                    added_date = q_df.index[q_df.index <= date][-1]
                else:
                    added_date = q_df.index[q_df.index <= date][-3]

                if(q_list.index(added_date)-q_list.index(last_added_date)<=2
                        and q_list.index(added_date)-q_list.index(last_added_date)>0):
                    continue
                else:
                    style_change.append(added_date + "@" + col)
                    last_added_date = added_date

            potential_date = diff2[diff2[col] >= t1].index.to_list()
            last_added_date = q_list[-1]
            for date in potential_date:
                if (diff1.loc[q_df.index[q_df.index <= date][-3]][col] >= t2):
                    added_date = q_df.index[q_df.index <= date][-3]
                elif (diff1.loc[q_df.index[q_df.index <= date][-2]][col] >= t2):
                    added_date = q_df.index[q_df.index <= date][-2]
                elif (diff1.loc[q_df.index[q_df.index <= date][-1]][col] >= t2):
                    added_date = q_df.index[q_df.index <= date][-1]
                else:
                    added_date = q_df.index[q_df.index <= date][-3]

                if (q_list.index(added_date) - q_list.index(last_added_date) <= 2
                        and q_list.index(added_date) - q_list.index(last_added_date) > 0):
                    continue
                else:
                    style_change.append(added_date + "@" + col)
                    last_added_date = added_date

        return list(set(style_change)),np.array(q_list)

    def cul_ret(self,weight,ret):

        cul_ret=1
        for i in range(len(weight)):
            cul_ret*=weight[i]*ret[i]+1

        return cul_ret

    def style_change_ret(self,df,q_list,col_list,t1,t2):

        style_change,q_list = self.style_change_detect(df,q_list,col_list,t1,t2)
        change_count = len(style_change)
        style_changedf=pd.DataFrame()
        style_changedf['date']=[x.split('@')[0] for x in style_change]
        style_changedf['style']=[x.split('@')[1] for x in style_change]
        style_changedf.sort_values('date',inplace=True,ascending=False)
        style_chang_extret=dict(zip(style_change,style_change))

        if(change_count>0):
            for style in style_changedf['style']:
                changedf=style_changedf[style_changedf['style']==style]
                end_date=q_list[-1]
                for date in changedf['date']:
                    observer_term=np.append(q_list[q_list<date][-2:],q_list[(q_list>=date)][0:2])
                    ext_ret=['']*3

                    new_exp=df[style].loc[observer_term[2]]
                    old_exp=df[style].loc[observer_term[1]]

                    q0=observer_term[0]
                    q1=observer_term[1]
                    tempdf=df.loc[(df.index>q0)*(df.index<=q1)]

                    sql = "select factor_ret,trade_date from st_ashare.r_st_barra_factor_return where trade_date>='{0}' and trade_date<='{1}' and UPPER(factor_name)='{2}'" \
                        .format(q0, q1, style.split('_')[0].upper())
                    fac_ret_df = self.hbdb.db2df(sql, db='alluser')
                    fac_ret_df.set_index('trade_date', drop=True, inplace=True)
                    tempdf=tempdf[[style,style.replace("_exp","")]]
                    tempdf=pd.merge(tempdf,fac_ret_df,how='left',left_index=True,right_on='trade_date')


                    cul_ret_new=self.cul_ret([new_exp]*len(tempdf),tempdf['factor_ret'].values)
                    cul_ret_old=self.cul_ret([old_exp]*len(tempdf),tempdf['factor_ret'].values)
                    ext_ret[0] = cul_ret_new - cul_ret_old

                    q0=observer_term[2]
                    q1=observer_term[3]
                    tempdf=df.loc[(df.index>q0)*(df.index<=q1)]
                    tempdf=tempdf[[style,style.replace("_exp","")]]

                    sql = "select factor_ret,trade_date from st_ashare.r_st_barra_factor_return where trade_date>='{0}' and trade_date<='{1}' and UPPER(factor_name)='{2}'" \
                        .format(q0, q1, style.split('_')[0].upper())
                    fac_ret_df = self.hbdb.db2df(sql, db='alluser')
                    fac_ret_df.set_index('trade_date', drop=True, inplace=True)
                    tempdf = tempdf[[style, style.replace("_exp", "")]]
                    tempdf = pd.merge(tempdf, fac_ret_df, how='left', left_index=True, right_on='trade_date')

                    cul_ret_new=self.cul_ret([new_exp]*len(tempdf),tempdf['factor_ret'].values)
                    cul_ret_old=self.cul_ret([old_exp]*len(tempdf),tempdf['factor_ret'].values)
                    ext_ret[1]=cul_ret_new-cul_ret_old

                    q0=observer_term[1]
                    q1=observer_term[2]
                    tempdf=df.loc[(df.index>q0)*(df.index<=q1)]
                    tempdf=tempdf[[style,style.replace("_exp","")]]

                    sql = "select factor_ret,trade_date from st_ashare.r_st_barra_factor_return where trade_date>='{0}' and trade_date<='{1}' and UPPER(factor_name)='{2}'" \
                        .format(q0, q1, style.split('_')[0].upper())
                    fac_ret_df = self.hbdb.db2df(sql, db='alluser')
                    fac_ret_df.set_index('trade_date', drop=True, inplace=True)
                    tempdf = tempdf[[style, style.replace("_exp", "")]]
                    tempdf = pd.merge(tempdf, fac_ret_df, how='left', left_index=True, right_on='trade_date')


                    cul_ret_new = self.cul_ret(tempdf[style].iloc[1:].values, tempdf['factor_ret'].values)
                    cul_ret_old = self.cul_ret([old_exp]*len(tempdf), tempdf['factor_ret'].values)
                    ext_ret[2] = cul_ret_new - cul_ret_old

                    # end_date=q0
                    style_chang_extret[date+"@"+style]=ext_ret

        return style_chang_extret

    def plot_style(self,df,col,jjdm):

        from hbshare.fe.XZ import  functionality
        plot = functionality.Plot(fig_width=2000, fig_height=600)
        plot.plotly_line_style(df[col],'基金：{0}'.format(jjdm))

    def style_label_engine(self,df):

        desc=df.describe()
        desc_exp=desc[[x+"_exp_adj" for x in self.barra_col]]

        style_lable=[]
        stable_style_list=desc_exp.columns[(desc_exp.loc['std']<0.1).values].tolist()
        for style in stable_style_list:
            if(abs(desc_exp[style]['mean'])>=0.25 and abs(desc_exp[style]['mean'])<0.5):
                label="稳定偏好{}".format("较@"+self.style_trans_map[style.split('_')[0]])
            elif(abs(desc_exp[style]['mean'])>=0.5):
                label="稳定偏好{}".format("@"+self.style_trans_map[style.split('_')[0]])
            else:
                continue
            if(desc_exp[style]['mean'])<0:
                label=label.replace('@','低')
            else:
                label=label.replace('@','高')
            style_lable.append(label)

        return style_lable

    def style_shifting_analysis(self,df,q_list,col,t1,t2,name,jjdm):

        col_list=[x+"_exp_adj" for x in col]
        self.plot_style(df,col_list,jjdm)
        change_ret=self.style_change_ret(df,q_list,col_list,t1=t1,t2=t2)
        change_winning_pro=sum(np.array(list(change_ret.values()))[:,2]>0)/len(change_ret)
        left_ratio=sum(np.array(list(change_ret.values()))[:,1]<0)/len(change_ret)
        right_ratio=sum(np.array(list(change_ret.values()))[:,1]>0)/len(change_ret)
        one_q_ret=np.array(list(change_ret.values()))[:,2].mean()

        print("for {6},{5} shift : number of shifting is {4}, winning pro is {0}, left ratio is {1}, right ratio is {2},average return for next Q is {3}"
              .format(change_winning_pro,left_ratio,right_ratio,one_q_ret,len(change_ret),name,jjdm))

    def ret_analysis(self,df):

        ret_col_list=['hld_based_ret','barra_ret','stock_alpha_ret','industry_ret']
        for col in ret_col_list:
            df[col+'_adj']=df[col]/df['published_stock_weight']*df['gptzzjb']
        df=df[[x+'_adj' for x in ret_col_list]+['nv_ret']]

        df['unexplained_ret'] = df['hld_based_ret_adj'] - (
                    df['barra_ret_adj'] + df['industry_ret_adj'] + df['stock_alpha_ret_adj'])
        df['trading_ret'] =df['nv_ret']- df['hld_based_ret_adj']

        df=df*100
        ability_rank=(df.describe().loc['mean'].loc[['trading_ret','barra_ret_adj','stock_alpha_ret_adj','industry_ret_adj','unexplained_ret']].sort_values(ascending=False))/df['nv_ret'].mean()
        outstanding_ability=ability_rank[ability_rank>0.25].index.tolist()
        vol_rank=(df.describe().loc['std']/df.describe().loc['mean']).loc[outstanding_ability].sort_values()

        ability_label = []
        for ab in outstanding_ability:
            if(vol_rank.loc[ab]<=20):
                ext='稳定的'
            else:
                ext=''
            ability_label.append(ext+self.ability_trans[ab]+"能力")

        return ability_label

    def exp_analysis(self,df,q_list,jjdm):

        style_lable=self.style_label_engine(df)

        self.style_shifting_analysis(df[[x+"_exp_adj" for x in self.barra_col]+[x+"_adj" for x in self.barra_col]].astype(float),q_list,
                                  self.barra_col,t1=0.3,t2=0.2,name='barra style',jjdm=jjdm)
        self.style_shifting_analysis(df[[x + "_exp_adj" for x in self.indus_col]+[x+"_adj" for x in self.indus_col]].astype(float), q_list,
                                  self.indus_col, t1=0.1, t2=0.05, name='industry',jjdm=jjdm)

    def classify(self,jjdm,start_date,end_date):

        df,q_list=self.ret_div(jjdm,start_date,end_date)
        self.exp_analysis(df,q_list,jjdm)
        ability_label=self.ret_analysis(df)
        print(ability_label)

    def data_preparation(self):

        sql="""select distinct jjdm from st_fund.t_st_gm_gpzh where jsrq='20210930'
        """
        jjdm_list=self.hbdb.db2df(sql,db='funduser')['jjdm']
        #['000362','005821','009636','001487']
        for jjdm in jjdm_list :

            sql = """select min(jsrq) from st_fund.t_st_gm_gpzh where jjdm='{0}' and jsrq>=20150101
            """.format(jjdm)
            jsrq = str(self.hbdb.db2df(sql, db='funduser')['min(jsrq)'][0])

            for year in ['2016','2017','2018','2019','2020','2021']:
                if(year<jsrq[0:4]):
                    continue
                elif(year==jsrq[0:4]):
                    start_date=jsrq
                else:
                    start_date = str(int(year)-1) + "1231"

                end_date=year+"1231"
                try:
                    self.save_barra_ret2db(jjdm=jjdm,start_date=start_date,end_date=end_date)
                except Exception as e :
                    print(e)
                    print("{} failed at start date {} and end date{}".format(jjdm,start_date,end_date))

def test(fc,i):

    print('第{0}遍尝试'.format(i))
    i+=1

    try:
        risk_label = fc.label_risk_new(fc.today)
    except Exception as e:
        if("Read timed out" in str(e) ):
            risk_label=test(fc,i)
        else:
            print(e)
            risk_label=''

    return risk_label

if __name__ == '__main__':

    fc = Classifier_Ml('2021-12-31')
    fc.classify()

    # sql="select distinct(style_updated_date) from labled_fund"
    # asofdate_list=pd.read_sql(sql,con=db_engine.PrvFunDB().engine)['style_updated_date'].tolist()
    # for asofdate in asofdate_list:
    #     sql="select * from labled_fund where style_updated_date='{0}'".format(asofdate)
    #     fc=Classifier_Ml(asofdate[0:4]+"-"+asofdate[4:6]+"-"+asofdate[6:8])
    #     risk_label=test(fc,0)
    #     orgindf=pd.read_sql(sql,con=fc.localengine)
    #     print('')
