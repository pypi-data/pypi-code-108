
def model_metrics(model, x_train, y_train, x_test, y_test, show_graphs='Y', f_score = 0.50, classification = 'Y', algo=None):
    
    """
    Display a variety of model metrics for linear and logistic predictive models.
    
    See https://pypi.org/project/gitlabds/ for more information and example calls.
    """
    
    import pandas as pd
    import numpy as np
    from sklearn import metrics
    
    pd.set_option('display.float_format', lambda x: '%.5f' % x)
    
    # Feature Importance    
    if algo == 'mars':
        print('\nFeature Importance')
        features = pd.DataFrame()
        features['features'] = model.named_steps['earth'].xlabels_
        features['importance'] = np.round(model.named_steps['earth'].feature_importances_,4)
        features.sort_values(by=['importance'], ascending=False, inplace=True)
        display(features)
        
    if algo in ('rf', 'xgb'):
        import shap
        # explain the model's predictions using SHAP
        explainer = shap.Explainer(model)
        shap_values = explainer(x_train)

        # mean absolute value of the SHAP values
        print('Feature Importance')
        shap.plots.bar(shap_values)

        # visualize the first prediction's explanation
        #believe this is the log-likelihood. Would need to exp()
        shap.plots.waterfall(shap_values[0])

        # visualize the first prediction's explanation with a force plot
        shap.plots.beeswarm(shap_values)
       
        # Assign shap values based on test dataset
        shap_values = explainer.shap_values(x_test)
        
        # Make plot
        shap.summary_plot(shap_values[1], x_test)  
        
    
    # TRAIN DATA: Get Predicted and Actual
    score_train = model.predict_proba(x_train)
    score_train = pd.DataFrame([item[1] for item in score_train], columns=['predicted'])
    score_train.index = x_train.index
    score_train = pd.concat([score_train, pd.DataFrame(y_train)], axis = 1)
    score_train.rename(columns={score_train.columns[1]:'actual'}, inplace=True)

    # TEST DATA: Get Predicted and Actual
    score_test = model.predict_proba(x_test)
    score_test = pd.DataFrame([item[1] for item in score_test], columns=['predicted'])
    score_test.index = x_test.index
    score_test = pd.concat([score_test, pd.DataFrame(y_test)], axis = 1)
    score_test.rename(columns={score_test.columns[1]:'actual'}, inplace=True)
    
    # Model Metrics
    metricx = [('AUC', metrics.roc_auc_score(score_train['actual'], score_train['predicted']), metrics.roc_auc_score(score_test['actual'], score_test['predicted'])),
               ('R2', metrics.r2_score(score_train['actual'], score_train['predicted']), metrics.r2_score(score_test['actual'], score_test['predicted'])),
               ('Adj R2', 1 - (1 - metrics.r2_score(score_train['actual'], score_train['predicted']))*(len(score_train['predicted'])-1)/(len(score_train['predicted'])-x_train.shape[1]-1), 1 - (1 - metrics.r2_score(score_test['actual'], score_test['predicted']))*(len(score_test['predicted'])-1)/(len(score_test['predicted'])-x_test.shape[1]-1)),
               ('LogLoss', metrics.log_loss(score_train['actual'], score_train['predicted']), metrics.log_loss(score_test['actual'], score_test['predicted'])),
               ('MSE', metrics.mean_squared_error(score_train['actual'], score_train['predicted'], squared=False), metrics.mean_squared_error(score_test['actual'], score_test['predicted'], squared=False)),
               ('RMSE', metrics.mean_squared_error(score_train['actual'], score_train['predicted'], squared=True), metrics.mean_squared_error(score_test['actual'], score_test['predicted'], squared=True)),
               ('MSLE', metrics.mean_squared_log_error(score_train['actual'], score_train['predicted']), metrics.mean_squared_log_error(score_test['actual'], score_test['predicted'])),
               ('Actual Mean', score_train['actual'].mean(), score_test['actual'].mean()),
               ('Predicted Mean', score_train['predicted'].mean(), score_test['predicted'].mean())
              ]

    metricx = pd.DataFrame(metricx, columns=['metric', 'train', 'test'])
    metricx['deviation_pct'] = (metricx['test'] - metricx['train']) / metricx['train']
    
    print('\nModel Metrics')
    format_dict = {'train':'{0:,.4}', 'test': '{0:.4}', 'deviation_pct': '{:.2%}'}

    metricx.set_index('metric', inplace=True)
    display(metricx.style.format(format_dict))
    
    # Determine log-loss cutpoint
    actual=score_test['actual'].mean()
    multi=10000
    class_ratio = [actual, 1-actual]
    class_ratio = [round(i, 3) for i in class_ratio]
    
    actuals=[]
    for i,val in enumerate(class_ratio):
        actuals=actuals+[i for x in range(int(val*multi))]
        
    preds=[]
    for i in range(multi):
        preds+=[class_ratio]

    print(f'log-loss: values below {metrics.log_loss(actuals, preds)} are better than chance.\n\n')
    
    
    # Classification Metrics
    if classification == True:
        
        score_train['classification'] = np.where(score_train['predicted'] > f_score, 1, 0)
        score_test['classification'] = np.where(score_test['predicted'] > f_score, 1, 0)
        
        classification_metricx = [('accuracy', 
                                   metrics.accuracy_score(score_train['actual'], score_train['classification']), 
                                   metrics.accuracy_score(score_test['actual'], score_test['classification'])),
                                  ('precision',
                                   metrics.precision_score(score_train['actual'], score_train['classification']), 
                                   metrics.precision_score(score_test['actual'], score_test['classification'])),
                                  ('recall', 
                                   metrics.recall_score(score_train['actual'], score_train['classification']), 
                                   metrics.recall_score(score_test['actual'], score_test['classification'])),
                                  ('F1 Score', 
                                   metrics.f1_score(score_train['actual'], score_train['classification']), 
                                   metrics.f1_score(score_test['actual'], score_test['classification']))
                                 ]
        
        classification_metricx = pd.DataFrame(classification_metricx, columns=['metric', 'train', 'test'])
        classification_metricx['deviation_pct'] = (classification_metricx['test'] - classification_metricx['train']) / classification_metricx['train']
        
        print('Classification Metrics')
        print(f'Using an F-Score of {f_score}')
        format_dict = {'train':'{0:,.4}', 'test': '{0:.4}', 'deviation_pct': '{:.2%}'}
        classification_metricx.set_index('metric', inplace=True)
        display(classification_metricx.style.format(format_dict))
        
        print('Accuracy: % of Accurate Predictions. (True Positives + True Negatives) / Total Population')
        print('Precision: % of true positives to all positives. True Positives / (True Positives + False Positives)')
        print('Recall: % of postive cases accurately classified. True Positives / (True Positives + False Negatives)')
        print('F1 Score: The harmonic mean between precision and recall.')
            
    
    # Lift Table
    # Compute Deciles
    temp, decile_breaks = pd.qcut(score_train['predicted'], 10, retbins= True, duplicates = 'drop', precision = 10) 
    score_train['decile'], decile_breaks = pd.qcut(score_train['predicted'], 10, labels = np.arange(len(decile_breaks)-1, 0, step=-1), retbins= True, duplicates='drop', precision=10)
    
    score_train['decile'] = pd.to_numeric(score_train['decile'], downcast="integer")  
    decile_breaks = np.round(decile_breaks,10)
    decile_breaks = [float(i) for i in decile_breaks] #Convert to Float from Sci Notation
    
    #For Logistic Regression we want to set the lower and upper bounds to 0 and 1 so we can properly decile test records that may exceed the values shown in training
    decile_breaks[0] = 0
    decile_breaks[10] = 1
    
    print(f'\nDecile Breaks: \n{decile_breaks}\n')
    
    # Apply Deciles to Test
    score_test['decile'] = pd.cut(score_test['predicted'], decile_breaks, labels = np.arange(len(decile_breaks)-1, 0, step=-1), include_lowest=True)
    score_test['decile'] = pd.to_numeric(score_test['decile'], downcast="integer")  
    
    # Model Descriptives
    print("\nTrain Descriptives:")
    display(score_train[['predicted', 'actual', 'decile']].describe())
    display(x_train.describe())
    
    print("\nTest Descriptives:")
    display(score_test[['predicted', 'actual', 'decile']].describe())
    display(x_test.describe())
        
    # Construct Lift Table
    lift = score_test.groupby(['decile']).agg({'decile': ['count'],     
                                                'actual': [lambda value: sum(value ==1), 'mean'], 
                                                'predicted': ['mean', 'min', 'max']
                                                })    
    lift.columns = ['count', 'actual_instances', 'actual_mean', 'predicted_mean', 'predicted_min', 'predicted_max']
    
    lift['cume_count'] = lift['count'].cumsum()
    lift['cume_actual_instances'] = lift['actual_instances'].cumsum()
    lift['cume_actual_mean'] = lift['cume_actual_instances'] / lift['cume_count']
    lift['cume_pct_actual'] = lift['cume_actual_instances'] / lift['actual_instances'].sum()

    # Lift = Resp Mean for each Decile / Total Cume Responses (i.e. last Row of Cume Resp Mean). 
    # This shows how much more likely the outcome is to happe to that decile compared to the average. 
    # 300 Lift = 3x (or 300%) more likely to respond/attrite/engage/etc.
    # 40 Lift = 60% (100 - 40)less likely to respond/attrite/engage/etc.
    lift['lift'] = lift['actual_mean'] / (lift['actual_instances'].sum() / lift['count'].sum()) * 100
    lift['lift'] = lift['lift'].astype(int)

    # Cume Lift = Cume. Resp n for each Decile / Total Cume Responses (i.e. last row of cume resp n)
    # This shows how "deep" you can go in the model while still gettting better results than randomly selecting records for treatment
    # Cume Lift 100 = Would expect to get as many posititve instances of the outcome as chance/random guessing
    lift['cume_lift'] = lift['cume_actual_mean'] / (lift['actual_instances'].sum() / lift['count'].sum()) * 100
    lift['cume_lift'] = lift['cume_lift'].astype(int)  
        
    if show_graphs == True:
        
        import matplotlib.pyplot as plt
        import seaborn as seaborn
        
        # ROC
        metrics.plot_roc_curve(model, x_test, y_test)  
        plt.title('ROC')
        plt.show() 
        
        # Precision vs Recall
        metrics.plot_precision_recall_curve(model, x_test, y_test)
        plt.title('2-class Precision-Recall curve')
        plt.show()

        # Score Distribution
        score_train['predicted'].plot.hist(bins=10, label='jlkj')
        score_test['predicted'].plot.hist(bins=10)
        plt.title('Train/Test Predicted Value Distribution')
        plt.show()
        
        if classification == True:
        
            # Confusion Matrix Prep
            score_test['pred_class'] = np.where(score_test['predicted'] >= f_score, 1, 0)
            #score_test['class'] = np.where(self.scored_test['group'] == 'High', 1, 0)
            cfm = metrics.confusion_matrix(score_test['actual'], score_test['pred_class'])
            class_names=[0,1] # name  of classes
            fig, ax = plt.subplots()
            tick_marks = np.arange(len(class_names))
            plt.xticks(tick_marks, class_names)
            plt.yticks(tick_marks, class_names)

            # Confusion Matrix Heatmap
            seaborn.heatmap(pd.DataFrame(cfm), annot=True, cmap="YlGnBu" ,fmt='g')
            ax.xaxis.set_label_position("bottom")
            plt.tight_layout()
            plt.title('Confusion matrix', y=1.1)
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            plt.show()
        
        # Lift
        score_train['decile'].plot.hist(bins=19)
        score_test['decile'].plot.hist(bins=19)
        plt.xlabel('Decile')
        plt.title('Distribution')
        plt.show()

        lift['actual_mean'].plot(kind='line', grid=False, legend = True)
        lift['predicted_mean'].plot(kind='line', grid=False, legend = True)
        plt.title('Actual vs Predicted')
        plt.ylabel("Outcome %")
        plt.xticks(np.arange(1, 11, step=1))
        plt.show()

        lift['cume_lift'].plot(kind='line', grid=False, legend = True)
        plt.title('Cume. Lift')
        plt.ylabel("Lift")
        plt.xticks(np.arange(1, 11, step=1))
        plt.show()

        lift['cume_pct_actual'].plot(kind='line', grid=False, legend = True)
        plt.title('lift')
        plt.ylabel("% of Total Outcome")
        plt.xticks(np.arange(1, 11, step=1))
        plt.show()
            
    print('\nLift/Gains Table')
    display(lift)
    
    if classification == True:
        return metricx, lift, classification_metricx
    
    else:
        return metricx, lift
    

