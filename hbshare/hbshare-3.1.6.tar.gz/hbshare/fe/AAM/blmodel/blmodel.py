import numpy as np
import pandas as pd
from scipy import linalg
from cvxopt import solvers
solvers.options['show_progress'] = False
from cvxopt import matrix
from hbshare.fe.XZ import db_engine


class BL_Model:

    def __init__(self):


        self.hbdata=db_engine.HBDB()
        self.locdb=db_engine.PrvFunDB()

    def get_trade_date(self,end_date,fre,begin_date=None):

        #get the trading date for month or week end
        if(fre=='M'):
            fre_con="and SFYM='1'"
        elif(fre=='W'):
            fre_con="and SFZM='1'"
        else:
            raise Exception
            print('Please input correct frequency ')

        if(begin_date is None):
            begin_date_con=''
        else:
            begin_date_con=" and JYRQ>={0} ".format(begin_date)
        sql="SELECT JYRQ FROM funddb.JYRL where  JYRQ<={0} {1} {2}".format(end_date,fre_con,begin_date_con)
        trade_date=self.hbdata.db2df(sql,db='readonly').sort_values('JYRQ')['JYRQ'].values.tolist()
        return  trade_date

    def calculate_view_return(self,trade_month,asset_name):

        sql="""select zqdm,jyrq,pe,roe,zsz,gxl from st_market.t_st_zs_hq where zqdm='{0}' and jyrq in ({1}) """\
            .format(asset_name,','.join(trade_month))
        val_df=self.hbdata.db2df(sql,db='alluser')

        # sql="""select zqdm,jyrq,pe,roe,gxl from bl_valuation where zqdm='{0}' and jyrq in ({1}) """\
        #     .format(asset_name,','.join(trade_month))
        # val_df =pd.read_sql(sql,con=db_engine.PrvFunDB().engine)


        #calculate the PE median from the last 10 years(120 monthes)
        val_df['temp_pe']=val_df['pe'].rolling(120).median().shift(1)
        #calculate the implied return by temp_pe+roe+dividen_ratiio
        newpe=((val_df['temp_pe'][-1:]/val_df['pe'][-1:]).pow(1/5)-1).fillna(0)
        ret=newpe*100+val_df['gxl'][-1:]+val_df['roe'][-1:]
        ret.fillna(0,inplace=True)

        return  ret.values[0]/100

    def load_asset_return_data(self,trade_date,asset_name,asset_type):

        if (asset_type == 'index'):
            sql = "select rqzh,hb1z from st_market.t_st_zs_zhb where rqzh>= {0} and rqzh<={1} and zqdm='{2}' " \
                .format(trade_date[0], trade_date[-1], asset_name)

            ret_df = self.hbdata.db2df(sql, db='alluser')

            # sql = "select rqzh,hb1z from bl_weekly_return where rqzh>= {0} and rqzh<={1} and zqdm='{2}' " \
            #     .format(trade_date[0], trade_date[-1], asset_name)
            # ret_df =pd.read_sql(sql,con=db_engine.PrvFunDB().engine)

            ret_df=ret_df[ret_df['hb1z'].abs()!=99999]


        elif (asset_type == 'public_fund'):

            sql="select  jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm='{0}' and jzrq in ({1})"\
                .format(asset_name,','.join(trade_date))

            ret_df = self.hbdata.db2df(sql, db='funduser')
            ret_df['hb1z']=ret_df['fqdwjz'].pct_change()
            ret_df=ret_df[1:].drop('fqdwjz',axis=1)
            ret_df.rename(columns={'jzrq':'rqzh'},inplace=True)



        elif (asset_type == 'stock'):

            print('stock')
        else:
            raise Exception
            print('Please input correct asset_type, :index,stock,bond')


        ret_df['hb1z']=ret_df['hb1z']/100
        ret_df.rename(columns={'hb1z': 'ret_'+asset_name }, inplace=True)
        ret_df.rename(columns={'hb1z': asset_name}, inplace=True)
        ret_df['rqzh'] = ret_df['rqzh'].astype(str)

        return  ret_df

    def cov_mat_from_return(self,trade_date,asset_list,asset_type):

        cov_mat=pd.DataFrame()
        cov_mat['Date']=trade_date

        for asset in asset_list:
            cov_mat=pd.merge(cov_mat,self.load_asset_return_data(trade_date,asset,asset_type),
                             how='inner',left_on='Date',right_on='rqzh').drop('rqzh',axis=1)


        cov_mat = cov_mat.drop('Date', axis=1).cov()*52

        return cov_mat

    def get_risk_aversion(self,end_date,engine):

        end_month=end_date[0:6]
        #get the monthly return of the bond return and calculate its mean as R_mkr:using 000012's return as market return temparary
        sql="select hb1y,tjyf from st_market.t_st_zs_yhb where zqdm='000012' and tjyf<='{0}'".format(end_month)
        deposit_rate_df=self.hbdata.db2df(sql,db='alluser')
        deposit_rate_df=deposit_rate_df[deposit_rate_df['hb1y']!=99999]
        deposit_rate_df['hb1y']=deposit_rate_df['hb1y']/100

        #get the monthly return of the market return and calculate its mean as R_mkr:using 000001's return as market return temparary
        sql="select hb1y,tjyf from st_market.t_st_zs_yhb where zqdm='000001'"
        mkt_ret_df=self.hbdata.db2df(sql,db='alluser')
        mkt_ret_df=mkt_ret_df[mkt_ret_df['hb1y']!=99999]
        mkt_ret_df['hb1y']=mkt_ret_df['hb1y']/100


        risk_df=pd.merge(mkt_ret_df,deposit_rate_df,how='inner',left_on='tjyf',right_on='tjyf')
        rf=risk_df['hb1y_y'].mean()
        rmkr=risk_df['hb1y_x'].mean()
        varmkr=risk_df['hb1y_x'].var()
        risk_aversion=(rmkr-rf)/varmkr


        #save the risk aversion into local db
        inputdf=pd.DataFrame()
        inputdf['risk_aversion']=[risk_aversion]
        inputdf['date']=end_month

        #check if data already exist
        sql="select count(*) c from bl_risk_aversion where date='{0}' "\
            .format(end_month)
        if(pd.read_sql(sql,con=engine)['c'].values[0]>0):
            sql = "delete from bl_risk_aversion where date='{0}'"\
                .format(end_month)
            engine.execute(sql)

        inputdf.to_sql('bl_risk_aversion',con=engine,index=False,if_exists='append')

        return risk_aversion

    def get_weight(self,end_date,asset_list,engine):

        sql="select mkr_value from bl_market_value where Date='{0}' and code in ({1})"\
            .format(end_date,"'"+"','".join(asset_list)+"'")
        weight_list=pd.read_sql(sql,con=engine)['mkr_value'].values.tolist()

        return weight_list

    def implied_return_from_weight(self,mkt_val,risk_aversion,asset_list,cov_matrix):

        weights=np.array(mkt_val)/sum(mkt_val)
        implied_ret=risk_aversion*np.dot(cov_matrix,weights)

        return implied_ret

    def set_boundary(self,asset_num,lb,ub):

        G = matrix(np.vstack((np.diag([-1]*asset_num), np.diag([1]*asset_num))), tc='d')
        h = matrix(np.array(lb+ub), tc='d') # 为各参数的上下限！！！！
        A = matrix(np.array([[1]*asset_num]), tc='d')
        b = matrix(np.array([1]), tc='d')

        boundary=dict()
        boundary['G']=G
        boundary['h'] = h
        boundary['A'] = A
        boundary['b'] = b

        return boundary

    def cov2db(self,cov_matrix,engine,end_date,version,table_sur_name):

        # write cov_matrix into database
        inputdata=cov_matrix.copy()
        inputdata['row_name'] = inputdata.index
        inputdata['Date'] = end_date
        table_name=table_sur_name+version

        #check if table exist already
        sql="SELECT count(*) as c  FROM information_schema.tables WHERE table_name = '{0}'"\
            .format(table_name)
        if(pd.read_sql(sql,con=engine)['c'].values[0]>0):

            sql="select count(*) as c from {0} where Date='{1}' ".format(table_name,end_date)
            # check if data already exist,if yes delete the old data and replace with new one
            if(pd.read_sql(sql,con=engine)['c'].values[0]>0):
                sql="delete from {0} where Date={1}".format(table_name,end_date)
                engine.execute(sql)

        inputdata.to_sql(table_name, engine, index=False, if_exists='append')

    def return2db(self,tabel_name,ret_list,engine,asset_list,end_date,version,col):

        # write implied return into database
        inputdata=pd.DataFrame()
        inputdata['code']=asset_list
        inputdata[col] = ret_list
        inputdata['Date'] = end_date
        inputdata['version']=version

        #check if data already exist
        sql="select count(*) c from {2} where version='{0}' and Date='{1}' and code in ({3})"\
            .format(version,end_date,tabel_name,"'"+"','".join(asset_list)+"'")
        if(pd.read_sql(sql,con=engine)['c'].values[0]>0):
            sql = "delete from {2} where Date='{0}' and version= '{1}'"\
                .format( end_date,version,tabel_name)
            engine.execute(sql)

        inputdata.to_sql('{0}'.format(tabel_name), engine, index=False, if_exists='append')

    def mkrvalue2db(self,asset_list,mkr_v,end_date,engine):

        # write implied return into database
        inputdata=pd.DataFrame()
        inputdata['code']=asset_list
        inputdata['mkr_value'] = mkr_v
        inputdata['Date'] = end_date

        #check if data already exist
        sql="select distinct code from bl_market_value where Date='{0}'".format(end_date)
        current_list=pd.read_sql(sql,con=engine)['code'].values
        delete_list=list(set(current_list)&set(asset_list))
        if(len(delete_list)>0):
            sql="delete from bl_market_value where Date='{0}' and code in ({1})"\
                .format(end_date,"'"+"','".join(delete_list)+"'")
            engine.execute(sql)

        inputdata.to_sql('bl_market_value', engine, index=False, if_exists='append')

    def read_cov_fromdb(self,engine,asset_list,version,end_date,asset_type):

        table_name='bl_'+asset_type+'_cov_'+version
        #get the cov matrix from local database
        sql="select {0},row_name from {1} where Date='{2}' "\
            .format('ret_'+',ret_'.join(asset_list),table_name,end_date)

        cov_matrix=pd.read_sql(sql,con=engine)
        dfT=cov_matrix.T
        dfT.columns=cov_matrix['row_name']
        dfT=dfT[['ret_'+str(x) for x in  asset_list]]
        cov_matrix=dfT.T.drop('row_name',axis=1)
        #make sure the cov_matrix order is consistent with asset list
        cov_matrix=cov_matrix[['ret_'+str(x) for x in  asset_list]]

        return cov_matrix.astype(float)

    def read_return_fromdb(self,asset_list,engine,version,end_date,table_name,col):

        sql="select code,{4} from {3} where Date='{0}' and version='{1}' and code in ({2})"\
            .format(end_date,version,"'"+"','".join(asset_list)+"'",table_name,col)
        asset_order=pd.DataFrame()
        asset_order['Code']=asset_list
        tempdf=pd.merge(asset_order,pd.read_sql(sql,con=engine),how='left',left_on='Code',right_on='code')

        return tempdf[col].values

    def update_asset_pool(self,dir,version):

        local_file=pd.read_csv(dir,encoding='gbk')
        local_file['version']=version
        engine=db_engine.PrvFunDB().engine
        local_file.to_sql('bl_assets_pool',con=engine,index=False, if_exists='append')
        print('Update asset pool table Done..')

    def blm_solver(self,sigma,mu,P,Q,Omega,delta,constrains):

        prio_weight=linalg.inv(sigma)
        med_weight=np.dot(np.dot(P,linalg.inv(Omega)),P.T)

        post_cov = linalg.inv(prio_weight + med_weight)

        post_ret=np.dot(post_cov,(np.dot(mu,prio_weight)+np.dot(np.dot(P,linalg.inv(Omega)),np.array(Q).T)))

        # M = np.dot(np.dot(P, sigma), P.T) + Omega
        # M = M.astype(float)
        # M = linalg.inv(M)
        # er = mu.T + np.dot(np.dot(np.dot(sigma, P.T), M), (Q - np.dot(P, mu.T)))

        # 插入限制条件正向求解马克维茨方程
        p = matrix(delta * post_cov, tc='d')
        q = matrix(-post_ret, tc='d')

        G=constrains['G']
        h = constrains['h']
        A = constrains['A']
        b = constrains['b']
        sol = solvers.qp(p, q, G, h, A, b)

        return [ x for x in sol['x']]

    def bl_model_index_data_preparation(self, end_date, asset_list,version):

        engine=db_engine.PrvFunDB().engine

        #########################################for index asset #########################################
        # for index asset
        # get last 10 years trade month date
        trade_date_month = self.get_trade_date(end_date, fre='M')[-200:]

        # last 6 years weekly data is needed for calculating the cov martix
        begin_date = str(int(end_date[0:4]) - 6) + end_date[4:6] + '01'
        trade_date_week = self.get_trade_date(end_date=end_date, fre='W', begin_date=begin_date)

        # calcualte the Cov matrix based on weekly return for the laset 6years
        cov_matrix = self.cov_mat_from_return(trade_date_week, asset_list, asset_type='index')

        # write cov_matrix into database
        self.cov2db(cov_matrix, engine, end_date, version,'bl_index_cov_')

        # calcualte the risk_aversion
        risk_aversion = self.get_risk_aversion(end_date,engine)

        # calculate the prio return based on the market value weights, COV matrix and risk aversion
        mkt_val=self.get_weight(end_date,asset_list,engine)

        prio_return = self.implied_return_from_weight(mkt_val=mkt_val, risk_aversion=risk_aversion,
                                                     asset_list=asset_list, cov_matrix=cov_matrix)
        # write implied return into database
        self.return2db('bl_implied_return',prio_return, engine, asset_list, end_date, version,'implied_ret')
        #self.implied_ret2db(prio_return, engine, asset_list, end_date, version)


        # calculate the view return if necessary
        # use the last 10 years data for calculating view return
        view_ret = []
        for asset in asset_list:
            view_ret.append(self.calculate_view_return(trade_date_month, asset))

        # write view return into database
        #self.viewret2db(view_ret, engine, asset_list, end_date, version)
        self.return2db('bl_view_return', view_ret, engine, asset_list, end_date, version,'view_ret')

    def bl_model_publicfund_data_preparation(self,end_date,asset_list,version):

        engine = db_engine.PrvFunDB().engine

        #########################################for public fund asset #########################################
        # for index asset

        #last 3.5 years/ 182 weeks  weekly data is needed for calculating the cov martix
        trade_date_week=self.get_trade_date(end_date=end_date,fre='W')[-(182+1):]

        #calcualte the Cov matrix based on weekly return for the laset  3.5 years/ 182 weeks
        cov_matrix=self.cov_mat_from_return(trade_date_week,asset_list,asset_type='public_fund')

        # write cov_matrix into database
        self.cov2db(cov_matrix, engine, end_date, version,'bl_public_fund_cov_')

        #calcualte the risk_aversion
        risk_aversion=self.get_risk_aversion(end_date,engine)

        #calculate the prio return based on the market value weights, COV matrix and risk aversion
        mkt_val = [100]*len(asset_list)

        prio_return=self.implied_return_from_weight(mkt_val=mkt_val,risk_aversion=risk_aversion,
            asset_list=asset_list,cov_matrix=cov_matrix)

        # write implied return into database
        self.return2db('bl_implied_return',prio_return, engine, asset_list, end_date, version,'implied_ret')


        view_ret = []
        trade_date_week=trade_date_week[-(105+1):]
        for asset in asset_list:
            view_ret.append(self.load_asset_return_data(trade_date_week,asset,'public_fund')['ret_'+asset].mean()*52)

        # write view return into database
        self.return2db('bl_view_return', view_ret, engine, asset_list, end_date, version,'view_ret')
