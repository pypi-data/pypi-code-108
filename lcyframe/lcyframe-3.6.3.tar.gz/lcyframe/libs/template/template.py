#!/usr/bin/env python
# -*- coding:utf-8 -*-

handler_j2 = r''' #!/usr/bin/env python
# -*- coding:utf-8 -*-
from lcyframe.libs.route import route
from lcyframe.base import BaseHandler, BaseModel as Model
{% for resource in resources %}
@route("{{resource.api}}")
class {{resource.handler_name}}(BaseHandler):
    """
    {{resource.description}}
    """
{% for method, m in resource.method.items() %}
    def {{method}}(self):
        """{{m.summary}}
        {{m.description}}
        {% if m.parameters %}
        Request extra query params:
        {% for p in m.parameters -%}
           - {{p.name}} # {{p.description}} type: {{p.type}}
        {% endfor -%}
        {% endif %}

        :return:
        :rtype:
        """
        pass
{% endfor %}
{% endfor -%}'''


model_j2 = r''' #!/usr/bin/env python
# -*- coding:utf-8 -*-
from lcyframe.base import BaseModel
from bson.objectid import ObjectId
{% for resource in resources[:1] %}
class {{resource.schame_name}}(object):
    """
    {{resource.name}} 表
    """
    collection = "{{resource.name}}"
    structure = {
        # ID
        '_id': str(ObjectId()),
    }
class {{resource.model_name}}(BaseModel, {{resource.schame_name}}):

    @classmethod
    def get(cls, *args, **kwargs):
        """
        单条记录
        :return:
        :rtype:
        """
        pass

    @classmethod
    def query(cls, *args, **kwargs):
        """
        列表
        :return:
        :rtype:
        """
        pass

    @classmethod
    def create(cls, *args, **kwargs):
        """
        创建
        :return:
        :rtype:
        """
        pass

    @classmethod
    def modify(cls, *args, **kwargs):
        """
        修改
        :return:
        :rtype:
        """
        pass

    @classmethod
    def delete(cls, *args, **kwargs):
        """
        删除
        :return:
        :rtype:
        """
        pass

{% endfor -%}'''