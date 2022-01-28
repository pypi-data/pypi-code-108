import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sklearn

def group_differences(df, threshold, covariate_columns):
    print("Above threshold group:")
    print(df[df.pred_ranking > threshold][covariate_columns].describe())
    print("\nBelow threshold group:")
    print(df[df.pred_ranking <= threshold][covariate_columns].describe())
    
def print_model_stats(df, pred_threshold, observed_column='observed', pred_column='pred_observed'):
    
    df_stats, _ = rate_plot(df, thresholds=[pred_threshold])

    total_positive = df[observed_column].sum()
    total_negative = len(df) - total_positive
    total_pred_positive = df[pred_column].sum()
    response_rate = total_positive / len(df)

    print("Total positive: {:,} out of {:,} (response rate: {:.1f}%)".format(total_positive, len(df), 100*response_rate))
    print("Total predicted positive: {:,} out of {:,} (response rate: {:.1f}%)".format(total_pred_positive, len(df), 100*(total_pred_positive/len(df))))
    print("Proportion of predicted positives actually positive (precision): {:.1f}%".format(100.0*df_stats['precision_1'][0]))
    print("Proportion of positives, predicted as such (recall): {:.1f}%".format(100.0*df_stats['recall_1'][0]))
    print("Proportion of predicted negatives actually negative (precision): {:.1f}%".format(100.0*df_stats['precision_0'][0]))
    print("Proportion of negatives, predicted as such (recall): {:.1f}%".format(100.0*df_stats['recall_0'][0]))
    #print("F1: {:.2f}".format(2*(precision*recall)/(precision+recall)))


def gains_chart(df_in, ranking='pred_ranking', response='observed', 
                title='Cumulative Gains', xaxis_title='% Customers Contacted',
                yaxis_title='% Positive Response', n=100):

    df = df_in.sample(frac=1).sort_values(by=[ranking], ascending=False)

    scale = df[response].sum()

    gains = [0.0]

    nn = len(df)
    split_n = int( np.ceil(nn / (n)) )

    ii = 0
    gain = 0
    while ii < nn:

        delta = min(ii+split_n, nn)
        
        gain = gain + df.iloc[ii:delta,:][response].sum()
        gains.append(gain)

        ii = split_n + ii     

    gains = [100.0*g / scale for g in gains]
    first_n = len(gains)

    #for i,j in zip(cum_gains, np.linspace(0,1,first_n)):
    #    print(i,j)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=np.linspace(0,1,first_n)*100, y=np.linspace(0,1,first_n)*100,
                            mode='lines', name='random'))
    fig.add_trace(go.Scatter(x=np.linspace(0,1,first_n)*100, y=gains,
                            mode='lines', name='model'))

    fig.update_xaxes(tickvals=np.linspace(0,100,11))
    fig.update_yaxes(tickvals=np.linspace(0,100,11))

    # Edit the layout
    fig.update_layout(title=title,
                    xaxis_title=xaxis_title,
                    yaxis_title=yaxis_title)

    df_gains = pd.DataFrame([(g,l,g/l if l > 0 else 0) for g,l in zip(gains, np.linspace(0,1,first_n)*100)], columns=['gain','base','lift'])
    df_gains.set_index('base', inplace=True)

    return df_gains, fig


def roc_curve(df, observed_column = 'observed', ranking_column = 'pred_ranking', title='ROC', xaxis_title='False positive rate',
                yaxis_title='True postitive rate'):

    fpr,tpr,_ = sklearn.metrics.roc_curve(df[observed_column], df[ranking_column])

    auc = sklearn.metrics.auc(fpr,tpr)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.linspace(0,1,len(fpr)), y=np.linspace(0,1,len(fpr)), 
                            mode='lines', name='random'))
    fig.add_trace(go.Scatter(x=fpr, y=tpr,
                            mode='lines', name='ROC'))

    fig.update_layout(title=title, xaxis_title=xaxis_title,
                        yaxis_title=yaxis_title)

    return auc, fig
    

def rate_plot(df, thresholds = [0.5], observed_column = 'observed', pred_column = 'pred_observed', ranking_column = 'pred_ranking'):

    stats = []
    for t in thresholds:
        df[pred_column] = df[ranking_column].apply(lambda x: 1 if x > t else 0)

        accuracy = sklearn.metrics.accuracy_score(
            df[observed_column], df[pred_column])
        
        print("  threshold={}, accuracy={:.2f}".format(t, accuracy))
        
        tn, fp, fn, tp = sklearn.metrics.confusion_matrix(df[observed_column], 
                                                          df[pred_column]).ravel()
        
        total_positive = fn+tp
        total_negative = fp+tn
        total_pred_positive = df[pred_column].sum()
        response_rate = total_positive / len(df)
        pred_response_rate = total_pred_positive / len(df)
        precision_1 = tp/(fp+tp)
        recall_1 = tp/total_positive
        precision_0 = tn/(fn+tn)
        recall_0 = tn/total_negative

        stats.append((t, accuracy, response_rate, pred_response_rate, precision_1, recall_1, precision_0, recall_0))

    df_stats = pd.DataFrame(stats, columns=['threshold', 'accuracy', 'resp_rate', 'pred_resp_rate', 'precision_1', 'recall_1', 'precision_0', 'recall_0'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=thresholds, y=df_stats['accuracy'],
                            mode='lines', name='accuracy'))
    fig.add_trace(go.Scatter(x=thresholds, y=df_stats['resp_rate'],
                            mode='lines', name='resp rate'))
    fig.add_trace(go.Scatter(x=thresholds, y=df_stats['pred_resp_rate'],
                            mode='lines', name='pred resp rate'))
    fig.add_trace(go.Scatter(x=thresholds, y=df_stats['precision_1'],
                            mode='lines', name='precision_1'))
    fig.add_trace(go.Scatter(x=thresholds, y=df_stats['recall_1'],
                            mode='lines', name='recall_1'))      

    return df_stats, fig

