from codeviking.math.angle import Angle


def test_delta():
    cases = [(30, 60, 30),
             (30, 330, -60),
             (30, 210, -180),
             (30, 120, 90),
             (30, -60, -90)]
    for (a, b, d) in cases:
        Angle.rad_to_deg(Angle.delta(Angle.deg_to_rad(a),
                                     round(Angle.deg_to_rad(
                                             b))))
