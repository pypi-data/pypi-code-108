from preamble import *
from time_series import * 
from QL_tools import *
import QuantLib as ql
import numpy as np
import datetime
currentdir = os.path.dirname(os.path.realpath(__file__))

class PnL_time_series_generator(time_serie_generator):

    def get_params(**kwargs) :
        return kwargs.get('PnL_time_series_generator',{})

    def get_raw_data(self,**kwargs):
        params = time_serie_generator.get_params(**kwargs)
        csv_file = params.get('raw_data_csv',None)
        sep = params.get('sep',';')
        if csv_file is not None and os.path.exists(csv_file): data = pd.read_csv(csv_file,sep=sep, index_col = 0)
        else: data = PnL_time_series_generator.get_stocks_data(**kwargs)
        yf_params = params.get('yf_param',AssertionError("PnL_time_series_generator.get_raw_data needs yf_param"))
        date_format = yf_params.get('date_format','%d/%m/%Y')
        data = ts_data.interpolate(data,**params, float_fun = lambda x: ts_data.date_helper(x,date_format))
        return data

    def get_stocks_data(**kwargs):
        params = time_serie_generator.get_params(**kwargs)
        yf_params = params.get('yf_param',AssertionError("PnL_time_series_generator.get_raw_data needs yf_param"))
        data = ts_data.get_yf_ts_data(**yf_params)

        sep,csv_file,begin_date,end_date,date_format,yf_csv_date_format,time_col,select_columns = ts_data.get_param(**yf_params)

        data[time_col] = ts_data.date_helper(data.index,yf_csv_date_format)

        raw_data_csv = params.get('raw_data_csv',None)
        if raw_data_csv is not None and not os.path.exists(raw_data_csv): data.to_csv(raw_data_csv,sep = sep, index = True)
        return data
    

    def get_data(self, D=0,Nx=0,Ny=0,Nz=0, **kwargs):
        from sklearn.model_selection import train_test_split
        params = time_serie_generator.get_params(**kwargs)
        xfx_csv = params.get('xfx_csv', None)
        sep = params.get('sep',';')
        Shift = int(PnL_time_series_generator.get_params(**kwargs).get('H', None))
        x = self.get_raw_data(**kwargs)
        shifted_cols = list(map(lambda x:x+"_shift", x.columns))
        x_shifted = x.shift(periods = -Shift).dropna()
        x_shifted.columns = shifted_cols
        xfx = pd.concat([x_shifted,x], axis = 1).dropna()
        if xfx_csv is not None and not os.path.exists(xfx_csv): xfx.to_csv(xfx_csv,sep = sep, index = True)
        x,x_shifted = xfx.iloc[:,int(len(xfx.columns)/2):],xfx.iloc[:,:int(len(xfx.columns)/2)]
        test_size = time_serie_generator.get_test_size(**kwargs)
        fx = self.PnL(x,x_shifted, **kwargs)
        z,fz = xfx,fx
        if test_size is not None: 
            x, a, fx, a = train_test_split(xfx, fx, test_size = test_size, shuffle=False)
        else: x, z, fx, fz = xfx, xfx, fx,fx
        return x, fx,x, fx,z, fz

    def get_option_param(**kwargs):
        params = PnL_time_series_generator.get_params(**kwargs)
        option_type = params.get('option_type', ql.Option.Call)
        windows_volatility = params.get('windows_volatility', 10)
        weights = params.get('weights', [0.3,0.3,0.3])
        risk_free_rate = params.get('risk_free_rate', 0.0) 
        dividend_rate = params.get('dividend_rate', 0.01) 
        strike_price = params.get('strike_price', 3000) 
        volatility = params.get('volatility', 0.1) 
        maturity_date = params.get('maturity_date', ql.Date(1, 1, 2023))
        return option_type,weights,risk_free_rate,dividend_rate,strike_price,volatility,maturity_date
        
    def get_QL_dates(x):
        def ordinal_to_qldate(x):
            test = datetime.date.fromordinal(int(x))
            test = test.strftime("%d-%m-%Y")
            test = [int(x) for x in test.split("-")]
            return ql.Date(test[0],test[1],test[2])
        return x.apply(ordinal_to_qldate)

    def PnL(self, x,x_shifted, **kwargs):
        option_type,weights,risk_free_rate,dividend_rate,strike_price,volatility,maturity_date = PnL_time_series_generator.get_option_param(**kwargs)
        windows_volatility = params.get('windows_volatility', 10)
        PnL_csv = params.get('PnL_csv', None)
        sep = params.get('sep',';')
        PricesDates = PnL_time_series_generator.get_QL_dates(x.Date)
        ShiftPricesDates = PnL_time_series_generator.get_QL_dates(x_shifted.Date_shift)
        Spotprices = x.loc[:,x.columns != "Date"]
        ShiftSpotprices = x_shifted.loc[:,x_shifted.columns != "Date_shift"]
        Spot_PnL = np.array(Spotprices).dot(np.array(weights))
        Shifted_PnL = np.array(ShiftSpotprices).dot(np.array(weights))
        PnL = PNLVanillaOption(PricesDates, Spot_PnL, ShiftPricesDates, Shifted_PnL, risk_free_rate  = risk_free_rate, 
        dividend_rate  = dividend_rate, strike_price  = strike_price, volatility = volatility, maturity_date = maturity_date, notional = 1.)
        PnL= pd.DataFrame(PnL, columns=["PnL"],index = x.index)
        if PnL_csv is not None and not os.path.exists(PnL_csv): PnL.to_csv(PnL_csv,sep = sep, index = True)
        # plt.plot(PnL)
        # plt.show()
        return PnL


class PnL_codpy(data_predictor):
    
    def predictor(self,**kwargs):
        if (self.D*self.Nx*self.Ny*self.Nz ):
            self.f_z = op.projection(x = self.x,y = self.y,z = self.z, fx = self.fx,set_codpy_kernel=self.set_kernel,rescale = True,**kwargs)
            pass
    def id(self,name = ""):
        return "codpy pred"

class PnL_codpy_delta(data_predictor):
    def predictor(self,**kwargs):
        if (self.D*self.Nx*self.Ny*self.Nz ):
            #x =self.x.drop(['Date', ])
            x,z,fx,fz = self.x.values, self.z.values, self.fx.values, self.fz.values
            deltax = z - x
            grad = op.nabla(x=x, y=x, z=x, fx=fx, set_codpy_kernel=self.set_kernel, rescale = True, **kwargs)
            grad = np.squeeze(grad)
            self.product_ = np.reshape([np.dot(grad[n],deltax[n]) for n in range(grad.shape[0])],(len(grad),1))
            self.f_z = fx  + self.product_
            self.f_z = pd.DataFrame(self.f_z, columns = self.fz.columns)
            pass
    def id(self,name = ""):
        return "codpy delta"

class PnL_codpy_delta_gamma(data_predictor):
    def predictor(self,**kwargs):
        if (self.D*self.Nx*self.Ny*self.Nz ):
            x,z,fx,fz = self.x.values, self.z.values, self.fx.values, self.fz.values
            deltax = z - x
            grad = op.nabla(x=x, y=x, z=x, fx=fx, set_codpy_kernel=self.set_kernel, rescale = True, **kwargs)
            grad = np.squeeze(grad)
            hess = op.nabla(x=x, y=x, z = x, fx=grad, 
            set_codpy_kernel=None, rescale = False, **kwargs)
            self.product_ = np.reshape([np.dot(grad[n],deltax[n]) for n in range(grad.shape[0])],(len(grad),1))
            Hx = np.reshape([np.matmul(hess[n],deltax[n]) for n in range(hess.shape[0])],(hess.shape[0],hess.shape[1]))
            quadratic_form = np.reshape([np.dot(Hx[n],deltax[n]) for n in range(Hx.shape[0])], (grad.shape[0],1))
            self.f_z = fx  + self.product_ + 0.5*quadratic_form
            self.f_z = pd.DataFrame(self.f_z, columns = self.fz.columns)
            pass
    def id(self,name = ""):
        return "codpy delta gamma"

global_param = {
    'begin_date':'01/01/2020',
    'end_date':'01/01/2021',
    'yf_begin_date': '2020-01-01',
    'yahoo_columns': ['Close'],
    'H' : 1, #Shift
    'P' : 1,
    'symbols' : ["^GSPC", "^FTSE", "^FCHI"]
}

params = {
    'rescale:xmax': 1000,
    'rescale:seed':42,
    'sharp_discrepancy:xmax':1000,
    'sharp_discrepancy:seed':30,
    'sharp_discrepancy:itermax':10,
    'discrepancy:xmax':500,
    'discrepancy:ymax':500,
    'discrepancy:zmax':500,
    'discrepancy:nmax':2000,
    # 'validator_compute':['accuracy_score'],
    # 'set_kernel' : kernel_setters.kernel_helper(kernel_setters.set_linear_regressor_kernel, 2,1e-2 , map_setters.set_unitcube_map),
    'set_kernel' : kernel_setters.kernel_helper(kernel_setters.set_tensornorm_kernel, 2,1e-8 ,map_setters.set_unitcube_map),
    #'set_kernel' : kernel_setters.kernel_helper(kernel_setters.set_gaussian_kernel, 0 ,1e-8 ,map_setters.set_standard_mean_map),
    'time_serie_generator' : {
        'yf_param' : {
            'symbols':global_param['symbols'],
            'begin_date':global_param['begin_date'],
            'end_date':global_param['end_date'],
            'yahoo_columns': global_param['yahoo_columns'],
            'yf_begin_date': global_param['yf_begin_date'],
            'csv_file' : os.path.join(data_path,"PnL",'-'.join(global_param['symbols'])+'-'+global_param['begin_date'].replace('/','-')+"-"+global_param['end_date'].replace('/','-')+".csv"),
            'date_format' : '%d/%m/%Y',
            'yahoo_date_format':'%Y-m%-d%',            
            'csv_date_format':'%d/%m/%Y'            
        },
        'test_size': 0.01,
        'raw_data_csv' : os.path.join(data_path,"PnL","PnL_time_series_generator-"+'-'.join(global_param['symbols'])+'-'+global_param['begin_date'].replace('/','-')+"-"+global_param['end_date'].replace('/','-')+".csv"),
        'PnL_csv' : os.path.join(data_path,"PnL","PnL"+".csv"),
        'xfx_csv' : os.path.join(data_path,"PnL","xfx"+".csv")
        },
    'PnL_time_series_generator' : {
        'windows_volatility': 10,
        'weights': [0.3,0.3,0.3],
        'risk_free_rate': 0.0, 
        'dividend_rate': 0.01, 
        'strike_price': 6000., 
        'volatility': 0.1, 
        'maturity_date': ql.Date(1, 1, 2023), 
        'option_type': ql.Option.Call,
        'H': global_param['H']
    }

    # 'data_generator' : {
    #     'variables_cols_drop' : ['Date'],
    #     'values_cols_drop' : ['Date']
    # },
    # 'time_serie_generator' : {
    #     'raw_data_x_csv' : os.path.join(data_path,"PnL","ts_PnL_x-"+global_param['begin_date'].replace('/','-')+"-"+global_param['end_date'].replace('/','-')+"-H"+str(global_param['H'])+"-P"+str(global_param['P'])+".csv"),
    #     'raw_data_fx_csv' : os.path.join(data_path,"PnL","ts_PnL_fx-"+global_param['begin_date'].replace('/','-')+"-"+global_param['end_date'].replace('/','-')+"-H"+str(global_param['H'])+"-P"+str(global_param['P'])+".csv"),
    #     'H':global_param['H'],'P':global_param['P'],'test_size' : 0.5,
    #     'dates_csv_file' : os.path.join(data_path,"PnL","Dates"+".csv")
    #     },
}

def get_param(hist_depth=0,pred_depth=0):
    return params

def get_realized_vol(dataset, windows_volatility):
    dataset['returns'] = dataset[0] - dataset[0].shift(1) #np.log(dataset[0]/dataset[0].shift(1))
    dataset.fillna(0, inplace = True)
    volatility = dataset.returns.rolling(window=windows_volatility).std(ddof=0)*np.sqrt(252)
    volatility = volatility.dropna()
    return volatility.iloc[0]

if __name__ == "__main__":
    scenarios = get_scenarios(**get_param(),my_generator = [PnL_time_series_generator], my_predictor = [PnL_codpy])
    results = [scenarios.data_generator.format_output(scenarios.predictor.fz,**get_param())]
    for predictor,generator in zip(scenarios.accumulator.predictors,scenarios.accumulator.generators):
        debug = generator.format_output(predictor.f_z,**get_param()) 
        results.append(debug)


    # fx,fz,f_z = scenarios.predictor.fx,scenarios.predictor.fz, scenarios.predictor.f_z
    # data_generator.save_cd_data(scenarios.predictor,x_csv = os.path.join(data_path,"PnL","x.csv"),
    #     fx_csv = os.path.join(data_path,"PnL","fx.csv"),
    #     fz_csv = os.path.join(data_path,"PnL","fz.csv"),
    #     f_z_csv = os.path.join(data_path,"PnL","f_z.csv"))
    print("RMSE: ", scenarios.predictor.accuracy_score)
    print(scenarios.results)
    scenarios.plot_output(results = results,fun_x = lambda x : pd.to_datetime(x,format='%d/%m/%Y'),listlabels=["observed","generated","observed","mean average"],**get_param(),figsize = (5,5))
    pass
