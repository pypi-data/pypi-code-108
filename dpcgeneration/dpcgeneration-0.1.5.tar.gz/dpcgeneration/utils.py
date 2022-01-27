import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import gc
from matplotlib.ticker import FormatStrFormatter

def convert_dico_dataframe( data_dict, file):
    data_items = data_dict.items()
    data_list = list(data_items)

    df = pd.DataFrame(data_list)
    df.to_csv( file, index=False)
    import datetime
    now = datetime.datetime.now()
    #print("Current date and time : " + (now.strftime("%Y-%m-%d %H:%M:%S")))


def convert_numpy_dataframe( data_np, file):
    df = pd.DataFrame(data=data_np, index=[str(i) for i in range(len(data_np))],
                      columns=[str(i) for i in range(len(data_np))])

    df.to_csv( file, index=False)
    import datetime
    now = datetime.datetime.now()
    #print("Current date and time : " + (now.strftime("%Y-%m-%d %H:%M:%S")))

def calculate_oneWay(dataf, names, list_poss=None):

        df_oneway = pd.DataFrame()

        for attributename in (names):

            dico = dataf[attributename].value_counts()
            dfoneway0 = pd.DataFrame()
            for key in dico.keys():
                dfoneway0 = dfoneway0.append ({'Key':attributename+'_'+str(key).strip(),'Value':dico[key]}, ignore_index=True)


            if len(df_oneway) == 0:
                df_oneway = dfoneway0

            else:
                df_oneway = pd.concat([df_oneway, dfoneway0])
            del (dfoneway0)
            gc.collect()

        if list_poss != None:
            for possi in list_poss:
                if not possi in df_oneway['Key']:
                    df_oneway.append({'Key': possi, 'Value': 0}, ignore_index=True)
        return df_oneway.sort_values(by=['Key'])

def calculate_twoWay( dataf, colnames, list_poss=None, display_log=False):
        twoway = {}
        now = datetime.datetime.now()
        df_twoway = pd.DataFrame()
        for i in range(len(colnames)):
            if display_log == True:
                print(colnames[i])
            for j in range(i + 1, len(colnames)):

                key1 = colnames[i]
                key2 = colnames[j]

                twoway = pd.DataFrame(dataf[[key1, key2]].value_counts().reset_index())
                twoway[key1] = key1 + '_' + twoway[key1].map(str)
                twoway[key2] = key2 + '_' + twoway[key2].map(str)

                twoway = twoway.rename(columns={key1: 'key1', key2: 'key2', 0: 'Value'})



                if len(df_twoway) == 0:
                    df_twoway = twoway

                else:
                    df_twoway = pd.concat([df_twoway, twoway])
                del (twoway)
                gc.collect()



        if display_log == True:
            print("end two-way at %s " % (str(datetime.datetime.now() - now)))

        return df_twoway.sort_values(by=['key1','key2'])

def printgraph( attribute_to_predict, onewayerror_lap, onewayerror_cond, path_results, type):

        years = sorted(list(onewayerror_lap.keys()))

        gen_noisy_meanlap = [0 for x in years]
        gen_noisy_minlap = [0 for x in years]
        gen_noisy_maxlap = [0 for x in years]

        gen_noisy_meancond = [0 for x in years]
        gen_noisy_mincond = [0 for x in years]
        gen_noisy_maxcond = [0 for x in years]

        for year in years:
            gen_noisy_meanlap[years.index(year)] = (np.mean(onewayerror_lap[year]))
            gen_noisy_minlap[years.index(year)] = min(onewayerror_lap[year])
            gen_noisy_maxlap[years.index(year)] = max(onewayerror_lap[year])

            gen_noisy_meancond[years.index(year)] = (np.mean(onewayerror_cond[year]))
            gen_noisy_mincond[years.index(year)] = min(onewayerror_cond[year])
            gen_noisy_maxcond[years.index(year)] = max(onewayerror_cond[year])

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter((FormatStrFormatter('%d')))

        plt.ylabel('absolute error')

        plt.plot(years, gen_noisy_meanlap, color='green')
        ax.fill_between(years, gen_noisy_minlap, gen_noisy_maxlap, color='green', alpha=.25, label='Laplace random')

        plt.plot(years, gen_noisy_meancond, color='blue')
        ax.fill_between(years, gen_noisy_mincond, gen_noisy_maxcond, color='blue', alpha=.25,
                        label='conditional prediction')

        plt.xlabel('year')
        plt.legend(loc='best')
        plt.title('Absolute Error ' + type + ': Tax return')
        plt.savefig(path_results + type + 'absolute_error_tax_return.png')
        plt.show()
        plt.close()

def calculate_print(df_origs, df_gens, title, labels,figname='fig',  printgraph=True, savedata='dataout.csv'):

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    df_compares = []


    for nbb in range(1):

        df_orig = df_origs[nbb].rename(columns={"Value": "Origin"})
        df_gen = df_gens[nbb].rename(columns={"Value": "Gen"})

        if 'Key' in list(df_orig.columns):
            df_compare = pd.merge(df_orig, df_gen, on='Key',how="left").reset_index(drop=True)
        else:
            df_compare = pd.merge(df_orig, df_gen, on=["key1", "key2"],how="left").reset_index(drop=True)

        df_compare['absolute error'] = (df_compare.Origin - df_compare.Gen).abs()
        df_compare['relative error'] = df_compare['absolute error'] / np.maximum(100, df_compare.Origin) * 100
        df_compare['cdf_abserror'] = df_compare['absolute error'].rank(method='average', pct=True)
        df_compare['cdf_relerror'] = df_compare['relative error'].rank(method='average', pct=True)

        #if displ == True:
        #    display(df_compare.sort_values(by=['absolute error']))
        print (labels, nbb, title)
        df_compare.sort_values('absolute error').plot(ax=ax, x='absolute error', y='cdf_abserror', grid=True,
                                                      title=title, label=labels[nbb])
        plt.ylabel('cumulative distribution' )

        if printgraph == True:
            plt.show()

        plt.savefig(figname+str(nbb))
        plt.close()
        #df_compare.sort_values('relative error').plot(ax=ax2, x='relative error', y='cdf_relerror', grid=True,
        #                                              title=title + ' Relative Error')

        df_compares.append(df_compare)
        df_compare.to_csv(savedata+str(nbb)+'.csv', index=False)


    return df_compares
