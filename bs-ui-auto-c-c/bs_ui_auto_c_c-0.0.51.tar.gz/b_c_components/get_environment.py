

def get_environment_data(driver=None, environment=None):
    """

    :return:
    """

    if environment is None:
        environment = driver.global_instance.get('environment')

    url_dict = {
# https://assess.tms.beisen.net
        'test': {
            'italent_url': 'https://www.italent.link',
            'cloud_url': 'https://cloud.italent.link',
            'tms_url': 'https://tms.beisen.net',
            'account': 'https://account.italent.link',
            'assess': 'https://assess.tms.beisen.net'

        },
        'prod': {
            'italent_url': 'https://www.italent.cn',
            'cloud_url': 'https://cloud.italent.cn',
            'tms_url': 'https://tms.beisen.com',
            'account': 'https://account.italent.cn',
            'assess': 'https://assess.tms.beisen.com'
        }

    }

    return url_dict.get(environment)


def get_host(driver, environment=None):
    """
    return
    """

    if environment is None:
        environment = driver.global_instance.get('environment')

    host_dict = {
        'test': {
            'italent': 'www.italent.link',
            'cloud': 'cloud.italent.link',
            'tms': 'tms.beisen.net',
            'account': 'account.italent.link'

        },
        'prod': {
            'italent': 'www.italent.cn',
            'cloud': 'cloud.italent.cn',
            'tms': 'tms.beisen.com',
            'account': 'account.italent.cn'
        }
    }

    return host_dict.get(environment)

