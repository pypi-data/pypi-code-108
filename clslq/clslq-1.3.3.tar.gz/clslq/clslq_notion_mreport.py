import click
import datetime
import string
import os
import requests
import base64
import re
import traceback
import calendar
from io import BytesIO
from clspy.log import Logger

from .templates import monthreport
from .clslq_notion_report import Report

clslog = Logger().log


class MonthReport(Report):
    def belongs(self, date):
        if date > self._mdaystart and date <= self._mdayend:
            return True
        else:
            return False

    def week_belongs(self, sdate, edate):
        if sdate >= (self._mdaystart -
                     datetime.timedelta(days=1)) and edate <= (
                         self._mdayend + datetime.timedelta(days=1)):
            return True
        else:
            return False

    def _gen_lastmonth(self, nowdate):
        if nowdate.month == 1:
            self.report_month = 12
        else:
            self.report_month = nowdate.month - 1
        clslog.info("report_month: {}".format(self.report_month))
        self._mdaystart = nowdate - \
            datetime.timedelta(
                days=(nowdate.day + calendar.mdays[self.report_month]))
        self._mdayend = nowdate - datetime.timedelta(days=nowdate.day)
        clslog.critical("==月报[LastMonth]检索{}==>{}周报及读书学习笔记==".format(
            self._mdaystart.strftime("%Y%m%d"),
            self._mdayend.strftime("%Y%m%d")))

    def _gen_thismonth(self, nowdate):
        self.report_month = nowdate.month
        self._mdaystart = nowdate - datetime.timedelta(days=(nowdate.day))
        self._mdayend = nowdate
        clslog.critical("==月报[ThisMonth]检索{}==>{}周报及读书学习笔记==".format(
            self._mdaystart.strftime("%Y%m%d"),
            self._mdayend.strftime("%Y%m%d")))

    def init(self, title, user, department, force):

        nowdate = self.datetime_now
        if force:
            if nowdate.day > 6:
                self._gen_thismonth(nowdate)
            else:
                self._gen_lastmonth(nowdate)
        else:
            self._gen_lastmonth(nowdate)


        mtitle = "{}({}{:02})".format(title, nowdate.year, self.report_month)
        click.secho("{}".format(mtitle), fg='blue')
        self._title = mtitle

        self._book = str('')
        self._book_content = str('')
        self._study_list = str('')
        self._main_target = str('')
        self._team_target = str('')
        self._technology = str('')
        self._patent = str('')
        self._review = str('')
        self._tech_issues = str('')
        self._maintainance = str('')
        self._duties = str('')
        self._programming_tasks = str('')
        self._reading_share = str('')
        _template = """
            <li style="list-style-type: upper-roman;">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span></li>
        """
        self._reading_share += _template.format(**{
            'content': u"项目例会中结合技术管理、结构思考等方面书中所学",
            'solve': u"会议提议与解决着重高效"
        })
        self._reading_share += _template.format(
            **{
                'content': u"日常工作结合技术分享精神",
                'solve': u"利用自身高效整理的特点，将团队技术栈相关的有用信息分享给团队开发人员"
            })
        self._directions = str('')

        self._user = user
        self._department = department

    @property
    def mtitle(self):
        return self._title

    @mtitle.setter
    def mtitle(self, xtitle):
        if not isinstance(xtitle, str):
            raise ValueError("mtitle must be an string")
        else:
            self._title = xtitle

    def content_parse_title(self, item):
        result = None
        try:
            title = item[u'名称']['title']
            for i in title:
                result = i['plain_text']
        except Exception as e:
            pass
        finally:
            return result

    def content_parse_state(self, item):
        result = ''
        try:
            for i in item[u'状态']['multi_select']:
                result = "{} {}".format(result, i['name'])
        except Exception as e:
            pass
        finally:
            return result

    def content_parse_type(self, item):
        result = ''
        try:
            result = item[u'分类']['select']['name']
            if result == u'工作计划':
                return ''
        except Exception as e:
            pass
        finally:
            return result

    def content_parse_richtext(self, item, text):
        """Parse Notion Column content

        Args:
            item (dict): Notion Column content
            text (str): Unicode string means column title

        Returns:
            str: Cell result
        """
        result = ''
        try:
            title = item[text]['rich_text']
            for i in title:
                result = i['plain_text']
        except Exception as e:
            pass
        finally:
            return result.replace('\n', ' ')

    def block_parse_table_cell_properties(self, properties, key):
        _type = properties[key]['type']
        _result = ''

        def date_valid(x):
            return x if x is not None else ""

        def num_valid(x):
            return str(x) if x is not None else ""

        try:
            if _type == 'rich_text' or _type == 'title':
                for i in properties[key][_type]:
                    _result += i['plain_text']

            elif _type == 'multi_select':
                for i in properties[key][_type]:
                    _result += """<span style="color:{color};">{content}</span>""".format(
                        **{
                            'color': i['color'],
                            'content': i['name']
                        })
            elif _type == 'select':
                i = properties[key][_type]
                _result += """<span style="color:{color};">{content}</span>""".format(
                    **{
                        'color': i['color'],
                        'content': i['name']
                    })
            elif _type == 'url':
                _result += """<a href="{url}" target="_blank">{text}</a>""".format(
                    **{
                        'url': properties[key][_type],
                        'text': properties[key][_type]
                    })
            elif _type == 'date':
                _result += """{s} {e}""".format(
                    **{
                        's': date_valid(properties[key][_type]['start']),
                        'e': date_valid(properties[key][_type]['end'])
                    })
            elif _type == 'number':
                _result += num_valid(properties[key][_type])
            elif _type == 'files':
                for f in properties[key][_type]:

                    if 'file' in f:
                        url = f['file']['url']
                    elif 'external' in f:
                        url = f['external']['url']

                    img_template = """
                        <img style="width: 200px;" src="{img}"></img>
                    """
                    imgsrc = self.img_url_to_base64(url)
                    clslog.info(imgsrc[0:32] + '...')
                    if imgsrc:
                        _result += img_template.format(**{'img': imgsrc})
                    else:
                        _result += img_template.format(**{'img': url})
            else:
                clslog.warning("Unsupported: {}".format(properties[key]))
        except Exception as e:
            clslog.critical("Exception @{}: {}".format(
                e.__traceback__.tb_lineno, e))

        return _result

    def block_parse_table(self, client, b):
        database = client.databases.query(b['id'])
        table = str(
            '<table border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse; color: #3d3b4f; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">'
        )
        heads = []
        if len(database['results']):
            table += '<thead>'
            for h in database['results'][0]['properties']:
                heads.append(h)
            for hi in reversed(heads):
                table += """<th height="19" width="107"
                          style="border: 0.5pt solid #cfcfcf; width: 107pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">{h}</th>""".format(
                    **{'h': hi})
            table += '</thead>'
            table += '<tbody>'
            for i in database['results']:
                p = i['properties']
                table += '<tr height="19" style="height:14.0pt;background-color:rgb(253, 233, 217)">'
                for hi in reversed(heads):
                    table += """<td height="19" width="107"
                          style="border: 0.5pt solid #cfcfcf; width: 107pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">{v}</td>""".format(
                        **{'v': self.block_parse_table_cell_properties(p, hi)})
                table += '</tr>'
            table += '</tbody>'
        table += str('</table>')
        return table

    def block_common_types(self, client, b):
        children = str('')

        img_template = """
            <div style="width:100%;border: 1px dashed #ccc;
                vertical-align: middle;text-align: center; 
                box-shadow: 0px 0px 5px 5px rgba(10,10,10,0.2);
                -moz-box-shadow: 0px 0px 5px 5px rgba(10,10,10,0.2);
                -webkit-box-shadow: 0px 0px 5px 5px rgba(10,10,10,0.2);" >
                <img style="width: 80%; margin-top: 50px; margin-bottom: 50px;" src="{img}"></img>
            </div>
        """
        try:
            if b['type'] == "image":
                try:
                    if 'file' in b['image']:
                        url = b['image']['file']['url']
                    elif 'external' in b['image']:
                        url = b['image']['external']['url']

                    imgsrc = self.img_url_to_base64(url)
                    clslog.info(imgsrc[0:32] + '...')
                    if imgsrc:
                        children += img_template.format(**{'img': imgsrc})
                    else:
                        children += img_template.format(**{'img': url})
                except Exception as e:
                    clslog.critical("Exception @{}: {}".format(
                        e.__traceback__.tb_lineno, e))
                    clslog.info(b)

            elif b['type'] == "paragraph":
                text = str('')
                for t in b['paragraph']['text']:
                    text += t['plain_text']
                children += """<p>{p}</p>""".format(**{'p': text.strip()})

            elif b['type'] == 'heading_1':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<h1>{head}</h1>""".format(
                    **{'head': text.strip()})
            elif b['type'] == 'heading_2':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<h2>{head}</h2>""".format(
                    **{'head': text.strip()})
            elif b['type'] == 'heading_3':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<h3>{head}</h3>""".format(
                    **{'head': text.strip()})
            elif b['type'] == 'heading_4':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<h4>{head}</h4>""".format(
                    **{'head': text.strip()})
            elif b['type'] == 'heading_5':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<h5>{head}</h5>""".format(
                    **{'head': text.strip()})
            elif b['type'] == 'heading_6':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<h6>{head}</h6>""".format(
                    **{'head': text.strip()})
            elif b['type'] == 'code':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<pre style="background-color: f5f5f5"><code>{code}</code></pre>""".format(
                    **{'code': text.strip()})
            elif b['type'] == 'bookmark':
                text = str('')
                for t in b[b['type']]['caption']:
                    text += t['plain_text']
                children += """<a href="{bookmark}" target="_blank">{caption}</a><br/>""".format(
                    **{
                        'bookmark': b[b['type']]['url'],
                        'caption': text.strip()
                    })
            elif b['type'] == 'child_database':
                children += self.block_parse_table(client, b)
            elif b['type'] == 'callout':
                text = str('')
                for t in b[b['type']]['text']:
                    text += t['plain_text']
                children += """<pre style="background-color: f5f5f5"><code>{icon}{code}</code></pre>""".format(
                    **{
                        'code': text.strip(),
                        'icon': b[b['type']]['icon']['emoji']
                    })
            else:
                clslog.warning("An unsupported type was received")
                clslog.info(b)
        except Exception as e:
            clslog.critical("Exception @{}: {}".format(
                e.__traceback__.tb_lineno, e))
        return children

    def block_list_children(self, client, block, tag, level=0):
        """Recursive function"""
        bs = client.blocks.children.list(block['id'])
        children = str('')
        if tag == 'ol':
            if level % 4 == 0:
                children = "<" + tag + " type=\"1\">"
            elif level % 4 == 1:
                children = "<" + tag + " type=\"A\">"
            elif level % 4 == 2:
                children = "<" + tag + " type=\"a\">"
            elif level % 4 == 3:
                children = "<" + tag + " type=\"I\">"
            else:
                children = "<" + tag + " type=\"i\">"
        elif tag == 'ul':
            if level % 4 == 0:
                children = "<" + tag + " style=\"list-style-type:\1F44D\">"
            elif level % 4 == 1:
                children = "<" + tag + " style=\"list-style-type:\1F44D\">"
            elif level % 4 == 2:
                children = "<" + tag + " style=\"list-style-type:disc\">"
            elif level % 4 == 3:
                children = "<" + tag + " style=\"list-style-type:\1F44D\">"
            else:
                children = "<" + tag + " style=\"none\">"

        for i in range(len(bs['results'])):
            b = bs['results'][i]

            if b['type'] == 'numbered_list_item' or b[
                    'type'] == 'bulleted_list_item':

                plain_text = str('')
                for t in b[b['type']]['text']:
                    plain_text += t['plain_text']
                if b['has_children']:
                    level += 1
                    new_children = str('')
                    if b['type'] == 'bulleted_list_item':
                        new_children += self.block_list_children(
                            client, b, 'ul', level)
                    elif b['type'] == 'numbered_list_item':
                        new_children += self.block_list_children(
                            client, b, 'ol', level)
                    children += """<li>{item}{children}</li>""".format(
                        **{
                            'item': plain_text,
                            'children': new_children
                        })
                else:
                    children += """<li>{item}</li>""".format(
                        **{'item': plain_text})
            else:
                children += self.block_common_types(client, b)

        children += "</" + tag + ">"
        return children

    def render_block_list(self, client, block, tag, level):
        """Recurisve <ol><ul><li> tags management"""
        plain_text = str('')
        for t in block[block['type']]['text']:
            plain_text += t['plain_text']
        if block['has_children']:
            level += 1
            last = """<li>{item}{children}</li>""".format(
                **{
                    'item': plain_text,
                    'children': self.block_list_children(
                        client, block, tag, level)
                })
        else:
            last = """<li>{item}</li>""".format(**{'item': plain_text})
        # clslog.info(last)
        return last

    def img_url_to_base64(self, url):
        try:
            imgtype = os.path.splitext(url)[1].split('?')[0].replace('.', '/')
            response = requests.get(url)
            imgbase64 = base64.b64encode(BytesIO(response.content).read())
            return "data:image{};base64,".format(imgtype) + imgbase64.decode(
                "utf-8")
        except Exception as e:
            clslog.critical("Exception @{}: {}".format(
                e.__traceback__.tb_lineno, e))
            return None

    def render_block_items(self, client, page):
        page_html_tags = str('')
        p_template = """
            <p style="text-indent: 2em;">{p}</p>
        """
        img_template = """
            <div style="width:auto;border: 1px dashed #ccc;display: table-cell;
                vertical-align: middle;text-align: center; 
                box-shadow: 0px 0px 5px 5px rgba(10,10,10,0.2);
                -moz-box-shadow: 0px 0px 5px 5px rgba(10,10,10,0.2);
                -webkit-box-shadow: 0px 0px 5px 5px rgba(10,10,10,0.2);" >
                <img style="width: 80%;" src="{img}"></img>
            </div>
        """

        page_id = page['id']
        page_blocks = client.blocks.retrieve(page_id)
        page_content = client.blocks.children.list(page_blocks['id'])
        # clslog.info(json.dumps(page_content))
        """Supported blocks:
        paragraph, numbered_list_item, bulleted_list_item
        emoji icons
        """
        bulleted_list = str('')
        numbered_list = str('')
        last_type = None
        for i in range(len(page_content['results'])):
            b = page_content['results'][i]
            # End of <ol>
            if (last_type == 'numbered_list_item'
                    and b['type'] != 'numbered_list_item') or i == len(
                        page_content['results']) - 1:
                page_html_tags += """<ol type="1">{list}</ol>""".format(
                    **{'list': numbered_list})
                numbered_list = str('')
            # End of <ul>
            if (last_type == 'bulleted_list_item'
                    and b['type'] != 'bulleted_list_item') or i == len(
                        page_content['results']) - 1:
                page_html_tags += """<ul style="list-style-type:disc">{list}</ul>""".format(
                    **{'list': bulleted_list})
                bulleted_list = str('')
            if b['type'] == 'numbered_list_item':
                numbered_list += self.render_block_list(client, b, 'ol', 0)
            elif b['type'] == 'bulleted_list_item':
                bulleted_list += self.render_block_list(client, b, 'ul', 0)

            elif b['type'] == 'paragraph':
                text = str('')
                for t in b['paragraph']['text']:
                    text += t['plain_text']
                page_html_tags += p_template.format(**{'p': text.strip()})
            elif b['type'] == 'image' \
                or b['type'] == 'heading_1' \
                or b['type'] == 'heading_2' \
                or b['type'] == 'heading_3' \
                or b['type'] == 'heading_4' \
                or b['type'] == 'heading_5' \
                or b['type'] == 'heading_6' \
                or b['type'] == 'code' \
                    or b['type'] == 'bookmark':
                page_html_tags += self.block_common_types(client, b)
            elif  b['type'] == 'link_to_page':
                bs = client.blocks.retrieve(b['id'])
                
                # Into link page
                page = client.pages.retrieve(page_id=bs['link_to_page']['page_id'])
                title = page['properties']['title']['title'][0]['plain_text']
   
                page_html_tags += p_template.format(**{'p': title.strip()})
            else:
                clslog.warning("Type:{}".format(b['type']))
                bs = client.blocks.retrieve(b['id'])
                clslog.info(
                    "{} Not supported by current Notion API, more info please visit {}"
                    .format(
                        bs,
                        "https://developers.notion.com/docs"
                    ))

            last_type = b['type']
        return page_html_tags

    def render_reading_books(self, client, database):
        for page in database['results']:
            item = page['properties']
            date = datetime.datetime.fromisoformat(
                item[u'收录日期']['date']['start'])
            """Skip useless databases
            """
            if self.belongs(date):
                self._book += self.content_parse_title(item)
                self._book_content += self.render_block_items(client, page)

    def render_study_note(self, client, database):

        for page in database['results']:
            item = page['properties']
            date = datetime.datetime.fromisoformat(
                item[u'收录日期']['date']['start'])
            """Skip useless databases
            """
            if self.belongs(date):
                title_url = item[u'链接']['url']
                self._study_list += """<h1>{title}</h1><br/>""".format(
                    **{'title': self.content_parse_title(item)})
                if title_url:
                    self._study_list += """<a href="{url}" target="_blank"><p>{title}</p></a><br/>""".format(
                        **{
                            'title': "扩展阅读",
                            'url': title_url
                        })

                self._study_list += self.render_block_items(client, page)
        # clslog.info(self._study_list)

    def render_maintarget(self, database):
        for node in database['results']:
            item = node['properties']
            self._main_target += """<li style="list-style-type: demical;">{p}</li>""".format(
                **{'p': item[u'目标']['title'][0]['plain_text']})

    def render_teamtarget(self, database):
        for node in database['results']:
            item = node['properties']
            self._team_target += """<li style="list-style-type: demical;">{p}</li>""".format(
                **{'p': item[u'目标']['title'][0]['plain_text']})

    def render_technology(self, database):
        _template = """
            <li style="list-style-type: upper-roman; ">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'方案输出' or _type == u'技术预研':
                self._technology += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_review(self, database):
        _template = """
            <li style="list-style-type: upper-roman; ">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'代码评审' or _type == u'配置管理':
                self._review += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_maintainance(self, database):
        _template = """
            <li style="list-style-type: upper-roman; ">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:blue;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'项目维护' or _type == u'IT运维':
                self._maintainance += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_patent(self, database):
        _template = """
            <li style="list-style-type: upper-roman;">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'知识产权建设':
                self._patent += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_techissues(self, database):
        _template = """
            <li style="list-style-type: upper-roman; ">
            <span style="font-weight: bold;">{content}</span>&nbsp;
            <span style="color:red;">{problem}</span>&nbsp;
            <span style="color:green;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'项目支撑' or _type == u'技术问题指导':
                self._tech_issues += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'problem': self.content_parse_richtext(item, u'问题'),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_duties(self, database):
        _template = """
            <li style="list-style-type: upper-roman;">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'技术管理' or _type == u'内部支撑':
                self._duties += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_programming_work(self, database):
        _template = """
            <li style="list-style-type: upper-roman;">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'产品开发':
                self._programming_tasks += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_reading_share(self, database):
        _template = """
            <li style="list-style-type: upper-roman;">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """
        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'总结输出' or _type == u'会议记录' or _type == u'复盘分享':
                self._reading_share += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def render_directions(self, database):
        _template = """
            <li style="list-style-type: upper-roman;">
            <span style="font-weight: bold;">{content}</span>
            &nbsp;<span style="color:green;">{solve}</span>
            &nbsp;<span style="color:blue;">{summary}</span></li>
        """

        for node in database['results']:
            item = node['properties']
            _type = self.content_parse_type(item)
            if _type == u'技术分享' or _type == u'好书分享' or _type == u'好文章分享' or _type == u'工作指导':
                self._directions += _template.format(
                    **{
                        'content': self.content_parse_title(item),
                        'summary': self.content_parse_richtext(
                            item, u'评审、复盘、总结'),
                        'solve': self.content_parse_richtext(item, u'解决方法')
                    })

    def parse_week_tasks(self, database, weekdatestr):
        self.render_technology(database)
        self.render_patent(database)
        self.render_review(database)
        self.render_duties(database)
        self.render_techissues(database)
        self.render_maintainance(database)
        self.render_programming_work(database)
        self.render_reading_share(database)
        self.render_directions(database)

    def render_itor_database(self, client, dbid, title, database, force):
        try:
            for t in title:
                # Use BT-Panel timer task to trigger
                if not force:
                    if not (self.datetime_now.day >= 1
                            and self.datetime_now.day <= 6):
                        clslog.warning(
                            "Month report will not trigger except the day 1")
                        break

                plain_text = t['plain_text'].strip().replace(' → ', '~')
                """Reading list"""
                if plain_text == u"读书如斯":
                    self.render_reading_books(client, database)
                    break
                if plain_text == u"网络万象":
                    self.render_study_note(client, database)
                    break
                if plain_text == u"公司整体目标":
                    self.render_maintarget(database)
                    break
                if plain_text == u"团队技术方向和目标":
                    self.render_teamtarget(database)
                    break
                """Week report parse"""
                plain_text_head = t['plain_text'][0:3]  # Filter for week tasks
                value = re.compile(r'^[0-9][0-9][0-9]$')
                if t['type'] == 'mention':
                    sdate = datetime.datetime.fromisoformat(
                        t['mention']['date']['start'])
                    edate = datetime.datetime.fromisoformat(
                        t['mention']['date']['end'])
                    weekdatestr = """{s}===>{e}""".format(
                        **{
                            's': sdate.strftime("%Y-%m-%d"),
                            'e': edate.strftime("%Y-%m-%d")
                        })
                    """Skip useless databases
                    """
                    if sdate == edate:
                        break
                    if value.match(plain_text_head):
                        if self.week_belongs(sdate, edate):
                            click.secho("解析{}工作任务".format(weekdatestr),
                                        fg='blue')
                            self.parse_week_tasks(database, weekdatestr)
                        else:
                            clslog.info(
                                "Week {} report N/A".format(weekdatestr))
                            break
        except Exception as e:
            clslog.critical("Exception @{}: {}".format(
                e.__traceback__.tb_lineno, e))
            traceback.print_exc(e)

    def render_html(self, title):
        """Render html form template

        Note that some of the email display methods only support inline-css style,
        This method support inline-css for table headers and rows.

        Args:
            title (str): Title of html and email subject
        """
        clslog.info("Render[Inline-CSS] html for {}".format(title))

        with open(self.wbname + '.html', encoding='utf-8', mode='w') as f:

            html = string.Template(monthreport.mr_template)

            f.write(
                html.safe_substitute({
                    "title": self._title,
                    "book": self._book,
                    "book_content": self._book_content,
                    "study": self._study_list,
                    "main_target": self._main_target,
                    "team_target": self._team_target,
                    "technology": self._technology,
                    "patent": self._patent,
                    "review": self._review,
                    "technology_issues": self._tech_issues,
                    "maintainance": self._maintainance,
                    "duties": self._duties,
                    "programming_work": self._programming_tasks,
                    "reading_share": self._reading_share,
                    "direction": self._directions,
                    "user": self._user,
                    "department": self._department
                }))

    def render_study_html(self, title):
        """Render html form template

        Note that some of the email display methods only support inline-css style,
        This method support inline-css for table headers and rows.

        Args:
            title (str): Title of html and email subject
        """
        clslog.info(
            "Render study content[Inline-CSS] html for {}".format(title))

        html = string.Template(monthreport.mstudy_template)

        return html.safe_substitute({
            "title": title,
            "book": self._book,
            "book_content": self._book_content,
            "study": self._study_list,
            "user": self._user,
            "department": self._department
        })
