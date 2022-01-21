import time
import os
import numpy as np
from replifactory.util import read_csv_tail
from replifactory.growth_rate import calculate_last_growth_rate
from replifactory.device.dilution import log_dilution
from replifactory.util import write_variable
from replifactory.culture.blank import BlankCulture
from replifactory.culture.culture_functions import inoculate


class TurbidostatCulture(BlankCulture):
    """
    Implements a quasi-turbidostat culture in a multi-vial device.
    A discrete dilution is made when the OD reaches the threshold,
    allowing the pumps to sequentially maintain all 7 vials.
    The growth is more similar to a real, continuous-dilution turbidostat
    when the dilution factor is small and dilutions are made more frequently.
    """
    minimum_dilution_delay_hrs = 0.1
    pumps = (1, 4)

    def __init__(self, directory: str = None, vial_number: int = None, name: str = "Species 1",
                 description: str = "Strain 1", default_dilution_volume: float = 10,
                 dead_volume: float = 15, od_max_limit: float = 0.3):
        # Configuration parameters
        self.default_dilution_volume = default_dilution_volume
        self.dead_volume = dead_volume
        self.od_max_limit = od_max_limit

        # Running parameters
        self._mu = None
        self._mu_error = None
        self._t_doubling = None
        self._t_doubling_error = None
        self._medium2_concentration = 0
        self._medium3_concentration = 0
        self._log2_dilution_coefficient = 0
        self._inoculation_time = None
        self._samples_collected = {}
        self._is_aborted = False
        self._mu_max_measured = 0
        self._t_doubling_min_measured = np.inf
        self._time_last_dilution = {1: None,
                                    2: None,
                                    3: None,
                                    4: None}
        super().__init__(directory=directory, vial_number=vial_number, name=name, description=description)

    def inoculate(self, name=None, description=None):
        inoculate(culture=self, name=name, description=description)
        self._mu_max_measured = 0
        self._t_doubling_min_measured = np.inf
        self._is_aborted = False
        self.save()

    def collect_sample(self, sample_id, sample_volume=1):
        # TODO preserve drug concentrations while sampling
        device = self.device
        vial = self.vial_number
        device.locks_vials[vial].acquire()
        device.lock_pumps.acquire()
        q = input("ready to collect %d ml sample? [y/n]" % sample_volume)
        if q == "y":
            assert not device.is_pumping()  # must have been checked before releasing the pump_number lock
            assert not device.hard_stop_trigger
            device.stirrers.set_speed(vial=vial, speed=1)
            device.valves.open(vial)  # valve number might be different for e.g. a lagoon setup
            device.pump1.pump(sample_volume)
            device.pump1.stock_volume -= sample_volume
            log_dilution(device=device, vial_number=vial, pump1_volume=sample_volume)
            while device.is_pumping():
                time.sleep(0.5)
            q = input("Is vial volume at vacuum needle level? [y/n]")
            if q != "y":
                vacuum_volume = sample_volume + 5
                device.pump4.pump(vacuum_volume)
                while device.is_pumping():
                    time.sleep(0.5)
                log_dilution(device=device, vial_number=vial, pump4_volume=vacuum_volume)
            self._samples_collected[time.time()] = sample_id
            device.stirrers.set_speed(vial=vial, speed=2)
            assert not device.is_pumping()  # make sure before closing valves
            time.sleep(1)
            device.valves.close(valve=vial)
        device.locks_vials[vial].release()
        device.lock_pumps.release()
        self.device.locks_vials[self.vial_number].acquire()
        self.device.lock_pumps.acquire()

    # def show_parameters(self, increase_verbosity=False):
    #     if self.is_active():
    #         active = "ACTIVE"
    #     else:
    #         active = "NOT ACTIVE"
    #     print("****** Vial %d:" % self.vial_number, active)
    #     if self.is_active() or increase_verbosity:
    #         print("             name:", self.name)
    #         print("      description:", self.description)
    #         print("               od:", np.round(self.od, 4))
    #         print("     od_max_limit:", self.od_max_limit)
    #         print("    last dilution:", np.round(time.time() - self.time_last_dilution, 1)/60, "minutes ago")
    #
    #         print("               mu:", np.round(self.mu, 5), "±", np.round(np.float32(self._mu_error), 5),
    #               "[1/h];     max:", self._mu_max_measured)
    #         print("       t_doubling:", np.round(self.t_doubling, 3), "±", np.round(np.float32(self._t_doubling_error), 3),
    #               "hrs;     min:", self._t_doubling_min_measured)
    #         print("    Generation nr:", self.log2_dilution_coefficient)
    #         if increase_verbosity:
    #             print()
    #             print("      dead_volume:", self.dead_volume)
    #             print("  dilution_volume:", self.default_dilution_volume)
    #             if self._inoculation_time:
    #                 print("       inoculated:", time.ctime(self._inoculation_time))
    #             else:
    #                 print("       inoculated: NO")
    #
    #             print("samples_collected:", self._samples_collected)
    #             print("       is_aborted:", self._is_aborted)
    #             print("         od_blank:", self._od_blank)
    #
    #             vial_volume = self.dead_volume
    #             added_volume = self.default_dilution_volume
    #             dilution_factor = (vial_volume + added_volume) / vial_volume
    #             generations_per_dilution = np.log2(dilution_factor)
    #             generations_per_ml = generations_per_dilution / added_volume
    #             print("generations/Liter: %.1f" % (generations_per_ml * 1000))
    #         print()

    @property
    def log2_dilution_coefficient(self):
        return np.float32(self._log2_dilution_coefficient)

    @log2_dilution_coefficient.setter
    def log2_dilution_coefficient(self, value):
        self._log2_dilution_coefficient = value
        write_variable(culture=self, variable_name="log2_dilution_coefficient", value=value)
        self.save()

    @property
    def mu(self):
        """
        growth rate [1/h]
        :return:
        """
        return np.float32(self._mu)

    @mu.setter
    def mu(self, value):
        mu, error = value
        write_variable(culture=self, variable_name="mu", value=mu)
        write_variable(culture=self, variable_name="mu_error", value=error)
        self._mu = mu
        self._mu_error = error
        if mu != 0:
            t_doubling = np.log(2) / mu
            t_doubling_error = t_doubling * error / mu
            self.t_doubling = (t_doubling, t_doubling_error)

            if mu > self._mu_max_measured and error / mu < 0.05:
                self._mu_max_measured = mu
                self._t_doubling_min_measured = t_doubling
        self.save()

    @property
    def t_doubling(self):
        return np.float32(self._t_doubling)

    @t_doubling.setter
    def t_doubling(self, value):
        t_doubling, t_doubling_error = value
        write_variable(culture=self, variable_name="t_doubling", value=t_doubling)
        write_variable(culture=self, variable_name="t_doubling_error", value=t_doubling_error)
        self._t_doubling = t_doubling
        self._t_doubling_error = t_doubling_error
        self.save()

    def update_growth_rate(self):
        """
        reads last od values and calculates growth rate
        :return:
        """
        od_filepath = os.path.join(self.directory, "od.csv")
        df = read_csv_tail(od_filepath, lines=300)
        df = df[df.index >= df.index[-1]-60*60*5]  # cut last 5 hours
        if np.isfinite(self.time_last_dilution):
            df = df[df.index > np.float32(self.time_last_dilution)]
        t = df.index.values
        od = df.values.ravel() - self.od_blank
        od[od <= 0] = 1e-6
        timepoint, mu, error = calculate_last_growth_rate(t, od)
        if np.isfinite(mu):
            self.mu = (mu, error)

    @property
    def time_last_dilution(self):
        pump_dilution_times = np.array(list(self._time_last_dilution.values())).astype(float)
        most_recent_dilution_time = np.nanmax(pump_dilution_times)
        return np.float32(most_recent_dilution_time)

    @property
    def medium2_concentration(self):
        return np.float32(self._medium2_concentration)

    @medium2_concentration.setter
    def medium2_concentration(self, value):
        self._medium2_concentration = value
        write_variable(culture=self, variable_name="medium2_concentration", value=value)
        self.save()

    @property
    def medium3_concentration(self):
        return np.float32(self._medium3_concentration)

    @medium3_concentration.setter
    def medium3_concentration(self, value):
        self._medium3_concentration = value
        write_variable(culture=self, variable_name="medium3_concentration", value=value)
        self.save()

    @property
    def minutes_since_last_dilution(self):
        if not np.isfinite(self.time_last_dilution):
            seconds_since_last_dilution = time.time() - self._inoculation_time
        else:
            seconds_since_last_dilution = time.time() - self.time_last_dilution
        return np.float32(seconds_since_last_dilution/60)

    def update(self):
        """
        called every minute
        """
        if self.is_active():
            diluting_like_crazy = self.minutes_since_last_dilution < self.minimum_dilution_delay_hrs * 60
            if self.od > np.float32(self.od_max_limit):
                if not diluting_like_crazy:
                    self.lower_od()

    def lower_od(self):
        """
        makes a dilution, preserving the drug concentration in the vial
        :return:
        """
        medium2_target_concentration = self.medium2_concentration
        total_volume = self.dead_volume + self.default_dilution_volume

        drug1_total_amount = total_volume * medium2_target_concentration
        drug1_current_amount = self.dead_volume * self.medium2_concentration
        drug1_pumped_amount = drug1_total_amount - drug1_current_amount
        drug1_pumped_volume = drug1_pumped_amount / self.device.pump2.stock_concentration
        drug1_pumped_volume = min(self.default_dilution_volume, max(0, drug1_pumped_volume))
        if drug1_pumped_volume < 0.05:
            drug1_pumped_volume = 0

        drugfree_medium_volume = self.default_dilution_volume - drug1_pumped_volume  # - drug2_pumped_volume
        drugfree_medium_volume = min(self.default_dilution_volume, max(0, drugfree_medium_volume))

        self.dilute(pump1_volume=drugfree_medium_volume,
                    pump2_volume=drug1_pumped_volume)

    def dilute(self, pump1_volume=0.0, pump2_volume=0.0, pump3_volume=0.0, extra_vacuum=5):
        """
        pump_number the given volumes into the vial,
        pump_number the total volume + extra_vacuum out of the vial
        extra_vacuum has to be ~>3 to fill the waste tubing with air and prevent cross-contamination.
        """
        if pump2_volume > 0:
            assert self.medium2_concentration >= 0
            assert self.device.pump2.stock_concentration >= 0
        if pump3_volume > 0:
            assert self.medium3_concentration >= 0
            assert self.device.pump3.stock_concentration >= 0
        self.device.make_dilution(vial=self.vial_number,
                                  pump1_volume=pump1_volume,
                                  pump2_volume=pump2_volume,
                                  pump3_volume=pump3_volume,
                                  extra_vacuum=extra_vacuum)
        self.calculate_culture_concentrations_after_dilution(pump1_volume, pump2_volume, pump3_volume)

    # def do_blank_od(self):
    #     self.od_blank = read_csv_tail(os.path.join(self.directory, "od.csv"), 10).values.mean()


    def calculate_culture_concentrations_after_dilution(self, pump1_volume, pump2_volume, pump3_volume):
        """
        pump1_volume: Drug-free medium
        pump2_volume: Drug 1
        pump3_volume: Drug 2
        """

        dilution_volume = sum([pump1_volume, pump2_volume, pump3_volume])
        total_volume = self.dead_volume + dilution_volume
        dilution_coefficient = total_volume / self.dead_volume
        self.log2_dilution_coefficient = self.log2_dilution_coefficient + np.log2(dilution_coefficient)

        if pump2_volume > 0 or self.medium2_concentration > 0:
            medium2_pumped_amount = self.device.pump2.stock_concentration * pump2_volume
            medium2_vial_amount = self.dead_volume * self.medium2_concentration
            medium2_total_amount = medium2_vial_amount + medium2_pumped_amount
            self.medium2_concentration = medium2_total_amount / total_volume

        if pump3_volume > 0 or self.medium3_concentration > 0:
            medium3_pumped_amount = self.device.pump3.stock_concentration * pump3_volume
            medium3_vial_amount = self.dead_volume * self.medium3_concentration
            medium3_total_amount = medium3_vial_amount + medium3_pumped_amount
            self.medium3_concentration = medium3_total_amount / total_volume
        self.save()

    def check(self):
        assert self.device.is_connected()
        assert self.vial_number in [1, 2, 3, 4, 5, 6, 7]
        assert os.path.exists(self.directory)
        assert 0 < self.dead_volume <= 35
        assert 0 < self.default_dilution_volume <= 40-self.dead_volume
        # assert 0 < self.od_max_limit <= 50
        assert callable(self.device.od_sensors[self.vial_number].calibration_function)
        assert callable(self.device.pump1.calibration_function)
        assert callable(self.device.pump4.calibration_function)
        assert -0.3 < self.od_blank < 0.3
        self.device.stirrers.check_calibration(self.vial_number)

    @property
    def experiment_start_time(self):
        filepath = os.path.join(self.directory, "od.csv")
        if not os.path.exists(filepath):
            return np.nan
        with open(filepath) as f:
            time_first_od = np.float32(f.readlines(512)[1].split(",")[0])
        return np.float32(time_first_od)

    def flush_tubing_if_necessary(self):
        if not self._is_aborted:
            pump_volumes = {1: 0, 2: 0}
            tstart = self.experiment_start_time
            tinoc = np.float32(self._inoculation_time)
            for pump_number in self.pumps:
                tdil = np.float32(self._time_last_dilution[pump_number])
                last_pump_time = np.nanmax([tdil, tstart, tinoc])
                if (time.time() - last_pump_time) > self.device.delay_tube_wash_hrs * 3600:
                    pump_volumes[pump_number] = 0.1
            if pump_volumes[1] > 0 or pump_volumes[2] > 0:
                self.dilute(pump1_volume=pump_volumes[1], pump2_volume=pump_volumes[2], pump3_volume=0)


# class BasicCulture:
#     minimum_dilution_delay_hrs = 0.1
#
#     def __init__(self):
#         # self.experiment_directory = None
#         self.vial_number = None
#         # self.vial_directory = None
#         self.directory = None
#         self._device = None
#         self.file_lock = threading.Lock()
#
#         # Variables logged to csv files
#         self._od = None
#         self._mu = None
#         self._mu_error = None
#         self._t_doubling = None
#         self._t_doubling_error = None
#         self._medium2_concentration = 0
#         self._medium3_concentration = 0
#         self._log2_dilution_coefficient = 0
#
#         # User-assigned experiment parameters
#         self.name = "Culture"
#         self.description = "culture initialized on " + time.ctime()
#         self.od_blank = 0
#         self.dead_volume = 15  # volume below vacuum needle
#
#         self.inoculation_time = None
#         self.samples_collected = {}
#         self.is_aborted = False
#
#         # Running parameters
#         self.mu_max_measured = 0
#         self.t_doubling_min_measured = np.inf
#         self.last_dilution_time = {1: None,
#                                    2: None,
#                                    3: None,
#                                    4: None}
#
#         # if vial_number is not None:
#         #     assert experiment_directory is not None
#         #     assert os.path.exists(experiment_directory)
#         # if experiment_directory is not None:
#         #     assert 1 <= vial_number <= 7
#         #     assert not experiment_directory[:-1].endswith("vial_")
#         #     assert os.path.exists(experiment_directory)
#         #     self.vial_directory = os.path.join(experiment_directory, "vial_%d" % vial_number)
#         #     if not os.path.exists(self.vial_directory):
#         #         os.mkdir(self.vial_directory)
#         #         self.save()
#         #         print("Created new vial directory: %s" % self.vial_directory)
#         #     else:
#         #         self.load()
#
#     def inoculate(self, name, description):
#         assert self.inoculation_time is None, "Vial already inoculated"
#         self.name = name
#         self.description = description
#         self.inoculation_time = int(time.time())
#         self.mu_max_measured = 0
#         self.t_doubling_min_measured = np.inf
#         self.is_aborted = False
#         self.save()
#
#     def collect_sample(self, sample_id, sample_volume=1):
#         # TODO preserve drug concentrations while sampling
#         device = self.device
#         vial = self.vial_number
#         device.locks_vials[vial].acquire()
#         device.lock_pumps.acquire()
#         q = input("ready to collect %d ml sample? [y/n]" % sample_volume)
#         if q == "y":
#             assert not device.is_pumping()  # must have been checked before releasing the pump_number lock
#             assert not device.hard_stop_trigger
#             device.stirrers.set_speed(vial=vial, speed=1)
#             device.valves.open(vial)  # valve number might be different for e.g. a lagoon setup
#             device.pump1.pump_number(sample_volume)
#             device.pump1.stock_volume -= sample_volume
#             log_dilution(device=device, vial_number=vial, pump1_volume=sample_volume)
#             while device.is_pumping():
#                 time.sleep(0.5)
#             q = input("Is vial volume at vacuum needle level? [y/n]")
#             if q != "y":
#                 vacuum_volume = sample_volume + 5
#                 device.pump4.pump_number(vacuum_volume)
#                 while device.is_pumping():
#                     time.sleep(0.5)
#                 log_dilution(device=device, vial_number=vial, pump4_volume=vacuum_volume)
#             self.samples_collected[time.time()] = sample_id
#             device.stirrers.set_speed(vial=vial, speed=2)
#             assert not device.is_pumping()  # make sure before closing valves
#             time.sleep(1)
#             device.valves.close(valve=vial)
#         device.locks_vials[vial].release()
#         device.lock_pumps.release()
#         self.device.locks_vials[self.vial_number].acquire()
#         self.device.lock_pumps.acquire()
#
    def show_parameters(self, increase_verbosity=False):
        if self.is_active():
            active = "ACTIVE"
        else:
            active = "NOT ACTIVE"
        print("****** Vial %d:" % self.vial_number, active)
        if self.is_active() or increase_verbosity:
            print("             name:", self.name)
            print("      description:", self.description)
            print("               od:", np.round(self.od, 4))
            print("   medium 2 conc.:", np.round(self.medium2_concentration, 4))

            # print("     od_max_limit:", self.od_max_limit)
            print("    last dilution:", np.round(time.time() - self.time_last_dilution, 1)/60, "minutes ago")

            print("               mu:", np.round(self.mu, 5), "±", np.round(np.float32(self._mu_error), 5),
                  "[1/h];     max:", self._mu_max_measured)
            print("       t_doubling:", np.round(self.t_doubling, 3), "±", np.round(np.float32(self._t_doubling_error), 3),
                  "hrs;     min:", self._t_doubling_min_measured)
            print("    Generation nr:", self.log2_dilution_coefficient)
            if increase_verbosity:
                print()
                print("      dead_volume:", self.dead_volume)
                print("  dilution_volume:", self.default_dilution_volume)
                if self._inoculation_time:
                    print("       inoculated:", time.ctime(self._inoculation_time))
                else:
                    print("       inoculated: NO")

                print("samples_collected:", self._samples_collected)
                print("       is_aborted:", self._is_aborted)
                print("         od_blank:", self.od_blank)

                vial_volume = self.dead_volume
                added_volume = self.default_dilution_volume
                dilution_factor = (vial_volume + added_volume) / vial_volume
                generations_per_dilution = np.log2(dilution_factor)
                generations_per_ml = generations_per_dilution / added_volume
                print("generations/Liter: %.1f" % (generations_per_ml * 1000))
            print()
#
#     @property
#     def od_deblanked(self):
#         return np.float32(self.od - self.od_blank)
#
#     @property
#     def od(self):
#         return np.float32(self._od)
#
#     @od.setter
#     def od(self, value):
#         write_variable(culture=self, variable_name="od", value=value)
#         self._od = value
#         self.update_growth_rate()
#         self.save()
#
#     @property
#     def log2_dilution_coefficient(self):
#         return np.float32(self._log2_dilution_coefficient)
#
#     @log2_dilution_coefficient.setter
#     def log2_dilution_coefficient(self, value):
#         self._log2_dilution_coefficient = value
#         write_variable(culture=self, variable_name="log2_dilution_coefficient", value=value)
#         self.save()
#
#     @property
#     def mu(self):
#         """
#         growth rate [1/h]
#         :return:
#         """
#         return np.float32(self._mu)
#
#     @mu.setter
#     def mu(self, value):
#         mu, error = value
#         write_variable(culture=self, variable_name="mu", value=mu)
#         write_variable(culture=self, variable_name="mu_error", value=error)
#         self._mu = mu
#         self._mu_error = error
#         if mu != 0:
#             t_doubling = np.log(2) / mu
#             t_doubling_error = t_doubling * error / mu
#             self.t_doubling = (t_doubling, t_doubling_error)
#
#             if mu > self.mu_max_measured and error / mu < 0.05:
#                 self.mu_max_measured = mu
#                 self.t_doubling_min_measured = t_doubling
#         self.save()
#
#     @property
#     def t_doubling(self):
#         return np.float32(self._t_doubling)
#
#     @t_doubling.setter
#     def t_doubling(self, value):
#         t_doubling, t_doubling_error = value
#         write_variable(culture=self, variable_name="t_doubling", value=t_doubling)
#         write_variable(culture=self, variable_name="t_doubling_error", value=t_doubling_error)
#         self._t_doubling = t_doubling
#         self._t_doubling_error = t_doubling_error
#         self.save()
#
#     def update_growth_rate(self):
#         """
#         reads last od values and calculates growth rate
#         :return:
#         """
#         od_filepath = os.path.join(self.directory, "od.csv")
#         df = read_csv_tail(od_filepath, lines=300)
#         df = df[df.index >= df.index[-1]-60*60*5]  # cut last 5 hours
#         if np.isfinite(self.time_last_dilution):
#             df = df[df.index > np.float32(self.time_last_dilution)]
#         t = df.index.values
#         od = df.values.ravel() - self.od_blank
#         od[od <= 0] = 1e-6
#         timepoint, mu, error = calculate_last_growth_rate(t, od)
#         if np.isfinite(mu):
#             self.mu = (mu, error)
#
#     @property
#     def time_last_dilution(self):
#         pump_dilution_times = np.array(list(self.last_dilution_time.values())).astype(float)
#         most_recent_dilution_time = np.nanmax(pump_dilution_times)
#         return np.float32(most_recent_dilution_time)
#         # filepath = os.path.join(self.vial_directory, "dilutions.csv")
#         # if not os.path.exists(filepath):
#         #     return np.nan
#         # data = read_csv_tail(filepath=filepath, lines=1)
#         # last_timepoint = data.index.ravel()[-1]
#         # return last_timepoint
#
#     @property
#     def medium2_concentration(self):
#         return np.float32(self._medium2_concentration)
#
#     @medium2_concentration.setter
#     def medium2_concentration(self, value):
#         self._medium2_concentration = value
#         write_variable(culture=self, variable_name="medium2_concentration", value=value)
#         self.save()
#
#     @property
#     def medium3_concentration(self):
#         return np.float32(self._medium3_concentration)
#
#     @medium3_concentration.setter
#     def medium3_concentration(self, value):
#         self._medium3_concentration = value
#         write_variable(culture=self, variable_name="medium3_concentration", value=value)
#         self.save()
#
#     @property
#     def minutes_since_last_dilution(self):
#         if not np.isfinite(self.time_last_dilution):
#             seconds_since_last_dilution = time.time() - self.inoculation_time
#         else:
#             seconds_since_last_dilution = time.time() - self.time_last_dilution
#         return np.float32(seconds_since_last_dilution/60)
#
#     def plot(self, last_hours=24):
#         fig = plot_culture(culture=self, last_hours=last_hours)
#         return fig
#
#     def is_active(self):
#         return np.isfinite(np.float32(self.inoculation_time)) and not self.is_aborted
#
#     def save(self):
#         """
#         saves config to vial_directory/culture_config.yaml
#         """
#         self.file_lock.acquire()  # maybe not necessary?
#         config_path = os.path.join(self.directory, "culture_config.yaml")
#         save_object(self, filepath=config_path)
#         self.file_lock.release()
#
#     def load(self):
#         config_path = os.path.join(self.directory, "culture_config.yaml")
#         self.file_lock.acquire()
#         load_config(self, filepath=config_path)
#         self.file_lock.release()
#         print("Loaded vial %d config." % self.vial_number)
#
#     @property
#     def device(self):
#         return self._device
#
#     @device.setter
#     def device(self, dev):
#         if dev is not None:
#             if self.directory is not None:
#                 assert os.path.join(dev.directory, "vial_%d" % self.vial_number) == self.directory
#         self._device = dev
#         self.save()
#
#     def update(self):
#         """
#         called every minute
#         """
#         pass
#
#     def dilute(self, pump1_volume=0.0, pump2_volume=0.0, pump3_volume=0.0, extra_vacuum=5):
#         """
#         pump_number the given volumes into the vial,
#         pump_number the total volume + extra_vacuum out of the vial
#         extra_vacuum has to be ~>3 to fill the waste tubing with air and prevent cross-contamination.
#         """
#         if pump2_volume > 0:
#             assert self.medium2_concentration >= 0
#             assert self.device.pump2.stock_concentration >= 0
#         if pump3_volume > 0:
#             assert self.medium3_concentration >= 0
#             assert self.device.pump3.stock_concentration >= 0
#         self.device.make_dilution(vial=self.vial_number,
#                                   pump1_volume=pump1_volume,
#                                   pump2_volume=pump2_volume,
#                                   pump3_volume=pump3_volume,
#                                   extra_vacuum=extra_vacuum)
#         self.calculate_culture_concentrations_after_dilution(pump1_volume, pump2_volume, pump3_volume)
#
#     def do_blank_od(self):
#         od_blank = read_csv_tail(os.path.join(self.directory, "od.csv"), 10).values.mean()
#         self.od_blank = od_blank
#
#     def calculate_culture_concentrations_after_dilution(self, pump1_volume, pump2_volume, pump3_volume):
#         """
#         pump1_volume: Drug-free medium
#         pump2_volume: Drug 1
#         pump3_volume: Drug 2
#         """
#
#         dilution_volume = sum([pump1_volume, pump2_volume, pump3_volume])
#         total_volume = self.dead_volume + dilution_volume
#         dilution_coefficient = total_volume / self.dead_volume
#         self.log2_dilution_coefficient = self.log2_dilution_coefficient + np.log2(dilution_coefficient)
#
#         if pump2_volume > 0 or self.medium2_concentration > 0:
#             medium2_pumped_amount = self.device.pump2.stock_concentration * pump2_volume
#             medium2_vial_amount = self.dead_volume * self.medium2_concentration
#             medium2_total_amount = medium2_vial_amount + medium2_pumped_amount
#             self.medium2_concentration = medium2_total_amount / total_volume
#
#         if pump3_volume > 0 or self.medium3_concentration > 0:
#             medium3_pumped_amount = self.device.pump3.stock_concentration * pump3_volume
#             medium3_vial_amount = self.dead_volume * self.medium3_concentration
#             medium3_total_amount = medium3_vial_amount + medium3_pumped_amount
#             self.medium3_concentration = medium3_total_amount / total_volume
#         self.save()
#
#     def check(self):
#         assert self.device.is_connected()
#         assert 1 <= self.vial_number <= 7
#         assert os.path.exists(self.directory)
#         assert 0 < self.dead_volume <= 35
#         assert 0 < self.default_dilution_volume <= 40-self.dead_volume
#         assert 0 < self.od_max_limit <= 50
#         assert callable(self.device.od_sensors[self.vial_number].calibration_function)
#         assert callable(self.device.pump1.calibration_function)
#         assert callable(self.device.pump4.calibration_function)
#         assert -0.3 < self.od_blank < 0.3
#         self.device.stirrers.check_calibration(self.vial_number)
#
#     @property
#     def experiment_start_time(self):
#         filepath = os.path.join(self.directory, "od.csv")
#         if not os.path.exists(filepath):
#             return np.nan
#         with open(filepath) as f:
#             time_first_od = np.float32(f.readlines(512)[1].split(",")[0])
#         return time_first_od
#
#     def flush_tubing_if_necessary(self):
#         if not self.is_aborted:
#             pump_volumes = {1: 0, 2: 0}
#             tstart = self.experiment_start_time
#             tinoc = np.float32(self.inoculation_time)
#             for pump_number in [1, 2]:
#                 tdil = self.last_dilution_time[pump_number]
#                 last_pump_time = np.nanmax(np.array([tdil, tstart, tinoc]).astype(np.float32))
#                 if (time.time() - last_pump_time) * 3600 < self.device.delay_tube_wash_hrs:
#                     pump_volumes[pump_number] = 0.1
#             if pump_volumes[1] > 0 or pump_volumes[2] > 0:
#                 self.dilute(pump1_volume=pump_volumes[1], pump2_volume=pump_volumes[2], pump3_volume=0)
