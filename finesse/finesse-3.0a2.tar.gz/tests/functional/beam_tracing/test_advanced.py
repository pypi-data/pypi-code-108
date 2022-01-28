"""Advanced beam tracing tests - i.e. interferometers with multiple cavities and configurations \
with several user set nodes and cavity objects."""

from collections import OrderedDict

from finesse.cymath.gaussbeam import transform_q
from finesse.gaussian import BeamParam
from finesse.script import parse_legacy


def test_michelson_trace():
    """Test beam tracing for a Michelson interferometer (no Fabry-Perot cavities) with a single \
    user-defined beam parameter at the starting laser node."""
    L0_q = -1.4 + 2.5j
    SCRIPT = r"""
    l L0 1 0 nL0
    s s1 0.5 nL0 nBS1

    bs BS 0.5 0.5 0 0 nBS1 nBS2 nBS3 nBS4

    s sy0 1.0 nBS2 nMY1
    m MY 0.5 0.5 0 nMY1 nMY2
    attr MY Rc 2.5

    s sx0 1.0 nBS3 nMX1
    m MX 0.5 0.5 0 nMX1 nMX2
    attr MX Rc 2.5
    """
    model = parse_legacy(SCRIPT)
    model.L0.p1.o.q = L0_q
    result = model.beam_trace().data_qx

    target = OrderedDict()
    # L0 p1
    target[model.L0.p1.o] = BeamParam(q=L0_q)
    target[model.L0.p1.i] = -target[model.L0.p1.o].conjugate()
    # BS p1
    target[model.BS.p1.i] = transform_q(
        model.L0.p1.o.space.ABCD(model.L0.p1.o, model.BS.p1.i),
        target[model.L0.p1.o],
        1,
        1,
    )
    target[model.BS.p1.o] = -target[model.BS.p1.i].conjugate()
    # BS p3
    target[model.BS.p3.o] = transform_q(
        model.BS.ABCD(model.BS.p1.i, model.BS.p3.o), target[model.BS.p1.i], 1, 1,
    )
    target[model.BS.p3.i] = -target[model.BS.p3.o].conjugate()
    # MX p1
    target[model.MX.p1.i] = transform_q(
        model.BS.p3.o.space.ABCD(model.BS.p3.o, model.MX.p1.i),
        target[model.BS.p3.o],
        1,
        1,
    )
    target[model.MX.p1.o] = -target[model.MX.p1.i].conjugate()
    # MX p2
    target[model.MX.p2.o] = transform_q(
        model.MX.ABCD(model.MX.p1.i, model.MX.p2.o), target[model.MX.p1.i], 1, 1,
    )
    target[model.MX.p2.i] = -target[model.MX.p2.o].conjugate()
    # BS p2
    target[model.BS.p2.o] = transform_q(
        model.BS.ABCD(model.BS.p1.i, model.BS.p2.o), target[model.BS.p1.i], 1, 1,
    )
    target[model.BS.p2.i] = -target[model.BS.p2.o].conjugate()
    # MY p1
    target[model.MY.p1.i] = transform_q(
        model.BS.p2.o.space.ABCD(model.BS.p2.o, model.MY.p1.i),
        target[model.BS.p2.o],
        1,
        1,
    )
    target[model.MY.p1.o] = -target[model.MY.p1.i].conjugate()
    # MY p2
    target[model.MY.p2.o] = transform_q(
        model.MY.ABCD(model.MY.p1.i, model.MY.p2.o), target[model.MY.p1.i], 1, 1,
    )
    target[model.MY.p2.i] = -target[model.MY.p2.o].conjugate()
    # BS p4
    target[model.BS.p4.o] = transform_q(
        model.BS.ABCD(model.BS.p2.i, model.BS.p4.o), target[model.BS.p2.i], 1, 1,
    )
    target[model.BS.p4.i] = -target[model.BS.p4.o].conjugate()

    for node, q in target.items():
        assert q == result[node]
