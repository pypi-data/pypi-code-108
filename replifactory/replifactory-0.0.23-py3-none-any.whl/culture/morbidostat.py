from replifactory.culture.culture_functions import increase_stress_drug1
from replifactory.culture.turbidostat import TurbidostatCulture
import time
import numpy as np
import os
import threading


class CsvDataLogger:
    def __init__(self, directory, variable_name):
        self.lock = threading.Lock()
        header = "time,%s\n" % variable_name
        if not header.endswith("\n"):
            header = header+"\n"
        self.header = header
        self.filepath = os.path.join(directory, variable_name+".csv")
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w+") as f:
                f.write(header)

    def log_line(self, line):
        if not line.endswith("\n"):
            line = line+"\n"
        self.lock.acquire()
        try:
            with open(self.filepath, "a") as f:
                f.write(line)
        finally:
            self.lock.release()


class MorbidostatCulture(TurbidostatCulture):
    def __init__(self, directory: str = None, vial_number: int = None, name: str = "Species 1",
                 description: str = "Strain 1", default_dilution_volume: float = 10, dead_volume: float = 15,
                 od_max_limit: float = 0.3):
        self.t_doubling_max_limit = 24
        self.t_doubling_min_limit = 4
        self.delay_stress_increase_hrs = 4
        self.delay_rescue_dilution_hrs = 16
        self.default_dilution_volume = 10
        self.od_max_limit = 0.3

        # Running parameters
        self._last_stress_increase_time = None
        self._mu_max_measured = 0
        self._t_doubling_min_measured = np.inf
        super().__init__(directory=directory, vial_number=vial_number, name=name, description=description,
                         default_dilution_volume=default_dilution_volume, dead_volume=dead_volume,
                         od_max_limit=od_max_limit)

    def description_text(self):
        dilution_factor = (self.default_dilution_volume + self.dead_volume)/self.dead_volume
        generations_per_dilution = np.log2(dilution_factor)
        stress_increase_percent = (dilution_factor - 1)*50
        t = f"""
        When OD > {self.od_max_limit:.2f}, the {self.dead_volume:.1f}mL culture is diluted with {self.default_dilution_volume:.1f}mL total volume (every {generations_per_dilution:.2f} generations).
        While diluting the stress is increased by {stress_increase_percent :.1f}% and maintained for at least {self.delay_stress_increase_hrs:.1f}h if t_doubling <{self.t_doubling_min_limit:.1f}h.
        The stress is lowered by {stress_increase_percent:.1f}% with a rescue dilution if over the last {self.delay_rescue_dilution_hrs:.1f}h no dilutions were made and max(t_doubling)<{self.t_doubling_max_limit:.1f}h.
        """
        return t

    def update(self):
        """
        called every minute
        """
        if self.is_active():
            self.update_growth_rate()
            growing_too_fast = self.t_doubling < self.t_doubling_min_limit
            time_to_increase_stress = self.hrs_since_stress_increase > self.delay_stress_increase_hrs
            diluting_like_crazy = self.minutes_since_last_dilution < self.minimum_dilution_delay_hrs * 60

            if self.od > np.float32(self.od_max_limit):
                if not diluting_like_crazy:
                    if not growing_too_fast and time_to_increase_stress:
                        self.increase_stress()
                    else:
                        self.lower_od()
            else:
                self.rescue_if_necessary()

    @property
    def hrs_since_stress_increase(self):
        if not np.isfinite(np.float32(self._last_stress_increase_time)):
            return np.float32(time.time() - self._inoculation_time) / 3600
        else:
            return (time.time() - self._last_stress_increase_time) / 3600

    def rescue_if_necessary(self):
        hrs_inactive = self.minutes_since_last_dilution / 60
        if hrs_inactive > np.float32(self.delay_rescue_dilution_hrs):
            if self.t_doubling > np.float32(self.t_doubling_max_limit) or self.t_doubling < 0:
                self.decrease_stress()

    # def increase_stress(self, stress_increase_factor=None):
    #     dilution_factor = (self.dead_volume + self.default_dilution_volume) / self.dead_volume
    #     total_volume = self.dead_volume + self.default_dilution_volume
    #     if stress_increase_factor is None:
    #         stress_increase_factor = (dilution_factor + 1) / 2
    #     medium2_target_concentration = self.medium2_concentration * stress_increase_factor
    #     # medium3_target_concentration = None
    #
    #     drug1_total_amount = total_volume * medium2_target_concentration
    #     drug1_current_amount = self.dead_volume * self.medium2_concentration
    #     drug1_pumped_amount = drug1_total_amount - drug1_current_amount
    #     drug1_pumped_volume = drug1_pumped_amount / self.device.pump2.stock_concentration
    #     drug1_pumped_volume = round(drug1_pumped_volume, 3)
    #     drug1_pumped_volume = min(self.default_dilution_volume, max(0.1, drug1_pumped_volume))
    #     # drug2_pumped_volume = 0
    #     # if medium3_target_concentration:
    #     #     drug2_total_amount = total_volume * medium3_target_concentration
    #     #     drug2_current_amount = self.dead_volume * self.medium3_concentration
    #     #     drug2_pumped_amount = drug2_total_amount - drug2_current_amount
    #     #     drug2_pumped_volume = drug2_pumped_amount / self.device.pump3.stock_concentration
    #     #     drug2_pumped_volume = min(self.default_dilution_volume, max(0, drug2_pumped_volume))
    #
    #     drugfree_medium_volume = self.default_dilution_volume - drug1_pumped_volume   # - drug2_pumped_volume
    #     drugfree_medium_volume = min(self.default_dilution_volume, max(0, drugfree_medium_volume))
    #
    #     self.dilute(pump1_volume=drugfree_medium_volume,
    #                 pump2_volume=drug1_pumped_volume)
    #     self._last_stress_increase_time = int(time.time())



    def increase_stress(self, stress_increase_factor=None):
        increase_stress_drug1(culture=self, stress_increase_factor=stress_increase_factor)
        self._last_stress_increase_time = int(time.time())

    def decrease_stress(self):
        """
        makes standard dilution with no drug
        :return:
        """
        # dilution_factor = (self.dead_volume + self.default_dilution_volume) / self.dead_volume
        # stress_decrease_factor = dilution_factor
        self.dilute(pump1_volume=self.default_dilution_volume,
                    pump2_volume=0)

    def check(self):
        super().check()
        assert np.isfinite(self.t_doubling_min_limit)
        assert np.isfinite(self.t_doubling_max_limit)
        assert np.isfinite(self.delay_rescue_dilution_hrs)
        assert np.isfinite(self.delay_stress_increase_hrs)
        assert np.isfinite(self.device.pump_stock_concentrations[2])
        assert callable(self.device.pump2.calibration_function)

# class MorbidostatCulture(BasicCulture):
#     def __init__(self):
#         # User-assigned experiment parameters
#         self.t_doubling_max_limit = 24
#         self.t_doubling_min_limit = 4
#         self.delay_stress_increase_hrs = 4
#         self.delay_rescue_dilution_hrs = 16
#         self.default_dilution_volume = 10
#         self.od_max_limit = 0.3
#         # Running parameters
#         self.last_stress_increase_time = None
#         self.mu_max_measured = 0
#         self.t_doubling_min_measured = np.inf
#
#         super().__init__()
#
#     def show_parameters(self, increase_verbosity=False):
#         super().show_parameters(increase_verbosity=increase_verbosity)
#         if self.is_active() or increase_verbosity:
#             print("medium2_concentration:", self.medium2_concentration, "mM")
#             # print("medium 3 concentration", self.medium3_concentration)
#             print(" t_doubling_max_limit:", self.t_doubling_max_limit)
#             print(" t_doubling_min_limit:", self.t_doubling_min_limit)
#             print("stress increase delay: %.1f hours after last stress increase" % np.float32(self.delay_stress_increase_hrs))
#             print("         rescue delay: %.1f hours after last dilution" % np.float32(self.delay_rescue_dilution_hrs))
#             print()
#
#     # def update(self):
#     #     """
#     #     called every minute
#     #     """
#     #
#     #     if self.is_active():
#     #         growing_too_fast = self.t_doubling < self.t_doubling_min_limit
#     #         time_to_increase_stress = self.hrs_since_stress_increase > self.delay_stress_increase_hrs
#     #         diluting_like_crazy = self.minutes_since_last_dilution < self.minimum_dilution_delay_hrs * 60
#     #
#     #         if self.od_deblanked > np.float32(self.od_max_limit):
#     #             if not diluting_like_crazy:
#     #                 if growing_too_fast and time_to_increase_stress:
#     #                     self.increase_stress()
#     #                 else:
#     #                     self.lower_od()
#     #         else:
#     #             self.rescue_if_necessary()
#     #
#     # @property
#     # def hrs_since_stress_increase(self):
#     #     if not np.isfinite(np.float32(self.last_stress_increase_time)):
#     #         return np.float32(time.time() - self.inoculation_time) / 3600
#     #     else:
#     #         return (time.time() - self.last_stress_increase_time) / 3600
#     #
#     # def rescue_if_necessary(self):
#     #     hrs_inactive = self.minutes_since_last_dilution / 60
#     #     if hrs_inactive > np.float32(self.delay_rescue_dilution_hrs):
#     #         if self.t_doubling > np.float32(self.t_doubling_max_limit) or self.t_doubling < 0:
#     #             self.decrease_stress()
#     #
#     # def increase_stress(self, stress_increase_factor=None):
#     #     dilution_factor = (self.dead_volume + self.default_dilution_volume) / self.dead_volume
#     #     total_volume = self.dead_volume + self.default_dilution_volume
#     #     if stress_increase_factor is None:
#     #         stress_increase_factor = (dilution_factor + 1) / 2
#     #     medium2_target_concentration = self.medium2_concentration * stress_increase_factor
#     #     # medium3_target_concentration = None
#     #
#     #     drug1_total_amount = total_volume * medium2_target_concentration
#     #     drug1_current_amount = self.dead_volume * self.medium2_concentration
#     #     drug1_pumped_amount = drug1_total_amount - drug1_current_amount
#     #     drug1_pumped_volume = drug1_pumped_amount / self.device.pump2.stock_concentration
#     #     drug1_pumped_volume = round(drug1_pumped_volume, 3)
#     #     drug1_pumped_volume = min(self.default_dilution_volume, max(0.1, drug1_pumped_volume))
#     #     # drug2_pumped_volume = 0
#     #     # if medium3_target_concentration:
#     #     #     drug2_total_amount = total_volume * medium3_target_concentration
#     #     #     drug2_current_amount = self.dead_volume * self.medium3_concentration
#     #     #     drug2_pumped_amount = drug2_total_amount - drug2_current_amount
#     #     #     drug2_pumped_volume = drug2_pumped_amount / self.device.pump3.stock_concentration
#     #     #     drug2_pumped_volume = min(self.default_dilution_volume, max(0, drug2_pumped_volume))
#     #
#     #     drugfree_medium_volume = self.default_dilution_volume - drug1_pumped_volume   # - drug2_pumped_volume
#     #     drugfree_medium_volume = min(self.default_dilution_volume, max(0, drugfree_medium_volume))
#     #
#     #     self.dilute(pump1_volume=drugfree_medium_volume,
#     #                 pump2_volume=drug1_pumped_volume)
#     #     self.last_stress_increase_time = int(time.time())
#     #
#     # def lower_od(self):
#     #     """
#     #     makes a dilution, preserving the drug concentration in the vial
#     #     :return:
#     #     """
#     #     medium2_target_concentration = self.medium2_concentration
#     #     total_volume = self.dead_volume + self.default_dilution_volume
#     #
#     #     drug1_total_amount = total_volume * medium2_target_concentration
#     #     drug1_current_amount = self.dead_volume * self.medium2_concentration
#     #     drug1_pumped_amount = drug1_total_amount - drug1_current_amount
#     #     drug1_pumped_volume = drug1_pumped_amount / self.device.pump2.stock_concentration
#     #     drug1_pumped_volume = min(self.default_dilution_volume, max(0, drug1_pumped_volume))
#     #     if drug1_pumped_volume < 0.05:
#     #         drug1_pumped_volume = 0
#     #
#     #     drugfree_medium_volume = self.default_dilution_volume - drug1_pumped_volume  # - drug2_pumped_volume
#     #     drugfree_medium_volume = min(self.default_dilution_volume, max(0, drugfree_medium_volume))
#     #
#     #     self.dilute(pump1_volume=drugfree_medium_volume,
#     #                 pump2_volume=drug1_pumped_volume)
#     #
#     # def decrease_stress(self):
#     #     """
#     #     makes standard dilution with no drug
#     #     :return:
#     #     """
#     #     # dilution_factor = (self.dead_volume + self.default_dilution_volume) / self.dead_volume
#     #     # stress_decrease_factor = dilution_factor
#     #     self.dilute(pump1_volume=self.default_dilution_volume,
#     #                 pump2_volume=0)
#     #
#     # def check(self):
#     #     super().check()
#     #     assert np.isfinite(self.t_doubling_min_limit)
#     #     assert np.isfinite(self.t_doubling_max_limit)
#     #     assert np.isfinite(self.delay_rescue_dilution_hrs)
#     #     assert np.isfinite(self.delay_stress_increase_hrs)
#     #     assert np.isfinite(self.device.pump_stock_concentrations[2])
#     #     assert callable(self.device.pump2.calibration_function)
#
