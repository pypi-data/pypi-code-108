import datetime
import numpy as np
import pandas as pd
from ..XZ import functionality
from ..XZ import db_engine as dben


class Projects:

    def __init__(self):

        from ..XZ.config import config_pfa as config
        self.config_pfa=config.Config()

    # 1.资产配置时序：A股 / 港股 / 债券 / 基金 / 现金等类别时序的累计区域图；
    def asset_allocation_pic(self,plot,asset_allocation_df):

        # 1.资产配置时序：A股 / 港股 / 债券 / 基金 / 现金等类别时序的累计区域图；
        plot.plotly_area(asset_allocation_df[['活期存款', '债券', '基金', '权证', '其他', 'A股',
                                              '港股', '日期']], '资产配置时序')

    # 2.行业配置时序：基于申万一级行业分别规则，对持仓的行业分布做一个时序统计；
    def industry_allocation_pic(self,plot,ind_hld):
        plot.plotly_area(ind_hld, '行业配置时序')

    # 3. 行业集中度时序：持仓前一 / 三 / 五大行业的权重时序
    def industry_centralization_pci(self,plot,indutry_allocation_df_ranked):

        # 3. 行业集中度时序：持仓前一 / 三 / 五大行业的权重时序
        inputdf = indutry_allocation_df_ranked.copy()
        cols = inputdf.columns.tolist()
        cols.remove('日期')
        for col in cols:
            inputdf[col] = [x[0].sum() for x in inputdf[col]]
        plot.plotly_line(inputdf, '行业集中度时序')

    # 4.重仓明细：时序上各个时间点的持仓明细（表格）；
    def stock_holding_pic(self,plot,stk_hld):
        # 4.重仓明细：时序上各个时间点的持仓明细（表格）；
        tempdf = stk_hld.drop('日期',axis=1).T
        input_df=pd.DataFrame()
        for date in tempdf.columns:
            input_df[date]=tempdf[date].sort_values(ascending=False).index[0:20]\
                           +'( '+tempdf[date].sort_values(ascending=False).values[0:20].astype(str)+' )'

        plot.plotly_table(input_df, 5000, '持仓明细')

    # 5.持股集中度时序：持仓前三 / 五 / 十大权重和的时序折线图；
    def stock_centralization_pic(self,plot,asset_allocation_df_ranked):
        # 5.持股集中度时序：持仓前三 / 五 / 十大权重和的时序折线图；
        inputdf = asset_allocation_df_ranked.copy()
        cols = inputdf.columns.tolist()
        cols.remove('日期')
        for col in cols:
            inputdf[col] = [x[0].sum() for x in inputdf[col]]
        plot.plotly_line(inputdf, '持股集中度时序')

    # 6.组合中A股持仓的平均PE / PB / 股息率的折线图；
    def valuation_pic(self,plot,fin_hld,stk_hld,date_list):
        # 6.组合中A股持仓的平均PE / PB / 股息率的折线图；
        tempdf = pd.DataFrame()
        for item in ['PE', 'PB', 'DIVIDENDRATIO']:
            tempdf[item] = ((fin_hld.loc[:, (item, slice(None))].values) * (stk_hld.drop('日期', axis=1).values)).sum(
                axis=1) / stk_hld.drop('日期', axis=1).values.sum(axis=1)
        tempdf['日期'] = date_list
        plot.plotly_line_multi_yaxis(tempdf, '持股估值分析', ['PB', 'DIVIDENDRATIO'])

    # 7.持股分布：所持股票在各类宽基成分股中的权重时序的折线图，包括：沪深300、中证500、中证1000、1800以外。
    def hodling_in_benchmark(self,plot,ben_hld):
        # 7.持股分布：所持股票在各类宽基成分股中的权重时序的折线图，包括：沪深300、中证500、中证1000、1800以外。
        plot.plotly_area(ben_hld, '宽基成分股配置走势')

    # 8 单只基金Alpha R_Square 散点图
    def alpha_rsquare_pic(self,plot,fun,df1,date_list,Jydb):

        #read the factors information from hb database
        sec_code_A=df1['Stock_code'].dropna()[~df1['Stock_code'].dropna().str.contains('H')].unique()
        raw_factors=Jydb.extract_factors(sec_code_A,date_list)

        #calcualte the risk exposure for the fund as a whole
        fund_factors=fun.fund_risk_exposure(fun.purified_stk_hld[['Stock_code','Name','Weight','Stamp_date']].dropna(),
                                            raw_factors,
                                            ['Stamp_date','Stock_code','Weight'])

        #get the return of benchmark index as factors
        index_list=['000905','000300']
        factors_benchmark=Jydb.extract_benchmark_return(date_list,index_list+['000012'])
        factors_benchmark=fun.aggregate_by(factors_benchmark,['TJYF','ZQDM'],'sum','HB')

        #join the classical risk factors with benchmark factors
        fund_factors=pd.merge(fund_factors,factors_benchmark,how='inner',left_on='JYYF',right_on='日期').drop('日期',axis=1)
        factors_list=fund_factors.columns.drop(['JYYF']+index_list).tolist()

        #get the return of the fund by valuation table as the y input for the ols model
        ret_df=fun.generate_ret_df()
        ret_df['JYYF'] = [x.split('-')[0] + x.split('-')[1] for x in ret_df['Stamp_date'].astype(str)]
        ret_df.drop('Stamp_date',axis=1,inplace=True)
        ret_df['Return']=ret_df['Return'].shift(-1)
        ret_df.drop(ret_df.index[-1], axis=0, inplace=True)

        #combine all the data for ols in one dataframe
        ols_df=pd.merge(fund_factors,ret_df,how='inner',left_on='JYYF',right_on='JYYF')
        ols_df['const']=1
        del fund_factors,ret_df,raw_factors

        #8 单只基金Alpha R_Square 散点图

        for num_factors in [6]:
            # pick 6 factors for each round of run as suggested by the research paper of haitong security
            summary_df,simulated_df,selected_factors=fun.calculate_alpha(ols_df, factors_list, num_factors,
                                                                         ret_col= 'Return',date_col='JYYF',
                                                                         bench_factor=index_list)

            plot.plotly_scatter(summary_df[['alpha','rsquar']],'因子组合Alpha_R_square散点图',fix_range=True)

            plot.plotly_line(simulated_df[['simulated_ret', 'real_ret', '日期']], '基金多因子模型拟合效果_因子：{0}'.format(selected_factors))
            # plot.plotly_scatter(simulated_df[['simulated_ret','real_ret']].sort_values('real_ret'), '基金多因子模型拟合效果')

    def prv_hld_analysis (self,prd_name,tablename,pic_list=None):

        ########################################Collecting data########################################
        config=self.config_pfa

        # initial the temp database class
        Pfdb = dben.PrvFunDB()

        # write fold files to DB
        # Pfdb.write2DB(table_name='prvfund',fold_dir="E:\私募主观\主观股多估值表基地",increment=0)

        # initial the class
        Jydb = dben.HBDB()

        # extra data from the temp database
        df1 = Pfdb.extract_from_db(prd_name=prd_name, columns='*', tablename=tablename)

        # get the unique date list and stock code list
        date_list = df1['Stamp_date'].dropna().unique()
        sec_code = df1['Stock_code'].dropna().unique()

        # extra industry data from the JY database
        df2 = Jydb.extract_industry(sec_code)

        # extra financial data from the JY database
        df3 = Jydb.extract_fin_info(sec_code,date_list)

        # extra benchmark data from the JY database
        df4 = Jydb.extract_benchmark(config.Index_type, sec_code=sec_code,date_list=date_list)

        fun = functionality.Untils(df1[['Code','Name','Weight','Stamp_date','Stock_code']], df2, df3, df4)

        asset_allocation_df = fun.asset_allocation_stats()

        ind_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'FIRSTINDUSTRYNAME'], method='sum',
                                   method_on='Weight')
        indutry_allocation_df_ranked = fun.rank_filter(ind_hld, [1, 3, 5])

        stk_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'Name'], method='sum',
                                   method_on='Weight')
        asset_allocation_df_ranked = fun.rank_filter(stk_hld, [3, 5, 10])

        fin_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'Name'], method='sum',
                                   method_on=['PE', 'PB', 'DIVIDENDRATIO'])
        ben_hld = fun.aggregate_by(fun.bench_info, groupby=['Stamp_date', 'Index_type'], method='sum',
                                   method_on='Weight')

        ########################################Drawing Pictures ########################################

        # drawing the pics ,initial the instant
        plot = functionality.Plot(fig_width=1200, fig_height=600)

        if(pic_list is None):

            self.asset_allocation_pic(plot,asset_allocation_df)
            self.industry_allocation_pic(plot,ind_hld)
            self.industry_centralization_pci(plot, indutry_allocation_df_ranked)
            self.stock_holding_pic(plot, stk_hld)
            self.stock_centralization_pic(plot, asset_allocation_df_ranked)
            self.valuation_pic(plot, fin_hld, stk_hld, date_list)
            self.hodling_in_benchmark(plot,ben_hld)
            self.alpha_rsquare_pic(plot, fun, df1, date_list, Jydb)

        else:
            pic_list=[x+'_pic' for x in pic_list]

            if('asset_allocation_pic' in pic_list):
                self.asset_allocation_pic(plot, asset_allocation_df)
            if ('industry_allocation_pic' in pic_list):
                self.industry_allocation_pic(plot,ind_hld)
            if ('industry_centralization_pci' in pic_list):
                self.industry_centralization_pci(plot, indutry_allocation_df_ranked)
            if ('stock_holding_pic' in pic_list):
                self.stock_holding_pic(plot, stk_hld)
            if ('stock_centralization_pic' in pic_list):
                self.stock_centralization_pic(plot, asset_allocation_df_ranked)
            if ('valuation_pic' in pic_list):
                self.valuation_pic(plot, fin_hld, stk_hld, date_list)
            if ('hodling_in_benchmark' in pic_list):
                self.hodling_in_benchmark(plot,ben_hld)
            if ('alpha_rsquare_pic' in pic_list):
                self.alpha_rsquare_pic(plot, fun, df1, date_list, Jydb)

    def prv_fof_analysis(self,fund_code):

        hbdb=dben.HBDB()

        sql = """ 
        select d.*,b.jzrq,b.jjjz,b.ljjz  
        from 
        (
        select a.jjdm,a.jjjc,a.cpfl,a.jjfl,c.mjjdm,c.lhbz,c.sfzz,c.fofjjdl,c.fofejfl,c.tzmb,c.tzfw,c.tzcl,c.tzbz,c.fxsytz 
        from st_hedge.t_st_jjxx a, st_hedge.t_st_sm_jjxx c 
        where a.jjdm=c.jjdm and a.jjdm='{0}'
        ) d left join st_hedge.t_st_jjjz b on d.jjdm=b.jjdm """.format(fund_code)

        hld_prv=hbdb.db2df(sql,db='highuser')

        sql="select jzdm,yxj,moddt_etl from st_hedge.t_st_sm_jjbjjz a where jjdm='{}' ".format(fund_code)
        benchmark_code=hbdb.db2df(sql,db='highuser')

        print('Done')

    def fund_alpha_analysis(self,fund_list):

        fun=functionality.Untils()
        ########################################Collecting data########################################
        hbdb=dben.HBDB()
        for fund in fund_list:

            #read the holding info for the fund
            sql="select jjdm,jsrq,zqdm,zqmc,zjbl from st_fund.t_st_gm_gpzh where jjdm='{0}'".format(fund)
            fund_hld=hbdb.db2df(sql,db='funduser')

            #read the net value info for the fund
            sql="select jjdm,tjyf,hb1y from st_fund.t_st_gm_yhb where jjdm='{0}'".format(fund)
            ret_df=hbdb.db2df(sql,db='funduser')
            ret_df['hb1y']=ret_df['hb1y'] / 100
            ret_df['tjyf']=ret_df['tjyf'].astype(str)


            # read the factors information from hb database
            sec_code= fund_hld['zqdm'][~fund_hld['zqdm'].dropna().str.contains('H')].unique()
            date_list=fund_hld['jsrq'].unique()
            raw_factors = hbdb.extract_factors(sec_code, date_list)

            industry=False
            if(industry==True):
                #add the industry factors if necessary, i am not using the industry factors in the st_ashare.r_st_barra_style_factor
                #because it contains too many industries i am using the 中证指数行业分类2016版 which is less to reduce the computing burder

                sql = """
                select a.SecuCode,b.FirstIndustryName,b.XGRQ from HSJY_GG.SecuMain a 
                left join HSJY_GG.LC_ExgIndustry b on a.CompanyCode=b.CompanyCode  
                where Standard=28 and a.SecuCode in({0}) """.format("'"+"','".join(sec_code)+"'")
                industry_factors=hbdb.db2df(sql,db='readonly').sort_values('XGRQ').drop(['ROW_ID','XGRQ'],axis=1)
                industry_factors.drop_duplicates('SECUCODE',keep='last',inplace=True)

                # sql = """
                # select a.SecuCode,b.FirstIndustryName,b.UpdateTime from HSJY_GG.SecuMain a
                # left join HSJY_GP.LC_STIBExgIndustry b on a.CompanyCode=b.CompanyCode
                # where Standard=28 and a.SecuCode in({0}) """.format("'"+"','".join(sec_code)+"'")
                # industry_factors2=hbdb.db2df(sql,db='readonly').sort_values('UpdateTime').drop(['ROW_ID','UpdateTime'],axis=1)
                # industry_factors2.drop_duplicates('SECUCODE',keep='last',inplace=True)

                industry_factors=pd.concat([industry_factors,pd.get_dummies(industry_factors['FIRSTINDUSTRYNAME'])],axis=1).drop('FIRSTINDUSTRYNAME',axis=1)

                raw_factors=pd.merge(raw_factors,industry_factors,how='left',left_on='ticker',right_on=['SECUCODE']).drop('SECUCODE',axis=1)

            # calcualte the risk exposure for the fund as a whole
            fund_factors = fun.fund_risk_exposure(fund_hld,raw_factors,['jsrq','zqdm','zjbl'])

            jjfl=hbdb.db2df("select jjfl from st_fund.t_st_gm_flls where jjdm='{0}' ".format(fund),db='funduser')['jjfl'][0]
            jzdm_list=hbdb.db2df("select jzdm from st_hedge.t_st_sm_jjflbjjz where jjfl='{}' and jzdm not like 'H%%' ".format(jjfl),db='highuser')['jzdm']\
                .values.tolist()

            sql="select hb1y,zqdm,tjyf from st_market.t_st_zs_yhb  where zqdm in ({0}) ".format(','.join(jzdm_list+['000012']))
            benchmark_df=hbdb.db2df(sql,db='alluser')
            benchmark_df=benchmark_df[benchmark_df['hb1y']!=999]
            benchmark_df=benchmark_df.groupby(['zqdm', 'tjyf']).sum('hb1y').unstack().T
            benchmark_df['日期']=benchmark_df.index.get_level_values(1).astype(str)

            fund_factors=pd.merge(fund_factors,benchmark_df,how='inner',left_on='JYYF',right_on='日期').drop('日期',axis=1)

            factors_list=fund_factors.columns.drop(['JYYF']+jzdm_list).tolist()

            #standardlize the factors to be mean 1 std 1
            for col in factors_list:
                mean=fund_factors[col].mean()
                std=fund_factors[col].std()
                fund_factors[col]=fund_factors[col]/std+1-mean

            # combine all the data for ols in one dataframe
            ols_df = pd.merge(fund_factors, ret_df, how='inner', left_on='JYYF', right_on='tjyf')
            ols_df['const'] = 1
            del fund_factors, ret_df, raw_factors

            plot = functionality.Plot(fig_width=1200, fig_height=600)

            for num_factors in [6]:
                # pick 6 factors for each round of run as suggested by the research paper of haitong security
                summary_df, simulated_df,selected_factors = fun.calculate_alpha(ols_df, factors_list, num_factors, ret_col='hb1y',
                                                               date_col='JYYF',bench_factor=jzdm_list)

                fund_name=hbdb.db2df("select jjjc from st_fund.t_st_gm_jjxx where jjdm='{0}'".format(fund),db='funduser').values[0]
                plot.plotly_scatter(summary_df[['alpha', 'rsquar']], '因子组合Alpha_R_square散点图_{0}'.format(fund_name), fix_range=True)

                plot.plotly_line(simulated_df[['simulated_ret', 'real_ret', '日期']], '基金多因子模型拟合效果_{0}_因子：{1}'.format(fund_name,selected_factors))

    def read_riskaversionfromdb(self,date):

        sql = "select risk_aversion from bl_risk_aversion where date='{0}'".format(date)
        risk_aversion=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        return risk_aversion['risk_aversion'].values[0]

    def bl_model_data_preparation(self,end_date,version):


        from ..AAM.blmodel import  blmodel

        blm=blmodel.BL_Model()
        localdb_engine=dben.PrvFunDB().engine

        #get the assets from pool
        sql=" select * from bl_assets_pool where version='{0}' ".format(version)
        assets_df=pd.read_sql(sql, con=localdb_engine)
        index_assets=assets_df[assets_df['asset_type']=='index']['code'].values.tolist()
        public_funds = assets_df[assets_df['asset_type'] == 'public_fund']['code'].values.tolist()

        blm.bl_model_index_data_preparation(end_date=end_date,asset_list=index_assets,version=version)
        blm.bl_model_publicfund_data_preparation(end_date=end_date, asset_list=public_funds,version=version)

    def bl_model(self,end_date,asset_list,version,tau,ub,lb,asset_type,risk_aversion):

        from ..AAM.blmodel import blmodel

        blm = blmodel.BL_Model()
        engine = dben.PrvFunDB().engine

        # get the cov matrix from local database
        cov_matrix = blm.read_cov_fromdb(engine, asset_list, version, end_date,asset_type)

        # the cov matrix of average return is a shrink of the cov matrix of return itself
        cov_matrix = tau * cov_matrix.values

        # get prio_return from local db
        prio_return = blm.read_return_fromdb(asset_list, engine, version, end_date, 'bl_implied_return', 'implied_ret')

        # get the view_ret from local db
        view_ret = blm.read_return_fromdb(asset_list, engine, version, end_date, 'bl_view_return', 'view_ret')

        views = np.eye(len(asset_list))

        # calculate the view confidence if not read from database directlly
        view_confidence = np.dot(np.dot(views, cov_matrix), views.T) * np.eye(len(views))

        # set upper and lower bound

        constrains = blm.set_boundary(len(asset_list), lb, ub)

        opt_weight = blm.blm_solver(sigma=cov_matrix, mu=prio_return, P=views, Q=view_ret,
                                    Omega=view_confidence, delta=risk_aversion, constrains=constrains)

        opt_restul = pd.DataFrame()
        opt_restul['Asset'] = asset_list
        opt_restul['Weight'] = opt_weight

        return opt_restul

    def fund_classification(self):

        from ..Fund_classifier import classification
        #fc = classification.Classifier_Ml()
        #fc.wind_risk_data2localdb(asofdate='2016-01-01')

        #
        # fc.wind_theme_data2localdb(asofdate='2016-01-01')
        #
        #fc.wind_stock_style_data2localdb(asofdate='2016-01-01')

        #fc.model_generation_style(value_style='hld')
        #
        #fc.model_generation_theme(value_style='hld')
        #
        # fc.model_generation_risk_level()

        # plot=functionality.Plot(fig_width=1000,fig_height=600)
        # self.style_distribution(plot)

        for asofdate in ['2021-12-31']:
            fc=classification.Classifier_Ml(asofdate=asofdate)
            #fc.classify()
            fc.classify_hldbase()

    def style_distribution(self,plot,clbz='全部'):

        if(clbz=='全部'):
            sql="select * from labled_fund"
        else:
            sql = "select * from labled_fund where clbz='{}'".format(clbz)

        test = pd.read_sql(sql, con=dben.PrvFunDB().engine)
        date_list=test['style_updated_date'].unique().tolist()

        for col in ['style','theme','risk_level']:

            sql="select distinct {0} from labled_fund ".format(col)
            unique_items= pd.read_sql(sql, con=dben.PrvFunDB().engine)[col].tolist()
            unique_items.remove('')
            plot_df = pd.DataFrame()
            plot_df['items'] = unique_items
            for date in date_list:
                tempdf=test[test['style_updated_date']==date].groupby(col).count()
                tempdf['items']=tempdf.index
                plot_df=pd.merge(plot_df,tempdf[['items','jjdm']],how='left',on='items').fillna(0)
                plot_df.rename(columns={'jjdm':date},inplace=True)
                plot_df[date]=plot_df[date]/plot_df[date].sum(axis=0)*100

            plot_df.set_index('items',drop=True,inplace=True)
            plot.plotly_style_bar(plot_df.T,'{}分布'.format(col))

    def fund_classification_advance(self):
        from ..Fund_classifier import classification
        #fc=classification.Classifier()
        #fc.classify_threshold(20)
        fc2=classification.Classifier_brinson()
        fc2.classify_socring()

    def brinson_score_pic(self,jjdm):

        sql="select * from brinson_score where jjdm='{}'".format(jjdm)
        scoredf=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        plot=functionality.Plot(fig_width=1000,fig_height=600)

        new_name=['jjdm','交易能力_短期','交易能力_长期','行业配置能力_短期',
                  '行业配置能力_长期','选股能力_短期','选股能力_长期','大类资产配置能力_短期',
                  '大类资产配置能力_长期','asofdate']
        scoredf.columns=new_name
        col=['交易能力_短期','交易能力_长期','行业配置能力_短期',
                  '行业配置能力_长期','选股能力_短期','选股能力_长期','大类资产配置能力_短期',
                  '大类资产配置能力_长期']

        plot.ploty_polar(scoredf[col],'Brinson能力图')

    def fund_classification_barra(self):

        from ..Fund_classifier import classification
        fc=classification.Classifier_barra()
        fc.data_preparation()
        # for jjdm in ['000362','005821','009636','001487']:
        #     fc.classify(jjdm=jjdm,start_date='20181231',end_date='20211231')

    def mutual_fund_concept(self,asofdate):

        engine=dben.PrvFunDB().engine

        q3df = pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\重仓持股(汇总).xlsx")[
            ['代码', '名称', '持股总量(万股)', '季报持仓变动(万股)', '持股市值占基金净值比(%)']]
        target_list = q3df['代码'].fillna('0').tolist()
        q3df.fillna(0)
        q3df = q3df[q3df['持股总量(万股)'] > 0]

        sql = "select * from stock_concept where 证券代码 in ({0})".format("'" + "','".join(target_list) + "'")
        conceptdf = pd.read_sql(sql, con=engine).fillna('')

        df = pd.merge(q3df, conceptdf, how='inner', left_on='代码', right_on='证券代码')
        concept_listdf = pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\概念分类.xlsx")
        concept_class = concept_listdf.columns
        csv_df = pd.DataFrame()
        for cls in concept_class:
            con_weight = []
            con_change = []
            con_total = []
            outputdf = pd.DataFrame()
            concept_list = concept_listdf[concept_listdf[cls].notnull()][cls].astype(str)
            for concept in concept_list:
                try:
                    df[concept] = df['所属概念板块[交易日期] 最新收盘日'].str.contains(concept).astype(int)
                    df[concept + '_w'] = df[concept] * df['持股市值占基金净值比(%)']
                    df[concept + '_n'] = df[concept] * df['季报持仓变动(万股)']
                    df[concept + '_t'] = df[concept] * df['持股总量(万股)']
                    con_weight.append(df[concept + '_w'].sum(axis=0))
                    con_change.append(df[concept + '_n'].sum(axis=0))
                    con_total.append(df[concept + '_t'].sum(axis=0))
                except Exception:
                    print(concept)
                    concept_list.remove(concept)
                    continue

            outputdf[cls] = concept_list
            outputdf['持仓权重(%)_' + cls] = con_weight
            outputdf['季报持仓变动(万股)'] = con_change
            outputdf['持股总量(万股)'] = con_total

            outputdf['上季度持股总量(万股)'] = outputdf['持股总量(万股)'] - outputdf['季报持仓变动(万股)']
            outputdf['持股变动%_' + cls] = outputdf['季报持仓变动(万股)'].fillna(0) / outputdf['上季度持股总量(万股)'] * 100
            outputdf.loc[outputdf['持股变动%_' + cls]==np.inf,'持股变动%_' + cls]='新增'
            outputdf.drop(['上季度持股总量(万股)', '季报持仓变动(万股)', '持股总量(万股)'], axis=1, inplace=True)
            outputdf.sort_values(['持仓权重(%)_' + cls, '持股变动%_' + cls], inplace=True, ascending=False)
            outputdf = outputdf[outputdf['持仓权重(%)_' + cls] > 0].reset_index(drop=True)
            csv_df = pd.concat([csv_df, outputdf], axis=1)

        csv_df['asofdate'] = asofdate
        #check if data already exist
        sql='select distinct asofdate from mutual_fund_highlighthld_concept'
        asofdatelist=pd.read_sql(sql,con=engine)['asofdate']
        if(asofdate in asofdatelist):
            sql="delete from mutual_fund_highlighthld_concept where asofdate='{0}'".format(asofdate)
            engine.execute(sql)
        csv_df.to_sql('mutual_fund_highlighthld_concept', con=engine,index=False,if_exists='append')
        print('The concept distribution data has been inserted into tbale mutual_fund_highlighthld_concept')

    def mutual_fund_concept_heatmap(self,fig_width,fig_height,asofdate):

        plot = functionality.Plot(fig_width=fig_width, fig_height=fig_height)

        sql="select * from mutual_fund_highlighthld_concept where asofdate='{}'"\
            .format(asofdate)
        raw_df=pd.read_sql(sql,con=dben.PrvFunDB().engine)

        col_list=list(set([x.split('_')[-1] for x in  raw_df.columns]))
        item_list=list(set([x.split('_')[0] for x in  raw_df.columns]))
        item_list=list(set(item_list).difference(set(col_list)))
        item_list.sort()
        col_list.remove('asofdate')
        col_list.sort()

        f = lambda x: '%.4f%%' % x

        for col in col_list:
            new_list=[x+'_'+col for x in item_list]
            tempdf = raw_df[raw_df[col].notnull()][[col] + new_list]
            if(len(tempdf)>=9):
                width=3
            elif(len(tempdf)>=4):
                width=2
            tempdf=tempdf.iloc[0:width*width]
            tempdf.sort_values(new_list[0], ascending=False,inplace=True)
            z=tempdf[new_list[0]].astype(float).values.reshape(width,width)
            z_per=tempdf[new_list[0]].astype(float).apply(f).values.reshape(width,width)
            z_text=tempdf[col].values.reshape(width,width)
            z_text=z_text + '： ' +z_per
            plot.ploty_heatmap(z, z_text, col+"_权重")

            tempdf.sort_values(new_list[1], ascending=False,inplace=True)
            z=tempdf[new_list[1]].astype(float).values.reshape(width,width)
            z_per = tempdf[new_list[1]].astype(float).apply(f).values.reshape(width, width)
            z_text=tempdf[col].values.reshape(width,width)
            z_text=z_text + '： ' + z_per
            plot.ploty_heatmap(z,z_text,col+"_增长率")





