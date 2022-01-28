import pandas as pd
import numpy as np
from scipy.signal.windows import hann, hamming, blackman, blackmanharris
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.GenericMethods import progressiveLocalMaximumValueFilter, cruiserLocalMaximumValueFilter


class StatorCoreVibration:
    def __init__(self):
        """
        定子铁心振动某频率振幅分量计算

        [1] 方法
        ----------
        timeFreqDomainAnalyze:
            将输入的多个波形进行FFT分频,并抽取各指定频率的幅值

        [2] 返回
        -------
        waveAnalyzeResult:
            dict,输入的各波形的分析结果(与输入波形的顺序一致),形如:{'wave_0': {'freqs': list,频域数据, 'amps': list,振幅}, ...}

        targetFreqComponent:
            list[float],根据输入的各波形数据及其参数抽取出的目标频率的幅值(与输入波形的顺序一致)

        [3] 示例
        --------
        >>> def waveGenerator(amp: float, freq: float, phrase: float, dc: float, samplingFreq: float, samplingTime: float):
        >>>     _samplingFreq = np.linspace(0, samplingTime, samplingFreq * samplingTime)
        >>>     return amp * np.sin(2 * np.pi * freq * _samplingFreq + phrase) + dc
        >>> samplingFreq = 3600
        >>> noise = waveGenerator(1, 600, 0, 0, samplingFreq, 4)
        >>> a = waveGenerator(10, 50, 0, 0, samplingFreq, 4) + noise
        >>> b = waveGenerator(8, 100, 0, 0, samplingFreq, 4) + noise
        >>> c = waveGenerator(6, 150, 0, 0, samplingFreq, 4) + noise
        >>> wave = a + b + c + noise
        >>> obj = StatorCoreVibration()
        >>> obj.timeFreqDomainAnalyze(
        >>>     {"targetFreq": 100, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": wave},
        >>>     {"targetFreq": 50, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": a},
        >>>     {"targetFreq": 100, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": b[0:-1]},
        >>>     {"targetFreq": 150, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": c[0:-100]},
        >>> )
        >>> print(obj.waveAnalyzeResult)
        >>> print(obj.targetFreqComponent)
        """
        self.waveAnalyzeResult = {}
        self.targetFreqComponent = []

    def timeFreqDomainAnalyze(self, *args):
        """
        将输入的多个波形进行FFT分频,并抽取各指定频率的幅值

        :param args: 波形数据包args[i]形如:
                            {"targetFreq": 需要取出的目标频率(targetFreq/Hz),
                            "samplingFreq": 采样频率(samplingFreq/Hz),
                            "windowType": 加窗类型(windowType:str).可选项有hanning, hamming, blackman, blackmanharris,默认hanning,
                            "zerosComplement": 补零(zerosComplement:bool)、
                            "wave": 波形数据(wave:list(float))}
        :return: None
        """
        cache = pd.DataFrame(dict([(f"wave_{i}", pd.Series([args[i]["samplingFreq"]] + [args[i]["windowType"]] + [args[i]["zerosComplement"]] + [args[i]["targetFreq"]] + args[i]["wave"].tolist())) for i in range(len(args))]))
        for item in cache:
            _dict = {item: self.__eachWaveFftCal(cache[item].dropna())}
            self.waveAnalyzeResult = {**self.waveAnalyzeResult, **_dict}
            self.__targetFreqComponentExtract(_dict[item]["freqs"], _dict[item]["amps"], cache[item].values[3], method="progressiveLocalMaximumValueFilter")

    def __targetFreqComponentExtract(self, freq: list, amp: list, targetFreq: float, method="progressiveLocalMaximumValueFilter"):
        """
        输出指定频率的振幅

        :param freq: 全频域
        :param amp: 全频域的振幅列表
        :param targetFreq: 指定频率,Hz
        :param method: 频谱泄露情况下,指定频率振幅的选择方法,默认"渐进式局部最大值过滤器"progressiveLocalMaximumValueFilter,
                        可选"巡游式局部最大值过滤器"cruiserLocalMaximumValueFilter
        :return: None
        """
        if method=="progressiveLocalMaximumValueFilter":
            amp_main = progressiveLocalMaximumValueFilter(amp, filteredSampleMaximumQuant=20)
        elif method=="cruiserLocalMaximumValueFilter":
            amp_main = cruiserLocalMaximumValueFilter(amp).filteredData
        else:
            amp_main = progressiveLocalMaximumValueFilter(amp, filteredSampleMaximumQuant=20)
        locs = [i for (i, item) in enumerate(amp) if item in amp_main]
        amp_main = np.asarray(amp)[locs].flatten().tolist()
        freq_main = np.asarray(freq)[locs].flatten().tolist()
        _distances = list(map(np.abs, np.asarray([targetFreq]) - np.asarray(freq_main)))
        _min_loc = np.where(np.asarray(_distances)==min(_distances), True, False)
        self.targetFreqComponent.append(list(np.asarray(amp_main)[_min_loc])[0])

    def __eachWaveFftCal(self, singleFrame: pd.Series):
        """
        输入的各样本数据的FFT转换过程

        :param singleFrame: 需要进行FFT的数据.包括(顺序):需要取出的目标频率(targetFreq/Hz)、采样频率(samplingFreq/Hz)、加窗类型(windowType:str)、
                            补零(zerosComplement:bool)、波形数据(wave:list(float)).其中,windowType可选项有
                            hanning, hamming, blackman, blackmanharris,默认hanning
        :return: {"freqs": 频域:list, "amps": 幅值:list}
        """
        _array = singleFrame.values
        _samplingFreq = _array[0]
        _windowType = _array[1]
        _zerosComplement = _array[2]
        _waveValues = _array[4:None]
        # 是否补0
        if _zerosComplement:
            _zerosQuant2Add = _samplingFreq - len(_waveValues)
            _waveValues = _waveValues.tolist() + [0] * _zerosQuant2Add
        # 是否加窗
        coef = 1
        if _windowType:
            coef = 2
            if _windowType == "hanning":
                _waveValues = np.multiply(hann(len(_waveValues)), _waveValues)
            elif _windowType == "hamming":
                _waveValues = np.multiply(hamming(len(_waveValues)), _waveValues)
            elif _windowType == "blackman":
                _waveValues = np.multiply(blackman(len(_waveValues)), _waveValues)
            elif _windowType == "blackmanharris":
                _waveValues = np.multiply(blackmanharris(len(_waveValues)), _waveValues)
            else:
                _waveValues = np.multiply(hann(len(_waveValues)), _waveValues)
        _waveValues_fft = np.fft.fft(_waveValues)
        _waveValues_fftFreq = np.fft.fftfreq(len(_waveValues), 1/_samplingFreq)
        _waveModes_fft = np.abs(_waveValues_fft) / len(_waveValues)
        _waveModes_fft[1:None] = _waveModes_fft[1:None] * 2 * coef
        return {
            "freqs": _waveValues_fftFreq[0: (len(_waveValues_fftFreq)//2)].tolist(),
            "amps": _waveModes_fft[0: (len(_waveModes_fft)//2)].tolist()
        }
