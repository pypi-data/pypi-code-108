import json
import os

ignore_str="<>'\"{}`\\"

config_dir = ""

default_language = {
    # 0:common
    "0001": "取消",
    "0002": "确认",
    "0003": "保存",
    # 1:begin
    "1001": "Token在服务启动时于控制台以蓝色字体（部分控制台不支持颜色）输出，请注意查看。解锁密码则为之前的设置，默认情况下不可用。",
    "1002": "请输入Token或解锁密码",
    "1003": "提交",
    "1004": "Token输入错误或服务产生错误。若是服务产生错误，您可以查看Console信息。",
    # 2:tree
    "2001": "设置",
    "2002": "启动Git",
    "2003": "退出PyCheer",
    "2004": "关闭PyCheer",
    "2005": "新建文件",
    "2006": "新建文件夹",
    "2007": "重命名",
    "2008": "PyCheer已关闭。",
    "2009": "您真的确定关闭PyCheer吗？\\n所有未保存的更改将丢失！",
    "2010": "您真的确定退出PyCheer吗？\\n这不会停止PyCheer服务，只会使你暂时无法操作。",
    "2011": "新建的文件名：",
    "2012": "新建的文件夹名：",
    "2013": "新建成功。",
    "2014": "新建失败。您可以查看服务控制台输出内容。",
    "2015": "重命名成功。",
    "2016": "重命名失败。您可以查看服务控制台输出内容。",
    "2017": "将",
    "2018": "重命名为：",
    # 3:see
    "3001": "保存中，请稍等",
    "3002": "已保存，就绪",
    "3003": "保存失败，请查看服务控制台或Console",
    # 4:git
    "4001": "文件编辑信息",
    "4002": "刷新",
    "4003": "将所有已编辑的文件移至暂存区",
    "4004": "提交文件",
    "4005": "本地分支信息",
    "4006": "在当前分支的基础上新建本地分支",
    "4007": "远程分支信息",
    "4008": "新建远程分支",
    "4009": "确定切换至${branch}分支吗？",
    "4010": "切换成功。",
    "4011": "切换失败。您可以查看服务控制台输出内容。",
    "4012": "远程分支名：",
    "4013": "远程URL：",
    "4014": "确定删除远程分支${name}吗？",
    "4015": "删除成功。",
    "4016": "删除失败。您可以查看服务控制台输出内容。",
    "4017": "分支名：",
    "4018": "获取文件编辑信息失败。您可以查看服务控制台输出内容。",
    "4019": "暂存成功。",
    "4020": "暂存失败。您可以查看服务控制台输出内容。",
    "4021": "请输入提交信息。",
    "4022": "提交成功。",
    "4023": "提交失败。您可以查看服务控制台输出内容。",
    "4024": "确认拉取远程分支${remote}到本地分支${branch}吗？",
    "4025": "拉取成功。",
    "4026": "拉取失败。您可以查看服务控制台输出内容。",
    "4027": "确认推送本地分支${branch}到远程分支${remote}吗？",
    "4028": "推送成功。",
    "4029": "推送失败。您可以查看服务控制台输出内容。",
    "4030": "没有远程分支。",
    "4031": "当前分支",
    "4032": "切换至此分支",
    "4033": "推送当前分支至这个远程分支",
    "4034": "拉取这个远程分支至当前分支",
    "4035": "删除此远程分支",
    # 5:seeicon
    "5001": "文件（夹）图标（按类型）",
    "5002": "文件（夹）图标（按后缀）",
    # 6:setting
    "6001": "设置项",
    "6002": "设置值",
    "6003": "编辑器主题（对Markdown编辑器无效）",
    "6004": "设置解锁密码",
    "6005": "确认解锁密码",
    "6006": "删除解锁密码",
    "6007": "确认删除",
    "6008": "对于不支持的文本文件的打开方式",
    "6009": "仅以只读模式打开",
    "6010": "尝试以文本文件模式编辑",
    "6011": "设置密码与确认密码不一致。",
    "6012": "设置成功。",
    "6013": "设置失败。您可以查看服务控制台输出内容。",
    "6014": "删除成功。",
    "6015": "删除失败。您可以查看服务控制台输出内容。",
    "6016": "系统语言",
    "6017": "解锁密码可以在begin页面作为token使用",
    "6018": "默认（简体中文）",
    "6019": "选择参考",
    "6020": "PyCheer主题",
    # 7:hello
    "7001": "关于当前运行",
    "7002": "项目",
    "7003": "对应值",
    "7004": "PyCheer版本",
    "7005": "运行目录",
    "7006": "关于本软件",
    "7007": "软件作者",
    "7008": "Gitee地址",
    "7009": "开源许可证",
    "7010": "使用的开源软件",
    "7011": "软件名",
    "7012": "开源许可证",
    "7013": "用途",
    # 8:pycheer-theme
    "8001": "PyCheer主题名称",
    "8002": "操作",
    "8003": "编辑",
    "8004": "应用",
    "8005": "CSS代码",
    "8006": "保存成功。",
    "8007": "保存失败。您可以查看服务控制台输出内容。",
    "8008": "应用成功。",
    "8009": "应用失败。您可以查看服务控制台输出内容。",
    "8010": "新建",
    "8011": "删除",
    "8012": "新建成功。",
    "8013": "新建失败。您可以查看服务控制台输出内容。",
    "8014": "删除成功。",
    "8015": "删除失败。您可以查看服务控制台输出内容。",
    "8016": "确认删除吗？",
}


def set_language_dir(x):
    global language_dir
    language_dir = x
    if not os.path.exists(language_dir):
        os.makedirs(language_dir)


def get_support_language():
    ans = [["default", "￥{LanguageCode:6018}￥"]]
    for i in os.listdir(language_dir):
        if i.endswith(".json"):
            ans.append([i[:-5], i[:-5]])
    return ans


def render_language(input_content, language_type=""):
    if (not language_type) or language_type == 'default':
        for i in default_language.keys():
            input_content = input_content.replace("￥{LanguageCode:%s}￥" % i, default_language[i])
        return input_content
    try:
        language_content = json.loads(
            open(os.path.join(language_dir, "%s.json" % language_type), "r", encoding="utf-8").read())
        for i in language_content.keys():
            wait_for_replace=language_content.get(i, default_language[i])
            for j in ignore_str:
                if not j in default_language[i]:
                    wait_for_replace=wait_for_replace.replace(j,"")
            input_content = input_content.replace("￥{LanguageCode:%s}￥" % i,
                                                  wait_for_replace)
    except Exception as e:
        print(e)
        for i in default_language.keys():
            input_content = input_content.replace("￥{LanguageCode:%s}￥" % i, default_language[i])
    for i in default_language.keys():
        input_content = input_content.replace("￥{LanguageCode:%s}￥" % i, default_language[i])
    return input_content
