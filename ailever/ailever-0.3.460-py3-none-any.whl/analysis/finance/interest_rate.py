import numpy as np
import pandas as pd
from datetime import datetime

def earnings(principal = 1000, periods = 365*2, max_rate=20, standard='daily'):
    interests = np.arange(0, max_rate, 0.01)

    dataset = list()
    if standard.lower() == 'daily':
        for interest in interests:
            profit_rate = (principal*(interest/100))/1
            data = [principal + profit_rate*i for i in range(periods)]
            dataset.append(data)
    elif standard.lower() == 'weekly':
        for interest in interests:
            profit_rate = (principal*(interest/100))/7
            data = [principal + profit_rate*i for i in range(periods)]
            dataset.append(data)
    elif standard.lower() == 'monthly':
        for interest in interests:
            profit_rate = (principal*(interest/100))/(365/12)
            data = [principal + profit_rate*i for i in range(periods)]
            dataset.append(data)
    elif standard.lower() == 'yearly':
        for interest in interests:
            profit_rate = (principal*(interest/100))/365
            data = [principal + profit_rate*i for i in range(periods)]
            dataset.append(data)

    timeflow = pd.date_range(start=datetime.today().date(), freq='D', periods=periods)
    quarter = timeflow.quarter
    dayname = timeflow.day_name()
    
    standard = standard.lower()
    standard = standard[0].upper() + standard[1:]
    df = pd.DataFrame(data=np.array(dataset).T, columns=pd.Series(interests, name=standard+'InterestRate').round(2).astype(str)).round(2)
    df['Date'] = timeflow
    df['Quarter'] = quarter
    df['DayName'] = dayname

    df = df.set_index(['Date', 'Quarter', 'DayName'])
    return df

