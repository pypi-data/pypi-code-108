import math, statistics
from codeviking.random import LCG0, LCG1, LCG2, RNG

if __name__ == '__main__':
    import sys

    SEP = '        '
    rng = RNG(LCG0(0))
    FWID = 10
    print((SEP + 14 * ' ').join(['   '] + ['f2', 'f3', 'f4', 'f5', 'f6']))
    print(SEP.join(['         N'] + ["  mean    stdev "] * 5))

    for N in [10000, 100000, 1000000]:
        s2 = [rng.f2() for i in range(N)]
        s3 = [rng.f3() for i in range(N)]
        s4 = [rng.f4() for i in range(N)]
        s5 = [rng.f5() for i in range(N)]
        s6 = [rng.f6() for i in range(N)]

        mean = [statistics.mean(s) for s in [s2, s3, s4, s5, s6]]
        std = [statistics.stdev(s) for s in [s2, s3, s4, s5, s6]]

        print(SEP.join([str(N).rjust(10)] +
                       ["%+0.4f, %+0.4f" % (mean[i], std[i])
                        for i in range(5)]))
    print('\n\n')

    SV = [0.45, 1.0, 2.6, 3.7, 7.92]
    print(SEP.join(['          '] + [str(s).center(16) for s in SV]))
    print(SEP.join(['         N'] + ["  mean    stdev "] * len(SV)))
    for N in [10000, 100000, 1000000]:
        vals = []
        for nv in SV:
            s = [rng.normal(nv) for i in range(N)]
            m = statistics.mean(s)
            v = statistics.stdev(s)
            err = abs(v - nv) / nv
            err_sqrtN = err / math.sqrt(N)
            vals.append(( m, v, err, err_sqrtN))
        print(SEP.join([str(N).rjust(10)] +
                       ["%+0.4f, %+0.4f" % (m, s)
                        for m, s, _, _ in vals]))
