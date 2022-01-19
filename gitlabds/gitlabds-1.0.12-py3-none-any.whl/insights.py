def marginal_effects(model, x_test, dv_description, field_labels = None):
    
    import pandas as pd
    import numpy as np
    
    #Clean up model variable names in basis function
    
    #Get Variable and Coef List
    variables = []
    
    for v in model.named_steps['earth'].basis_:
        if v.is_pruned() is False:
            variables.append(str(v))

    coef = model.named_steps['log'].coef_[0]
    bf = pd.DataFrame({'feature' : variables, 'coef': coef})
    
    #Rename Intercept
    bf['feature'].replace('(Intercept)', 'Intercept', inplace = True)
    
    #Remove h() from variable
    bf['feature'].replace("h" + r"\(",'', regex = True, inplace = True)
    bf['feature'].replace(r"\)", '', regex = True, inplace = True)
    bf['orig_feature'] = bf['feature']
    
    #print(bf)
    
    #Clean up Variable names and create Hing points    
    for idx, v in enumerate(bf['feature']):
        
        #ensure index matches iterator
        if bf.loc[idx, 'feature'] != v:
            raise Exception('Index does not match iterator. reset index of bf dataframe before running this step')
        
        #When hinge value comes before variable name
        #As determined by if the first character of the field is numeric or if the second character is numeric (in case of a negative sign)
        if (v[0].isnumeric() is True) | (v[1].isnumeric() is True):
                
            #Trim variable name to what comes after the "-" sign
            bf.loc[idx, 'feature'] = str(v).rsplit("-", 1)[1]
                
            #if contains "-" and "+" then > and postive hinge value
            if (v.count('-') > 0) & (v.count('+') > 0):
                ### Not tested and verified. Number 8 on list. Not even sure if MARS will output a value like this
                print(f'Hinge feature found in format not previously encountered: {v}. This feature may not be properly captured in marginal effects')
                bf.loc[idx, 'sign'] = '>'
                bf.loc[idx, 'hinge'] = float(str(v).rsplit("+",1)[0])*-1
                
            #if contains 2 "-" then  then < and negative hinge value
            elif v.count('-') > 1:
                bf.loc[idx, 'sign'] = '<'
                bf.loc[idx, 'hinge'] = float(str(v).rsplit("-",1)[0])
                
            #if contains 1 "+" then > and negative hinge value
            elif v.count('+') > 0:
                ### Not tested and verified. Number 7 on list. Not even sure if MARS will output a value like this
                print(f'Hinge feature found in format not previously encountered: {v}. This feature may not be properly captured in marginal effects')
                bf.loc[idx, 'sign'] = '>'
                bf.loc[idx, 'hinge'] = float(str(v).rsplit("+",1)[0])*-1
                
            #if contains 1 "-" then < and positive hinge value
            elif v.count('-') > 0:
                bf.loc[idx, 'sign'] = '<'
                bf.loc[idx, 'hinge'] = float(str(v).rsplit("-",1)[0])
                
            
        #When hinge value comes after variable name or if there is no hinge
        else:
            
            #if the variable name can be broken into by "-" or "+" that indicates a hinge
            #Don't split dummy coded fields
            if (v.count('-') > 0) & (v.count('dummy') == 0):
                bf.loc[idx, 'feature'] = str(v).split("-")[0]
              
                #if  two "-" then < and negative hinge value
                if v.count('-') > 1:
                    ### Not tested and verified. Number 2 on list. Not even sure if MARS will output a value like this
                    print(f'Hinge feature found in format not previously encountered: {v}. This feature may not be properly captured in marginal effects')
                    bf.loc[idx, 'sign'] = '<'
                    bf.loc[idx, 'hinge'] = float(str(v).split("-", 1)[1])*-1
                
                #if only one "-" then > and positive hinge value
                else:
                    bf.loc[idx, 'sign'] = '>'
                    bf.loc[idx, 'hinge'] = float(str(v).split("-", 1)[1])
                                        
            #if the variable name can be broken into by "+" that indicates a hinge 
            elif v.count('+') > 0:
                bf.loc[idx, 'feature'] = str(v).split("+")[0]
                
                #if also contains "-" then < and positive hinge value
                if v.count('-') > 1:
                    ### Not tested and verified. Number 4 on list. Not even sure if MARS will output a value like this
                    print(f'Hinge feature found in format not previously encountered: {v}. This feature may not be properly captured in marginal effects')
                    bf.loc[idx, 'sign'] = '<'
                    bf.loc[idx, 'hinge'] = float(str(v).split("+", 1)[1])
                    
                #if just one "=" then > and negative hinge value
                else:
                    bf.loc[idx, 'sign'] = '>'
                    bf.loc[idx, 'hinge'] = float(str(v).split("+", 1)[1])*-1
                    
        #Determine binary features and MEM jump
        if v != 'Intercept':
            range = x_test[bf.loc[idx, 'feature']].std()
            
            #Determine Binary feature
            if x_test[bf.loc[idx, 'feature']].nunique() == 2:
                bf.loc[idx, 'binary_flag'] = True
                bf.loc[idx, 'increase_value'] = 1
            
            #Determine appropriate increase "jump" (.01/.1/1/10/100/1000)
            elif (range  < 1) & (x_test[bf.loc[idx, 'feature']].dtype != np.int64):
                bf.loc[idx, 'increase_value'] = 0.01
            elif (range  < 10) & (x_test[bf.loc[idx, 'feature']].dtype != np.int64):
                bf.loc[idx, 'increase_value'] = 0.1
            elif range <= 100:
                bf.loc[idx, 'increase_value'] = 1
            elif range <= 1000:
                bf.loc[idx, 'increase_value'] = 10
            elif range <= 10000:
                bf.loc[idx, 'increase_value'] = 100
            else:
                bf.loc[idx, 'increase_value'] = 1000
            

    #Determine lowest hinge value for each feature
    lowest_hinge = bf.groupby('feature').agg(lowest_hinge=('hinge', 'min'))
    bf = bf.join(lowest_hinge, on='feature', how='left', sort=True)
    bf.sort_values(['feature', 'hinge', 'sign'], axis=0, ascending=True, inplace=True)
    bf['prior_hinge'] = bf.groupby(['feature']).shift(1)['hinge']
    
    #Reset index so enumerate step below will work properly
    bf.reset_index(inplace=True, drop=True)
    
    #Add on Feature Labels
    if field_labels:
        bf['feature_label'] = bf['feature'].map(field_labels)
        bf['feature_label'] = np.where(bf['feature_label'].isna(), 
                                                 bf['feature'],
                                                 bf['feature_label']
                                                )
        
    else:
        bf['feature_label'] = bf['feature']
    
    #print(bf)

    #Calculate Marginal Effect at the Mean (MEM)
    #Purpose is to determine the likelihood for the "average" record and then see what happens when there is a an X-unit increase or decrease to a variable
    means = pd.DataFrame(x_test.mean()).transpose()
    mean_prob = np.round([item[1] for item in model.predict_proba(means)][0],3)
    print(f'Mean likelihood: {mean_prob}\n')   
    
    for idx, v in enumerate(bf['feature']):

        #ensure index matches iterator
        if bf.loc[idx, 'feature'] != v:
            raise Exception('Index does not match iterator. reset index of bf dataframe before running this step')
        
        #create copies of means df to be manipulated for each MEM calculation for each variable
        mean_zero = means.copy(deep=True)
        mean_increase = means.copy(deep=True)
        
        if v != 'Intercept':
        
            #Zero out mean for calculating MEM for binary variables. Everything else can be from its mean
            if bf.loc[idx, 'binary_flag'] == True:
                
                mean_zero[v] = 0
        
            #For hinge variables
            #print(pd.isnull(bf.loc[idx, 'hinge']))
            elif pd.isnull(bf.loc[idx, 'hinge']) is False:
                
                #For greater-than hinges, set the zero value to the hinge value
                if bf.loc[idx, 'sign'] == '>':
                    
                    mean_zero[v] = bf.loc[idx, 'hinge']
                
                #For less-than hinges
                if bf.loc[idx, 'sign'] == '<':
                    
                    #Set mean_zero value to lowest prior hinge
                    if pd.isnull(bf.loc[idx, 'prior_hinge']) is False:
                        
                        mean_zero[v] = bf.loc[idx, 'prior_hinge']
                                                
                    #If no lower mean_zero value, and hinge is a positive value, keep at current mean_zero value
                    elif bf.loc[idx, 'hinge'] > 0:
                        
                        pass
                    
                    #If no lower mean_zero value and hinge is a negative value set to 10x "jump" value bwelow hinge value
                    else:
                        
                        mean_zero[v] = bf.loc[idx, 'hinge'] - (bf.loc[idx, 'increase_value']*10)
                        
                
            #Create the mean score at the mean (or 0 for binary variables)
            mean_marginal_prob = np.round([item[1] for item in model.predict_proba(means)][0],3)
            #print(mean_zero_prob)
  
            #Calculate the mean score when variable increases by "jump" amount" (.01/.1/1/10/100/1000)
            mean_increase[v] = mean_zero[v] + bf.loc[idx, 'increase_value']
            mean_increase_prob = np.round([item[1] for item in model.predict_proba(mean_increase)][0],2)
            
            bf.loc[idx, 'marginal_effect'] = np.round(mean_increase_prob - mean_marginal_prob,3)
            
            #Directionality
            bf.loc[idx, 'direction'] = np.where(bf.loc[idx, 'marginal_effect'] > 0, 'increases', 'decreases')

        #Create Text Interp. of MEM
        #Binary features
        if bf.loc[idx, 'binary_flag'] == True:
            
            bf.loc[idx, 'interpretation'] = f"Increasing the value of \'{bf.loc[idx, 'feature_label']}\' from 0 to 1 {bf.loc[idx, 'direction']} the {dv_description} by {np.round(np.abs(bf.loc[idx, 'marginal_effect']*100),2)} percentage points"

        #Hinge features
        elif pd.isnull(bf.loc[idx, 'hinge']) is False:
            
            bf.loc[idx, 'interpretation'] = f"When \'{bf.loc[idx, 'feature_label']}\' {bf.loc[idx, 'sign']} {round(bf.loc[idx, 'hinge'],3)}, for every increase of {bf.loc[idx, 'increase_value']} unit(s), the {dv_description} {bf.loc[idx, 'direction']} by {np.round(np.abs(bf.loc[idx, 'marginal_effect']*100),2)} percentage points"

        elif bf.loc[idx, 'feature'] == 'Intercept':
            pass
        
        else:
            
            bf.loc[idx, 'interpretation'] = f"When \'{bf.loc[idx, 'feature_label']}\' increases by {bf.loc[idx, 'increase_value']} unit(s), the {dv_description} {bf.loc[idx, 'direction']} by {np.round(np.abs(bf.loc[idx, 'marginal_effect']*100),2)} percentage points"
            
            
    
    bf = bf[['feature', 'orig_feature', 'feature_label', 'coef', 'sign', 'hinge', 'increase_value', 'binary_flag', 'direction', 'marginal_effect', 'interpretation']]
    #display(bf)
        
    return bf


def prescriptions(model, input_df, scored_df, actionable_fields, dv_description, field_labels=None, returned_insights=5):

    import pandas as pd
    import numpy as np
    
    bf = pd.DataFrame(input_df.columns.tolist(), columns=['feature'])
    
    change_score = pd.DataFrame()
    
    #Determine Increase "jump" value to use for each feature
    for idx, v in enumerate(bf['feature']):
        
        range = input_df[bf.loc[idx, 'feature']].std() 
 
        #Determine Binary feature
        if input_df[bf.loc[idx, 'feature']].nunique() == 2:
            binary_flag = True

        else:
            binary_flag = False
            
        #Determine appropriate increase "jump" (.01/.1/1/10/100/1000)
        if binary_flag == True:
            increase_value = 1
            
        elif (range  < 1) & (input_df[v].dtype != np.int64):
            increase_value = 0.01
            
        elif (range  < 10) & (input_df[v].dtype != np.int64):
            increase_value = 0.1
            
        elif range <= 100:
            increase_value = 1
            
        elif range <= 1000:
            increase_value = 10
            
        elif range <= 10000:
            increase_value = 100
            
        else:
            increase_value = 1000
        
        #Calculate change for increasing actionable values by jump amount
        if v in actionable_fields.keys():
            
            input_increase = input_df.copy(deep=True)

            #Calculate positive jump effect
            if binary_flag is True:   
                input_increase[v] = 1

            else:
                input_increase[v] = input_increase[v] + increase_value
          
            input_change_prob= pd.DataFrame(model.predict_proba(input_increase), columns=['can_be_dropped', 'new_score'])
            input_change_prob['new_score'] = input_change_prob['new_score'].round(decimals=4)
            input_change_prob.drop(columns='can_be_dropped', inplace=True)
            input_change_prob.index = input_increase.index
            input_change_prob['feature'] = v
            input_change_prob['direction'] = 'Increasing'
            input_change_prob['increase_value'] = increase_value
            input_change_prob['type'] = 'actionable'
            input_change_prob['binary'] = binary_flag

            #Only include if field is an actionable direction
            if actionable_fields[v] != 'Decreasing':
                
                change_score = pd.concat([change_score, input_change_prob], axis = 0)
                
            del input_increase, input_change_prob
                
            #Calculate negative jump effect for those feaures that are at least 1 jump above zero
            
            input_decrease = input_df.copy(deep=True)
            
            if binary_flag is True: 
                input_decrease[v] = 0
            
            else:
                input_decrease[v] = np.where(input_decrease[v] <= (0 + increase_value), input_decrease[v], input_decrease[v] - increase_value) 

            input_change_prob= pd.DataFrame(model.predict_proba(input_decrease), columns=['can_be_dropped', 'new_score'])
            input_change_prob['new_score'] = input_change_prob['new_score'].round(decimals=4)
            input_change_prob.drop(columns='can_be_dropped', inplace=True)
            input_change_prob.index = input_decrease.index
            input_change_prob['feature'] = v
            input_change_prob['direction'] = 'Decreasing'
            input_change_prob['increase_value'] = increase_value
            input_change_prob['type'] = 'actionable'
            input_change_prob['binary'] = binary_flag

            #Only include if field is an actionable direction
            if actionable_fields[v] != 'Increasing':
                change_score = pd.concat([change_score, input_change_prob], axis = 0)
                
            del input_decrease, input_change_prob
        
        #For all non-actionable features, determine how the records value is contributing to its score
        #Score all scores when the feature is set to 0. Will compare it to the actual score after the join
        
        input_zero = input_df.copy(deep=True)

        feature_value = pd.DataFrame(input_zero[v].copy(deep=True))
        feature_value.rename(columns={v:"feature_value"}, inplace=True)
        input_zero[v] = 0
            
        input_change_prob= pd.DataFrame(model.predict_proba(input_zero), columns=['can_be_dropped', 'new_score'])
        input_change_prob['new_score'] = input_change_prob['new_score'].round(decimals=4)
        input_change_prob.drop(columns='can_be_dropped', inplace=True)
        input_change_prob.index = input_zero.index
        input_change_prob['feature'] = v
        input_change_prob['type'] = 'explainable'
        input_change_prob['binary'] = binary_flag
        
        input_change_prob = pd.concat([input_change_prob, feature_value], axis=1)

        change_score = pd.concat([change_score, input_change_prob], axis = 0)
            
        del input_zero, input_change_prob
            
    #display(change_score)
    #display(bf)

    #Join scored df to change df to calc effect change
    change_score = change_score.join(scored_df['score'], how='left')
    change_score['effect'] = np.where(change_score['type'] == 'actionable',
                                      change_score['new_score'] - change_score['score'],
                                      change_score['score'] - change_score['new_score'] 
                                     )
    
    change_score['effect_pct'] = np.where(change_score['score'] > 0,                        # if actionable and current score greater than zero
                                          change_score['effect'] / change_score['score'] ,  # then calculate percentage change
                                          1                                                 # else when type is actionable and current score is = 0 then return 1 (for 100% increase)
                                         )
    change_score['effect_pct'] = np.where((change_score['score'] == 0) & (change_score['new_score'] == 0),
                                          0,
                                          change_score['effect_pct']
                                         )
                                          
    
    #For actionable items, limit to just positive effects 
    change_score = change_score[(change_score['effect'] > 0.001) | (change_score['type'] != 'actionable')]
    
    #For Expainable items, determine directionality
    change_score['direction'] = np.where((change_score['type'] == 'explainable') & (change_score['effect'] < 0),
                                         'decreases',
                                         np.where((change_score['type'] == 'explainable') & (change_score['effect'] > 0),
                                                  'increases',
                                                  change_score['direction']
                                        ))
        
    #Calc abs of effect to be used for sorting
    change_score['effect_pct_abs'] = change_score['effect_pct'].abs()
    
    #Remove features with zero effect
    change_score = change_score[(change_score['effect_pct_abs'] > 0.005)]
        
    #Sort by index (asc), type (asc), absoulte value of effect (desc)
    change_score.sort_values(by=[change_score.index.name, 'type', 'effect_pct_abs'], axis=0, ascending=(True, True, False), inplace=True)
    
    #Add on Feature Labels
    #Add on Feature Labels
    if field_labels:
        change_score['feature_label'] = change_score['feature'].map(field_labels)
        change_score['feature_label'] = np.where(change_score['feature_label'].isna(), 
                                                 change_score['feature'],
                                                 change_score['feature_label']
                                                )
        
    else:
        change_score['feature_label'] = change_score['feature']
    
    
    #Add insight text
    #For Actionable Features
    #change_score['insight'] = np.where(change_score['binary'] == False,
    #                                   "Changing the value of \'"+change_score['feature_label']+"\' to "+np.where(change_score['direction']=='Increasing', '\'Yes\'', '\'No\'')+" will increase the score by "+round(change_score['effect']*100,1).astype(str)+" percentage points."
    #                                   ) 
    
    #Remove "by step_jump" and change "by percentag_point percentage points" to increase relative to current score
    change_score['insight'] = np.where(change_score['binary'] == False,
                                       change_score['direction']+" \'"+change_score['feature_label']+f"\' will increase {dv_description} by "+(change_score['effect_pct']*100).astype(int).astype(str)+"%.",
                                       "Changing the value of \'"+change_score['feature_label']+"\' to "+np.where(change_score['direction']=='Increasing', '\'Yes\'', '\'No\'')+f" will increase {dv_description} by "+(change_score['effect_pct']*100).astype(int).astype(str)+"%."
                                       )     
    
    #For Explainable (not-Actionable) Features
    change_score['insight'] = np.where(change_score['type'] == 'explainable',
                                       "'"+change_score['feature_label']+"\' = "+round(change_score['feature_value'],1).astype(str)+", which "+np.where(change_score['effect_pct'] > 1, 'greatly ', np.where(change_score['effect_pct'] < .1, 'somewhat ', ''))+change_score['direction']+f" {dv_description}.",
                                       change_score['insight']
                                       )
    
    #For Explainable (not-Actionable) Binary Features
    change_score['insight'] = np.where((change_score['type'] == 'explainable') & (change_score['binary'] == True),
                                       "'"+change_score['feature_label']+"\' = "+np.where(change_score['feature_value'] == 1, '\'Yes\'', '\'No\'')+", which "+np.where(change_score['effect_pct'] > 1, 'greatly ', np.where(change_score['effect_pct'] < .1, 'somewhat ', ''))+change_score['direction']+f" {dv_description}.",
                                       change_score['insight']
                                       )
    
    #Cleanup
    change_score = change_score[['feature', 'type', 'effect', 'effect_pct', 'insight']]   

    #limit to number of insights as defined by 'returned_insights'
    change_score = change_score.groupby(change_score.index.name).head(returned_insights)
    
    #Aggregate to index-level, collasping index to one line
    scores_w_insights = change_score.groupby([change_score.index.name])['insight'].apply(' '.join)
    #display(scores_w_insights)
        
    return scores_w_insights 