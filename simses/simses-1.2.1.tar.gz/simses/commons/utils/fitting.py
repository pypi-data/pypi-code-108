from matplotlib import pyplot
from numpy import ndarray, linspace, inf, mean
from pandas import DataFrame, read_csv
from scipy.optimize import curve_fit

bounds_for_custom_fitting_parameters = ([0, -inf, -inf], [inf, inf, inf])


def custom_fitting_function(x, b, c, d):
    return x / (x + b + c*x + d*x**2)


def polynomial_fit(x, *args):
    res = 0
    for order in range(len(args)):
        res += args[order] * x**order
    return res


# def multi_dimensional_fitting_function(X, a, b, c):
#     x,y = X
#     return np.log(a) + b*np.log(x) + c*np.log(y)

sorted = linspace(0.0, 1.0, 100)


class AixAcDcFitter:

    __FILE_NAME: str = './efficiencies.csv'
    __POWER_COL: str = 'Power'
    __EFFICIENCY_COL: str= 'Efficiency'
    __MODULE_COL: str = 'Module'
    __BLOCK_COL: str = 'Block'
    __DIRECTION_COL: str = 'Direction'
    __RESULT_FILE: str = './fitting.csv'

    __CHARGE: str = 'Quelle'
    __DISCHARGE: str = 'Senke'

    __MAX_POWER: float = 166.0  # kW

    __DO_PLOT: bool = True

    def __init__(self, block: int, module: int):
        data: DataFrame = read_csv(self.__FILE_NAME, sep=';', decimal=',')
        filtered_data: DataFrame = self.__filter(data=data, block=block, module=module)
        filtered_power: DataFrame = self.__filter_power_range(data=filtered_data, block=block, module=module)
        self.__power_data = filtered_power[self.__POWER_COL].to_numpy()
        self.__efficiency_data: ndarray = filtered_power[self.__EFFICIENCY_COL].to_numpy() / 100.0
        if self.__DO_PLOT:
            fig, self.__ax = pyplot.subplots()
            self.__ax.plot(self.__power_data, self.__efficiency_data, label='measured', marker='o', linestyle='none')

    def __filter(self, data: DataFrame, block: int, module: int) -> ndarray:
        filtered_data: DataFrame = data.loc[(data[self.__BLOCK_COL] == block) &
                                            (data[self.__MODULE_COL] == module) &
                                            (data[self.__EFFICIENCY_COL] > 0) &
                                            (data[self.__POWER_COL] > 0), :].copy().reset_index()
        return filtered_data

    def __normalize_power_of(self, data: DataFrame) -> None:
        power_data: ndarray = data[self.__POWER_COL]
        data[self.__POWER_COL] = power_data / self.__MAX_POWER

    def __filter_power_range(self, data: DataFrame, block: int, module: int) -> DataFrame:
        self.__normalize_power_of(data)
        power_scale: float = block * module
        min_power: float = 0.02  # max(0.02, min(0.5, 0.25 * (power_scale - 1)))
        max_power: float = 1.0  # 0.25 * power_scale
        filtered_data: DataFrame = data.loc[(data[self.__POWER_COL] > min_power) &
                                            (data[self.__POWER_COL] < max_power), :].copy().reset_index()
        return filtered_data

    def fit_polynomial_function(self, order: int) -> ndarray:
        popt, pcov = curve_fit(polynomial_fit, xdata=self.__power_data, ydata=self.__efficiency_data, p0=[0] * (order + 1))
        return polynomial_fit(sorted, *popt)

    def fit_order_range(self, start: int, end: int, step: int) -> None:
        for order in range(start, end, step):
            if self.__DO_PLOT:
                fit_data = self.fit_polynomial_function(order)
                self.__ax.plot(sorted, fit_data, label='polyn. fit, order ' + str(order), linestyle='--')

    def fit_custom_function(self):
        optimal_fit, variance_fit = curve_fit(custom_fitting_function, xdata=self.__power_data, ydata=self.__efficiency_data,
                                              bounds=bounds_for_custom_fitting_parameters, maxfev=10000)
        mean_error, max_error = self.get_mean_standard_error_from(optimal_fit)
        print(mean_error, max_error, optimal_fit)
        if self.__DO_PLOT:
            fit_data = custom_fitting_function(sorted, *optimal_fit)
            self.__ax.plot(sorted, fit_data, label='custom fit', linestyle='--')
        return optimal_fit

    def get_mean_standard_error_from(self, optimal_fit) -> (float, float):
        fit = custom_fitting_function(self.__power_data, *optimal_fit)
        error = abs(self.__efficiency_data - fit)
        return mean(error), max(error)

    def fit(self) -> None:
        # self.fit_order_range(4, 5, 1)
        optimal_fit = self.fit_custom_function()
        self.show()
        return optimal_fit

    def show(self) -> None:
        if self.__DO_PLOT:
            self.__ax.legend(loc='lower right')
            # plt.savefig(self.__path + self.alphanumerize(self.__title) + '.pdf')
            pyplot.show()


if __name__ == '__main__':
    optimal_fits: list = list()
    for module in range(1, 3, 1):
        for block in range(1,3,1):
            print('Fitting for block ' + str(block) + ' and module ' + str(module))
            fitter: AixAcDcFitter = AixAcDcFitter(block=block, module=module)
            optimal_fits.append(fitter.fit())
    fig, ax = pyplot.subplots()
    count: int = 0
    for optimal_fit in optimal_fits:
        count += 1
        fit_data = custom_fitting_function(sorted, *optimal_fit)
        ax.plot(sorted, fit_data, label='custom fit ' + str(count), linestyle='--')
    ax.legend(loc='lower right')
    pyplot.show()
