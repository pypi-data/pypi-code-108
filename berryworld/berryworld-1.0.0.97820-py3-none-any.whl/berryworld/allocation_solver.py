import pandas as pd
import numpy as np


class AllocationSolver:
    """ Class to run a suboptimal solution for the Allocation by splitting evenly to customers when possible"""

    def __init__(self, production, sales, ranking):
        """ Initialize the class
        :param production: Production DataFrame
        :param sales: Sales DataFrame
        :param ranking: Ranking Matrix DataFrame
        """
        self.prod = production
        self.sales = sales
        self.ranking = ranking

    def solver(self, rank_col='Cij', index_prod='Index_Production', index_sales='Index_Sales', value_col='Tonnage', tol = 1e-4):
        """ Solving the Linear Problem Ax = b using the Simplex and the Interior-Point methods
        :param rank_col: Name of the column gathering the Ranking Values
        :param index_prod: Index of elements to use from the Production DataFrame
        :param index_sales: Index of elements to use from the Sales DataFrame
        :param value_col: Name of the column in Production and Sales containing the values to be allocated
        :param tol: Tolerance to apply to the distributed values
        :return: Result of the allocation in a DataFrame
        """

        # Production, Sales and Ranking will be mutable and they need to be allocated to a local variable
        production_df = self.prod.copy(deep=True)
        sales_df = self.sales.copy(deep=True)
        ranking_df = self.ranking.copy(deep=True)

        # Remove null Tonnages as they do not require allocation
        production_df = production_df.loc[production_df[value_col] > 0]
        sales_df = sales_df.loc[sales_df[value_col] > 0]
        ranking_df = ranking_df.loc[(ranking_df[index_prod].isin(production_df[index_prod])) & (
            ranking_df[index_sales].isin(sales_df[index_sales]))]

        shared_cols = [col for col in np.intersect1d(production_df.columns, sales_df.columns) if col != value_col]
        if len(shared_cols) == 0:
            production_df.loc[:, 'Shared'] = 1
            sales_df.loc[:, 'Shared'] = 1
            shared_cols = ['Shared']

        # Define some variables
        alloc_res = pd.DataFrame()
        features_cols = list(set(production_df.columns.tolist() + sales_df.columns.tolist()))
        features_cols = ['TonnageAllocated' if col == value_col else col for col in features_cols]

        # While Production and Sales have a shape greater than 0
        while (production_df.shape[0] > 1) & (sales_df.shape[0] > 1):
            # Find maximum Ranking Value
            max_rank_value = ranking_df[rank_col].max()
            max_matrix = ranking_df.loc[ranking_df[rank_col] == max_rank_value]

            # Get Production, Sales and their relationship associated with the maximum Ranking Value
            max_prod = production_df.loc[production_df[index_prod].isin(max_matrix[index_prod])]
            max_sales = sales_df.loc[sales_df[index_sales].isin(max_matrix[index_sales])]
            max_alloc = max_prod.merge(max_sales, on=shared_cols)

            # The one with less potential future Ranking Value will be used in the first instance
            ranking_df_gr = ranking_df.loc[(ranking_df[index_prod].isin(max_alloc[index_prod])) & (
                ranking_df[index_sales].isin(max_alloc[index_sales]))].sort_values(rank_col, ascending=False)[:5]
            weak_index = ranking_df_gr.groupby(index_prod, as_index=False).sum().sort_values(rank_col, ascending=False)[
                         -1:]

            # Get production element to be allocated
            max_prod = production_df.loc[production_df[index_prod].isin(weak_index[index_prod])]
            n_max_alloc = max_matrix.loc[
                (max_matrix[index_prod].isin(weak_index[index_prod])) & (max_matrix[rank_col] == max_rank_value)]
            max_sales = sales_df.loc[sales_df[index_sales].isin(n_max_alloc[index_sales])]

            # If Sales are bigger than Production
            if max_prod[value_col].sum() <= max_sales[value_col].sum():
                # Allocate all the tonnage from the production considered
                n_max_alloc = max_alloc.loc[
                    max_alloc[index_prod].isin(weak_index[index_prod]) & max_alloc[index_sales].isin(
                        max_sales[index_sales])]
                n_max_alloc['TonnageAllocated'] = 0

                # Split evenly amongst all the orders
                total_sales = n_max_alloc[value_col + '_y'].sum()
                n_max_alloc['Split'] = n_max_alloc[value_col + '_y'] / total_sales
                n_max_alloc['TonnageAllocated'] = n_max_alloc.loc[:, 'Split'] * max_prod.loc[
                    max_prod[index_prod].isin(n_max_alloc[index_prod]), value_col].values[0]

                # Update Orders and Supply based on allocated values
                n_max_alloc[value_col + '_y'] = n_max_alloc[value_col + '_y'] - n_max_alloc['TonnageAllocated']
                n_max_alloc[value_col + '_y'] = np.where(n_max_alloc[value_col + '_y'] > tol,
                                                         n_max_alloc[value_col + '_y'],
                                                         0)
                n_max_alloc[value_col + '_x'] = 0

            # If Production is bigger than Sales
            elif max_prod[value_col].sum() > max_sales[value_col].sum():
                # Allocate all the tonnages from the from the production considered
                n_max_alloc = max_alloc.loc[
                    max_alloc[index_prod].isin(weak_index[index_prod]) & max_alloc[index_sales].isin(
                        max_sales[index_sales])]
                n_max_alloc['TonnageAllocated'] = n_max_alloc[value_col + '_y']

                # Update Orders and Supply based on allocated values
                n_max_alloc[value_col + '_x'] = n_max_alloc[value_col + '_x'].values[0] - n_max_alloc[
                    'TonnageAllocated'].sum()
                n_max_alloc[value_col + '_x'] = np.where(n_max_alloc[value_col + '_x'] > tol,
                                                         n_max_alloc[value_col + '_x'],
                                                         0)
                n_max_alloc[value_col + '_y'] = 0

            # Update Production according to the allocated values
            new_prod = production_df.merge(n_max_alloc[[index_prod, value_col + '_x']].drop_duplicates(), how='left')
            production_df[value_col] = np.where(new_prod[value_col + '_x'].isnull(), new_prod[value_col],
                                                new_prod[value_col + '_x'])
            production_df = production_df.loc[production_df[value_col] != 0]

            # Update Sales according to the allocated values
            new_sales = sales_df.merge(n_max_alloc[[index_sales, value_col + '_y']], how='left')
            sales_df[value_col] = np.where(new_sales[value_col + '_y'].isnull(), new_sales[value_col],
                                           new_sales[value_col + '_y'])
            sales_df = sales_df.loc[sales_df[value_col] != 0]

            # Update Ranking Matrix according to the allocated values
            ranking_df = ranking_df.loc[(ranking_df[index_prod].isin(production_df[index_prod])) & (
                ranking_df[index_sales].isin(sales_df[index_sales]))]

            # Store Allocation results
            alloc_res = alloc_res.append(n_max_alloc[features_cols])

        # Allocate the remaining
        if production_df.shape[0] == 1:
            # Allocate everything to the latest available Supplier
            alloc_aux = production_df.merge(sales_df, on=shared_cols, how='left')
            alloc_aux.rename(columns={value_col + '_y': 'TonnageAllocated'}, inplace=True)
            alloc_aux.drop([value_col + '_x'], axis=1, inplace=True)
            alloc_res = alloc_res.append(alloc_aux)
        else:
            # Allocate everything to the latest available Customer
            alloc_aux = production_df.merge(sales_df, on=shared_cols, how='left')
            alloc_aux.rename(columns={value_col + '_x': 'TonnageAllocated'}, inplace=True)
            alloc_aux.drop([value_col + '_y'], axis=1, inplace=True)
            alloc_res = alloc_res.append(alloc_aux)

        alloc_res.rename(columns={'TonnageAllocated': value_col}, inplace=True)
        alloc_res = alloc_res.loc[alloc_res[value_col] > 0]

        return alloc_res.merge(self.ranking[[index_prod] + [index_sales] + [rank_col]],
                               on=[index_prod] + [index_sales], how='left')
