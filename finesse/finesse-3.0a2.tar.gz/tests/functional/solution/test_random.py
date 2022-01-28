from finesse import Model


def test_model_run_no_detectors():
    """Ensure model runs even if no detectors present."""
    model = Model()
    model.parse(
        """
        l L0 P=1
        s s1 L0.p1 ETM.p1
        m ETM T=1e-5 L=1e-6 Rc=10
        """
    )
    model.run()
