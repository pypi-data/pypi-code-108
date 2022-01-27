'''
Compute voter power index for 2 party vote using either Banzhaf or Shapley–Shubik mehods

Usage:
--------------
INPUT: Dataframe 
    DataFrame: 5 columns (df, TotalPopCol, TargetPopCol, Party1, Party2, vIndex=None, filename=None)

PARAMETERS: Index, df or list of dfs
    Index: Either/Both bpi for (Banzhaf Power Index)  and ssi for (Shapley–Shubik index)

OUTPUT:
    Default: {Index-Type}.csv 
        option: filename = {filename}-{Index-Type}.csv

'''
import pandas as pd
import itertools
import math
import collections 
import logging


def block_classification(df, OtherPopCol, TargetPopCol, OtherParty, ColilitionParty):
    df['Target_Percentage'] = df[TargetPopCol]/(df[OtherPopCol]+df[TargetPopCol])
    df['Group'] = None
    df = df.reset_index(drop=True)

    for i ,row in df.iterrows():
        if row['Target_Percentage'] >= .9:
            df['Group'].iloc[i] = 'T90%'
        if row['Target_Percentage'] < .9:
            df['Group'].iloc[i] = 'T60%'
        if row['Target_Percentage'] < .6:
            df['Group'].iloc[i] = 'N50%'
        if row['Target_Percentage'] <= .4:
            df['Group'].iloc[i] = 'O60%'
        if row['Target_Percentage'] <= .1:
            df['Group'].iloc[i] = 'O90%'
    quoat = df[[OtherParty,ColilitionParty]].sum()
    quoat = (quoat[ColilitionParty] + quoat[OtherParty])/2
    voteGroups = df[['Group',ColilitionParty]].groupby('Group').sum().reset_index()
    voteGroups = voteGroups.values.tolist()
    return voteGroups, quoat


def bpi(group, quoat, filename):
    idx = 0
    output = {}
    for i in range(1,len(group)+1):
        for j in itertools.combinations(group,i):
            c = 0
            for k in j:
                c += k[1]
                if c > quoat:
                    idx += 1
                    output[idx] = {}
                    output[idx]['Coliltion'] = j
                    output[idx]['Total'] = c
                    break
    crit_count = {'T90%':0,'T60%':0,'O90%':0,'O60%':0,'N50%':0}
    for key, value in output.items():
        wC = value['Total']
        for i in value['Coliltion']:
            if wC - i[1] < quoat:
                crit_count[i[0]] += 1
    df_share = pd.DataFrame(list(crit_count.items()),columns = ['Cat','T_Index'])
    T_IdxSum = df_share['T_Index'].sum()
    df_share['T_PowerShare'] = (df_share['T_Index']/T_IdxSum) * 100
    df_share['T_Critical_Vote'] = (df_share['T_Index']/(2**(5-1)))*100
    if filename is None:
        df_share.to_csv(f'Banzhaf-Power.csv',index=False)
    else:
        df_share.to_csv(f'{filename}-Banzhaf-Power.csv',index=False)

def ssi(group, quoat, filename):
    output = {'T90%':0,'T60%':0,'O90%':0,'O60%':0,'N50%':0}
    for i in itertools.permutations(group):
        c = 0
        for j in i:
            c += j[1]
            if c > quoat:
                output[j[0]] += 1
                break
    df_share = pd.DataFrame(list(output.items()),columns = ['Cat','T_Count'])
    factorial = math.factorial(len(output.keys()))
    df_share['T_Index'] = df_share['T_Count']/factorial
    if filename is None:
        df_share.to_csv(f'Shapley–Shubik.csv',index=False)
    else:
        df_share.to_csv(f'{filename}-Shapley–Shubik.csv',index=False)

def power_index(df, OtherPopCol, TargetPopCol, OtherParty, ColilitionParty, vIndex=None, filename=None):
    if len(df.index) < 2:
        raise Exception('Dataframe needs 2 or more rows to compare')
    group, quoat = block_classification(df, TotalPopCol, TargetPopCol, OtherParty, ColilitionParty)
    if vIndex is None or vIndex == 'bpi':
        bpi(group, quoat, filename)
    if vIndex is None or vIndex == 'ssi':
        ssi(group, quoat ,filename)