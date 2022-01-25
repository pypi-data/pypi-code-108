import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, Dict, List
from ....common.math import numerical
from ....common.math.charts.linexy import LineXY


@dataclass
class DeriveProcedure:
    excel_filename: str
    excel_worksheet: str
    raw_data: pd.DataFrame = None
    base_records: np.ndarray = None
    pgas_unique: np.ndarray = None
    all_raw_curves: Dict = field(default_factory=dict)
    all_L_values: List = field(default_factory=dict)
    average_L_values: np.ndarray = None
    thresholds: np.ndarray = None

    pga_at_threshold_for_base_record: List = field(default_factory=dict)
    pga_at_threshold_for_damage_state: List = field(default_factory=dict)

    pga_for_thresholds: np.ndarray = None

    def __post_init__(self):
        self.raw_data = pd.read_excel(self.excel_filename, self.excel_worksheet)
        self.base_records = self.raw_data['base_record'].unique()
        self.pgas_unique = np.sort(self.raw_data['pga'].unique())



    def calc(self):
        self.all_raw_curves = {}
        self.all_L_values = []
        for rec_name in self.base_records:
            tmp_df = self.raw_data_for_single_base_record(rec_name)
            xyxhart = LineXY(x=np.array(tmp_df['pga'].tolist()),
                             y=np.array(tmp_df['loss_index'].tolist()),
                             name=rec_name)
            self.all_raw_curves[rec_name] = xyxhart
            self.all_L_values.append(xyxhart.y)

        self.average_L_values = np.average(self.all_L_values, axis=0)

        self.pga_for_thresholds = self.get_pga_for_thresholds(self.thresholds, self.average_L_values, self.pgas_unique)

        self.pga_at_threshold_for_base_record = []
        for i in self.all_L_values:
            self.pga_at_threshold_for_base_record.append(self.get_pga_for_thresholds(self.thresholds,
                                                                                     i,
                                                                                     self.pgas_unique))

        self.pga_at_threshold_for_damage_state = np.transpose(self.pga_at_threshold_for_base_record)


    @staticmethod
    def get_pga_for_thresholds(_thresholds, _L_values, _pgas):
        return np.interp(_thresholds, _L_values, _pgas)

    def raw_data_for_single_base_record(self, base_record):
        return self.raw_data[self.raw_data.base_record==base_record]
