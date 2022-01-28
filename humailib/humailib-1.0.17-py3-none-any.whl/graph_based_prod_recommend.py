import numpy as np
import pandas as pd
import datetime
import os
import math

import networkx as nx
from humailib.cloud_tools import GoogleCloudStorage

class HumaiGraphBasedRecommender:

    # Hyper-parameters
    also_bought_bias = 0.0
    also_bought_atten = 0.25
    node_weight_atten = 5.0

    def __init__(self):
        self.df_trans = None
        self.df_items = None
        self.G = None
        self.product_ranking = []
        self.custom_weights = {}
        self.cid_column = 'Customer_ID'
        self.product_column = 'Product_ID'

        self.product_ranking_weight = 1.0
        self.bought_together_weight = 1.0
        self.also_bought_weight = 1.0
        self.also_bought_bias = 1.0

    def init(self, df_trans, df_items, product_column = 'Product_ID', cid_column='Customer_ID'):

        self.df_trans = df_trans#.copy()
        self.df_items = df_items#.copy()
        
        # We assume the product column is an integer.
        self.product_column = product_column
        self.cid_column = cid_column

    def train(self, product_ranking_weight=1.0, bought_together_weight=1.0, also_bought_weight=1.0, verbose=False):

        self.product_ranking_weight = product_ranking_weight
        self.bought_together_weight = bought_together_weight
        self.also_bought_weight = also_bought_weight

        self.__calc_product_ranking(verbose)

        self.G = nx.Graph()

        # Add product nodes to the graph, with their popularity
        # rank as node weight.
        for product,rank,w in self.product_ranking:
            w = self.product_ranking_weight * (1.0 - np.exp(-self.node_weight_atten*w))
            #self.G.add_node( pname, {'prod_rank':rank, 'ranking_weight':w} ) # networkx version 1.x
            self.G.add_node( product, prod_rank=rank, ranking_weight=w )
            #if verbose:
            #    print("{0} - rank:{1}, weight:{2}".format(pname, rank, w))

        self.__generate_bought_together_edges(verbose)
        self.__generate_also_bought_edges(verbose)
        self.__calculate_final_proximity(verbose)

        print("Done learning!")
        
    def get_recommendations_product(self, products):
        rset = set()

        for product in products:
            ranked = self.__get_sorted_recommendations_rank(product)
            rset.update([tuple(x) for x in ranked])
        
        return [product for product,_ in sorted(list(rset), key=lambda x: -x[1])]

    def get_most_popular_products(self, n=5):
        
        products = []
        for p in self.product_ranking:
            
            pr = p[0]
            wt = p[2]
            if pr in self.custom_weights:
                
                wt = self.custom_weights[pr] * wt
                if wt > 0.0:
                    products.append(tuple[pr,wt])
                    
            else:    
                products.append(tuple([pr,wt]))
            
        return [p for p,_ in sorted(products, key=lambda x: -x[1])][:n]

    def __get_sorted_recommendations_rank(self, product):

        n_failed = 0
        candidates = []

        if self.G is not None:
            try:
                for neighbour in self.G.neighbors(product):

                    edge = self.G.edges[product,neighbour]
                    if neighbour not in self.custom_weights:
                        candidates.append( 
                            (neighbour, (1.0 - edge['final_proximity']))
                        )
                    elif self.custom_weights[neighbour] > 0.0:
                        # If custom weight for product [neighbour] is 0, it means
                        # [neighbour] is to be excluded from ever being recommended.
                        candidates.append( 
                            (neighbour, (1.0 - edge['final_proximity']) * self.custom_weights[neighbour])
                        )

                    #print("{0} -> {1}".format(neighbour, edge))
            except:
                print("[__get_sorted_recommendations_rank] fail on {}".format(product))
                n_failed = 1 + n_failed

        #print(candidates)

        sorted_candidates = sorted(candidates, key=lambda x: -x[1])
        return [[p,x] for p,x in sorted_candidates]

    def save(self, filename, gcs):

        if self.G is not None:
            if gcs is None:
                gcs = GoogleCloudStorage()
            
            # Save the graph
            gcs.pickle_and_upload([
                self.G,
                self.product_ranking,
                self.custom_weights,
                self.product_ranking_weight,
                self.bought_together_weight,
                self.also_bought_weight,
                self.cid_column,
                self.product_column
            ], filename)

    def load(self, filename, gcs):

        if gcs is None:
            gcs = GoogleCloudStorage()
            
        # For some reason, assigning straight to self.G, etc in here doesn't work
        # and results in self.G being NoneType. So we load into temp variables first.
        G, pr, cws, prw, btw, abw, cid_col, prod_col = gcs.download_and_unpickle(filename)
        print(type(G))
        
        self.G = G
        self.product_ranking = pr
        self.custom_weights = cws
        self.product_ranking_weight = prw
        self.bought_together_weight = btw
        self.also_bought_weight = abw
        self.cid_column = cid_col
        self.product_column = prod_col
        
        print(type(self.G))
        
    # Dictionary of key=product_ID, value=weight in interval: [0,1]
    def add_custom_weights(self, weights, zero_others=False):
        
        self.custom_weights = weights
        
        if zero_others:
            for p in self.product_ranking:
                if p[0] not in self.custom_weights:
                    self.custom_weights[ p[0] ] = 0.0
                    
    def reset_custom_weights(self):
        
        self.custom_weights = {}
        
    def __calculate_final_proximity(self, verbose):

        # Calculate final proximity value for each edge.
        # The lower this value, the more strongly the two connecting
        # nodes (products) are associated with each other.
        n_edges = len(self.G.edges())
        n = 0
        print("Calculating final proximity values (number of edges={:,})...".format(n_edges))
        # Generate final weights
        for product_1, product_2, data in self.G.edges(data=True):
            #print("{0} - {1}".format(product_1, product_2))
            #weight_1 = self.G.node[product_1]['ranking_weight'] # networkx version 1.x
            #weight_2 = self.G.node[product_2]['ranking_weight']
            weight_1 = self.G.nodes[product_1]['ranking_weight']
            weight_2 = self.G.nodes[product_2]['ranking_weight']
            #print("node weights: {0} - {1}".format(weight_1, weight_2))
            min_strength = 0.0001
            bias = 0.0
            #print(data)
            if data.get('bought_together') is not None:
                edge_strength = self.bought_together_weight * data['bought_together']
            elif data.get('also_bought') is not None:
                edge_strength = self.also_bought_weight * self.also_bought_atten * data['also_bought']
                bias = self.also_bought_weight * self.also_bought_bias

            proximity = (1.0 / (edge_strength + min_strength))*(1.0 - weight_1)*(1.0 - weight_2) + bias
            
            #self.G.edge[product_1][product_2]['final_proximity'] = proximity # networkx version 1.x
            self.G.edges[product_1,product_2]['final_proximity'] = proximity 
            
            if verbose:
                print("Proximity between ({},{}) = {:.4f}".format(product_1, product_2, proximity))

            n = 1 + n
            if n % 5000 == 0:
                print("{:,}/{:,}".format(n, n_edges))

    def __generate_also_bought_edges(self, verbose):

        dfg_customers = self.df_trans.groupby(by=self.cid_column)
        dfg_transactions = self.df_items.groupby('Transaction_ID')

        # Generate edges between product nodes that have been bought
        # by the same customer, but not necessarily together in the same transaction.
        N = self.df_trans[self.cid_column].nunique()
        n = 0
        transactions_missing = set()
        print("Generating 'also bought' edges (number of unique customers={:,})...".format(N))
        for _, transactions in dfg_customers:
            #num_trans = int( transactions['transaction_rank'].max() )
            num_trans = len(transactions)
            
            #print(N)
            if num_trans > 1:
                #print("Customer_ID: {0} (num_trans={1})".format(customer_id, num_trans))
                for i in range(num_trans-1):
                    
                    trans_id = transactions.iloc[i,:]['Transaction_ID']
                    
                    try:
                        products_1 = dfg_transactions.get_group(trans_id)[self.product_column].values
                        
                        #print("  {0}".format(itemsA))
                        for j in range(i+1, num_trans):
                            trans_id = transactions.iloc[j,:]['Transaction_ID']
                            
                            try:
                                products_2 = dfg_transactions.get_group(trans_id)[self.product_column].values
                                self.__add_edges(products_1, products_2)
                            except:
                                transactions_missing.add(trans_id)
                    except:
                        transactions_missing.add(trans_id)

            if verbose:            
                n = 1 + n
                if n % 5000 == 0:
                    print("{:,}/{:,}".format(n,N))

        num_transactions = self.df_trans['Transaction_ID'].nunique()

        print("num_transactions_lost: {0} out of {1} total ({2}%)".format(
            len(transactions_missing), num_transactions, 
            100.0*len(transactions_missing)/num_transactions))

    def __generate_bought_together_edges(self, verbose):

        dfg_trans = self.df_items.groupby(by=['Transaction_ID'])

        # Generate edges between product nodes that have been
        # bought together in the same transaction. With
        # "bought_together" weight being the number of times
        # they have shown up in the same basket, across all customers.
        n = 0
        N = self.df_items['Transaction_ID'].nunique()
        print("Generating 'bought together' edges (number of transactions = {:,})...".format(N))
        for _, items in dfg_trans:
            
            for i in range(0, len(items)-1):
                product_1 = items.iloc[i,:][self.product_column]
                for j in range(i+1, len(items)):
                    product_2 = items.iloc[j,:][self.product_column]
                    
                    if product_1 != product_2:
                        data = self.G.get_edge_data(product_1, product_2)
                        if data != None:
                            data['bought_together'] = 1 + data['bought_together']
                            #print("({0} - {1}) + 1 ({2})".format(itemA, itemB, G.edge[itemA][itemB]['same_transaction'])) 
                        else:
                            self.G.add_edge(product_1, product_2, bought_together=1)

            if verbose:
                n = 1 + n    
                if n % 5000 == 0:
                    print("{:,}/{:,}".format(n, N))   

    def __calc_product_ranking(self, verbose):

        if self.df_trans is None or self.df_items is None:
            raise Exception("Attempting to call __calc_product_ranking() when initWithData() has not been called.")

        N = len(self.df_items)
        n = 0

        print("Calculating product popularity ranking (number of line items={:,})...".format(N))

        # Calculate product popularity. 
        # For each product, calculate the number of times it has been purchased.
        products = {}
        for _, item in self.df_items.iterrows():
            #print(data.Item_Name)
            product = item[self.product_column]
            if product not in products:
                #print(key)
                products[product] = 1
            else:
                products[product] = 1 + products[product]

            if verbose:  
                n = 1 + n
                if n % 10000 == 0:
                    print("{:,}/{:,}".format(n,N))

        len(products.keys()) == self.df_items[self.product_column].nunique()

        popular_products = sorted(products.items(), key=lambda x: x[1])

        total_prod_n = len(popular_products)

        self.product_ranking = [
            (product, total_prod_n - rank, float(rank)/total_prod_n) for rank,(product,x) in zip(range(total_prod_n),popular_products)
        ]

    def __add_edges(self, products_1, products_2):

        for product_1 in products_1:
            for product_2 in products_2:

                if product_1 != product_2:
                    data = self.G.get_edge_data(product_1, product_2)
                    if data is not None:
                        data['also_bought'] = 1 + data['also_bought']
                        #print("({0} - {1}) + 1 ({2})".format(itemA, itemB, G.edge[itemA][itemB]['same_transaction']))
                    else:
                        self.G.add_edge(itemA, itemB, also_bought=1)
                        #print("({0} - {1})".format(itemA, itemB))
                        
    
def get_product_recommendations(pr, df, cid_column='Customer_ID', product_column='Product_ID', top_n=5, verbose=True):
        
    ii = 0
    nn = df[cid_column].nunique()
        
    dfg = df.groupby(by=[cid_column])
    recoms = []
    for cid, df in dfg:

        if ii % 500 == 0:
            print("{:,}/{:,} ({:.2f}%)".format(ii, nn, 100.0*ii/nn))

        recom = pr.get_recommendations_product(df[product_column].values)
        if len(recom) < top_n:
            recom = recom + ['']*(top_n - len(recom))

        recoms.append(tuple([cid] + recom[:top_n]))
        #print(recoms[-1])
                
        ii = 1 + ii

    columns = [cid_column] + ['product_{}'.format(i) for i in range(1, top_n+1)]
    df_recom = pd.DataFrame(recoms, columns=columns)

    return df_recom

    
def pad_product_recommendations(pr, df_r, df_products, product_column='Product_ID', method='popular'):
    
    df_r_out = df_r.copy()
    
    num_corrected = 0
    prod_recom_columns = []
    for col in df_r.columns:
        if 'product_' in col:
            prod_recom_columns.append(col)
            
    pad_products = []
    if method=='popular' or method is None:
        pad_products = pr.get_most_popular_products(n=len(prod_recom_columns)) 
    
    pids = {r:i for i,r in enumerate(df_products[product_column].values)}
        
    n = len(df_r)
    for i,row in df_r.iterrows():
    
        if i % 5000 == 0:
            print("{:,}/{:,} ({:.2f} %)".format(i, n, 100.0*i/n))

        j = 0
        #print(i)
        for col in prod_recom_columns:
            #print(row[col])
            if row[col] not in pids or row[col] == '':
                #print(pr.product_ranking[-j][0])
                df_r_out.at[i,col] = str(pad_products[j])
                j = 1 + j
                num_corrected = 1 + num_corrected

    print("Done.")
    
    return df_r_out