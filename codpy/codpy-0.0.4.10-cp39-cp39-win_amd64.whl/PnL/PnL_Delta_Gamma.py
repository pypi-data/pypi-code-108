from PnLexplanation import *

class Valuation_time_series_generator(PnL_time_series_generator):

    def get_params(**kwargs) :
        return kwargs.get('Valuation_time_series_generator',{})


    def get_data(self, D=0,Nx=0,Ny=0,Nz=0, **kwargs):
        Shift = int(PnL_time_series_generator.get_params(**kwargs).get('H', None))
        x = self.get_raw_data(**kwargs)

        fx = self.Valuation(x, **kwargs)

        z = x.iloc[Shift:,:]
        x = x.iloc[:-Shift,:]
        fz = fx.iloc[Shift:,:]
        fx = fx.iloc[:-Shift,:]

        return x, fx,x, fx, z, fz
        

    def Valuation(self, x, **kwargs):

        option_type,weights,risk_free_rate,dividend_rate,strike_price,volatility,maturity_date = PnL_time_series_generator.get_option_param(**kwargs)
        PricesDates = PnL_time_series_generator.get_QL_dates(x.Date)
        value_csv = params.get('value_csv', None)
        sep = params.get('sep',';')
        Spotprices = x.loc[:,x.columns != "Date"]
        Spot_basket = np.array(Spotprices).dot(np.array(weights))
        value = np.zeros(len(PricesDates))
        for i in range(len(PricesDates)) :
            datei = PricesDates.values[i]
            spoti = Spot_basket[i]
            value[i] = VanillaOption(datei, spoti, risk_free_rate, dividend_rate, strike_price, volatility, maturity_date)
        value= pd.DataFrame(value, columns=["value"],index = x.index)

        if value_csv is not None and not os.path.exists(value_csv): value.to_csv(value_csv,sep = sep, index = True)
        return value

def get_realized_vol(dataset, windows_volatility):
    dataset['returns'] = dataset[0] - dataset[0].shift(1) #np.log(dataset[0]/dataset[0].shift(1))
    dataset.fillna(0, inplace = True)
    volatility = dataset.returns.rolling(window=windows_volatility).std(ddof=0)*np.sqrt(252)
    volatility = volatility.dropna()
    return volatility.iloc[0]

def main():    
    scenarios = get_scenarios(**get_param(),my_generator = [Valuation_time_series_generator], my_predictor = [PnL_codpy_delta])
    print("RMSE: ", scenarios.predictor.accuracy_score)
    print(scenarios.results)

    results = [scenarios.data_generator.format_output(scenarios.predictor.fz,**get_param())]
    for predictor,generator in zip(scenarios.accumulator.predictors,scenarios.accumulator.generators):
        debug = generator.format_output(predictor.f_z,**get_param()) 
        results.append(debug)


    scenarios.plot_output(results = results,fun_x = lambda x : pd.to_datetime(x,format='%d/%m/%Y'),listlabels=["observed","generated"],**get_param())

    scenarios = get_scenarios(**get_param(),my_generator = [Valuation_time_series_generator], my_predictor = [PnL_codpy_delta_gamma])
    print("RMSE: ", scenarios.predictor.accuracy_score)
    print(scenarios.results)

    results = [scenarios.data_generator.format_output(scenarios.predictor.fz,**get_param())]
    for predictor,generator in zip(scenarios.accumulator.predictors,scenarios.accumulator.generators):
        debug = generator.format_output(predictor.f_z,**get_param()) 
        results.append(debug)


    scenarios.plot_output(results = results,fun_x = lambda x : pd.to_datetime(x,format='%d/%m/%Y'),listlabels=["observed","generated"],**get_param())

if __name__ == "__main__":
    main()
    pass
