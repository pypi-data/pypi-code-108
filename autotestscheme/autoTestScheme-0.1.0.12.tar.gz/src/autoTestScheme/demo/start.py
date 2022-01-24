

from autoTestScheme import run


if __name__ == "__main__":
    run = run.Run()
    tags = {'info': '冒烟'}
    run.load_case('data')
    run.load_allure_tmp('allure-results')
    run.register_tags(tags)
    run.run(tags=['info'], process_num=1, is_debug=False, env='dev', case='all')
