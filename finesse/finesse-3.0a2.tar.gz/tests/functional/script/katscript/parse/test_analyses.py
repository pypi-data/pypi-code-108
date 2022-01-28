"""Kat file compiler analysis parsing tests."""

from finesse.script import parse
from finesse.analysis.actions import Xaxis, BeamTrace, ABCD
from ....diff import assert_actions_equivalent


def test_nested_analysis():
    """Test that a kat script with a two level nested analysis builds correctly."""
    model = parse(
        """
        mirror m1
        xaxis(
            m1.phi,
            lin,
            0,
            90,
            100,
            pre_step=beam_trace(
                name="My Beam Trace"
            ),
            post_step=abcd(
                "My ABCD"
            ),
            name="myxaxis"
        )
        """
    )
    # FIXME: the assert function below doesn't check much here - needs improved.
    assert_actions_equivalent(
        model.analysis,
        Xaxis(
            model.m1.phi,
            "lin",
            0,
            90,
            100,
            pre_step=BeamTrace(name="My Beam Trace"),
            post_step=ABCD("My ABCD"),
            name="myxaxis",
        ),
    )


def test_parallel():
    model = parse(
        """
        l L0 P=1
        s s0 L0.p1 m1.p1
        m m1 R=0 T=1
        pd P m1.p2.o

        parallel(
            xaxis(m1.R, lin, 0, 1, 10),
            xaxis(L0.P, lin, 10, 100, 20, name="myxaxis")
        )
        """
    )
    # First xaxis.
    assert (
        model.analysis.actions[0].parameter
        == model.analysis.actions[0].parameter1
        == model.m1.R
    )
    assert model.analysis.actions[0].mode == model.analysis.actions[0].mode1 == "lin"
    assert model.analysis.actions[0].start == model.analysis.actions[0].start1 == 0
    assert model.analysis.actions[0].stop == model.analysis.actions[0].stop1 == 1
    assert model.analysis.actions[0].steps == model.analysis.actions[0].steps1 == 10
    assert model.analysis.actions[0].name == "xaxis"

    # Second xaxis.
    assert (
        model.analysis.actions[1].parameter
        == model.analysis.actions[1].parameter1
        == model.L0.P
    )
    assert model.analysis.actions[1].mode == model.analysis.actions[1].mode1 == "lin"
    assert model.analysis.actions[1].start == model.analysis.actions[1].start1 == 10
    assert model.analysis.actions[1].stop == model.analysis.actions[1].stop1 == 100
    assert model.analysis.actions[1].steps == model.analysis.actions[1].steps1 == 20
    assert model.analysis.actions[1].name == "myxaxis"

    # FIXME: test pre_step, etc. too - see #93


def test_expressions_as_action_arguments():
    """Test that action arguments can be expressions.

    See #130.
    """
    model = parse(
        """
        var f_m 1e5
        fsig(10)

        l pump P=1e3 f=-&f_m
        s s1 pump.p1 m1.p1
        m m1 T=5.9e-4 L=0
        s scav m1.p2 m2.p1 L=5
        m m2 T=1e-6 L=0

        ad aor m1.p1.o f=&fsig.f-&f_m
        ad aot m2.p2.o f=&fsig.f-&f_m

        sgen sig1 pump.amp.i 1 0

        xaxis(
            parameter=fsig.f,
            mode=lin,
            start=-5000+&f_m,
            stop=5000+&f_m,
            steps=300
        )
        """
    )

    assert float(model.analysis.start) == -5000 + 1e5
    assert float(model.analysis.stop) == 5000 + 1e5
