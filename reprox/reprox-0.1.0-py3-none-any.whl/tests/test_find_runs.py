def test_find_runs():
    from reprox import find_runs
    find_runs.find_data(
        targets='event_info_double',
        exclude_from_invalid_cmt_version='global_v6',
        context_kwargs=dict(context='xenonnt_online',
                            package='straxen',
                            config_kwargs=None,
                            _minimum_run_number=20_000,
                            _maximum_run_number=21_000,
                            )
    )
