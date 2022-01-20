import skextremes as sk
import pandas as pd
from thresholdmodeling import thresh_modeling as tm
from rpy2.robjects.packages import importr
POT = importr('POT')


def BM(data,period):
    data[["year", "month", "day"]] = data["Date"].str.split("-", expand = True)
    maxClaim=data.groupby(["year"]).agg({"Loss": max})
    maxClaim.sort_values(ascending=False,by="Loss")
    return pd.DataFrame(maxClaim)

def gevfit(data,fit_method='mle',ci=0,ci_method='delta'):
    model = sk.models.classic.GEV(data, fit_method = fit_method, ci = ci,ci_method=ci_method)
    return model
    
def gevparams(model):
    return model.params
    
def summary(model):
    return model.plot_summary()
      
def MRL(data,alpha=0.05):
    plot=tm.MRL(data, alpha)
    return plot
                   
def pot(data,threshold):
    exce=data[data["Loss"].gt(threshold)].sort_values(ascending=False, by="Loss")
    return pd.DataFrame(exce)

def gpdfit(sample,threshold,fit_method='mle'):
    fit=tm.gpdfit(sample, threshold, fit_method)
    return fit

def gpdpdf(data,threshold,fit_method,bin_method,alpha):
    fitpdf=tm.gpdpdf(data, threshold,fit_method,bin_method,alpha)
    return fitpdf
   
def gpdcdf(data,threshold,fit_method,alpha):
    fitcdf=tm.gpdcdf(data,threshold,fit_method,alpha)
    return fitcdf
   
def qqplot(data,threshold,fit_method,alpha):
    fitqqplot=tm.qqplot(data, threshold,fit_method,alpha)
    return fitqqplot
   
def ppplot(data,threshold,fit_method,alpha):
    fitppplot=tm.ppplot(data, threshold,fit_method,alpha)
    return fitppplot
   
def returnValue(data,threshold,alpha, block_size,return_period,fit_method):
    retval = tm.return_value(data,threshold,alpha, block_size,return_period,fit_method)
    return retval
       
       
        
