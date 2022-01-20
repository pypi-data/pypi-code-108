from ..logging_system import logger
from .data_transformation import DataTransformer

import os
import re
from copy import deepcopy
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

mpl.font_manager._rebuild()
plt.style.use('seaborn-whitegrid')

class ExploratoryDataAnalysis(DataTransformer):
    def __init__(self, frame, save=False, path='ExploratoryDataAnalysis', type_info=True, verbose:bool=True):
        self.frame = frame
        self.path = path
        self.results = dict()
        
        # classification column properties
        self.normal_columns = frame.isna().sum().to_frame().rename(columns={0:'NumMV'}).loc[lambda x: x.NumMV == 0].index.to_list()
        self.abnormal_columns = frame.isna().sum().to_frame().rename(columns={0:'NumMV'}).loc[lambda x: x.NumMV != 0].index.to_list()
        self.numerical_columns = list()
        self.categorical_columns = list()
        for column in frame.columns:
            if re.search('float|int', str(frame[column].dtype)):
                self.numerical_columns.append(column)
            else:
                self.categorical_columns.append(column)

        # for verbose option
        data = np.array([["eda.table_definition()", "view,"],
                         ["eda.attributes_specification()", "visual_on,"],
                         ["eda.cleaning()", "as_float,as_int,as_category,as_str,as_date,verbose,"],
                         ["eda.univariate_frequency()", "mode,view,"],
                         ["eda.univariate_percentile()", "mode,view,percent,visual_on,"],
                         ["eda.univariate_conditional_frequency()", "base_column,view"],
                         ["eda.univariate_conditional_percentile()", "base_column,view,mode,percent,depth,visual_on,"],
                         ["eda.frequency_visualization()", "base_column,column_sequence,"],
                         ["eda.information_value()", "target_column,target_event,verbose,visual_on,"],
                         ["eda.feature_importance()", ""]])
        if verbose:
            print('* Column Date Types')
            print(frame.dtypes)
            print('\n* EDA object method list')
            print(pd.DataFrame(data=data, columns=['Commands', 'Core Arguments']).set_index('Commands'))

        if save:
            self._excel()     

    def cleaning(self, priority_frame=None, save=False, path=None, saving_name=None, as_float:list=None, as_int:list=None, as_category:list=None, as_str:list=None, as_date:list=None, verbose:bool=False):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()

        """ Core """
        # base clearning 1
        table.columns = list(map(lambda x: x.strip(), table.columns))
        origin_columns = table.columns.to_list()
        valid_columns = list()
        self.null_columns = set()
        for column in origin_columns:
            # things all instance is null for numeric columns
            if table[column].dropna().shape[0]:
                valid_columns.append(column)
            else:
                self.null_columns.add(column)
            # things all instance is null for categorical columns
            if table[column][table[column]=='nan'].shape[0] == table.shape[0]:
                self.null_columns.add(column)
            else:
                valid_columns.append(column)
        self.null_columns = list(self.null_columns)
        self.not_null_columns = list(set(valid_columns))
        table = table[self.not_null_columns].copy()
        cleaning_failures = list()
        
        # base clearning 2
        for column in table.columns:
            if re.search('object', str(table[column].dtype)):
                table.loc[:, column] = table[column].astype(str).apply(lambda instance: instance.strip())
            elif re.search('float', str(table[column].dtype)):
                table.loc[:, column] = table[column].astype(float)
            elif re.search('int', str(table[column].dtype)):
                table.loc[:, column] = table[column].astype(int)
            elif re.search('category', str(table[column].dtype)):
                table.loc[:, column] = table[column].astype('category').apply(lambda instance: instance.strip())

        # all type-cleaning
        if as_int is all:
            for column in table.columns:
                try:
                    table.loc[:, column] = table[column].astype(int)
                except:
                    pass
            as_int = None
        if as_float is all:
            for column in table.columns:
                try:
                    table.loc[:, column] = table[column].astype(float)
                except:
                    pass
            as_float = None
        if as_category is all:
            for column in table.columns:
                table.loc[:, column] = table[column].astype('category')
            as_category = None
        if as_str is all:
            for column in table.columns:
                table.loc[:, column] = table[column].astype(str)
            as_str = None

        converting_failures = list()
        # to convert as float data-type
        if as_float is not None:
            if isinstance(as_float, str):
                as_float = list(as_float)
            for column in as_float:
                try:
                    table.loc[:, column] = table[column].astype(float)
                except:
                    converting_failures.append(column)
        # to convert as int data-type
        if as_int is not None:
            if isinstance(as_int, str):
                as_int = list(as_int)
            for column in as_int:
                try:
                    table.loc[:, column] = table[column].astype(int)
                except:
                    converting_failures.append(column)
        # to convert as category data-type
        if as_category is not None:
            if isinstance(as_category, str):
                as_category = list(as_category)
            for column in as_category:
                try:
                    table.loc[:, column] = table[column].astype('category')
                except:
                    converting_failures.append(column)
        # to convert as str data-type
        if as_str is not None:
            if isinstance(as_str, str):
                as_str = list(as_str)
            for column in as_str:
                try:
                    table.loc[:, column] = table[column].astype(str)
                except:
                    converting_failures.append(column)
        # to convert as datetime64 data-type
        if as_date is not None:
            if isinstance(as_date, str):
                as_date = list(as_date)
            for column in as_date:
                try:
                    table.loc[:, column] = pd.to_datetime(table[column].astype(str))
                except:
                    converting_failures.append(column)
        
        if cleaning_failures:
            print(f'Cleaning failure list about changing data-type: {cleaning_failures}')
        if converting_failures:
            print(f'Converting failure list about changing data-type: {converting_failures}')

        self.string_columns = set()
        self.float_columns = set()
        self.integer_columns = set()
        self.category_columns = set()
        for column in table.columns:
            if re.search('object', str(table[column].dtype)):
                self.string_columns.add(column)
            elif re.search('float', str(table[column].dtype)):
                self.float_columns.add(column)
            elif re.search('int', str(table[column].dtype)):
                self.integer_columns.add(column)
            elif re.search('category', str(table[column].dtype)):
                self.category_columns.add(column)
        self.string_columns = list(self.string_columns)
        self.float_columns = list(self.float_columns)
        self.integer_columns = list(self.integer_columns)
        self.category_columns = list(self.category_columns)
        """ Core """


        if priority_frame is None:
            self.frame = table

        if verbose:
            return self.attributes_specification(priority_frame=priority_frame, save=False, path=None, saving_name=None, visual_on=False)
        return table

    
    def _excel(self, priority_frame=None, save=False, path=None, saving_name=None):
        pass


    def table_definition(self, priority_frame=None, save=False, path=None, saving_name=None, view='summary'):
        if priority_frame is not None:
            table = priority_frame
        else:
            table = self.frame

        """ Core """
        base_columns = ['NumRows', 'NumColumns', 'NumNumericColumnType', 'NumCategoricalColumnType', ]
        lettertype_columns = table.columns[(table.dtypes == 'category') | (table.dtypes == 'object')]
        table_definition = pd.DataFrame(columns=base_columns)
        C = 0; N = 0
        for column in table.columns:
            ColumnType = 'Letter' if column in lettertype_columns else 'Number' 
            if ColumnType == 'Letter':
                C += 1
            else:
                N += 1
        a_row = pd.DataFrame(data=[[table.shape[0], table.shape[1], N, C]], columns=base_columns)
        table_definition = table_definition.append(a_row)
        """ Core """
        
        self.results['table_definition'] = table_definition
        saving_name = f'{saving_name}_EDA_TableDefinition.csv' if saving_name is not None else 'EDA_TableDefinition.csv'
        _csv_saving(table_definition, save, self.path, path, saving_name)
        return table_definition


    def plot(self, priority_frame=None):
        if priority_frame is not None:
            table = priority_frame
        else:
            table = self.frame

        self.string_columns = set()
        self.float_columns = set()
        self.integer_columns = set()
        self.category_columns = set()
        for column in table.columns:
            if re.search('object', str(table[column].dtype)):
                self.string_columns.add(column)
            elif re.search('float', str(table[column].dtype)):
                self.float_columns.add(column)
            elif re.search('int', str(table[column].dtype)):
                self.integer_columns.add(column)
            elif re.search('category', str(table[column].dtype)):
                self.category_columns.add(column)
        self.string_columns = list(self.string_columns)
        self.float_columns = list(self.float_columns)
        self.integer_columns = list(self.integer_columns)
        self.category_columns = list(self.category_columns)

        gridcols = 4
        num_columns = (table.shape[1])
        quotient = num_columns//gridcols
        reminder = num_columns%gridcols
        layout = (quotient, gridcols) if reminder==0 else (quotient+1, gridcols)
        fig = plt.figure(figsize=(25, layout[0]*5))
        axes = dict()
        for i in range(0, layout[0]):
            for j in range(0, layout[1]):
                idx = i*layout[1] + j
                axes[idx]= plt.subplot2grid(layout, (i, j))

        for idx, column in tqdm(enumerate(table[self.string_columns+self.category_columns].columns), total=table[self.string_columns+self.category_columns].columns.shape[0]):
            categorical_variable_frame = table[column].value_counts()
            axes[idx].bar(range(categorical_variable_frame.shape[0]), categorical_variable_frame.values)
            axes[idx].set_xticks(range(categorical_variable_frame.shape[0]))
            axes[idx].set_xticklabels(categorical_variable_frame.index.tolist(), rotation=20)
            axes[idx].set_title(column)

        _idx = idx
        for idx, column in tqdm(enumerate(table[self.integer_columns+self.float_columns].columns), total=table[self.integer_columns+self.float_columns].columns.shape[0]):
            idx = _idx + idx + 1
            axes[idx].hist(table[column].values, edgecolor='white')
            axes[idx].set_title(column)
        plt.tight_layout()



    def attributes_specification(self, priority_frame=None, save=False, path=None, saving_name=None, visual_on=False):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()

        """ Core """
        base_columns = ['Column', 'ColumnType', 'NumUniqueInstance', 'NumMV', 'DataType', 'DataExample', 'MaxInstanceLength']
        lettertype_columns = table.columns[(table.dtypes == 'category') | (table.dtypes == 'object')]
        attributes_matrix = pd.DataFrame(columns=base_columns)
        for column in table.columns:
            ColumnType = 'Letter' if column in lettertype_columns else 'Number' 
            NumUniqueInstance = table[column].value_counts().shape[0]
            MaxInstanceLength = table[column].astype('str').apply(lambda x: len(x)).max()
            NumMV = table[column].isna().sum()
            NumMV += table[column][table[column]=='nan'].shape[0]
            DataType = table[column].dtype.type
            a_row = pd.DataFrame(data=[[column, ColumnType, NumUniqueInstance, NumMV, DataType, table[column].iloc[np.random.randint(NumUniqueInstance)], MaxInstanceLength]], columns=base_columns)
            attributes_matrix = attributes_matrix.append(a_row)

        attributes_matrix.insert(2, 'NumRows', table.shape[0])
        attributes_matrix.insert(4, 'IdealSymmetricCount', table.shape[0]/attributes_matrix['NumUniqueInstance'])
        attributes_matrix.insert(5, 'IdealSymmericRatio', 1/attributes_matrix['NumUniqueInstance'])    
        attributes_matrix.insert(6, 'MVRate', attributes_matrix['NumMV']/table.shape[0])
        attributes_matrix = attributes_matrix.reset_index().drop('index', axis=1)

        self.normal_columns = attributes_matrix[attributes_matrix['MVRate'] == 0]['Column'].to_list()
        self.abnormal_columns = attributes_matrix[attributes_matrix['MVRate'] != 0]['Column'].to_list()
        self.numerical_columns = attributes_matrix[attributes_matrix['ColumnType'] == 'Number']['Column'].to_list()
        self.categorical_columns = attributes_matrix[attributes_matrix['ColumnType'] == 'Letter']['Column'].to_list()
        """ Core """
        
        self.results['attributes_specification'] = attributes_matrix
        saving_name = f'{saving_name}_EDA_AttributesSpecification.csv' if saving_name is not None else 'EDA_AttributesSpecification.csv'
        _csv_saving(attributes_matrix, save, self.path, path, saving_name)

        # Visualization
        if visual_on:
            temp_table = table.copy()
            temp_table_columns = temp_table.columns
            etc_rates = dict()
            for column in temp_table_columns:
                count_series = temp_table[column].value_counts()
                try:
                    temp_table.loc[:, column] = temp_table[column].astype(int)
                    count_series = temp_table[column].value_counts()
                    if count_series.shape[0] > 30:
                        high_freq_instances = count_series.index[:30].to_list()
                        temp_table.loc[:, column] = temp_table[column].apply(lambda x: x if x in high_freq_instances else np.nan)
                        etc_rates[column] = ('int', temp_table[column].isna().sum()/temp_table.shape[0])
                    else:
                        etc_rates[column] = ('int', 0)
                    

                except:
                    if count_series.shape[0] > 30:
                        high_freq_instances = count_series.index[:30].to_list()
                        if 'nan' in high_freq_instances:
                            del high_freq_instances[high_freq_instances.index('nan')]
                        temp_table.loc[:, column] = temp_table[column].apply(lambda x: x if (x in high_freq_instances) else '__ETC__')
                        etc_rates[column] = ('str', temp_table[temp_table[column]=='__ETC__'].shape[0]/temp_table.shape[0])
                    else:
                        temp_table.loc[:, column] = temp_table[column].apply(lambda x: x if x != 'nan' else '__ETC__')
                        etc_rates[column] = ('int', temp_table[temp_table[column]=='__ETC__'].shape[0]/temp_table.shape[0])
            
            gridcols = 3
            num_columns = (temp_table_columns.shape[0])
            quotient = num_columns//gridcols
            reminder = num_columns%gridcols
            layout = (quotient, gridcols) if reminder==0 else (quotient+1, gridcols)
            fig = plt.figure(figsize=(25, layout[0]*5))
            axes = dict()
            for i in range(0, layout[0]):
                for j in range(0, layout[1]):
                    idx = i*layout[1] + j
                    axes[idx]= plt.subplot2grid(layout, (i, j))
            for idx, column in tqdm(enumerate(temp_table_columns), total=temp_table_columns.shape[0]):
                num_unique = len(pd.unique(temp_table[column]))
                if etc_rates[column][0] == 'int':
                    #temp_table[column].dropna().hist(ax=axes[idx], bins=num_unique, xrot=30, edgecolor='white')
                    #temp_table[column].dropna().value_counts(ascending=True).plot.barh(ax=axes[idx], edgecolor='white')
                    data = temp_table[column].dropna().value_counts(ascending=False).to_frame().reset_index().rename(columns={'index':column, column:'count'})
                    #sns.barplot(data=data, x='count', y=column, ax=axes[idx], color='red', orient='h')
                else:
                    #temp_table[column][temp_table[column] != '__ETC__'].hist(ax=axes[idx], bins=num_unique, xrot=30, edgecolor='white')
                    #temp_table[column][(temp_table[column] != '__ETC__')].value_counts(ascending=True).plot.barh(ax=axes[idx], edgecolor='white')
                    data = temp_table[column][(temp_table[column] != '__ETC__')].value_counts(ascending=False).to_frame().reset_index().rename(columns={'index':column, column:'count'})
                try:
                    sns.barplot(data=data, x='count', y=column, ax=axes[idx], color='red', orient='h')
                except:
                    axes[idx].set_title(column+f'(CONSIDER OTHER DATATYPE)')
                #data.set_index(column)['count'].sort_values(ascending=True).plot.barh(ax=axes[idx], title=column, color='r', edgecolor='white')
                #sns.histplot(temp_table[column].dropna(), ax=axes[idx], edgecolor='white')
                etc_rate = etc_rates[column][1]
                sns.despine(left=True, bottom=True)
                axes[idx].set_title(column+f'(NOT SHOWING RATE : {etc_rate}%)')
            plt.savefig('EDA_ValueCounts.png')
            plt.tight_layout()
            self.results['value_counts_figure'] = fig
        return attributes_matrix

        
        

    def descriptive_statistics(self, priority_frame=None, save=False, path=None, saving_name=None):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()
        
        describing_matrix = table.describe().T
        saving_name = f'{saving_name}_EDA_DescriptiveStatistics.csv' if saving_name is not None else 'EDA_DescriptiveStatistics.csv'
        _csv_saving(describing_matrix, save, self.path, path, saving_name)

        return describing_matrix

    def univariate_frequency(self, priority_frame=None, save=False, path=None, saving_name=None, mode='base', view='summary'):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()
        
        """ Core """
        category_columns = table.columns[table.dtypes == 'category']
        for column in category_columns:
            table.loc[:, column] = table[column].astype(str)

        base_columns = ['Column', 'NumMV', 'Instance', 'NumUniqueInstance', 'Count', 'Rank']
        frequency_matrix = pd.DataFrame(columns=base_columns)
        for column in table.columns:
            instance_count = table.value_counts(column, ascending=False).to_frame()
            rank_mapper = instance_count.rank(ascending=False)
            instance_frequency = instance_count.sort_index(ascending=True).reset_index().rename(columns={column:'Instance', 0:'Count'})
            instance_frequency.insert(0, 'Column', column)
            instance_frequency.insert(2, 'NumMV', table[column].isna().sum())
            instance_frequency.insert(3, 'NumUniqueInstance', instance_count.shape[0] + int(bool(table[column].isna().sum())) if mode == 'missing' else instance_count.shape[0])
            instance_frequency.insert(5, 'Rank', instance_frequency.Instance.apply(lambda x: rank_mapper.loc[x]))
            frequency_matrix = frequency_matrix.append(instance_frequency)
        NumRows = table.shape[0]
        frequency_matrix.insert(1, 'NumRows', NumRows)
        frequency_matrix.insert(3, 'MVRate', frequency_matrix.NumMV/frequency_matrix.NumRows)
        frequency_matrix.insert(4, 'NumRows_EFMV', frequency_matrix.NumRows - frequency_matrix.NumMV)
        frequency_matrix.insert(7, 'IdealSymmetricCount', frequency_matrix.NumRows/frequency_matrix.NumUniqueInstance)
        frequency_matrix.insert(9, 'IdealSymmericRatio', 1/frequency_matrix.NumUniqueInstance)
        frequency_matrix.insert(10, 'Ratio', frequency_matrix.Count/frequency_matrix.NumRows)
        frequency_matrix.insert(11, 'InstanceImportance', frequency_matrix.Count/frequency_matrix.IdealSymmetricCount)

        for column in category_columns:
            table.loc[:, column] = table[column].astype('category')
        """ Core """
        
        self.results['univariate_frequency'] = frequency_matrix
        saving_name = f'{saving_name}_EDA_UnivariateFrequencyAnalysis.csv' if saving_name is not None else 'EDA_UnivariateFrequencyAnalysis.csv'
        _csv_saving(frequency_matrix, save, self.path, path, saving_name)

        if view == 'full':
            frequency_matrix = frequency_matrix
        elif view=='summary':
            frequency_matrix = frequency_matrix[['Column', 'Instance', 'Count', 'InstanceImportance', 'Rank']].sort_values(['Column', 'Rank'])
        return frequency_matrix


    def univariate_conditional_frequency(self, priority_frame=None, save=False, path=None, saving_name=None, base_column=None, view='summary'):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()

        """ Core """
        category_columns = table.columns[table.dtypes == 'category']
        for column in category_columns:
            table.loc[:, column] = table[column].astype(str)

        if base_column is not None:
            base = table.groupby([base_column])[base_column].count().to_frame()
            base.columns = pd.Index(map(lambda x : (x, 'Instance') ,base.columns))
            for idx, column in enumerate(table.columns):
                if column != base_column:
                    concatenation_frame = table.groupby([base_column, column])[base_column].count().to_frame().unstack(column)
                    multi_index_frame = concatenation_frame.columns.to_frame()
                    multi_index_frame[0] = concatenation_frame.columns.names[1]
                    concatenation_frame.columns = multi_index_frame.set_index([0, column]).index                
                    base = pd.concat([base, concatenation_frame], axis=1).fillna(0)
        else:
            for idx, column in enumerate(table.columns):
                if idx == 0:
                    base_column = column
                    base = table.groupby([base_column])[base_column].count().to_frame()
                    base.columns = pd.Index(map(lambda x : (x, 'Instance') ,base.columns))
                else:
                    concatenation_frame = table.groupby([base_column, column])[base_column].count().to_frame().unstack(column)
                    multi_index_frame = concatenation_frame.columns.to_frame()
                    multi_index_frame[0] = concatenation_frame.columns.names[1]
                    concatenation_frame.columns = multi_index_frame.set_index([0, column]).index                
                    base = pd.concat([base, concatenation_frame], axis=1).fillna(0)

        base = base.reset_index()            
        base.insert(0, 'Column', base_column)
        
        columnidx = base.columns.to_frame()
        columnidxframe = pd.DataFrame(columnidx.values)
        columnidxframe.iat[0,0] = 'BaseColumn'    
        columnidxframe.iat[1,0] = 'Column'
        columnidxframe.iat[1,1] = 'Instance'
        columnidxframe.iat[2,1] = 'InstanceCount'
        base.columns = columnidxframe.set_index([0,1]).index

        for column in category_columns:
            table.loc[:, column] = table[column].astype('category')
        """ Core """

        self.results['univariate_conditional_frequency'] = base
        saving_name = f'{saving_name}_EDA_UnivariateConditionalFrequencyAnalysis.csv' if saving_name is not None else 'EDA_UnivariateConditionalFrequencyAnalysis.csv'
        _csv_saving(base, save, self.path, path, saving_name)

        print(f'[AILEVER] base_column : {base_column}')
        print(f'[AILEVER] Column list : {table.columns.to_list()}')
        return base


    def univariate_percentile(self, priority_frame=None, save=False, path=None, saving_name=None, mode='base', view='summary', percent=5, visual_on=True):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()
        
        """ Core """
        # for Numeric Columns
        table = table[table.columns[(table.dtypes != 'object') & (table.dtypes != 'category')]]
        assert table.shape[1] >= 1, "This table doesn't even have a single numerical column. Change data-type of columns on table"
        
        percentile_range = list()
        percent_ = (percent/100); i = 0
        while True:
            i += 1
            cumulative_percent = round(percent_*i, 4)
            if cumulative_percent >= 1 :
                break
            percentile_range.append(cumulative_percent)
        
        self.percentiles = percentile_range
        describing_matrix = table.describe(percentiles=percentile_range).T
        describing_matrix.insert(3, 'DiffMaxMin', describing_matrix['max'] - describing_matrix['min'])
        describing_matrix.insert(4, 'Density', describing_matrix['count']/(describing_matrix['max'] - describing_matrix['min']))
        describing_matrix.insert(5, 'DiffMaxMin_PRU', (describing_matrix['max'] - describing_matrix['min'])/(len(percentile_range)+1))    
        percentile_columns = describing_matrix.columns[3:]
        
        base_columns = ['Column', 'NumRows', 'NumRows_EFMV', 'MVRate' , 'NumUniqueInstance', 'IdealSymmetricCount', 'IdealSymmetricRatio', 'Skew', 'Kurtosis']
        data = dict()
        data['Column'] = describing_matrix.index.to_list()
        data['NumRows'] = [table.shape[0]]*describing_matrix.shape[0]
        data['NumRows_EFMV'] = describing_matrix['count'].to_list()
        data['MVRate'] = ((table.shape[0] - describing_matrix['count'])/table.shape[0]).to_list()
        data['NumUniqueInstance'] = [table.value_counts(column, ascending=False).to_frame().shape[0] + int(bool(table[column].isna().sum())) if mode == 'missing' else table.value_counts(column, ascending=False).to_frame().shape[0] for column in describing_matrix.index ]
        data['IdealSymmetricCount'] = list(map(lambda x: table.shape[0]/x if x !=0 else np.nan, data['NumUniqueInstance'])) 
        data['IdealSymmetricRatio'] = list(map(lambda x: 1/x if x !=0 else np.nan, data['NumUniqueInstance']))
        data['Skew'] = table.skew().to_list()
        data['Kurtosis'] = table.kurtosis().to_list()
        percentile_base = pd.DataFrame(data=data, columns=base_columns) #percentile_matrix = pd.DataFrame(columns=describing_matrix.columns[4:-1])
        percentile_matrix = pd.concat([percentile_base, describing_matrix.reset_index().drop(['index', 'count'], axis=1)], axis=1)
        
        base_column_for_diff = 'min'
        percentile_matrix_for_diff = percentile_matrix.loc[:, 'min':'max']
        for column in percentile_matrix_for_diff.columns:
            percentile_matrix[base_column_for_diff+'-'+column] = percentile_matrix_for_diff[column] - percentile_matrix_for_diff[base_column_for_diff]
            base_column_for_diff = column 
        percentile_matrix.drop('min-min', axis=1, inplace=True)
        percentile_base_matrix = percentile_matrix.loc[:, f'{percent}%':'max']
        percentile_diff_matrix = percentile_matrix.loc[:, f'min-{percent}%':]
        percentile_matrix['HighDensityRange'] = percentile_diff_matrix.columns[percentile_diff_matrix.values.argmin(axis=1)]
        percentile_matrix['HighDensityInstance'] = list(map(lambda x: percentile_base_matrix.iloc[x[0], x[1]], zip(percentile_base_matrix.index, percentile_diff_matrix.values.argmin(axis=1))))
        percentile_matrix['HighDensityMinMaxRangeRatio'] = (percentile_matrix['HighDensityInstance'] - percentile_matrix['min'])/(percentile_matrix['max'] - percentile_matrix['min'])
        """ Core """
        
        self.results['univariate_percentile'] = percentile_matrix
        saving_name = f'{saving_name}_EDA_UnivariatePercentileAnalysis.csv' if saving_name is not None else 'EDA_UnivariatePercentileAnalysis.csv'
        _csv_saving(percentile_matrix, save, self.path, path, saving_name)
        

        if mode == 'base':
            percentile_matrix = percentile_matrix[percentile_matrix.columns.drop('NumRows')]
        elif mode == 'missing':
            percentile_matrix = percentile_matrix[percentile_matrix.columns.drop('NumRows_EFMV')]
        
        if visual_on:
            _, ax = plt.subplots(1, 1, figsize=(25, 5))
            minmax_percentile_matrix = percentile_matrix.copy().set_index('Column').loc[:, 'min':'max'].dropna()
            array = minmax_percentile_matrix.values
            array_diff = (array[:,-1][:, np.newaxis] - array[:,0][:, np.newaxis])
            index_0 = np.where(array_diff==0)[0]
            index_1 = np.where(array_diff==0)[1]
            for index in zip(index_0, index_1):
                i = index[0]
                j = index[1]
                array_diff[i, j] = np.inf
            minmax_percentile_matrix.loc[:,'min':'max'] = (array - array[:,0][:, np.newaxis])/array_diff
            sns.heatmap(minmax_percentile_matrix)

        if view == 'full':
            percentile_matrix = percentile_matrix
        elif view == 'p': # percentils
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, 'min':'max'], percentile_matrix.loc[:, 'HighDensityRange' : 'HighDensityMinMaxRangeRatio']], axis=1)
        elif view == 'ap':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, 'DiffMaxMin':'max'], percentile_matrix.loc[:, 'HighDensityRange': 'HighDensityMinMaxRangeRatio']], axis=1)
        elif view == 'dp':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, f'min-{percent}%':]], axis=1)
        elif view == 'adp':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:,'DiffMaxMin':'min'], percentile_matrix.loc[:,'max'], percentile_matrix.loc[:, f'min-{percent}%':]], axis=1)
        elif view == 'result':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, 'HighDensityRange': 'HighDensityMinMaxRangeRatio']], axis=1)
        elif view == 'summary':
            percentile_matrix = percentile_matrix[['Column', 'Density', 'HighDensityRange', 'HighDensityInstance', 'HighDensityMinMaxRangeRatio', 'min', 'max', 'mean', 'std', 'Skew', 'Kurtosis']+[ 'NumRows' if mode=='missing' else 'NumRows_EFMV']]
        return percentile_matrix


    def univariate_conditional_percentile(self, priority_frame=None, save=False, path=None, saving_name=None, base_column=None, view='summary', mode='base', percent=5, depth=10, visual_on=False):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()

        """ Core """
        percentile_range = list()
        percent_ = (percent/100); i = 0
        while True:
            i += 1
            cumulative_percent = round(percent_*i, 4)
            if cumulative_percent >= 1 :
                break
            percentile_range.append(cumulative_percent)
        self.percentiles = percentile_range

        # for Numeric&Categorical Columns
        numerical_table = table[table.columns[(table.dtypes != 'object') & (table.dtypes != 'category')]]
        categorical_table = table[table.columns[(table.dtypes == 'object') | (table.dtypes == 'category')]]
        assert numerical_table.shape[1] >= 1, "This table doesn't even have a single numerical column. Change data-type of columns on table"        
        assert categorical_table.shape[1] >= 1, "This table doesn't even have a single categorical column. Change data-type of columns on table"        
        if base_column is not None:
            assert base_column in numerical_table.columns, "base_column must be have numerical data-type."

        base_percentile_matrix = self.univariate_percentile(priority_frame=numerical_table, save=False, path=path, mode=mode, view='full', percent=percent, visual_on=False)
        percentile_matrix = pd.DataFrame(columns=base_percentile_matrix.columns.to_list() + ['CohenMeasure', 'CohenMeasureRank', 'ComparisonInstance', 'ComparisonColumn'])
        for numerical_column in base_percentile_matrix['Column']:
            if base_column is None:
                pass
            elif base_column != numerical_column:
                continue
            print(f'* Base Numeric Column : {numerical_column}')
            base_percentile_row = base_percentile_matrix.loc[lambda x: x.Column == numerical_column]
            base_percentile_row.insert(base_percentile_row.shape[1], 'CohenMeasure', 0)
            base_percentile_row.insert(base_percentile_row.shape[1], 'CohenMeasureRank', np.inf)
            base_percentile_row.insert(base_percentile_row.shape[1], 'ComparisonInstance', '-')
            base_percentile_row.insert(base_percentile_row.shape[1], 'ComparisonColumn', '-')
            for categorical_column in categorical_table.columns:
                base_row_frame = pd.DataFrame(columns=base_percentile_matrix.columns.to_list() + ['CohenMeasure', 'CohenMeasureRank', 'ComparisonInstance'])
                for categorical_instance  in categorical_table[categorical_column].value_counts().iloc[:depth].index:
                    appending_table = table.loc[lambda x: x[categorical_column] == categorical_instance]
                    appending_percentile_matrix = self.univariate_percentile(priority_frame=appending_table, save=False, path=path, mode=mode, view='full', percent=percent, visual_on=False)
                    appending_percentile_matrix.loc[:,'CohenMeasure'] = np.nan
                    appending_percentile_matrix.loc[:,'CohenMeasureRank'] = np.nan
                    appending_percentile_matrix.loc[:,'ComparisonInstance'] = categorical_instance
                    base_row_frame = base_row_frame.append(appending_percentile_matrix.loc[lambda x: x.Column == numerical_column])
                base_row_frame.loc[:,'ComparisonColumn'] = categorical_column
                base_percentile_row = base_percentile_row.append(base_row_frame)
            percentile_matrix = percentile_matrix.append(base_percentile_row)
            
            percentile_matrix_by_cloumn = percentile_matrix.loc[lambda x: x.Column==numerical_column]
            if percentile_matrix_by_cloumn.shape[0] <= 1:
                continue
            base_num = percentile_matrix_by_cloumn.iloc[0]['NumRows' if mode == 'missing' else 'NumRows_EFMV']
            base_mean = percentile_matrix_by_cloumn.iloc[0]['mean']
            base_std = percentile_matrix_by_cloumn.iloc[0]['std']
            
            num = percentile_matrix_by_cloumn['NumRows' if mode == 'missing' else 'NumRows_EFMV']
            mean = percentile_matrix_by_cloumn['mean']
            std = percentile_matrix_by_cloumn['std']
            m = base_mean - mean
            s = np.sqrt(((base_num-1)*base_std + (num-1)*std) / (base_num+num-2))  # the pooled standard deviation

            percentile_matrix.loc[lambda x: x['Column']==numerical_column, 'CohenMeasure'] = m/s
            percentile_matrix.loc[lambda x: x['Column']==numerical_column, 'CohenMeasureRank'] = abs(percentile_matrix.loc[lambda x: x['Column']==numerical_column, 'CohenMeasure']).rank(ascending=False)
        """ Core """

        self.results['univariate_conditional_percentile'] = percentile_matrix
        saving_name = f'{saving_name}_EDA_UnivariateConditionalPercentileAnalysis.csv' if saving_name is not None else 'EDA_UnivariateConditionalAnalysis.csv'
        _csv_saving(percentile_matrix, save, self.path, path, saving_name)

        if visual_on:
            _, ax = plt.subplots(1, 1, figsize=(25, 5))
            minmax_percentile_matrix = percentile_matrix.copy().set_index('ComparisonInstance').loc[:, 'min':'max'].dropna()
            array = minmax_percentile_matrix.values
            array_diff = (array[:,-1][:, np.newaxis] - array[:,0][:, np.newaxis])
            index_0 = np.where(array_diff==0)[0]
            index_1 = np.where(array_diff==0)[1]
            for index in zip(index_0, index_1):
                i = index[0]
                j = index[1]
                array_diff[i, j] = np.inf
            minmax_percentile_matrix.loc[:,'min':'max'] = (array - array[:,0][:, np.newaxis])/array_diff
            sns.heatmap(minmax_percentile_matrix)

        if view == 'full':
            percentile_matrix = percentile_matrix
        elif view == 'p': # percentils
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, 'min':'max'], percentile_matrix.loc[:, 'HighDensityRange' : 'ComparisonColumn']], axis=1)
        elif view == 'ap':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, 'DiffMaxMin':'max'], percentile_matrix.loc[:, 'HighDensityRange': 'ComparisonColumn']], axis=1)
        elif view == 'dp':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, f'min-{percent}%':], percentile_matrix.loc[:, 'ComparisonInstance':'ComparisonColumn']], axis=1)
        elif view == 'adp':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:,'DiffMaxMin':'min'], percentile_matrix.loc[:,'max'], percentile_matrix.loc[:, f'min-{percent}%':], percentile_matrix.loc[:, 'ComparisonInstance':'ComparisonColumn']], axis=1)
        elif view == 'result':
            percentile_matrix = pd.concat([percentile_matrix['Column'], percentile_matrix.loc[:, 'HighDensityRange': 'ComparisonColumn']], axis=1)
        elif view == 'summary':
            percentile_matrix = percentile_matrix[['Column', 'ComparisonColumn', 'ComparisonInstance', 'CohenMeasureRank', 'HighDensityRange', 'HighDensityInstance', 'HighDensityMinMaxRangeRatio', 'min', 'max', 'mean', 'std', 'Skew', 'Kurtosis']+[ 'NumRows' if mode=='missing' else 'NumRows_EFMV']].sort_values(['Column', 'ComparisonColumn', 'CohenMeasureRank'])

        return percentile_matrix


    def frequency_visualization(self, priority_frame=None, save=False, path=None, saving_name=None, base_column=None, column_sequence=None):
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()
        
        """ Core """
        assert base_column is not None, 'Set your base_column.'
        
        residual_column_sequence = table.columns.copy().to_list()
        del residual_column_sequence[residual_column_sequence.index(base_column)]
        
        if column_sequence is not None:
            seq_len = len(column_sequence)
            for column in column_sequence:
                del residual_column_sequence[residual_column_sequence.index(column)]
        else:
            seq_len = 0
            
        print('[AILEVER] The Rest Columns, Set the column_sequence of list-type \n', residual_column_sequence)
        if seq_len:
            _, axes = plt.subplots(seq_len+1, 1, figsize=(25, 5*(seq_len+1)))
            sns.heatmap(table.groupby([base_column]).agg('count'), ax=axes[0]).set_title('<base_column : '+base_column+f'> : {pd.unique(table[base_column])}')
            for idx in range(seq_len):
                local_seq = column_sequence[:idx+1]
                table_ = table.groupby([*local_seq, base_column])[base_column].agg('count')

                local_seq.reverse()
                for column in local_seq:
                    table_ = table_.unstack(column).fillna(0)
                    if idx == 0 : common_diff = table_.shape[1]

                sns.heatmap(table_, ax=axes[idx+1]).set_title(f'{column_sequence[idx]} : {pd.unique(table[column_sequence[idx]])[::-1]}')
                split_base = 1
                for column in local_seq:
                    for num_split in range(pd.unique(table[column]).shape[0]*split_base):
                        axes[idx+1].axvline(common_diff*(num_split+1), ls=':', c='yellow')
                        if num_split == pd.unique(table[column]).shape[0]-1:
                            split_base *= pd.unique(table[column]).shape[0]

                for column in pd.unique(table_.columns.to_frame().iloc[:,0]):
                    if idx >= 1:
                        axes[idx+1].axvline(table_.columns.get_loc(column).stop, c='red')

                            
        else:
            _, ax = plt.subplots(1, 1, figsize=(25, 5))
            sns.heatmap(table.groupby([base_column]).agg('count'), ax=ax).set_title('<base_column : '+base_column+f'> : {pd.unique(table[base_column])}')
            
        plt.tight_layout()
        """ Core """


    def correlation(self, priority_frame=None, save=False, path=None, saving_name=None):
        pass

    def information_values(self, priority_frame=None, save=False, path=None, saving_name=None, target_column=None, target_event=None, verbose:bool=True, visual_on=True):
        assert target_column is not None, 'Target Column must be defined. Set a target(target_column)  on columns of your table'
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()
        table['SELECTION_CRITERION'] = np.random.normal(0,1, size=table.shape[0])

        """ Core """
        all_columns = table.columns.to_list()
        del all_columns[all_columns.index(target_column)]
        columns_except_for_target = all_columns 
        for idx, column in enumerate(columns_except_for_target):
            if idx == 0:
                base_value_counts = table.value_counts(column, ascending=False).reset_index()
                base_value_counts.insert(0, 'Column', column)
                base_value_counts = base_value_counts.values
            else:
                value_counts = table.value_counts(column, ascending=False).reset_index()
                value_counts.insert(0, 'Column', column)
                value_counts = value_counts.values
                base_value_counts = np.r_[base_value_counts, value_counts]

        base = pd.DataFrame(data=base_value_counts, columns=['Column', 'Instance', 'Count'])
        base['Count'] = base['Count'].astype(int)
        base.insert(1, 'NumRows', table.shape[0])
        base.insert(base.shape[1], 'Ratio', base['Count']/base['NumRows'])

        logger['analysis'].info(f"Selected target column(target_column) : {target_column}")
        target_instances = pd.unique(table[target_column])
        if target_event is not None:
            event_table = table[table[target_column] == target_event]
            nonevent_table = table[table[target_column] != target_event]
            logger['analysis'].info(f'Selected target event(target_event) : {target_event}')
        else:
            event_table = table[table[target_column] == target_instances[0]]
            nonevent_table = table[table[target_column] != target_instances[0]]
            logger['analysis'].info(f'Selected target event(target_event) : {target_instances[0]}')

        if verbose:
            consider_cols = str(columns_except_for_target).strip('[]')
            consider_ints = str(target_instances).strip('[]')
            logger['analysis'].info(f'Considerable another target columns : {consider_cols}')
            logger['analysis'].info(f'Considerable another target events : {consider_ints}')
        base.insert(2, 'NumEventRows', event_table.shape[0])
        base.insert(3, 'NumNonEventRows', nonevent_table.shape[0])

        eventcount_mapper = dict()
        for column in columns_except_for_target:
            for instance in table.value_counts(column, ascending=False).index:
                conditional_event_table = event_table[event_table[column] == instance]
                eventcount_mapper[(column, instance)] = conditional_event_table.shape[0]
        base['EventCount'] = eventcount_mapper.values()
        base = base.assign(NonEventCount=lambda x: x.Count-x.EventCount)
        base = base.assign(EventRatio=lambda x: x.EventCount/x.NumEventRows)
        base = base.assign(NonEventRatio=lambda x: x.NonEventCount/x.NumNonEventRows)
        base = base.assign(AdjEventCount=lambda x: x.EventCount + 0.5)
        base = base.assign(AdjNonEventCount=lambda x: x.NonEventCount + 0.5)
        base = base.assign(AdjEventRate=lambda x: x.AdjEventCount/x.NumEventRows)
        base = base.assign(AdjNonEventRate=lambda x: x.AdjNonEventCount/x.NumNonEventRows)

        basetable_fordist = base[['Column', 'AdjEventRate', 'AdjNonEventRate']]
        event_sum = dict()
        nonevent_sum = dict()
        for column in pd.unique(basetable_fordist['Column']):
            conditional_basetable = basetable_fordist[basetable_fordist['Column'] == column]['AdjEventRate']
            event_sum[column] = conditional_basetable.sum()
            conditional_basetable = basetable_fordist[basetable_fordist['Column'] == column]['AdjNonEventRate']
            nonevent_sum[column] = conditional_basetable.sum()

        conditional_summation_table = base['Column']
        conditional_summation_table = pd.concat([conditional_summation_table, base.Column.apply(lambda x: event_sum[x]).rename('EventSum')], axis=1)
        conditional_summation_table = pd.concat([conditional_summation_table, base.Column.apply(lambda x: nonevent_sum[x]).rename('NonEventSum')], axis=1)
        conditional_summation_table

        base = base.assign(DistAdjEventRate=lambda x: x.AdjEventRate/conditional_summation_table.loc[x.Column.index]['EventSum'])
        base = base.assign(DistAdjNonEventRate=lambda x: x.AdjNonEventRate/conditional_summation_table.loc[x.Column.index]['NonEventSum'])
        base = base.assign(AdjEventWOE=lambda x: np.log(x.DistAdjEventRate/x.DistAdjNonEventRate))
        base = base.assign(AdjNonEventWOE=lambda x: np.log(x.DistAdjNonEventRate/x.DistAdjEventRate))
        base = base.assign(AdjEventInstanceIV=lambda x: (x.DistAdjEventRate - x.DistAdjNonEventRate) * x.AdjEventWOE)
        base = base.assign(AdjNonEventInstanceIV=lambda x: (x.DistAdjNonEventRate - x.DistAdjEventRate) * x.AdjNonEventWOE)

        base['InstanceIVRank'] = np.nan
        for column in pd.unique(base['Column']):
            base.loc[lambda df : df['Column']==column, 'InstanceIVRank'] = base[base['Column']==column].AdjEventInstanceIV.rank(ascending=False)
        

        nonevent_iv_avg = dict()
        base['EventIVSum'] = np.nan
        base['NonEventIVSum'] = np.nan
        base['EventIVAvg'] = np.nan
        base['NonEventIVAvg'] = np.nan
        for column in pd.unique(base['Column']):
            base.loc[lambda df: df['Column'] == column, 'EventIVSum'] = base[base['Column'] == column]['AdjEventInstanceIV'].sum()
            base.loc[lambda df: df['Column'] == column, 'NonEventIVSum'] = base[base['Column'] == column]['AdjNonEventInstanceIV'].sum()
            base.loc[lambda df: df['Column'] == column, 'EventIVAvg'] = base[base['Column'] == column]['AdjEventInstanceIV'].mean()
            base.loc[lambda df: df['Column'] == column, 'NonEventIVAvg'] = base[base['Column'] == column]['AdjNonEventInstanceIV'].mean()

        IVRank_mapper = base.drop_duplicates('Column', keep='first')[['Column', 'EventIVSum']]
        IVRank_mapper['IVSumRank'] = IVRank_mapper.EventIVSum.rank(ascending=False)
        IVRank_mapper = IVRank_mapper[['Column', 'IVSumRank']].set_index('Column').to_dict()['IVSumRank']
        base['IVSumRank'] = base.Column.apply(lambda x: IVRank_mapper[x])
        IVRank_mapper = base.drop_duplicates('Column', keep='first')[['Column', 'EventIVAvg']]
        IVRank_mapper['IVAvgRank'] = IVRank_mapper.EventIVAvg.rank(ascending=False)
        IVRank_mapper = IVRank_mapper[['Column', 'IVAvgRank']].set_index('Column').to_dict()['IVAvgRank']
        base['IVAvgRank'] = base.Column.apply(lambda x: IVRank_mapper[x])

        NumUnique_mapper = pd.Series([], dtype=int)
        for column in table.columns:
            NumUniqueInstance = table[column].value_counts().shape[0]
            NumUnique_mapper[column] = NumUniqueInstance
        base['NumUniqueInstance'] = base['Column'].apply(lambda x: NumUnique_mapper[x])

        self.results['information_values'] = base
        self.iv_summary = dict()
        self.iv_summary['result'] = base
        self.iv_summary['column'] = base[['NumRows', 'NumEventRows', 'Column', 'NumUniqueInstance', 'EventIVSum', 'EventIVAvg', 'IVSumRank', 'IVAvgRank']].drop_duplicates()
        self.iv_summary['column']['QuasiBVF'] = self.iv_summary['column']['EventIVSum']*self.iv_summary['column']['EventIVAvg'] # Quasi Bias-Variance Factor
        self.iv_summary['column']['IVQBVFRank'] = self.iv_summary['column']['QuasiBVF'].rank(ascending=False)
        self.iv_summary['column'] = self.iv_summary['column'].sort_values('IVSumRank')
        self.iv_summary['instance'] = base[['NumRows', 'Column', 'NumEventRows', 'Instance', 'Count', 'EventCount', 'AdjEventWOE', 'AdjEventInstanceIV', 'InstanceIVRank', 'IVSumRank', 'IVAvgRank']].sort_values(['InstanceIVRank', 'Column', 'IVSumRank'])
        """ Core """
        

        saving_name = f'{saving_name}_EDA_InformationValues.csv' if saving_name is not None else 'EDA_InformationValues.csv'
        _csv_saving(base, save, self.path, path, saving_name)
        iv_description = pd.DataFrame(data=['Not useful for prediction',
                                            'Weak predictive Power',
                                            'Medium predictive Power',
                                            'Strong predictive Power',
                                            'Suspicious Predictive Power'],
                                      index=['Less than 0.02',
                                             '0.02 to 0.1',
                                             '0.1 to 0.3',
                                             '0.3 to 0.5',
                                             '>0.5'],
                                      columns=['Variable Predictiveness'])
        iv_description.index.name = 'Information Value'
        print(iv_description)

        if visual_on:
            height = int(self.iv_summary['column'].shape[0]/5)
            height = int(7*3) if height < 7 else int(height*3)

            gridcols = 1
            gridrows = 3
            layout = (gridrows, gridcols)

            fig = plt.figure(figsize=(25, height))
            axes = dict()
            for i in range(0, layout[0]):
                for j in range(0, layout[1]):
                    idx = i*layout[1] + j
                    axes[idx]= plt.subplot2grid(layout, (i, j))
            self.iv_summary['column'].set_index('Column').EventIVSum.sort_values(ascending=True).plot.barh(ax=axes[0], title='EventIVSum')
            self.iv_summary['column'].set_index('Column').EventIVAvg.sort_values(ascending=True).plot.barh(ax=axes[1], title='EventIVAvg')
            self.iv_summary['column'].set_index('Column').QuasiBVF.sort_values(ascending=True).plot.barh(ax=axes[2], title='QuasiBVF')
            plt.tight_layout()
            plt.savefig('EDA_InformationValues.png')



    def feature_importance(self, priority_frame=None, save=False, path=None, saving_name=None, target_column=None, target_instance_covering=10, decimal=1, visual_on=True):
        assert target_column is not None, 'Target Column must be defined. Set a target(target_column)  on columns of your table'
        assert target_instance_covering > 1, 'When the target_instance_covering is 1, target/nontarget instances are not able to be classified.'
        if priority_frame is not None:
            table = priority_frame.copy()
        else:
            table = self.frame.copy()
        from sklearn.tree import DecisionTreeClassifier, export_graphviz
        import graphviz
        
        self.attributes_specification(priority_frame=priority_frame, save=False, path=None, saving_name=None, visual_on=False)
        valid_categorical_columns = list(filter(lambda x: (x in self.normal_columns) and (x != target_column), self.categorical_columns))
        valid_numerical_columns = list(filter(lambda x: (x in self.normal_columns) and (x != target_column), self.numerical_columns))
        
        explanation_columns = list()
        explanation_columns.extend(valid_categorical_columns)
        explanation_columns.extend(valid_numerical_columns)
        assert len(explanation_columns) != 0, 'Explainable columns are not exist in your frame. Check missing values.'
        
        # concatenation for non_target columns(categorical)
        fitting_table = table[[target_column]].copy()
        for vc_column in valid_categorical_columns:
            frequencies = table[vc_column].value_counts()
            probabilities = frequencies/frequencies.sum()
            fitting_table.loc[:, vc_column] = table[vc_column].apply(lambda x: round(probabilities[x], decimal))
        # concatenation for non_target columns(numerical)
        for vn_column in valid_numerical_columns:
            zscore_normalization = (table[vn_column] - table[vn_column].mean())/table[vn_column].std()
            fitting_table.loc[:, vn_column] = zscore_normalization.apply(lambda x: round(x, decimal))
        
        # first-order numericalizing target-column
        target_frequencies = fitting_table[target_column].value_counts()
        if not re.search('float|int', str(fitting_table[target_column].dtype)):
            target_probabilities = target_frequencies/target_frequencies.sum()
            fitting_table.loc[:, target_column] = fitting_table[target_column].apply(lambda x: round(target_probabilities[x], decimal))

        # target_instance_covering : padding target_instance being relative-low frequency
        target_frequencies = fitting_table[target_column].value_counts().sort_values(ascending=False)
        if target_frequencies.shape[0] > target_instance_covering:
            high_freq_instances = target_frequencies.index[:target_instance_covering-1].to_list()
            etc = min(map(lambda x: target_frequencies[x], high_freq_instances)) - 1
            fitting_table.loc[:, target_column] = fitting_table[target_column].apply(lambda x: x if x in high_freq_instances else etc)
            high_freq_instances.append(etc)
        else:
            high_freq_instances = target_frequencies.index.to_list()

        # second-order numericalizing target-column
        target_frame = pd.DataFrame(pd.unique(fitting_table[target_column])).reset_index().set_index(0).astype(int)
        target_mapper = pd.Series(data=target_frame['index'].to_list(), index=target_frame.index)
        fitting_table.loc[:, target_column] = fitting_table[target_column].apply(lambda x: target_mapper[x])

        X = fitting_table[explanation_columns].values
        y = fitting_table[target_column].values
        criterion = ['gini', 'entropy']
        model = DecisionTreeClassifier(criterion=criterion[0])
        model.fit(X, y)
        feature_importance = pd.DataFrame(data=model.feature_importances_[np.newaxis,:], columns=explanation_columns).T.rename(columns={0:'FeatureImportance'})
        feature_importance['Rank'] = feature_importance.rank(ascending=False)

        dot_data=export_graphviz(model,
                                 out_file=None,
                                 feature_names=explanation_columns,
                                 class_names=list(map(lambda x:str(x), target_mapper.index.to_list())),
                                 filled=True,
                                 rounded=True,
                                 special_characters=True)

        self.fi_summary = dict()
        self.fi_summary['fitting_table'] = fitting_table
        self.fi_summary['feature_importance'] = feature_importance.sort_values(by='Rank', ascending=True)
        self.fi_summary['decision_tree'] = graphviz.Source(dot_data)
        
        if visual_on:
            height = int(self.fi_summary['feature_importance'].shape[0]/5)
            height = int(7) if height < 7 else int(height)

            gridcols = 1
            gridrows = 1
            layout = (gridrows, gridcols)

            fig = plt.figure(figsize=(25, height))
            axes = dict()
            for i in range(0, layout[0]):
                for j in range(0, layout[1]):
                    idx = i*layout[1] + j
                    axes[idx]= plt.subplot2grid(layout, (i, j))

            #sns.barplot(data=feature_importance[['FeatureImportance']].sort_values(by='FeatureImportance', ascending=False).T, orient='h', color='red').set_title('Feature Importance')
            barplot_table = self.fi_summary['feature_importance']['FeatureImportance'].sort_values(ascending=True)
            barplot_table.index.name = 'Column' # X axis title
            barplot_table.plot.barh(figsize=(25,height), title='Feature Importance', color='red', ax=axes[0])
        return feature_importance.sort_values(by='Rank', ascending=True)

    def permutation_importance(self):
        pass




class Counting:
    def __init__(self, frame, path='ExploratoryDataAnalysis'):
        self.frame = frame
        self.path = path

    def CountUniqueValues(self, view='table', save=False, path=None):
        if view == 'table':
            data = list()
            for column in self.frame.columns:
                data.append([column, self.frame.value_counts(column).shape[0]])
            EDAframe = pd.DataFrame(data, columns=['Column', 'NumUniqueInstance'])
            _csv_saving(EDAframe, save, self.path, path, 'CountColumns.csv')

        elif view == 'column':
            EDAframe = pd.DataFrame(columns=['Column', 'Instance', 'Count'])
            for column in self.frame.columns:
                base = self.frame[column].value_counts().reset_index().rename(columns={'index':'Instance', column:'Count'})
                base.insert(0, 'Column', column)
                EDAframe = EDAframe.append(base)
            _csv_saving(EDAframe, save, self.path, path, 'CountInstances.csv')

        return EDAframe


def _cohen_d(data1, data2):
    u1, u2 = np.mean(data1), np.mean(data2)
    n1, n2 = len(data1), len(data2)
    s1, s2 = np.var(data1, ddof=1), np.var(data2, ddof=1)
    s = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))  # the pooled standard deviation
    return (u1 - u2) / s


def _csv_saving(frame, save, default_path, priority_path, name):
    if save:
        if not priority_path:
            if not os.path.isdir(default_path):
                os.mkdir(default_path)
            frame.to_csv(os.path.join(default_path, name))
            print(f'[AILEVER] The file {name} is saved at {default_path}.')

        else:
            if not os.path.isdir(priority_path):
                os.mkdir(priority_path)
            frame.to_csv(os.path.join(priority_path, name))
            print(f'[AILEVER] The file {name} is saved at {priority_path}.')

