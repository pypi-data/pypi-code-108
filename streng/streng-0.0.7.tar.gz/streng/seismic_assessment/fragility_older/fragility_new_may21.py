import numpy as np
import pandas as pd
import h5py
import csv
from os import listdir
from os.path import isfile, join
# import seaborn as sns
# sns.set_style("whitegrid")

# martins&silva css files
martins_silva_css_path = r'D:\mypythons\jupyters\phd\FragilityCurvesCollection\Martins2020' + '\\'
martins_silva_css_fragility_avgsa = martins_silva_css_path + r'\fragility_curves\fragility_AvgSa' + '\\'
martins_silva_css_fragility_other = martins_silva_css_path + r'\fragility_curves\fragility_other_IMs' + '\\'
martins_silva_css_vulnerability_avgsa = martins_silva_css_path + r'\vulnerability_curves\vulnerability_AvgSa' + '\\'
martins_silva_css_vulnerability_other = martins_silva_css_path + r'\vulnerability_curves\vulnerability_other_IMs' + '\\'

# hdf5 collection
file_hdf5_collection = r'D:\my_db_h5_vault\fragility_curves\Frags_v03.h5'


class FragilityCurves:
    def __init__(self):
        
        # descriptions
        self.format = None               # e.g. 'discrete', 'lognormal'
        self.typology = None             # e.g. 'RC3.1LL'
        self.intensity_measure = None    # e.g. 'PGA', 'Sa03', 'AvgSa'
        self.units = None                # e.g. 'g'
        self.ds_descriptions = None      # e.g. ['slight', 'moderate', 'extensive', 'complete']
        
        # values
        self.thresholds = None           # e.g. np.array([0.001, 0.01, 0.1, 0.3, 0.6])
        self.centrals = None             # e.g. [0.05, 0.2, 0.6, 1.0]
        self.ims = None                  # np.array - intensity measure values
        self.probabilities = None        # np.array - probabilities for all intensity measure values
        
        # private
        self._dataframe = None       # dataframe with intensity measure and probability values
        
    @property
    def dataframe(self):
        return self._dataframe
        
    @classmethod
    def from_dataframe(cls, dataframe):
        fc = cls()
        fc._dataframe = dataframe
        fc.get_values_from_dataframe()
        return fc
        
    @classmethod    
    def from_martins_silva_2020_csv(cls, path, csv_filename):
        fc = cls()
        typology = csv_filename[0:len(csv_filename)-4]
                
        # Read .csv
        df = pd.read_csv(f'{path}{csv_filename}', index_col=0, sep=r",").T
        # changing index column to float
        df.index = df.index.astype(float)
        
        # get intensity measure
        intensity_measure = df.columns.name
        df.columns.name=None
        df.index.name = intensity_measure
        
        # get damge state names
        ds_names = list(df.columns)        
        
        fc._dataframe = df
        fc.get_values_from_dataframe()
        fc.typology = typology
        fc.intensity_measure = intensity_measure
        fc.format = 'discrete'
        fc.units = 'g'
        fc.ds_descriptions = ds_names
        fc.centrals = [0.05, 0.2, 0.6, 1.0]

        return fc          


    def to_hdf5_discrete(self, filename, group_path, dataset_name):
        with h5py.File(filename, "a") as hdf5_file:
            
            if not group_path in hdf5_file.keys():                          
                hdf5_group = hdf5_file.create_group(group_path)
            else:
                hdf5_group = hdf5_file[group_path]
    
    
#         f_df = f_df_temp.reset_index().rename(columns={'index': im}).astype({im: 'float64'})
#         f_df.axes[1].name = ''
      
        # Read column names and datatypes
#         df_col_name_types = list(zip(list(f_df.columns),list(f_df.dtypes)))
        # Convert data to a list of tuples, adding names and datatypes
            df_data = np.column_stack((self.ims, self.probabilities))
        
        
            dataset = hdf5_group.create_dataset(self.typology, data=df_data, data_columns=True, complib='zlib', complevel=9, index=False)
#             dataset = hdf5_group.create_dataset(self.typology, data=df_data, compression='gzip', compression_opts=9)

            dataset.attrs['typology'] = self.typology
            dataset.attrs['format'] = 'discrete' # or 'continuous'
            dataset.attrs['units'] = 'g'

      
        
        
    def get_values_from_dataframe(self):
        df = self._dataframe
        self.ims = df.index.to_numpy()
#         self.im_values = np.array(_df[self.intensity_measure])
        self.probabilities = df.to_numpy()
#         self.probabilities = df[df.columns[1:]].to_numpy()
        

    def draw_dataframe(self):    
        self._dataframe.plot(x=self.intensity_measure,
                             y=self.ds_descriptions,
                             figsize=(12, 8),
                             kind='line',
                             ylabel='Probability of Exceedance')

    def draw_more(self): 
        pgas04 = np.linspace(0.001, 3, 500)
        f, ax = plt.subplots(figsize=(12, 8))

#         for i, (m, st) in enumerate(list(zip(means, stddevs))):
#             dist = lognorm(s=st, scale=m)
#             ys = dist.cdf(pgas04)
#             ax.plot(pgas04, ys, lw=2, linestyle = '-', label=f"DS{i+1}")

        for i, ds in enumerate(self.ds_descriptions):
            ys = self.probabilities[:, i]
            ax.plot(self.ims, ys, lw=2, linestyle = '-', label=f"DS{i+1}")
        

        ax.set_title(self.typology, fontsize = 20)
        ax.set_ylabel('Probability of Exceedance', fontsize = 16)
        ax.set_xlabel(f'{self.intensity_measure} ({self.units})', fontsize = 16)
        ax.legend()
        ax.set_xlim(0.0, max(self.ims))
        ax.set_ylim(0.0, 1.0)
        return f

        
    def get_centrals_from_thresholds(self):
        _centrals = []
        _thresholds = self.thresholds.copy()
        _thresholds.append(1.0)
        for i in range(0, len(_thresholds) - 1):
            _centrals.append(0.5 * (_thresholds[i] + _thresholds[i + 1]))

        # Για το DS0 θεωρώ ότι ο κεντρικός δείκτης βλάβης είναι 0
        self.centrals = [0.0] + _centrals

#     def get_martins_silva(self, filename, typology):
#         self._dataframe = pd.read_hdf(filename, f'/MartinsSilva2020/fragility_other_IMs/{typology}')
#         self.im = self._dataframe.columns[0]
#         self.ds_descriptions = list(self._dataframe.columns[1:])
        
#         self.get_values_from_dataframe()

#         with h5py.File(filename, "r") as hdf5_file:
#             self.units = hdf5_file[f'/MartinsSilva2020/fragility_other_IMs/{typology}'].attrs['units']
#             self.typology = hdf5_file[f'/MartinsSilva2020/fragility_other_IMs/{typology}'].attrs['typology']
#             self.format = hdf5_file[f'/MartinsSilva2020/fragility_other_IMs/{typology}'].attrs['format']


f_df_temp = FragilityCurves.from_martins_silva_2020_csv(martins_silva_css_fragility_other, "CR_LDUAL-DUH_H3.csv")
print(f_df_temp.dataframe)

df_data = np.column_stack((f_df_temp.ims, f_df_temp.probabilities))
df_data.dtype=[('name', np.float16), ('ds1', np.float16), ('ds2', np.float16), ('ds3', np.float16), ('ds4', np.float16)]
print(df_data)

