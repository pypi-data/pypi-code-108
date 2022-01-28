from chaosreliably.controls import experiment


def test_experiment_controls_exposes_correct___all___values() -> None:
    for func in [
        "after_activity_control",
        "after_experiment_control",
        "after_hypothesis_control",
        "after_method_control",
        "after_rollback_control",
        "before_experiment_control",
        "before_hypothesis_control",
        "before_method_control",
        "before_rollback_control",
        "before_activity_control",
    ]:
        assert func in experiment.__all__
