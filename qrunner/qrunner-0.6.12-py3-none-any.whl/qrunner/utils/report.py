import os
import sys
from lxml import etree


def read_report(report_file) -> dict:
    try:
        html = etree.parse(report_file, etree.HTMLParser())
        total = html.xpath('//p[2]/text()')[0].split()[0]
        pass_num = html.xpath('//span[@class="passed"]/text()')[0].split()[0]
        fail_num = html.xpath('//span[@class="failed"]/text()')[0].split()[0]
        data = {'total': total, 'pass_num': pass_num, 'fail_num': fail_num}
        print(f'报告数据: {data}')
        return data
    except Exception as e:
        print(f'读取文件异常, 退出程序\n{str(e)}')
        sys.exit()
    finally:
        try:
            os.remove(report_file)
        except FileNotFoundError:
            print(f'{report_file} 不存在')


if __name__ == '__main__':
    file1 = 'report.html'
    read_report(file1)
