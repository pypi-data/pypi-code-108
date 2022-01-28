import finesse


def test_angular_spring_phi_dependence():
    model = finesse.Model()
    # This really just tests the model runs, I don't have an analytic solution
    # for the TF to test against.
    model.parse(
        """
        l l1 P=1k
        s s1 l1.p1 m1.p1 L=0
        m m1 R=0.99 T=0.01 Rc=-2076
        s s2 m1.p2 m2.p1 L=4000
        m m2 R=1 T=0 Rc=2076

        cav c1 m2.p1

        pendulum m1_sus m1.mech I_pitch=1 fpitch=0.6 Qpitch=1000 I_yaw=1 fyaw=0.6 Qyaw=1000
        pendulum m2_sus m2.mech I_pitch=1 fpitch=0.6 Qpitch=1000 I_yaw=1 fyaw=0.6 Qyaw=1000

        pd P m1.p2.o
        ad y1 m1.mech.yaw &fsig.f
        ad y2 m2.mech.yaw &fsig.f
        ad a00 m2.p1.o f=&fsig.f n=0 m=0
        ad a10 m2.p1.o f=&fsig.f n=0 m=1

        sgen signal m2.mech.F_yaw

        fsig(1)
        modes(maxtem=1)
        xaxis(signal.f, log, 0.01, 10, 1000)
        """
    )
    out1 = model.run()
    # Shift cavity but length still on resonance
    # result should be the same
    model.m1.phi = 90
    model.m2.phi = 90
    out2 = model.run()
    # if this isn't true then the signal sidebands are not
    # picking up the correct tuning phase
    assert all(abs(out1["y1"] - out2["y1"]) / abs(out1["y1"]) < 1e-10)
    assert all((abs(out1["y2"] - out2["y2"]) / abs(out1["y2"])) < 1e-10)
