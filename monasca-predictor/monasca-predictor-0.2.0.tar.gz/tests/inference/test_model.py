import logging
import pathlib

import monasca_predictor.inference.model as inf_mod

log = logging.getLogger(__name__)
tests_dir = pathlib.Path(__file__).parent.absolute()


def test_model():
    model_dump = (tests_dir / "model.h5").absolute()
    scaler_dump = (tests_dir / "scaler.joblib").absolute()

    log.debug("Using model dump at '%s'.", model_dump)
    log.debug("Using scaler dump at '%s'.", scaler_dump)

    model = inf_mod.Model()
    model.load(
        model_dump=model_dump,
        scaler_dump=scaler_dump,
    )

    x = [0.0] * 24
    y = model.predict(x)

    log.debug("y (%s): %s", type(y), str(y))


def test_linear_model():
    model = inf_mod.LinearModel(10)

    log.debug(
        "Using linear model with prediction offset set to %d.", model._prediction_offset
    )

    x = [0, 1, 2]
    y = model.predict(x)

    log.debug("y (%s): %s", type(y), str(y))


if __name__ == "__main__":
    # test_model()
    test_linear_model()
