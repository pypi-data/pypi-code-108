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

        sql="select jjdm,jjjc from st_fund.t_st_gm_jjxx where cpfl='2' and (jjfl='1' or jjfl='3')"
        jjdm=self.hbdb.db2df(sql,db='funduser')

        tempdf=self.lable_trans(self.style_label.copy())
        tempdf['style']=tempdf['wdszsx']+tempdf['wdfgsx']
        jjdm=pd.merge(jjdm,tempdf[['jjdm','style']],how='left',on='jjdm')

        tempdf= self.theme_trans(self.theme_label.copy())
        tempdf.rename(columns={'所属主题基金类别(Wind行业)':'theme'},inplace=True)
        jjdm = pd.merge(jjdm, tempdf, how='left', left_on='jjdm',right_on='证券代码').drop('证券代码',axis=1)


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

        sql = """
        select distinct(jsrq)  from st_fund.t_st_gm_gpzhhytj where hyhfbz= 2 and jsrq>='{0}' and jsrq<='{1}' and 
        (substr(ltrim(jsrq),5,2)='06' or substr(ltrim(jsrq),5,2)='12')
        """.format( start_date, end_date)
        data_list=self.hbdb.db2df(sql,db='funduser')['jsrq'].tolist()


        hld=pd.DataFrame()
        for date in data_list:
            sql = """select jjdm,jsrq,fldm,zzjbl from st_fund.t_st_gm_gpzhhytj where hyhfbz=2 and zzjbl<200 and jsrq='{0}'  {1} 
            """.format(date,ext_con)
            temphld = self.hbdb.db2df(sql, db='funduser')
            temphld['jsrq'] = temphld['jsrq'].astype(str)
            hld=pd.concat([hld,temphld],axis=0)

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

        sql = """
        select distinct(jsrq) from st_fund.t_st_gm_gpzh where jsrq>='{0}' and jsrq<='{1}' {2} 
        and (substr(ltrim(jsrq),5,2)='06' or substr(ltrim(jsrq),5,2)='12')
        """.format(start_date,end_date,ext_con)
        data_list=self.hbdb.db2df(sql,db='funduser')['jsrq'].tolist()

        hld=pd.DataFrame()
        for date in data_list:
            sql="""select jjdm,jsrq,zqdm,zjbl from st_fund.t_st_gm_gpzh where jsrq='{0}'  {1}
            """.format(date,ext_con)
            temphld=self.hbdb.db2df(sql,db='funduser')
            temphld['jsrq']=temphld['jsrq'].astype(str)
            hld=pd.concat([hld,temphld],axis=0)

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
                where wdfgsx is null or  wdszsx is null and cpfl='2' and (jjfl='1' or jjfl='3') 
                """

                mu_list = self.hbdb.db2df(sql=sql, db='funduser')['jjdm'].tolist()

            else:
                sql = """
                select jjdm from st_fund.t_st_gm_jjxx 
                where cpfl='2' and (jjfl='1' or jjfl='3')
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
                where (wdfgsx is null or  wdszsx is null) and cpfl='2' and (jjfl='1' or jjfl='3')
                """
                mu_list = self.hbdb.db2df(sql=sql, db='funduser')['jjdm'].tolist()

            else:
                sql = """
                select jjdm from st_fund.t_st_gm_jjxx 
                where cpfl='2' and (jjfl='1' or jjfl='3')
                """
                mu_list1 = self.hbdb.db2df(sql=sql, db='funduser')['jjdm'].tolist()

                mu_list2 = self.read_theme_lable_fromloacldb()['证券代码']
                mu_list = list(set(mu_list1).difference(set(mu_list2)))

            ext_con ="and jjdm in ("+ "'" + "','".join(mu_list) + "'"+")"

        if(attr_type=='style_allo'):

            styledf = self.read_stock_style_fromloacldb()

            hld = self.read_hld_fromdb(start_date, end_date,ext_con)
            ticker_list = hld['zqdm'].unique().tolist()
            ticker_con = "'" + "','".join(ticker_list) + "'"

            hld = pd.merge(hld, styledf[['证券代码', '所属规模风格类型']], how='left',
                           left_on='zqdm', right_on='证券代码')
            hld['所属规模风格类型'].fillna('无风格',inplace=True)

            date = hld['jsrq'].unique().tolist()[0]
            tempdf1 = hld[hld['jsrq'] == date].groupby(by=['jjdm', '所属规模风格类型'],
                                                       as_index=False).sum()
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

    def read_stock_style_fromloacldb(self):

        sql="select distinct record_date from juchao_style where record_date<='{0}' "\
            .format(self.today.replace('-',''))
        latest_date=pd.read_sql(sql,con=self.localengine).sort_values('record_date')['record_date'].tolist()[-1]

        sql = "select * from juchao_style where record_date='{0}'".format(latest_date)
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
        print("the best fited model is saved at E:\GitFolder\hbshare\fe\Fund_classifier")

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
        style_list=style_exp['style_factor'].unique().tolist()
        style_list.sort()
        for style in style_list:
            tempddf=style_exp[style_exp['style_factor']==style][['data_value','jjdm']]
            tempddf.rename(columns={'data_value':style},inplace=True)
            #inputdf[style]=style_exp[style_exp['style_factor']==style]['data_value'].values
            inputdf=pd.merge(inputdf,tempddf,how='left',on='jjdm').fillna(0)


        # #standardlize the exp df
        # inputdf,rs=classifier.standardlize(inputdf,style_list)

        #join the two df
        inputdf=pd.merge(fund_style,inputdf,how='inner',left_on='jjdm',right_on='jjdm')
        del fund_style,style_exp

        #transfrom the style name from int to strings
        inputdf=self.lable_trans(inputdf)
        inputdf['Label']=inputdf['wdszsx']+inputdf['wdfgsx']
        inputdf.drop(['wdfgsx','wdszsx','jjdm'],axis=1,inplace=True)

        features_col=inputdf.columns.tolist()
        features_col.sort()
        inputdf=inputdf[features_col]
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

        #standardlize the exp df
        # inputdf,rs=classifier.standardlize(inputdf,self.theme_map.keys())

        #join the two df
        inputdf=pd.merge(fund_theme,inputdf,how='inner',left_on='证券代码',right_on='jjdm').drop(['证券代码','jjdm'],axis=1)
        del fund_theme,theme_exp

        inputdf.rename(columns={'所属主题基金类别(Wind行业)':'Label'},inplace=True)

        features_col=inputdf.columns.tolist()
        features_col.sort()
        inputdf=inputdf[features_col]
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
        style_list=style_exp['style_factor'].unique().tolist()
        style_list.sort()
        for style in style_list:
            tempddf=style_exp[style_exp['style_factor']==style][['data_value','jjdm']]
            tempddf.rename(columns={'data_value':style},inplace=True)
            #inputdf[style]=style_exp[style_exp['style_factor']==style]['data_value'].values
            inputdf=pd.merge(inputdf,tempddf,how='left',on='jjdm').fillna(0)
        del style_exp

        # for col in style_list:
        #     inputdf[col]=style_rs[col].transform(inputdf[col].values.reshape(-1,1))
        inputdf = classifier.standardlize(inputdf, style_list)

        #make the prediction of the lables
        label=trained_model.predict(inputdf[style_list])
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

        # for col in  self.theme_map.keys():
        #     inputdf[col]=theme_rs[col].transform(inputdf[col].values.reshape(-1,1))
        inputdf = classifier.standardlize(inputdf, self.theme_map.keys())

        input_col=list(self.theme_map.keys())
        input_col.sort()
        # make the prediction of the lables
        label = trained_model.predict(inputdf[input_col])
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

        sql = "select jjdm from st_hedge.t_st_jjxx where jjfl='1' and (zzrq is null or zzrq>='{}')".format(end_date)
        prv_stock_fund_list = self.hbdb.db2df(sql, db='highuser')['jjdm'].to_list()
        jjdmcon="'"+"','".join(prv_stock_fund_list)+"'"

        # sql = "select jjdm,max(tjrq) as tjrq from st_hedge.t_st_sm_zqjbdl where jjdm in ({2}) and zblb='2106' and tjrq>='{0}' and tjrq<='{1}' and zbnp!=99999 group by jjdm" \
        #     .format(start_date,end_date,jjdmcon)
        # jjdmdf = self.hbdb.db2df(sql, db='highuser')
        jjdmdf=pd.read_csv('vol_{0}_{1}.csv'.format(start_date,end_date))
        # jjdmdf.to_csv('vol_{0}_{1}.csv'.format(start_date,end_date),index=False)
        tjrq_list = jjdmdf['tjrq'].unique().tolist()

        prv_vol=pd.DataFrame()
        for tjrq in tjrq_list:
            jjdm_list=jjdmdf[jjdmdf['tjrq']==tjrq]['jjdm'].to_list()
            jjdmcon="'"+"','".join(jjdm_list)+"'"
            sql="select jjdm,zbnp from st_hedge.t_st_sm_zqjbdl where jjdm in ({0}) and zblb='2106' and tjrq='{1}'"\
                .format(jjdmcon,tjrq)
            prv_vol=pd.concat([prv_vol,self.hbdb.db2df(sql,db='highuser')],axis=0)

        return pd.concat([mu_vol,prv_vol],axis=0)

    def read_fund_drawback_fromdb(self,asofdate):

        end_date = asofdate
        start_date = datetime.datetime.strftime(
              datetime.datetime.strptime(asofdate,"%Y%m%d")-datetime.timedelta(days=30),"%Y%m%d")

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
            sql="select jjdm,zbnp from st_fund.t_st_gm_rqjzdhc where jjdm in ({0}) and zblb='2106' and jzrq='{1}' and zbnp!=99999 "\
                .format(jjdmcon,tjrq)
            mu_db=pd.concat([mu_db,self.hbdb.db2df(sql,db='funduser')],axis=0)


        sql = "select jjdm from st_hedge.t_st_jjxx where jjfl='1' and (zzrq is null or zzrq>='{}')".format(end_date)
        prv_stock_fund_list = self.hbdb.db2df(sql, db='highuser')['jjdm'].to_list()
        jjdmcon="'"+"','".join(prv_stock_fund_list)+"'"

        # sql = "select jjdm,max(tjrq) as tjrq from st_hedge.t_st_sm_zqjbdl where jjdm in ({2}) and zblb='2106' and tjrq>='{0}' and tjrq<='{1}' and zbnp!=99999 group by jjdm" \
        #     .format(start_date,end_date,jjdmcon)
        # jjdmdf = self.hbdb.db2df(sql, db='highuser')
        # jjdmdf.to_csv('db_{0}_{1}.csv'.format(start_date, end_date), index=False)
        jjdmdf=pd.read_csv('db_{0}_{1}.csv'.format(start_date, end_date))
        tjrq_list = jjdmdf['tjrq'].unique().tolist()

        prv_db=pd.DataFrame()
        for tjrq in tjrq_list:
            jjdm_list=jjdmdf[jjdmdf['tjrq']==tjrq]['jjdm'].to_list()
            jjdmcon="'"+"','".join(jjdm_list)+"'"
            sql="select jjdm,zbnp from st_hedge.t_st_sm_qjzdhc where jjdm in ({0}) and zblb='2106' and jzrq='{1}' and zbnp!=99999"\
                .format(jjdmcon,tjrq)
            prv_db=pd.concat([prv_db,self.hbdb.db2df(sql,db='highuser')],axis=0)

        return pd.concat([mu_db,prv_db],axis=0)

    def label_risk_new(self,asofdate):

        df_vol=self.read_fund_vol_fromdb_new(asofdate)

        # temp=df_vol.describe()
        # threshold=[(temp.loc['mean']-temp.loc['std'])[0],(temp.loc['mean']+temp.loc['std'])[0]]

        threshold=df_vol.quantile([0.2,0.4,0.6,0.8])['zbnp'].tolist()

        df_vol['risk_level']='R3'
        df_vol.loc[df_vol['zbnp']<=threshold[0],'risk_level']='R1'
        df_vol.loc[(df_vol['zbnp'] <= threshold[1])&(df_vol['zbnp'] > threshold[0]), 'risk_level'] = 'R2'
        df_vol.loc[df_vol['zbnp'] >= threshold[-1], 'risk_level'] = 'R5'
        df_vol.loc[(df_vol['zbnp'] >= threshold[-2])&(df_vol['zbnp'] < threshold[-1]), 'risk_level'] = 'R4'

        df_db=self.read_fund_drawback_fromdb (asofdate)

        # temp=df_db.describe()
        # threshold=[(temp.loc['mean']-temp.loc['std'])[0],(temp.loc['mean']+temp.loc['std'])[0]]

        threshold = df_db.quantile([0.2, 0.4, 0.6, 0.8])['zbnp'].tolist()

        df_db['draw_back_level']='D3'
        df_db.loc[df_db['zbnp']<=threshold[0],'draw_back_level']='D1'
        df_db.loc[(df_db['zbnp'] <= threshold[1])&(df_db['zbnp'] > threshold[0]), 'draw_back_level'] = 'D2'
        df_db.loc[df_db['zbnp'] >= threshold[-1], 'draw_back_level'] = 'D5'
        df_db.loc[(df_db['zbnp'] >= threshold[-2])&(df_db['zbnp'] < threshold[-1]), 'draw_back_level'] = 'D4'


        outputdf=pd.merge(df_vol[['jjdm','risk_level']],df_db[['jjdm','draw_back_level']],how='outer',on='jjdm')

        print('risk label marked')
        return outputdf.fillna('')

    def classify(self):

        style_label=self.label_style(asofdate=self.exp_quater,filename='model_style_nv_2022-01-26.pkl')
        theme_label=self.label_theme(asofdate=self.exp_quater,filename='model_theme_nv_2022-01-26.pkl')
        #risk_label=self.label_risk(asofdate=self.vol_week, filename='model_risk_2022-01-10.pkl')
        risk_label=self.test(0)
        # risk_label=self.label_risk_new(asofdate=self.exp_quater)

        extra_info_mu = self.read_mu_extra_info()

        if(theme_label['theme'].dtype==np.float32):
            maplist=extra_info_mu['theme'].unique().tolist()
            maplist.remove(np.nan)
            maplist.sort()
            theme_label['theme']=[ maplist[int(x)] for x in theme_label['theme']]

        if (style_label['style'].dtype == np.float32):
            maplist = extra_info_mu['style'].unique().tolist()
            maplist.remove(np.nan)
            maplist.sort()
            style_label['style'] = [maplist[int(x)] for x in theme_label['style']]

        style_label['style_source']='model'
        theme_label['theme_source'] = 'model'

        final_df=pd.merge(style_label,theme_label,how='outer',left_on='jjdm',right_on='jjdm')
        final_df=pd.merge(final_df,risk_label,how='outer',left_on='jjdm',right_on='jjdm')

        sql="select jjdm,jjjc,clbz from st_hedge.t_st_jjxx where jjdm in ({0}) and clbz in('1','2','3','4')"\
            .format("'"+"','".join(final_df['jjdm'].unique())+"'")
        extra_info_prv=self.hbdb.db2df(sql,db='highuser')
        for key in self.clbz.keys():
            extra_info_prv.loc[extra_info_prv['clbz']==key,'clbz']=self.clbz[key]

        final_df=pd.merge(final_df,extra_info_prv,how='left',on='jjdm')
        final_df.loc[final_df['clbz'].isnull(),'clbz']='公募'

        prv=final_df[final_df['clbz']!='公募']
        mu=final_df[final_df['clbz']=='公募']
        del final_df


        mu=pd.merge(extra_info_mu,mu,how='left',on='jjdm')

        mu.fillna('', inplace=True)

        for i in mu.index:
            if(mu.loc[i]['style_x']=='' and mu.loc[i]['style_y']!=''):
                mu.loc[i,'style_x']=mu.loc[i]['style_y']
            if((mu.loc[i]['theme_x'] =='') and (mu.iloc[i]['theme_y'] !='')):
                mu.loc[i,'theme_x']=mu.iloc[i]['theme_y']

        for col in ['style_source','theme_source']:
            mu.loc[mu[col]=='',col]='wind'
        mu['clbz']='公募'
        mu.drop(['style_y','theme_y','jjjc_y'],axis=1,inplace=True)

        mu.rename(columns={'style_x':'style', 'theme_x':'theme','jjjc_x':'jjjc'},inplace=True)
        mu=mu[prv.columns]

        final_df=pd.concat([prv,mu],axis=0)
        final_df['style_updated_date']=self.exp_quater
        final_df['vol_updated_date'] = self.vol_week

        #check if the same data exists already, if yes, updates them with latest data
        # sql="select distinct (style_updated_date) from labled_fund_nv"
        # date_list=pd.read_sql(sql,con=self.localengine)['style_updated_date'].tolist()
        # if(self.today in date_list):
        #     sql="delete from labled_fund_nv where style_updated_date='{}'".format(self.today)
        #     self.localengine.execute(sql)
        #
        # sql="select distinct (vol_updated_date) from labled_fund_nv"
        # date_list=pd.read_sql(sql,con=self.localengine)['vol_updated_date'].tolist()
        # if(self.today in date_list):
        #     sql="delete from labled_fund_nv where vol_updated_date='{}'".format(self.today)
        #     self.localengine.execute(sql)

        final_df.fillna('',inplace=True)

        final_df[['jjjc','jjdm','clbz','style','theme','risk_level','draw_back_level','style_updated_date','vol_updated_date','style_source', 'theme_source']].to_sql('labled_fund_nv',con=self.localengine,index=False,if_exists='append')

        print('Fund has benn labled and saved in labled_fund_nv table ')

    def test(self,i):

        i+=1
        print("第{}次尝试".format(i))
        try:
            risk_label=self.label_risk_new(asofdate=self.exp_quater)
        except Exception as e:
            if ("Read timed out" in str(e)):
                risk_label=self.test(i)
            else:
                print(e)
                risk_label=''

        return risk_label

    def classify_hldbase(self):

        theme_label = self.label_theme(asofdate=self.exp_quater, filename='model_theme_hld_2022-01-28.pkl',
                                       value_style='hld')

        style_label = self.label_style(asofdate=self.exp_quater, filename='model_style_hld_2022-01-28.pkl',
                                       value_style='hld')

        style_label['style_source']='model'
        theme_label['theme_source'] = 'model'

        mu=pd.merge(style_label,theme_label,how='outer',left_on='jjdm',right_on='jjdm')

        extra_info_mu=self.read_mu_extra_info()
        mu=pd.merge(extra_info_mu,mu,how='left',on='jjdm')

        mu.fillna('', inplace=True)

        for i in mu.index:
            if(mu.loc[i]['style_x']=='' and mu.loc[i]['style_y']!=''):
                mu.loc[i,'style_x']=mu.loc[i]['style_y']
            if((mu.iloc[i]['theme_x'] =='') and (mu.iloc[i]['theme_y'] !='')):
                mu.loc[i,'theme_x']=mu.loc[i]['theme_y']

        for col in ['style_source','theme_source']:
            mu.loc[mu[col]=='',col]='wind'
        mu['clbz']='公募'
        mu.drop(['style_y','theme_y'],axis=1,inplace=True)
        mu.rename(columns={'style_x': 'style', 'theme_x': 'theme'}, inplace=True)

        mu['style_updated_date']=self.exp_quater
        mu['vol_updated_date'] = self.vol_week

        #check if the same data exists already, if yes, updates them with latest data
        sql="select distinct (style_updated_date) from labled_fund_hld"
        date_list=pd.read_sql(sql,con=self.localengine)['style_updated_date'].tolist()
        if(self.today.replace("-","") in date_list):
            sql="delete from labled_fund_hld where style_updated_date='{}'".format(self.today.replace("-",""))
            self.localengine.execute(sql)

        sql="select distinct (vol_updated_date) from labled_fund_hld"
        date_list=pd.read_sql(sql,con=self.localengine)['vol_updated_date'].tolist()
        if(self.today.replace("-","") in date_list):
            sql="delete from labled_fund_hld where vol_updated_date='{}'".format(self.today.replace("-",""))
            self.localengine.execute(sql)

        mu.fillna('',inplace=True)
        mu[['jjjc','jjdm','clbz','style','theme','style_updated_date','vol_updated_date','style_source', 'theme_source']].to_sql('labled_fund_hld',con=self.localengine,index=False,if_exists='append')

        print('Fund has benn labled and saved in labled_fund_hld table ')

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

        self.industry_name_map_e2c = dict(zip(self.indus_col,chinese_name))

        self.style_trans_map=dict(zip(self.barra_col,['市值','市场','动量','波动率','价值','非线性市值','流动性','盈利','成长','杠杆',]))

        self.ability_trans=dict(zip(['stock_alpha_ret_adj', 'trading_ret', 'industry_ret_adj',
       'unexplained_ret', 'barra_ret_adj'],['股票配置','交易','行业配置','Alpha','风格配置']))

    def read_barra_fromdb(self,date_sql_con,tickerlist):

        # date_list=[''.join(x.split('-')) for x in date_list.astype(str)]
        # date_con="'"+"','".join(date_list)+"'"
        ticker_con="'"+"','".join(tickerlist)+"'"

        sql="""
        select ticker,trade_date,size,beta,momentum,resvol,btop,sizenl,liquidity,earnyield,growth,leverage,
        aerodef,agriforest,auto,bank,builddeco,chem,conmat,commetrade,computer,conglomerates,eleceqp,electronics,
        foodbever,health,houseapp,ironsteel,leiservice,lightindus,machiequip,media,mining,nonbankfinan,nonfermetal,
        realestate,telecom,textile,transportation,utilities 
        from st_ashare.r_st_barra_style_factor where trade_date in ({0}) and ticker in ({1})
        """.format(date_sql_con,ticker_con)
        expdf=self.hbdb.db2df(sql,db='alluser')

        fac_ret_df=pd.DataFrame()
        date_list=date_sql_con.split(',')
        date_list.sort()
        for i in range(len(date_list)-1):
            t0=date_list[i]
            t1=date_list[i+1]
            sql="select factor_name,factor_ret,trade_date from st_ashare.r_st_barra_factor_return where trade_date>={0} and trade_date<{1} "\
                .format(t0,t1)
            temp=self.hbdb.db2df(sql,db='alluser')
            temp['factor_ret']=temp['factor_ret']+1
            temp=temp.groupby('factor_name').prod()
            temp['factor_ret'] = temp['factor_ret'] -1
            temp.reset_index(drop=False,inplace=True)
            temp['trade_date']=t0.replace("'","")
            fac_ret_df=pd.concat([fac_ret_df,temp],axis=0)


        return expdf,fac_ret_df

    def read_anon_fromdb(self,date_list,tickerlist):

        # date_list=[''.join(x.split('-')) for x in date_list.astype(str)]
        ticker_con="'"+"','".join(tickerlist)+"'"
        date_list.sort()
        outputdf=pd.DataFrame()
        for i in range(len(date_list)-1):
            t0=date_list[i]
            t1=date_list[i+1]
            sql=""" select ticker,trade_date,s_ret from st_ashare.r_st_barra_specific_return where ticker in ({0})
            and trade_date >='{1}' and trade_date<'{2}'
            """.format(ticker_con,t0,t1)

            anon_ret=self.hbdb.db2df(sql,db='alluser')
            anon_ret['s_ret']=1+anon_ret['s_ret']
            temp=anon_ret.groupby('ticker').prod()
            temp['s_ret']=temp['s_ret']-1
            temp['trade_date']=t0
            temp.reset_index(drop=False,inplace=True)
            outputdf=pd.concat([outputdf,temp],axis=0)

        return outputdf

    def read_hld_fromdb(self,start_date,end_date,jjdm):

        sql="""select jsrq,zqdm,zjbl from st_fund.t_st_gm_gpzh where jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}'
        """.format(jjdm,start_date,end_date)
        hld=self.hbdb.db2df(sql,db='funduser')
        hld['jsrq']=hld['jsrq'].astype(str)
        return hld

    def smooth_hld(self,hld,date_list_orgi,weight_col,date_col,code_col):

        date_list=date_list_orgi.copy()
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


            ext_date_list = self.hbdb.db2df(sql, db='alluser')
            ext_date_list['yeatmonth'] = [x[0:6] for x in ext_date_list['trade_date']]

            # if(q0 not in ext_date_list['trade_date'].tolist()):
            #     hld.loc[hld['jsrq']==q0,'jsrq']=ext_date_list['trade_date'].to_list()[0]
            #     q0=ext_date_list['trade_date'].to_list()[0]
            #     date_list[i]=q0
            # else:
            #     ext_date_list.drop(ext_date_list[ext_date_list['yeatmonth'] == q0[0:6]].index, axis=0, inplace=True)
            #
            # if(q1 not in ext_date_list['trade_date'].tolist()):
            #     hld.loc[hld['jsrq']==q1,'jsrq']=ext_date_list['trade_date'].to_list()[-1]
            #     q1=ext_date_list['trade_date'].to_list()[-1]
            #     date_list[i+1] = q1

            ext_date_list.drop(ext_date_list[ext_date_list['yeatmonth']==q1[0:6]].index,axis=0,inplace=True)

            ext_date_list=ext_date_list.drop_duplicates('yeatmonth', keep='last')['trade_date'].to_list()

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

        sql = """select jsrq,fldm,zzjbl from st_fund.t_st_gm_gpzhhytj where jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}' and hyhfbz='2'
        """.format(jjdm, start_date, end_date)
        hld = self.hbdb.db2df(sql, db='funduser')
        hld['jsrq'] = hld['jsrq'].astype(str)

        sql="select fldm,flmc from st_market.t_st_zs_hyzsdmdyb where hyhfbz='2'"
        industry_map=self.hbdb.db2df(sql,db='alluser')

        hld=pd.merge(hld,industry_map,how='left',on='fldm')
        hld.drop(hld[hld['flmc'].isnull()].index,axis=0,inplace=True)
        hld['flmc']=[ self.industry_name_map[x] for x in hld['flmc']]

        hld.loc[hld['zzjbl']==99999,'zzjbl']=0
        hld['zzjbl']=hld['zzjbl']/100

        return hld

    def read_hld_ind_fromstock(self,hld,tickerlist,hfbz=24):

        ticker_con="'"+"','".join(tickerlist)+"'"

        sql="select a.zqdm,b.yjxymc,b.xxfbrq from st_ashare.t_st_ag_zqzb a left join st_ashare.t_st_ag_gshyhfb b on a.gsdm=b.gsdm where a.zqdm in ({0}) and b.xyhfbz={1} "\
            .format(ticker_con,hfbz)
        ind_map=self.hbdb.db2df(sql,db='alluser')
        ind_map.sort_values(['zqdm','xxfbrq'],inplace=True)
        temp=ind_map['zqdm']
        temp.drop_duplicates(keep='last', inplace=True)
        ind_map=ind_map.loc[temp.index][['zqdm','yjxymc']]

        ind_hld=pd.merge(hld,ind_map,how='left',on='zqdm')

        ind_hld=ind_hld.groupby(['jsrq', 'yjxymc'], as_index=False).sum()
        ind_hld.rename(columns={'yjxymc': 'flmc', 'zjbl': 'zzjbl'}, inplace=True)
        ind_hld['fldm']=''
        ind_hld['flmc']=[self.industry_name_map[x] for x in ind_hld['flmc']]
        ind_hld['zzjbl']=ind_hld['zzjbl']/100

        return ind_hld[['fldm','zzjbl', 'jsrq','flmc']]

    def weight_times_exp(self,fund_exp,col_list):

        for col in col_list:
            fund_exp[col]=fund_exp[col]*fund_exp['zjbl']

        return  fund_exp

    def _shift_date(self,date):
        trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, date)
        df=self.hbdb.db2df(sql_script,db='readonly')
        df=df.rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                      "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isOpen'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    def stock_price(self,date_sql_con,tickerlist):

        # date_list=[''.join(x.split('-')) for x in date_list.astype(str)]
        ticker_con="'"+"','".join(tickerlist)+"'"

        sql="""
        select ZQDM,JYRQ,DRJJ from FUNDDB.ZGJY where ZQDM in ({0}) and JYRQ in ({1})
         """.format(ticker_con,date_sql_con)

        stock_price=self.hbdb.db2df(sql,db='readonly')

        jyrq_list=stock_price['JYRQ'].unique().tolist()
        jyrq_list.sort()
        right_df=pd.DataFrame()
        for i in range(0,len(jyrq_list)-1):
            tempdf=pd.merge(stock_price[stock_price['JYRQ']==jyrq_list[i]][['ZQDM','JYRQ','DRJJ']]
                            ,stock_price[stock_price['JYRQ']==jyrq_list[i+1]][['ZQDM','DRJJ']]
                            ,how='inner',on='ZQDM')
            tempdf['hld_ret']=tempdf['DRJJ_y']/tempdf['DRJJ_x']-1
            right_df=pd.concat([right_df,tempdf[['ZQDM','JYRQ','hld_ret']]])

        #stock_price['hld_ret']=stock_price['SPJG']/stock_price['QSPJ']-1
        stock_price=pd.merge(stock_price,right_df,how='left',on=['ZQDM','JYRQ'])

        return stock_price

    @staticmethod
    def hld_compenzation(hlddf,fund_allocation):

        q_date=hlddf.loc[[(x[4:6] == '03') | (x[4:6] == '09') for x in hlddf['jsrq']]]['jsrq'].unique().tolist()
        a_date=hlddf.loc[[(x[4:6] == '06') | (x[4:6] == '12') for x in hlddf['jsrq']]]['jsrq'].unique().tolist()
        q_list=hlddf['jsrq'].unique().tolist()
        q_list.sort()

        hld_H=pd.DataFrame()
        hld_L = pd.DataFrame()
        #get heavy hld for annual and half_annual report
        for date in a_date:
            hld_H=pd.concat([hld_H,hlddf[hlddf['jsrq']==date].sort_values('zjbl')[-10:].reset_index(drop=True)],axis=0)
            hld_L=pd.concat([hld_L,hlddf[hlddf['jsrq']==date].sort_values('zjbl')[0:-10].reset_index(drop=True)],axis=0)
        for date in q_date:
            hld_H=pd.concat([hld_H,hlddf[hlddf['jsrq']==date]],axis=0)


        for i in range(len(q_list)):
            t1=q_list[i]
            if((i>0) and (t1[4:6] == '03') or  (t1[4:6] == '09')):
                t0=q_list[i-1]
            else:
                continue
            #calculate the no hevay hld for quarter report data by the mean of two annaul data if next annaul report exists
            if(i!=len(q_list)-1):
                t2=q_list[i+1]
                temp=pd.merge(hlddf[hlddf['jsrq']==t0].sort_values('zjbl')[0:-10],
                              hlddf[hlddf['jsrq']==t2].sort_values('zjbl')[0:-10],
                              how='outer',on='zqdm').fillna(0)
                temp.set_index('zqdm',inplace=True)
                if(len(temp)==0):
                    continue
                drop_list=list(set(temp.index).intersection( set(hlddf[hlddf['jsrq']==t1]['zqdm'])))
                temp.drop(drop_list,axis=0,inplace=True)
                temp['zjbl']=(temp['zjbl_x']+temp['zjbl_y'])/2
                temp['zjbl']=temp['zjbl']*((fund_allocation[fund_allocation['jsrq'] == t1]['gptzzjb']*100-hld_H[hld_H['jsrq']==t1]['zjbl'].sum()).values[0]/temp['zjbl'].sum())
                temp['jsrq']=t1
                temp.reset_index(drop=False,inplace=True)
                hld_L=pd.concat([hld_L,temp[['zjbl','jsrq','zqdm']]],axis=0)

            else:
                temp=hlddf[hlddf['jsrq']==t0].sort_values('zjbl')[0:-10]
                temp['zjbl']=temp['zjbl']/temp['zjbl'].sum()
                temp['zjbl']=temp['zjbl']*(fund_allocation[fund_allocation['jsrq'] == t1]['gptzzjb']*100-hld_H[hld_H['jsrq']==t1]['zjbl'].sum()).values[0]
                temp['jsrq']=t1
                temp.reset_index(drop=False,inplace=True)
                hld_L=pd.concat([hld_L,temp[['zjbl','jsrq','zqdm']]],axis=0)
        return pd.concat([hld_H,hld_L],axis=0).sort_values('jsrq').reset_index(drop=True)

    def save_barra_ret2db(self,jjdm,start_date,end_date,add=False,hld_compenzation=False):

        hld=self.read_hld_fromdb(start_date,end_date,jjdm)

        tickerlist=hld['zqdm'][~hld['zqdm'].dropna().str.contains('H')].unique()

        org_date_list=hld['jsrq'].unique().tolist()
        date_list = [self._shift_date(x) for x in org_date_list]
        date_map=dict(zip(org_date_list,date_list))
        changed_date=set(org_date_list).difference(set(date_list))


        fund_allocation = self.fund_asset_allocation(jjdm, org_date_list)

        if(hld_compenzation):
            hld = self.hld_compenzation(hld,fund_allocation)
            table_sur='barra_style_hldcom_'
            hld_industry = self.read_hld_ind_fromstock(hld,tickerlist)
        else:
            table_sur='barra_style_'
            hld_industry = self.read_hld_ind_fromdb(start_date, end_date, jjdm)

        for date in changed_date:
            hld.loc[hld['jsrq']==date,'jsrq']=date_map[date]
            hld_industry.loc[hld_industry['jsrq'] == date, 'jsrq'] = date_map[date]
            fund_allocation.loc[fund_allocation['jsrq'] == date, 'jsrq'] = date_map[date]


        hld=self.smooth_hld(hld,date_list,weight_col='zjbl',date_col='jsrq',code_col='zqdm')
        hld_industry=self.smooth_hld(hld_industry[['zzjbl','jsrq','flmc']],date_list,weight_col='zzjbl',date_col='jsrq',code_col='flmc')
        fund_allocation = self.smooth_hld(fund_allocation, date_list, weight_col='gptzzjb', date_col='jsrq',
                                          code_col='jjdm')
        date_sql_con="'"+"','".join(hld['jsrq'].unique().tolist())+"'"

        expdf, fac_ret_df=self.read_barra_fromdb(date_sql_con,tickerlist)

        stock_df = self.stock_price(date_sql_con, tickerlist)

        anno_df=self.read_anon_fromdb(hld['jsrq'].unique().tolist(),tickerlist)

        fund_exp=pd.merge(hld,expdf[['ticker','trade_date']+self.barra_col],
                          how='inner',left_on=['zqdm','jsrq'],
                          right_on=['ticker','trade_date']).drop(['ticker', 'trade_date'],axis=1)

        fund_exp=pd.merge(fund_exp, stock_df[['ZQDM', 'JYRQ', 'hld_ret']], how='inner', left_on=['zqdm', 'jsrq'],
                 right_on=['ZQDM', 'JYRQ']).drop(['ZQDM','JYRQ'],axis=1)

        fund_exp=pd.merge(fund_exp, anno_df, how='left', left_on=['zqdm', 'jsrq'],
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

        for date in fac_ret_df['trade_date'].unique():

            tempdf=fac_ret_df[fac_ret_df['trade_date']==date][['factor_ret','factor_name']].T
            tempdf.columns = [x.lower() for x in  tempdf.loc['factor_name']]

            indus_exp=pd.merge(indus_exp,hld_industry[hld_industry['jsrq']==date][['zzjbl','flmc','jsrq']]
                               ,how='left',left_on='industry',right_on='flmc').drop(['flmc','jsrq'],axis=1).fillna(0)
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
            sql="select distinct jjrq from {1}hld_ret where jjdm='{0}'".format(jjdm,table_sur)
            date_list=pd.read_sql(sql,con=self.localengine)['jjrq']
            common_date=list(set(date_list).intersection(set(fund_allocation['jsrq'] )))
            date_con="'"+"','".join(common_date)+"'"

            sql="delete from {2}fund_exp where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con,table_sur)
            self.localengine.execute(sql)
            sql="delete from {2}indus_exp where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con,table_sur)
            self.localengine.execute(sql)
            sql="delete from {2}hld_ret where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con,table_sur)
            self.localengine.execute(sql)
            sql="delete from {2}s_ret where jjdm='{0}' and jjrq in ({1})".format(jjdm,date_con,table_sur)
            self.localengine.execute(sql)
            sql = "delete from {2}fund_allocation where jjdm='{0}' and jsrq in ({1})".format(jjdm, date_con,table_sur)
            self.localengine.execute(sql)

        fund_exp.to_sql(table_sur+'fund_exp',con=self.localengine,index=False,if_exists='append')
        indus_exp.to_sql(table_sur+'indus_exp', con=self.localengine,index=False,if_exists='append')
        hld_ret.to_sql(table_sur+'hld_ret', con=self.localengine,index=False,if_exists='append')
        s_ret.to_sql(table_sur+'s_ret', con=self.localengine,index=False,if_exists='append')
        fund_allocation.to_sql(table_sur+'fund_allocation', con=self.localengine,index=False,if_exists='append')

        #print('{0} data for {1} to {2} has been saved in local db'.format(jjdm,start_date,end_date))

    def read_barra_retfromdb(self,jjdm,start_date,end_date,hld_com):

        if(hld_com):
            surname='barra_style_hldcom_'
        else:
            surname='barra_style_'

        sql="select * from {3}fund_exp where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date,surname)
        fund_exp=pd.read_sql(sql,con=self.localengine).drop(['jjdm','jjrq'],axis=1)
        fund_exp.set_index('index',drop=True,inplace=True)

        sql="select * from {3}indus_exp where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date,surname)
        indus_exp=pd.read_sql(sql,con=self.localengine).drop(['jjdm','jjrq'],axis=1)
        indus_exp.set_index('index', drop=True,inplace=True)

        sql="select * from {3}hld_ret where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date,surname)
        hld_ret=pd.read_sql(sql,con=self.localengine).drop(['jjdm'],axis=1)
        hld_ret.set_index('jjrq', drop=True,inplace=True)

        sql="select * from {3}s_ret where jjdm='{0}' and jjrq>='{1}' and jjrq<='{2}'"\
            .format(jjdm,start_date,end_date,surname)
        s_ret=pd.read_sql(sql,con=self.localengine).drop(['jjdm'],axis=1)
        s_ret.set_index('jjrq', drop=True,inplace=True)

        sql="select * from {3}fund_allocation where jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}'"\
            .format(jjdm,start_date,end_date,surname)
        fund_allocation=pd.read_sql(sql,con=self.localengine).drop(['jjdm'],axis=1)

        sql="""select jsrq from st_fund.t_st_gm_gpzh where jjdm='{0}' and jsrq>='{1}' and jsrq<='{2}'
        """.format(jjdm,start_date,end_date)
        hld=self.hbdb.db2df(sql,db='funduser')
        hld['jsrq']=hld['jsrq'].astype(str)

        date_list=hld['jsrq'].unique().tolist()

        return fund_exp, indus_exp, hld_ret, s_ret, date_list,fund_allocation

    def fund_nv(self,jjdm,date_list):

        date_con="'"+"','".join(date_list)+"'"

        sql="""
        select jzrq,zbnp from st_fund.t_st_gm_rqjhb where jjdm='{0}' and zblb='2101'
        and jzrq in ({1})
        """.format(jjdm,date_con)

        fundnv=self.hbdb.db2df(sql,db='funduser')
        fundnv.rename(columns={'zbnp':'hbdr'},inplace=True)
        fundnv['jzrq']=fundnv['jzrq'].astype(str)
        fundnv['hbdr']=fundnv['hbdr']/100

        return fundnv

    def fund_asset_allocation(self,jjdm,date_list):

        sql="select jjdm,jsrq,jjzzc,gptzzjb from st_fund.t_st_gm_zcpz where jjdm='{2}' and jsrq>='{0}' and jsrq<='{1}'"\
            .format(date_list[0],date_list[-1],jjdm)
        fund_allocation=self.hbdb.db2df(sql,db='funduser')
        fund_allocation['gptzzjb']=fund_allocation['gptzzjb']/100
        fund_allocation['jsrq']=fund_allocation['jsrq'].astype(str)
        return fund_allocation

    def ret_div(self,jjdm,start_date,end_date,hld_com):

        fund_exp,indus_exp,hld_ret,s_ret,date_list,fund_allocation=self.read_barra_retfromdb(jjdm,start_date,end_date,hld_com)

        fundnv=self.fund_nv(jjdm,hld_ret.index.tolist())

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

    def cul_ret(self,weight,ret):

        cul_ret=1
        for i in range(len(weight)):
            cul_ret*=weight[i]*ret[i]+1

        return cul_ret

    def style_change_detect_engine(self,q_df,diff1,diff2,q_list,col_list,t1,t2):

        style_change=[]

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

                if((q_list.index(added_date)-q_list.index(last_added_date)<=2
                        and q_list.index(added_date)-q_list.index(last_added_date)>0) or added_date==q_list[-1]):
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

        return style_change

    def style_change_detect_engine2(self, q_df, diff1, col_list, t1, t2):

        style_change=[]
        t3=t2/2

        for col in col_list:

            tempdf=pd.merge(q_df[col],diff1[col],how='left',on='date')
            tempdf['style']=''
            style_num=0
            tempdf['style'].iloc[0:2] = style_num

            for i in range(2,len(tempdf)-1):
                if(tempdf[col+'_y'].iloc[i]>t1 and tempdf[col+'_y'].iloc[i+1]>-1*t3 ):
                    style_num+=1
                    added_date = tempdf.index[i]
                    style_change.append(added_date + "@" + col)
                elif(tempdf[col+'_x'].iloc[i]-tempdf[tempdf['style']==style_num][col+'_x'][0]>t1 and
                     tempdf[col+'_y'].iloc[i]>t2 and tempdf[col+'_y'].iloc[i+1]>-1*t3):
                    style_num += 1
                    added_date=tempdf.index[i]
                    style_change.append(added_date + "@" + col)
                elif(tempdf[col+'_y'].iloc[i]<-1*t1 and tempdf[col+'_y'].iloc[i+1]<t3 ):
                    style_num += 1
                    added_date = tempdf.index[i]
                    style_change.append(added_date + "@" + col)
                elif (tempdf[col + '_x'].iloc[i] - tempdf[tempdf['style'] == style_num][col + '_x'][0] < -1*t1 and
                      tempdf[col + '_y'].iloc[i] < -1*t2 and tempdf[col + '_y'].iloc[i + 1] <  t3):
                    style_num += 1
                    added_date = tempdf.index[i]
                    style_change.append(added_date + "@" + col)

                tempdf['style'].iloc[i] = style_num

        return style_change

    def style_change_detect(self,df,q_list,col_list,t1,t2):

        q_list.sort()
        q_df = df.loc[q_list]
        diff1=q_df.diff(1)
        # diff2=q_df.rolling(3).mean().diff(2)
        # diff4 = q_df.rolling(3).mean().diff(4)

        # style_change_short=self.style_change_detect_engine(q_df,diff1,diff2,q_list,col_list,t1,t2)
        # style_change_long=self.style_change_detect_engine(q_df,diff1,diff4,q_list,col_list,t1,t2)
        # style_change=style_change_short+style_change_long

        style_change = self.style_change_detect_engine2(q_df, diff1, col_list, t1, t2)

        return list(set(style_change)),np.array(q_list)

    def shifting_expression(self,change_ret,name,jjdm,style='Total'):

        change_winning_pro = sum(change_ret[2] > 0) / len(change_ret)
        left_ratio = sum(change_ret[0] < 0) / len(change_ret)
        right_ratio = sum(change_ret[0] > 0) / len(change_ret)
        one_q_ret = change_ret[2].mean()
        current_q_ret = change_ret[1].mean()
        # print(
        #     "for {6},{5} {8} shift : number of shifting is {4}, winning pro is {0}, left ratio is {1}, right ratio is {2},average return for next Q is {3},average return for this Q is {7}"
        #     .format(change_winning_pro, left_ratio, right_ratio, one_q_ret, len(change_ret), name, jjdm, current_q_ret,style))

        return  np.array([style.split('_')[0],len(change_ret),change_winning_pro,one_q_ret,current_q_ret,left_ratio,right_ratio])

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

    def style_shifting_analysis(self,df,q_list,col_list,t1,t2,name,jjdm):

        # col_list=[x+"_exp_adj" for x in col]
        change_ret=self.style_change_ret(df,q_list,col_list,t1=t1,t2=t2)
        change_ret = pd.DataFrame.from_dict(change_ret).T
        change_ret['style'] = list([x.split('@')[1] for x in change_ret.index])
        change_ret['date'] = list([x.split('@')[0] for x in change_ret.index])

        data=[]

        if(len(change_ret)>0):
            data.append(self.shifting_expression(change_ret,name,jjdm))
            for style in change_ret['style'].unique():
                tempdf=change_ret[change_ret['style']==style]
                data.append(self.shifting_expression(tempdf,name,jjdm,style))

        shift_df = pd.DataFrame(data=data,columns=['风格类型','切换次数','胜率','下季平均收益','当季平均收益','左侧比率','右侧比例'])

        for col in ['胜率','下季平均收益','当季平均收益','左侧比率','右侧比例']:
            shift_df[col] = shift_df[col].astype(float).map("{:.2%}".format)

        return  shift_df

    def style_label_engine(self,desc,style_stable_list,exp1,exp2,exp3,map_dict):

        style_lable=[]

        for style in style_stable_list:
            if(abs(desc[style]['mean'])>=exp2 and abs(desc[style]['mean'])<exp1):
                label="稳定偏好{}".format("较@"+map_dict[style.split('_')[0]])
            elif(abs(desc[style]['mean'])>=exp1):
                label="稳定偏好{}".format("@"+map_dict[style.split('_')[0]])
            elif(abs(desc[style]['mean'])<=exp3):
                label = "规避{}暴露".format(map_dict[style.split('_')[0]])
            else:
                continue
            if(desc[style]['mean'])<0:
                label=label.replace('@','低')
            else:
                label=label.replace('@','高')
            style_lable.append(label)

        return style_lable

    def style_label_generator(self,df,style_shift_df,ind_shift_df,average_a_w,hld_com):

        style_noshift_col=list(set(self.barra_col).difference(set(style_shift_df.iloc[1:]['风格类型'])))
        ind_noshift_col=list(set(self.indus_col).difference(set(ind_shift_df.iloc[1:]['风格类型'])))

        if(len(style_noshift_col)>0):
            if (hld_com):
                desc=df[[x+"_exp" for x in style_noshift_col]].describe()
            else:
                desc=df[[x+"_exp_adj" for x in style_noshift_col]].describe()

            style_stable_list=desc.columns[((desc.loc['max'] - desc.loc['min']) < 0.5*average_a_w).values].tolist()
            style_lable = self.style_label_engine(desc, style_stable_list,0.75*average_a_w,0.5*average_a_w,0.25*average_a_w,self.style_trans_map)
        else:
            style_lable=[]


        if(len(ind_noshift_col)>0):
            if (hld_com):
                desc=df[[x+"_exp" for x in ind_noshift_col]].describe()
            else:
                desc=df[[x+"_exp_adj" for x in ind_noshift_col]].describe()

            ind_stable_list=desc.columns[((desc.loc['max'] - desc.loc['min']) < 0.1*average_a_w).values].tolist()
            ind_lable = self.style_label_engine(desc, ind_stable_list,0.2*average_a_w,0.1*average_a_w,0.05*average_a_w,self.industry_name_map_e2c)
        else:
            ind_lable=[]

        return style_lable+ind_lable

    def ret_analysis(self,df,a_list,hld_com):

        ret_col_list = ['hld_based_ret', 'barra_ret', 'stock_alpha_ret', 'industry_ret']

        if(hld_com):
            for col in ret_col_list:
                df[col + '_adj'] = np.append([np.nan], df[col][0:-1])
        else:
            for col in ret_col_list:
                df[col+'_adj']=df[col]/df['published_stock_weight']*df['gptzzjb']
                df[col+'_adj'] = np.append([np.nan], df[col+'_adj'][0:-1])

        df = df[[x + '_adj' for x in ret_col_list] + ['nv_ret']]

        df['unexplained_ret'] = df['hld_based_ret_adj'] - (
                    df['barra_ret_adj'] + df['industry_ret_adj'] + df['stock_alpha_ret_adj'])
        df['trading_ret'] =df['nv_ret']- df['hld_based_ret_adj']

        ability_label = []
        for col in ['barra_ret_adj','industry_ret_adj','stock_alpha_ret_adj','unexplained_ret']:
            temp=(df[col]/df['hld_based_ret_adj']).describe()
            print(col)
            print(temp['50%'])
            print(temp['std'])
            if(abs(temp['50%'])>0.35):
                if(temp.std()/temp.mean()<=1):
                    ext = '稳定'
                else:
                    ext = ''
                if(temp['50%']>0):
                    ext2='良好的'
                else:
                    ext2 = '糟糕的'
                ability_label.append(ext+ext2 + self.ability_trans[col] + "能力")

        temp=(df['trading_ret']/df['nv_ret']).describe()

        if(abs(temp['50%'])>0.5):
            if(temp.std()/temp.mean()<=1):
                ext = '稳定'
            else:
                ext = ''
            if(temp['50%']>0):
                ext2='良好的'
            else:
                ext2 = '糟糕的'
            ability_label.append(ext+ext2 + self.ability_trans[col] + "能力")

        return ability_label

    def exp_analysis(self,df,q_list,jjdm,average_a_w,hld_com):

        if(hld_com):
            style_shift_df = self.style_shifting_analysis(
                df[[x + "_exp" for x in self.barra_col] + [x for x in self.barra_col]].astype(float),
                q_list,[x + "_exp" for x in self.barra_col],
                t1=0.5 * average_a_w, t2=0.2 * average_a_w, name='barra style', jjdm=jjdm)

            ind_shift_df = self.style_shifting_analysis(
                df[[x + "_exp" for x in self.indus_col] + [x  for x in self.indus_col]].astype(float),
                q_list,[x + "_exp" for x in self.indus_col],
                t1=0.1 * average_a_w, t2=0.075 * average_a_w, name='industry', jjdm=jjdm)

        else:

            style_shift_df=self.style_shifting_analysis(
                df[[x+"_exp_adj" for x in self.barra_col]+[x+"_adj" for x in self.barra_col]].astype(float)
                ,q_list,[x+"_exp_adj" for x in self.barra_col],t1=0.3*average_a_w,
                t2=0.15*average_a_w,name='barra style',jjdm=jjdm)

            ind_shift_df=self.style_shifting_analysis(
                df[[x + "_exp_adj" for x in self.indus_col]+[x+"_adj" for x in self.indus_col]].astype(float),
                q_list,[x+"_exp_adj" for x in self.indus_col], t1=0.1*average_a_w,
                t2=0.05*average_a_w, name='industry',jjdm=jjdm)

        style_lable = self.style_label_generator(df,style_shift_df,ind_shift_df,average_a_w,hld_com)

        return  style_shift_df,ind_shift_df,style_lable

    def centralization_level(self,df):

        outputdf=pd.DataFrame(index=df.index,columns=['c_level'])

        for i in range(len(df)):
            outputdf.iloc[i]['c_level']=(df.iloc[i].sort_values()[-5:].sum()+df.iloc[i].sort_values()[-3:].sum())/2/df.iloc[i].sum()

        return outputdf.mean()[0]

    def ind_shift_rate(self,indf):
        indf.sort_index(inplace=True)
        for col in self.indus_col:
            indf[col+'_mkt']=indf[col+'_exp']*indf['jjzzc']
        diff=indf[[x+'_mkt' for x in self.indus_col]].diff(1)
        diff['jjzzc']=indf[[x+'_mkt' for x in self.indus_col]].sum(axis=1)
        diff['jjzzc']=diff['jjzzc'].rolling(2).mean()
        shift_ratio=diff[[x+'_mkt' for x in self.indus_col]].abs().sum(axis=1)/2/diff['jjzzc']
        return shift_ratio.describe()

    def ind_analysis(self,df,hld_com):

        q_date=df.loc[[(x[4:6] == '03') | (x[4:6] == '09') for x in df.index]].index
        a_date=df.loc[[(x[4:6] == '06') | (x[4:6] == '12') for x in df.index]].index
        q_list=q_date.to_list()+a_date.to_list()

        if(not hld_com):
            #calculate the ratio between quarter report stock weigth and annual report stock weight
            average_q_w=(df.loc[q_date]['published_stock_weight']).mean()
            average_a_w=(df.loc[a_date]['published_stock_weight']).mean()
            shift_confidence=average_q_w/average_a_w

            # calculate the average industry exp num
            inddf = df[[x + '_exp_adj' for x in self.indus_col]].loc[q_list]
            average_ind_num = (inddf.loc[a_date] > 0).sum(axis=1).mean()
            adj_average_ind_num = ((inddf > 0).sum(axis=1) * df.loc[q_list][
                'published_stock_weight']).mean() / average_a_w

            # calculate the industry holding centralization_level
            average_ind_cen_level = self.centralization_level(inddf.loc[a_date])

            # calculate the industry holding shift ratio
            shift_ratio = self.ind_shift_rate(df[[x + '_exp' for x in self.indus_col] + ['jjzzc']].loc[a_date])

            # the 50,75,25 for c is 0.0.63,0.72,0.56
            # the 50,75,25 for r is 0.43,0.51,0.34
            if (average_ind_cen_level > 0.63 and shift_ratio['mean'] > 0.43):
                ind_label = '行业博弈型'
            elif (average_ind_cen_level > 0.63 and shift_ratio['mean'] < 0.43):
                ind_label = '行业专注型'
            elif (average_ind_cen_level < 0.63 and shift_ratio['mean'] > 0.43):
                ind_label = '行业轮动型'
            elif (average_ind_cen_level < 0.63 and shift_ratio['mean'] < 0.43):
                ind_label = '行业配置型'
            else:
                ind_label = ''

            a_date=a_date.tolist()

        else:
            shift_confidence=1
            inddf = df[[x + '_exp' for x in self.indus_col]]

            average_q_w = (df.loc[q_date]['published_stock_weight']).mean()
            average_a_w = (df.loc[a_date]['published_stock_weight']).mean()

            # calculate the average industry exp num
            average_ind_num = (inddf.loc[q_list] > 0).sum(axis=1).mean()

            # calculate the industry holding centralization_level
            average_ind_cen_level = self.centralization_level(inddf)

            # calculate the industry holding shift ratio
            shift_ratio = self.ind_shift_rate(df[[x + '_exp' for x in self.indus_col] + ['jjzzc']].loc[q_list])
            #the 50,75,25 for c is 0.0.63,0.72,0.56
            #the 50,75,25 for r is 0.43,0.51,0.34
            if(average_ind_cen_level>0.63 and shift_ratio['mean']>0.43):
                ind_label='行业博弈型'
            elif (average_ind_cen_level > 0.63 and shift_ratio['mean'] < 0.43):
                ind_label = '行业专注型'
            elif (average_ind_cen_level < 0.63 and shift_ratio['mean'] > 0.43):
                ind_label = '行业轮动型'
            elif (average_ind_cen_level <0.63 and shift_ratio['mean'] < 0.43):
                ind_label = '行业配置型'
            else:
                ind_label=''

            a_date=q_list

        # print(ind_label)

        return ind_label,q_list,average_a_w,average_ind_cen_level,shift_ratio['mean'],shift_confidence,a_date

    def classify(self,jjdm,start_date,end_date,hld_com=False):

        df,q_list=self.ret_div(jjdm,start_date,end_date,hld_com)

        ind_label,q_list,average_a_w,average_ind_cen_level,shift_ratio,shift_confidence,a_list=self.ind_analysis(df,hld_com)

        style_shift_df,ind_shift_df,style_lable=self.exp_analysis(df,a_list,jjdm,average_a_w,hld_com)

        ability_label=self.ret_analysis(df,a_list,hld_com)

        if(hld_com):
            df=df[[x + "_exp" for x in self.barra_col]+[x + "_exp" for x in self.indus_col]]
        else:
            df = df[[x + "_exp_adj" for x in fc.barra_col] + [x + "_exp_adj" for x in self.indus_col]]

        return df,style_shift_df,ind_shift_df,style_lable,average_ind_cen_level,shift_ratio,shift_confidence,average_a_w,ind_label,ability_label

    def data_preparation(self,hld_compenzation=False):


        sql="""select distinct jjdm from st_fund.t_st_gm_gpzh where jsrq='20210930'
        """
        jjdm_list=self.hbdb.db2df(sql,db='funduser')

        sql="select distinct jjdm from st_fund.t_st_gm_jjxx where jjfl='1' or jjfl='3' "
        stock_jjdm=self.hbdb.db2df(sql,db='funduser')

        jjdm_list=pd.merge(jjdm_list,stock_jjdm,how='inner',on='jjdm')['jjdm']
        #'000172'
        for i in range(36,len(jjdm_list)):
            jjdm=jjdm_list.iloc[i]
        # for jjdm in jjdm_list:

            sql = """select min(jsrq) from st_fund.t_st_gm_gpzh where jjdm='{0}' and jsrq>=20150101
            """.format(jjdm)
            jsrq = str(self.hbdb.db2df(sql, db='funduser')['min(jsrq)'][0])
            #['2016','2017','2018','2019','2020','2021']
            for year in ['2016','2017','2018','2019','2020','2021']:
                if(year<jsrq[0:4]):
                    continue
                elif(year==jsrq[0:4]):
                    start_date=jsrq
                else:
                    start_date = str(int(year)-1) + "1231"

                end_date=year+"1231"
                try:
                    self.save_barra_ret2db(jjdm=jjdm,start_date=start_date,end_date=end_date,add=False,hld_compenzation=hld_compenzation)
                except Exception as e :
                    print(e)
                    print("{} failed at start date {} and end date{}".format(jjdm,start_date,end_date))

if __name__ == '__main__':

    fc=Classifier_barra()

    #fc.data_preparation(hld_compenzation=True)

    for jjdm in ['000001']:

        df,style_shift_df,ind_shift_df,style_lable,average_ind_cen_level,\
        shift_ratio,shift_confidence,average_a_w,ind_label\
            ,ability_label=fc.classify(jjdm, '20151231', '20210930',hld_com=True)

        #print("风格/行业切换(置信度{0}%)".format(shift_confidence * 100))
        print("平均持股比例{0}%".format(average_a_w * 100))
        from hbshare.fe.XZ import  functionality
        plot = functionality.Plot(fig_width=2000, fig_height=600)
        # plot.plotly_line_style(df[[x + "_exp_adj" for x in fc.barra_col]], '基金：{0}'.format(jjdm))
        # plot.plotly_line_style(df[[x + "_exp_adj" for x in fc.indus_col]], '基金：{0}'.format(jjdm))
        plot.plotly_line_style(df[[x + "_exp" for x in fc.barra_col]], '基金：{0}'.format(jjdm))
        plot.plotly_line_style(df[[x + "_exp" for x in fc.indus_col]], '基金：{0}'.format(jjdm))

        plot = functionality.Plot(fig_width=2000, fig_height=600)

        plot.plotly_table(style_shift_df, 500, '基金：{0} 风格切换汇总(置信度{1}%)'.format(jjdm, shift_confidence * 100))
        plot.plotly_table(ind_shift_df, 500, '基金：{0} 行业切换汇总(置信度{1}%)'.format(jjdm, shift_confidence * 100))


    # sql="select min(jjrq) as t0,max(jjrq) as t1,jjdm from barra_style_s_ret GROUP BY jjdm  "
    # jjdm_list=pd.read_sql(sql,fc.localengine)
    # cen_list=[]
    # ratio_list=[]
    # for i in range(len(jjdm_list)):
    #     jjdm=jjdm_list.iloc[i]['jjdm']
    #     t0=jjdm_list.iloc[i]['t0']
    #     t1=jjdm_list.iloc[i]['t1']
    #     average_ind_cen_level,shift_ratio=fc.classify(jjdm,t0,t1)
    #     cen_list.append(average_ind_cen_level)
    #     ratio_list.append(shift_ratio)
    # test=pd.DataFrame()
    # test['c']=cen_list
    # test['r']=ratio_list
    # print(test.describe())
    # test.to_csv('cr_sta.csv',index=False)
    # print('done')