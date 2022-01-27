import time
from jira import JIRA


def create_issue(title: str, content: str, to='kun.chen', env='pre', epc_id='APP-23662'):
    """
    :param title: bug标题
    :param content: bug详细描述
    :param to: 指派给人员的姓名，如kang.yang
    :param env: 问题环境，如nts、test、pre、prd
    :param epc_id: epic页面链接最后的id，如APP-23662
    :return: {
        'title': 'bug标题',
        'issue_url': 'https://jira.qizhidao.com/browse/APP-38532'
    }
    """

    jira = JIRA(server='http://jira.qizhidao.com', auth=('kang.yang', 'wz888888'))
    # print(jira.projects())

    if env == 'test':
        env_name = 'SIT环境'
    elif env == 'pre':
        env_name = 'PRE环境'
    elif env == 'nts':
        env_name = 'NTS环境'
    elif env == 'prd':
        env_name = '线上环境'
    else:
        env_name = 'PRE环境'

    date_now = time.strftime('%Y-%m-%d')

    issue_dict = {
        'project': '10002',  # 企知道APP，设为默认
        'summary': title,
        'description': content,
        'priority': {'name': 'Medium'},
        'assignee': {'name': to},
        'customfield_10612': {'value': env_name},
        'customfield_10400': {'value': '一般'},
        'duedate': date_now,
        'issuetype': {'name': 'Bug'},
        'customfield_10000': epc_id
    }

    new_issue = jira.create_issue(issue_dict)

    issue_info = {
        'title': title,
        'issue_url': f"https://jira.qizhidao.com/browse/{new_issue.raw.get('key')}"
    }
    print(issue_info)
    return issue_info


# 批量提单
def create_issues(info_list: list):
    """
    param info_list: [
        {'title': 'bug标题', 'content': 'bug描述'},
        ...
    ]
    return: [
        {'title': 'bug标题', 'issue_url': 'bug链接'},
        ...
    ]
    """

    result_list = []
    for info in info_list:
        title = info.get('title')
        content = info.get('content')
        issue_info = create_issue(title, content)
        result_list.append(issue_info)
    return result_list


if __name__ == '__main__':
    create_issue('test', 'test')
