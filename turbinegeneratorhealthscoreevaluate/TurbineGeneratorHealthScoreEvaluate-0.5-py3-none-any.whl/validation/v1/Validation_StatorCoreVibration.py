import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_StatorCoreVibration import StatorCoreVibration


def main():
    def waveGenerator(amp: float, freq: float, phrase: float, dc: float, samplingFreq: float, samplingTime: float):
        _samplingFreq = np.linspace(0, samplingTime, samplingFreq * samplingTime)
        return amp * np.sin(2 * np.pi * freq * _samplingFreq + phrase) + dc

    samplingFreq = 3600
    noise = waveGenerator(1, 600, 0, 0, samplingFreq, 4)
    a = waveGenerator(10, 50, 0, 0, samplingFreq, 4) + noise
    b = waveGenerator(8, 100, 0, 0, samplingFreq, 4) + noise
    c = waveGenerator(6, 150, 0, 0, samplingFreq, 4) + noise
    wave = a + b + c + noise
    obj = StatorCoreVibration()
    obj.timeFreqDomainAnalyze(
        {"targetFreq": 100, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": wave},
        {"targetFreq": 50, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": a},
        {"targetFreq": 100, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": b[0:-1]},
        {"targetFreq": 150, "samplingFreq": samplingFreq, "windowType": "hanning", "zerosComplement": True, "wave": c[0:-100]},
    )
    print(obj.waveAnalyzeResult)
    print(obj.targetFreqComponent)

if __name__ == '__main__':
    main()