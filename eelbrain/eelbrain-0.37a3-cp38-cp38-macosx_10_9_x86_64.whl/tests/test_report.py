# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import logging

from eelbrain import datasets, testnd
from eelbrain.fmtxt import html
from eelbrain.report._auto import result_report
from eelbrain.testing import requires_framework_build


@requires_framework_build
def test_result_report():
    "Test result_report function for different Results"
    ds = datasets.get_uts(True)
    sds = ds.sub("B == 'b0'")
    ys = [
        'uts',  # time
        "utsnd.summary(time=(0.25, 0.35))",  # sensor
        'utsnd',  # sensor x time
    ]

    for y in ys:
        y_obj = sds.eval(y)
        kwargs = dict(pmin=0.1, samples=100)
        if y_obj.has_dim('time'):
            kwargs['tstart'] = 0.2
            kwargs['tstop'] = 0.4

        for match in (None, 'rm'):
            logging.info("    match=%s", match)
            res = testnd.TTestOneSample(y, match=match, ds=sds, **kwargs)
            rep = result_report(res, ds)
            html(rep)

        res = testnd.TTestIndependent(y, 'A', ds=sds, **kwargs)
        rep = result_report(res, ds)
        html(rep)

        res = testnd.TTestRelated(y, 'A', ds=sds, match='rm', **kwargs)
        rep = result_report(res, sds)
        html(rep)

        res = testnd.ANOVA(y, 'A * B', ds=ds, **kwargs)
        rep = result_report(res, ds)
        html(rep)

        res = testnd.ANOVA(y, 'A * rm', ds=sds, match='rm', **kwargs)
        rep = result_report(res, ds)
        html(rep)
