import requests
import socket


def push_data(url, metric_name, metric_value, job_name, labels: dict, timeout=5):
    """
    通过api的形式向Pushgateway推送数据，支持设置多个标签

    :param url: <ip地址>:<端口>；不需要填写http协议头
    :param metric_name: 指标名称
    :param metric_value: 指标的值
    :param job_name: job的名称
    :param labels: [字典类型]标签；可以自行设定多个标签，格式：<key>:<value>
    :param timeout: 设定推送数据时的超时时间，默认值为5秒
    :return: 布尔类型
    """
    dim = ''
    if "instance" in labels.keys():
        pass
    else:
        labels['instance'] = socket.gethostname()
    headers = {
        'X-Requested-With': 'Python Requests',
        'Content-type': 'application/json'
    }
    for key, value in labels.items():
        dim += '/{}/{}'.format(key, value)
    try:
        result = requests.post(
            headers=headers,
            url="http://{}/metrics/job/{}{}".format(url, job_name, dim),  # 外网地址
            data="{} {}\n".format(metric_name, metric_value),
            timeout=timeout,
        )
        return True
    except Exception:
        return False


if __name__ == "__main__":
    try:
        push_data(
            url="<192.168.0.1:9091>",
            metric_name="<metric_name>",
            metric_value="<metric_value>",
            job_name="<job_name>",
            labels={
                "key1": "value1",
                "key2": "value2",
                "key3": "value3"
            }
        )
    except Exception:
        print("数据推送失败！")
