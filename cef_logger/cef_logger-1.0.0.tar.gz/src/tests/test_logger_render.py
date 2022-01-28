from cef_logger import Fields


def test_render():
    fields = Fields(
        **{
            'Version': 1, 'DeviceProduct': 'MyProduct\r',
            'DeviceVersion': '1.0\n', 'DeviceVendor': 'MyCompany\r\n',
            'DeviceEventClassID': 'base\\', 'Name': 'base|', 'Severity': 1,
            'src': '192.168.0.1', 'act': 'error=', 'custom_field': 'error\\'
        },
    )

    assert fields.render() == 'CEF:1|MyCompany|MyProduct|1.0|base\\\\' \
                              '|base\\||1|src=192.168.0.1 ' \
                              'act=error\\= custom_field=error\\\\'


def test_none_in_extension_field():
    fields = Fields(
        **{
            'Version': 1, 'DeviceProduct': 'MyProduct',
            'DeviceVersion': '1.0', 'DeviceVendor': 'MyCompany',
            'DeviceEventClassID': 'base', 'Name': 'base', 'Severity': 1,
            'src': None, 'act': None, 'custom_field': None
        },
    )

    assert fields.render() == 'CEF:1|MyCompany|MyProduct|1.0|base' \
                              '|base|1|src= act= custom_field='


def test_syslog_flag_true():
    fields = Fields(
        syslog_flag=True,
    )

    assert fields.render_syslog_header()


def test_field_ordering_extensions():
    fields = Fields(
        **{
            'Version': 1, 'DeviceProduct': 'MyProduct',
            'DeviceVersion': '1.0', 'DeviceVendor': 'MyCompany',
            'DeviceEventClassID': 'base', 'Name': 'base', 'Severity': 1,
            'src': None, 'act': None,
        },
    )
    assert fields.render() == 'CEF:1|MyCompany|MyProduct|1.0|base' \
                              '|base|1|src= act='


def test_field_ordering_customs_extensions():
    fields = Fields(
        **{
            'Version': 1, 'DeviceProduct': 'MyProduct',
            'DeviceVersion': '1.0', 'DeviceVendor': 'MyCompany',
            'DeviceEventClassID': 'base', 'Name': 'base', 'Severity': 1,
            'act': 1, 'src': 2, 'custom_field_2': 4, 'custom_field_1': 3
        },
    )
    assert fields.render() == 'CEF:1|MyCompany|MyProduct|1.0|base|base|1|' \
                              'act=1 src=2 custom_field_2=4 custom_field_1=3'
