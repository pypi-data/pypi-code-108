import time
import numpy as np
import scipy.optimize
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from replifactory.device.stepper import Stepper


def calibrate_pump(device, pump_number):
    p = device.pumps[pump_number]
    n_rotations = float(input("How many rotations?"))
    n_repetitions = float(input("How many repetitions?"))
    assert n_repetitions % 1 == 0
    n_repetitions = int(n_repetitions)
    total_volume = n_rotations * n_repetitions * 0.1
    p.fit_calibration_function()
    if callable(p.calibration_function):
        def opt_function(volume):
            return p.calibration_function(volume) - n_rotations

        predicted_mls = fsolve(opt_function, 1)[0]
        predicted_total_mls = predicted_mls * n_repetitions
        print("Predicted %.2f mls from existing calibration data" % predicted_total_mls)
        total_volume = predicted_total_mls
    q = input("Are ~%d ml available? \nZero the scale and press ENTER; q to exit" % round(total_volume))
    if q == "":
        for i in range(n_repetitions):
            p.move(n_rotations)
            print("%d/%d" % (i + 1, n_repetitions), end="\t\r")
            while p.is_pumping():
                time.sleep(0.1)
            time.sleep(1)
        ml = float(input("How many mls?"))
        ml = ml / n_repetitions
        device.calibration_pump_rotations_to_ml[pump_number][n_rotations] = round(ml, 3)
        device.save()


def pump_calibration_function(x, a, b, c):
    """
    converts pumped volume (x) to motor rotations(y)
    """
    y = a * x + b * x * np.exp(-c * x)
    return y


class Pump(Stepper):
    def __init__(self, device, cs):
        super().__init__(device=device, cs=cs)

        self.device = device
        self.cs = cs
        self.pump_number = cs + 1
        self.calibration_function = None
        if len(self.calibration_rotations_to_ml.keys()) >= 4:
            self.fit_calibration_function()

    def show_parameters(self):
        print("pump_number %d stock volume:" % self.pump_number, self.stock_volume)
        print("pump_number %d stock concentration:" % self.pump_number, self.stock_concentration)
        self.calibration_curve()
        plt.show()

    @property
    def stock_concentration(self):
        return np.float32(self.device.pump_stock_concentrations[self.pump_number])

    @stock_concentration.setter
    def stock_concentration(self, value):
        value = float(value)
        self.device.pump_stock_concentrations[self.pump_number] = value
        self.device.save()

    @property
    def stock_volume(self):
        return np.float32(self.device.pump_stock_volumes[self.pump_number])

    @stock_volume.setter
    def stock_volume(self, value):
        value = float(value)
        self.device.pump_stock_volumes[self.pump_number] = value
        self.device.save()

    @property
    def calibration_rotations_to_ml(self):
        return self.device.calibration_pump_rotations_to_ml[self.pump_number]

    @calibration_rotations_to_ml.setter
    def calibration_rotations_to_ml(self, value):
        self.device.calibration_pump_rotations_to_ml[self.pump_number] = value
        self.fit_calibration_function()
        self.device.save()

    def pump(self, volume):
        rotations = self.calibration_function(abs(volume))
        if volume < 0:
            rotations *= -1
        if volume != 0:
            self.move(n_rotations=rotations)

    def add_calibration_point(self, rotations, volume):
        temp = self.calibration_rotations_to_ml
        temp[rotations] = volume
        self.calibration_rotations_to_ml = temp

    def calibrate(self, rotations_to_ml=None, dummy_data=False):
        self.device.save()
        self.calibration_rotations_to_ml = rotations_to_ml
        if rotations_to_ml is None and dummy_data:
            self.calibration_rotations_to_ml = {1: 0.145,
                                                5: 0.563,
                                                10: 1.012,
                                                20: 2.14,
                                                50: 5.14,
                                                100: 9.21}

    def fit_calibration_function(self):
        calibration_n_rotations = sorted(list(self.calibration_rotations_to_ml.keys()))
        calibration_volumes = sorted(list(self.calibration_rotations_to_ml.values()))
        if calibration_n_rotations is not None:
            if len(calibration_n_rotations) >= 4:
                coefs, _ = scipy.optimize.curve_fit(pump_calibration_function, calibration_volumes,
                                                    calibration_n_rotations,
                                                    p0=(10, -10, 1),
                                                    bounds=[(-50, -50, 0.1), (50, 50, 1)],
                                                    sigma=np.array(calibration_volumes) * 0.1)
                a, b, c = coefs

                def f(volume):
                    """
                    converts volume to number of pump_number rotations
                    """
                    return pump_calibration_function(volume, a, b, c)

                self.calibration_function = f
                return a, b, c

    def calibration_curve(self):

        calibration_n_rotations = sorted(list(self.calibration_rotations_to_ml.keys()))
        calibration_volumes = sorted(list(self.calibration_rotations_to_ml.values()))
        if len(calibration_n_rotations) < 4:
            print("PUMP %d: NOT ENOUGH CALIBRATION POINTS (%d/4)" % (self.pump_number, len(calibration_n_rotations)))
        else:
            a, b, c = self.fit_calibration_function()
            plt.figure(figsize=[6, 4], dpi=100)
            x = np.linspace(0, 20, 101)
            y = [self.calibration_function(vol) for vol in x]
            plt.plot(calibration_volumes, calibration_n_rotations, "bs")
            plt.plot(x, y, "k:")
            plt.xlabel("pumped volume [mL]")
            plt.ylabel("motor rotations")
            plt.title("Pump %d calibration\n a (slope): %.3f    b: %.3f    c: %.3f" % (self.pump_number, a, b, c))
            # plt.show()
