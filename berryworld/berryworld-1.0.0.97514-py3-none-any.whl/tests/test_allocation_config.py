import unittest
import pandas as pd
import warnings
from bwgds.berryworld.allocation_solver import AllocationSolver
from bwgds.berryworld.transportation_solver import TransportationAlgorithm

warnings.filterwarnings('ignore')


class TestAllocation(unittest.TestCase):
    """ Testing the implemented classes """

    def test_allocation_solver(self):
        production_df = pd.DataFrame({'Index_Prod': ['sup1', 'sup2'], 'Value': [1, 3]})
        sales_df = pd.DataFrame({'Index_Sales': ['cust1', 'cust2'], 'Value': [5, 1]})
        ranking_df = pd.DataFrame({
                                      'Index_Sales': ['cust1', 'cust2', 'cust1', 'cust2', 'cust1', 'cust2', '.STOCK',
                                                      '.STOCK', '.STOCK'],
                                      'Index_Prod': ['sup1', 'sup1', 'sup2', 'sup2', '.SHORTAGES', '.SHORTAGES', 'sup1',
                                                     'sup2', '.SHORTAGES'], 'Rank': [10, 2, 5, 1, 0, 0, 0, 0, -100]
                                      })
        production_df = production_df.append({'Index_Prod': '.SHORTAGES', 'Value': 0}, ignore_index=True)
        sales_df = sales_df.append({'Index_Sales': '.STOCK', 'Value': 0}, ignore_index=True)
        if production_df['Value'].sum() > sales_df['Value'].sum():
            sales_df.loc[sales_df['Index_Sales'] == '.STOCK', 'Value'] = production_df['Value'].sum() - sales_df[
                'Value'].sum()
        else:
            production_df.loc[production_df['Index_Prod'] == '.SHORTAGES', 'Value'] = sales_df['Value'].sum() - \
                                                                                      production_df['Value'].sum()
        alloc_solver = AllocationSolver(production_df, sales_df, ranking_df)
        results_alloc = alloc_solver.solver(rank_col='Rank', index_prod='Index_Prod', index_sales='Index_Sales',
                                            value_col='Value')
        results_df = pd.DataFrame({
            'Index_Sales': ['cust1', 'cust1', 'cust1', 'cust2'], 'Value': [1.0, 3.0, 1.0, 1.0],
            'Index_Prod': ['sup1', 'sup2', '.SHORTAGES', '.SHORTAGES'],
            'Shared': [1, 1, 1, 1], 'Rank': [10, 5, 0, 0]
            })
        pd.testing.assert_frame_equal(results_alloc, results_df)

    def test_transportation_solver(self):
        production_df = pd.DataFrame({'Index_Prod': ['sup1', 'sup2'], 'Value': [1, 3]})
        sales_df = pd.DataFrame({'Index_Sales': ['cust1', 'cust2'], 'Value': [5, 1]})
        ranking_df = pd.DataFrame({'Index_Sales': ['cust1', 'cust2', 'cust1', 'cust2', 'cust1',
                                                   'cust2', '.STOCK', '.STOCK', '.STOCK'],
                                   'Index_Prod': ['sup1', 'sup1', 'sup2', 'sup2', '.SHORTAGES',
                                                  '.SHORTAGES', 'sup1', 'sup2', '.SHORTAGES'],
                                   'Rank': [10, 2, 5, 1, 0, 0, 0, 0, -100]})
        production_df = production_df.append({'Index_Prod': '.SHORTAGES', 'Value': 0}, ignore_index=True)
        sales_df = sales_df.append({'Index_Sales': '.STOCK', 'Value': 0}, ignore_index=True)
        if production_df['Value'].sum() > sales_df['Value'].sum():
            sales_df.loc[sales_df['Index_Sales'] == '.STOCK', 'Value'] = production_df['Value'].sum() - sales_df[
                'Value'].sum()
        else:
            production_df.loc[production_df['Index_Prod'] == '.SHORTAGES', 'Value'] = sales_df['Value'].sum() - \
                                                                                      production_df['Value'].sum()
        alloc_solver = TransportationAlgorithm(production_df, sales_df, ranking_df, index_prod='Index_Prod',
                                               index_sales='Index_Sales')
        results_alloc, res_success, method = alloc_solver.solve_lp(rank_col='Rank', col_name='Value', display=False)
        results_alloc = results_alloc.loc[results_alloc['Value'] > 0.0001].reset_index(drop=True)
        results_df = pd.DataFrame({'Index_Sales': ['cust1', 'cust1', 'cust1', 'cust2'],
                                   'Index_Prod': ['.SHORTAGES', 'sup1', 'sup2', '.SHORTAGES'],
                                   'Rank': [0, 10, 5, 0], 'Value': [1.0, 1.0, 3.0, 1.0]})
        pd.testing.assert_frame_equal(results_alloc, results_df)


if __name__ == '__main__':
    TestAllocation().test_allocation_solver()
    TestAllocation().test_transportation_solver()
