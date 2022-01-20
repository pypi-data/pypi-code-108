import numpy as np
import pandas as pd
from datetime import datetime

def earnings(principal = 1000, periods = 365*5, max_rate=20):
    interests = np.arange(0, max_rate, 0.1)

    dataset = list()
    for interest in interests:
        profit_rate = (principal*(interest/100))/365
        data = [principal + profit_rate*i for i in range(periods)]
        dataset.append(data)

    timeflow = pd.date_range(start=datetime.today().date(), freq='D', periods=periods)
    quarter = timeflow.quarter
    dayname = timeflow.day_name()
    
    df = pd.DataFrame(data=np.array(dataset).T, columns=pd.Series(interests, name='AnnualInterestRate').round(1).astype(str)).round(2)
    df['Date'] = timeflow
    df['Quarter'] = quarter    
    df['DayName'] = dayname
    
    df = df.set_index(['Date', 'Quarter', 'DayName'])
    return df 
