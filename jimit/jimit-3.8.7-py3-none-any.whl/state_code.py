#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'James Iter'
__date__ = '15/4/27'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2015 by James Iter.'


index_state = {
    'trunk': {
        '200': {
            'code': '200',
            'zh-cn': '成功',
            'en-us': 'OK'
        },
        '201': {
            'code': '201',
            'zh-cn': '已创建',
            'en-us': 'Created'
        },
        '202': {
            'code': '202',
            'zh-cn': '已接受',
            'en-us': 'Accepted'
        },
        '204': {
            'code': '204',
            'zh-cn': '没有内容',
            'en-us': 'No Content'
        },
        '205': {
            'code': '205',
            'zh-cn': '重置内容',
            'en-us': 'Reset Content'
        },
        '206': {
            'code': '206',
            'zh-cn': '部分内容',
            'en-us': 'Partial Content'
        },
        '207': {
            'code': '207',
            'zh-cn': '扩展状态码',
            'en-us': 'Multi-Status'
        },
        '400': {
            'code': '400',
            'zh-cn': '坏请求',
            'en-us': 'Bad request'
        },
        '401': {
            'code': '401',
            'zh-cn': '未授权',
            'en-us': 'Unauthorized'
        },
        '403': {
            'code': '403',
            'zh-cn': '禁止',
            'en-us': 'Forbidden'
        },
        '404': {
            'code': '404',
            'zh-cn': '未找到',
            'en-us': 'Not found'
        },
        '405': {
            'code': '405',
            'zh-cn': '不允许使用的方法',
            'en-us': 'Method Not Allowed'
        },
        '409': {
            'code': '409',
            'zh-cn': '请求冲突',
            'en-us': 'Conflict'
        },
        '412': {
            'code': '412',
            'zh-cn': '先决条件失败',
            'en-us': 'Precondition Failed'
        },
        '500': {
            'code': '500',
            'zh-cn': '内部服务器错误',
            'en-us': 'Internal Server Error'
        },
        '501': {
            'code': '501',
            'zh-cn': '未实现',
            'en-us': 'Not Implemented'
        },
        '503': {
            'code': '503',
            'zh-cn': '服务不可用',
            'en-us': 'Service Unavailable'
        }
    },
    'branch': {
        '40101': {
            'code': '40101',
            'zh-cn': '未授权'
        },
        '40301': {
            'code': '40301',
            'zh-cn': '禁止(无权)访问'
        },
        '40401': {
            'code': '40401',
            'zh-cn': '目标不存在'
        },
        '40901': {
            'code': '40901',
            'zh-cn': '目标已存在'
        },
        '40001': {
            'code': '40001',
            'zh-cn': '缺少参数'
        },
        '40002': {
            'code': '40002',
            'zh-cn': '参数类型未达预期'
        },
        '40003': {
            'code': '40003',
            'zh-cn': '参数值超出合理范围'
        },
        '40004': {
            'code': '40004',
            'zh-cn': '预检策略原语类型有误，期待tuple类型'
        },
        '40005': {
            'code': '40005',
            'zh-cn': '预检策略原语参数有误，期待3个'
        },
        '40006': {
            'code': '40006',
            'zh-cn': '预检策略原语取值范围描述有误'
        },
        '40007': {
            'code': '40007',
            'zh-cn': '预检策略原语字段描述有误，字段标识必须为basestring类型'
        },
        '40008': {
            'code': '40008',
            'zh-cn': '无效的token'
        },
        '40009': {
            'code': '40009',
            'zh-cn': '正则匹配失败'
        },
        '50000': {
            'code': '50000',
            'zh-cn': '参见父描述'
        },
        '50001': {
            'code': '50001',
            'zh-cn': '错误码类型错误'
        },
        '50002': {
            'code': '50002',
            'zh-cn': '未定义的错误码'
        },
        '50003': {
            'code': '50003',
            'zh-cn': 'SQL对象序列化为json失败'
        },
        '50004': {
            'code': '50004',
            'zh-cn': '计算文件hash失败'
        }
    }
}
