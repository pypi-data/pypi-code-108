import numpy as np
import numba as nb
class TIPP :
    
    def __init__(self,risk_returns,safe_asset,Lock_in,\
                 Min_risk_part,Capital_reinjection_rate,Initial_funds\
                ,floor_percent,multiplier,Rebalancement_frequency = 252):

            self.risk_returns = risk_returns
            self.Rebalancement_frequency = Rebalancement_frequency
            self.safe_asset = safe_asset
            self.Lock_in = Lock_in
            self.Min_risk_part = Min_risk_part
            self.Capital_reinjection_rate = Capital_reinjection_rate
            self.Initial_funds = Initial_funds
            self.floor_percent = floor_percent
            self.multiplier = multiplier
            self.tipp = self.tipp(risk_returns,safe_asset,Lock_in,Min_risk_part \
                                  ,Capital_reinjection_rate,Initial_funds \
                                  ,floor_percent,multiplier,Rebalancement_frequency)

    def initiate_funds(self,risk_returns_mtx,safe_asset_mtx,Initial_funds,Rebalancement_frequency,floor_percent) :

        Goal = risk_returns_mtx.size / Rebalancement_frequency   #This initiate the goal of xxx days of investment to today.
        Actualizer = (1+safe_asset_mtx[0] * Rebalancement_frequency / 252)**Goal
        floor_cap = Initial_funds * floor_percent / Actualizer
        return floor_cap,Goal


    def Matrix_Preparation(self,risk_return_mtx,safe_asset_mtx,floor_cap,Initial_funds):
        mtx= np.ones(risk_return_mtx.size)
        floor_matrix = mtx * floor_cap
        Reference_cap_matrix , Fund_matrix  = mtx * Initial_funds , mtx *  Initial_funds
        Capital_reijection_matrix  =np.zeros( len(risk_return_mtx) )
        return floor_matrix , Reference_cap_matrix , Capital_reijection_matrix \
               , Fund_matrix


    def tipp(self,risk_returns,safe_asset,Lock_in,Min_risk_part \
             ,Capital_reinjection_rate,Initial_funds ,floor_percent,multiplier\
             ,Rebalancement_frequency) :

        if len(risk_returns) < 2 and len(safe_asset) < 2  : 
            raise ValueError('More than 2 entries are required for each input')

        risk_return_mtx = risk_returns.values.reshape(-1)
        safe_asset_mtx = safe_asset.values.reshape(-1)
        
        if safe_asset_mtx.size != risk_return_mtx : 
            raise ValueError('x and y must be of the same length')

        floor_cap,Goal = self.initiate_funds(risk_return_mtx,safe_asset_mtx,Initial_funds,Rebalancement_frequency,floor_percent)
        floor_matrix , Reference_cap_matrix , Capital_reijection_matrix , Fund_matrix = self.Matrix_Preparation(risk_return_mtx,safe_asset_mtx,floor_cap,Initial_funds)

        try :
            Fund_matrix , floor_matrix , Capital_reijection_matrix , Reference_cap_matrix,return_mtx = self.TPPI_calculator_MC(risk_return_mtx,floor_matrix , Reference_cap_matrix \
                                                                                                            ,Capital_reijection_matrix,Fund_matrix ,Lock_in \
                                                                                                            ,floor_percent,Goal,multiplier,Min_risk_part,safe_asset_mtx\
                                                                                                            ,Rebalancement_frequency,Capital_reinjection_rate)
        except : 
            raise ValueError('Cannot divide by 0')

        return Fund_matrix , floor_matrix , Capital_reijection_matrix ,\
                Reference_cap_matrix,risk_return_mtx[1:],safe_asset_mtx[1:], return_mtx



    @staticmethod
    @nb.njit
    def TPPI_calculator_MC(risk_return_mtx,floor_matrix , Reference_cap_matrix , Capital_reijection_matrix \
                          ,Fund_matrix ,Lock_in,floor_percent,Goal,multiplier,Min_risk_part,safe_asset\
                          ,Rebalancement_frequency,Capital_reinjection_rate) :

        for i in range(1,floor_matrix.size) :

            if Fund_matrix[i-1] >= (1+Lock_in)*Reference_cap_matrix[i - 1]:
                Reference_cap_matrix[i] = Fund_matrix[ i - 1]
            else :
                Reference_cap_matrix[i] = Reference_cap_matrix[i - 1]
                
            floor_cap_update  = Fund_matrix[i-1] * floor_percent/((1+safe_asset[i-1] * Rebalancement_frequency)**Goal)

            if floor_cap_update > floor_matrix[i-1] : 
                floor_matrix[i] = floor_cap_update 
            else : 
                floor_matrix[i] = floor_matrix[i-1]
                    
            if Fund_matrix[i-1] < Reference_cap_matrix[i-1] * Capital_reinjection_rate :
                diff = Reference_cap_matrix[i-1] * Capital_reinjection_rate - Fund_matrix[i-1]
                Reference_cap_matrix[i] = Reference_cap_matrix[i-1] - diff
                Fund_matrix[i - 1]  = Fund_matrix[i - 1] + diff 
                Capital_reijection_matrix[i] = diff
            else : 
                Capital_reijection_matrix[i] = 0

            C = Fund_matrix[i-1] - floor_matrix[i-1]
            risk_asset = max(min(multiplier * C, Fund_matrix[i-1]),Min_risk_part * Fund_matrix[i-1]) 
            riskless_asset = Fund_matrix[i-1] - risk_asset
            Fund_matrix[i] = risk_asset * (1 + risk_return_mtx[i]) + riskless_asset * ( 1 + safe_asset[i])
            Goal = Goal - 1/Rebalancement_frequency
        
        return_mtx = (Fund_matrix[1:] - Fund_matrix[:-1])/Fund_matrix[:-1]

        return  Fund_matrix , floor_matrix , Capital_reijection_matrix , Reference_cap_matrix,return_mtx
