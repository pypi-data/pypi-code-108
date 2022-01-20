

import os
from pytest_autoTestScheme import run


if __name__ == "__main__":
    run = run.Run()
    tags = {'info': '冒烟'}
    run.load_case('data')
    run.load_allure_tmp('allure-results')
    run.register_tags(tags)
    run.debug(tags=['info'])
    # run.run(tags=['info'], process_num=1, is_debug=True, env='dev', case='all')
    run.get_report('allure', 'allure')
