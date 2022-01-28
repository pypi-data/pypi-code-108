import pandas as pd
import numpy as np
from scipy import stats
import datetime
import os
import math
import matplotlib.pyplot as plt 

from libraries.cloud_tools import loadDatasetToPandas
from libraries.hasher import XORHasher
from libraries.product_category_model import HumaiProdCategoryFeatureGen, HumaiProdCategoryModel
from libraries.proportional_hazards_model import HumaiPropHazardsFeatureGen, HumaiPropHazardsModel

import sklearn

class HumaiProductLaunchCustomerRanking:

    def __init__(self):
        return

    def getRanking(self, new_item_name, launch_date, 
                   model,       # item name to category model
                   model_feature_gen,
                   df_prod,     # item name and category table
                   df_cds_all,  # customer discount sensitivity table
                   df_cb_all,   # customer behaviour table
                   df_items,    # table of all items in all transactions
                   phm,         # prop haz model
                   ph_feature_gen,  # feature generator used for Prop Haz model
                   use_discount_sensitivity = False,
                   use_score_to_launch = True,
                   max_days_before_launch = 30,
                   max_days_after_launch = 0,
                   score_to_launch_max_days = 30,
                   cid_col = 'Customer_ID',
                   item_name_col = 'item_name',
                   category_col = 'category',
                   verbose = True):

        # Convert item names to upper-case
        #df_prod = df_prod[[item_name_col, category_col]]
        #df_prod.dropna(inplace=True)
        #df_prod.drop_duplicates(subset=[item_name_col], inplace=True)
        #df_prod[item_name_col] = df_prod[item_name_col].apply(lambda x: x.upper())
        
        # 1-gram product name vectoriser
        #feature_gen = HumaiProdCategoryFeatureGen()
        #feature_gen.init(df_prod, item_name=item_name_col, category=category_col)

        df_items[item_name_col] = df_items[item_name_col].apply(lambda x: x.upper())

        # vectorise the new item name
        new_item_vec = model_feature_gen.generate( [new_item_name] )[0]
        print(new_item_vec)

        # Get category prediction for new item
        category = model.predict(new_item_vec)
        if verbose:
            print("Category Prediction: {0}".format(category[0]))

        dfg_prod = df_prod.groupby(category_col)

        # Keep only those items that are in the predicted category, and rank them by
        # how similar they are to the new one in terms of vector distance.

        def similarityKey(elem):
            return elem[1]

        item_similarity_score = []
            
        for category_name, df_category in dfg_prod:
            if category == category_name:
                item_names = df_category[item_name_col].tolist()
                items_vec_matrix = model_feature_gen.generate( item_names )
                
                similarities = sklearn.metrics.pairwise.cosine_similarity(items_vec_matrix, 
                                                                        new_item_vec)
                
                item_similarity_score = [ (name,sim[0]) for (name,sim) in zip(item_names, similarities) ]
                item_similarity_score.sort(key=similarityKey)
                #print(item_names)
                
                item_similarity_score = dict(item_similarity_score)

        # Discard all behaviour that doesn't involve the predicted category
        dfg_cb_all = df_cb_all.groupby(category_col)
        df_cb = pd.DataFrame()

        for category_name, df_category in dfg_cb_all:
            if category == category_name:
                
                df_cb = df_category[[cid_col, 'Num_Items_Purchased', item_name_col, 'Datetime']]

        #df_cb.Datetime = pd.to_datetime(df_cb.Datetime, format='%Y-%m-%dT%H:%M:%S.000Z')

        df_cb.Item_Name = df_cb.Item_Name.apply(lambda name: name.upper())

        #df_items['Datetime'] = pd.to_datetime(df_items['Datetime'], format='%Y-%m-%dT%H:%M:%S.000Z')
        df_items[item_name_col] = df_items[item_name_col].apply(lambda x: x.upper())

        # Calculate first launch date for each item
        dfg_items = df_items.groupby(item_name_col)

        launch_dates = []
        for item_name, df_dates in dfg_items:
            #print('Item Name: {0}, first purchase date: {1}'.format(item_name, df_dates['Datetime'].min()))
            launch_dates.append( (item_name, df_dates['Datetime'].min()) )
            
        launch_dates = dict(launch_dates)

        # Create score_to_launch for customer product purchases: 
        # The closer to initial launch date for a given product, the higher the number (0,1]
        # 1/(days_between_purchase and product launch)

        def get_score_to_launch(row):
            return 1.0 / (1.0 + (row['Datetime'] - launch_dates[row[item_name_col]]).total_seconds() / (3600*24))

        if use_score_to_launch:
            df_cb['Score_To_Launch'] = df_cb.apply(get_score_to_launch, axis=1)
        else:
            df_cb['Score_To_Launch'] = 1.0

        if verbose:
            print(df_cb['Score_To_Launch'].describe())

        # Create item_similarity_score for customer product pucrhases.
        def get_item_similarity(row):
            return item_similarity_score.get(row[item_name_col], 0.0)

        df_cb['Item_Similarity_Score'] = df_cb.apply(get_item_similarity, axis=1)

        if verbose:
            print(df_cb['Item_Similarity_Score'].describe())

        if use_score_to_launch:
            score_to_launch_max_days = 30

            # Filter customers and items, based on score_to_launch cutoff.

            # This gets rid of customers that have never bought near the launch date,
            # as well as items that specific customers have never bought near a launch date.
            df_cb.drop( df_cb[df_cb['Score_To_Launch'] < 1.0/score_to_launch_max_days ].index, inplace=True )
            len(df_cb)

        def get_discount_sens(row):
            return df_cds_all[ df_cds_all[cid_col] == row[cid_col] ].iloc[0,:].Discount_Sensitivity

        if use_discount_sensitivity:
            df_cb['Discount_Sensitivity'] = df_cb.apply(get_discount_sens, axis=1)
        else:
            df_cb['Discount_Sensitivity'] = 100.0

        # For each row, calculate score:
        # (Total_Num_Items_Purchased for customer) * item_similarity_score * score_to_launch

        def calc_score(row):
            return row['Item_Similarity_Score'] * row['Score_To_Launch'] * row['Discount_Sensitivity']

        df_cb['Final_Score'] = df_cb.apply(calc_score, axis=1)

        if verbose:
            print(df_cb['Final_Score'].describe())

        # Get ranking, then get unique customers
        df_cb.sort_values(by=['Final_Score'], ascending=False, inplace=True)
        df_cb.drop_duplicates(subset=[cid_col], inplace=True)

        df_to_pred = ph_feature_gen.dataset.loc[ph_feature_gen.dataset[cid_col].isin(df_cb[cid_col])]

        # Predictions
        pred, dates = phm.predict(df_to_pred, 
                        features=None,
                        threshold=0.7)

        send_dates = pd.DataFrame()
        send_dates[cid_col] = df_to_pred[cid_col]
        send_dates['Datetime'] = dates

        if verbose:
            print(send_dates['Datetime'].head())

        date_col = 'Send_Mail_Datetime'
        df_cb[date_col] = launch_date
        # Set predicted send date for all customers for which we could predict it.
        # For all othe customers, set predicted send date to be the launch date.
        mask = df_cb[df_cb[cid_col].isin(send_dates[cid_col])].index
        df_cb.loc[mask,date_col] = pd.to_datetime(send_dates['Datetime'].values)

        if verbose:
            print(df_cb[date_col].head())

        earliest_mail_date = launch_date - datetime.timedelta(days=max_days_before_launch)
        latest_mail_date = launch_date + datetime.timedelta(days=max_days_after_launch)
        df_cb[date_col] = df_cb[date_col].apply(lambda x: min(latest_mail_date, earliest_mail_date if x <= earliest_mail_date else x) )

        df_cb = df_cb[['Email', 'Final_Score', 'Send_Mail_Datetime']]

        return df_cb


