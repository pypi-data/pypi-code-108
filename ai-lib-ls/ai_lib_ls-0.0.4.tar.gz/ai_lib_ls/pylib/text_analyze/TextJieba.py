# -*- coding: utf-8 -*-
# 注意上面这个非常重要(# -*- coding: utf-8 -*-) 不能忽略否则会报错: Non-UTF-8 code

import jieba

class JieBaCut:

    def fenci(self, text):
        ''' 精确模式分词 '''
        seg_list = jieba.cut(text, cut_all=False)
        return '分词精确模式:' + '/'.join(seg_list)

    def ci_index(self, text):
        '''获取词所在的下标位置'''
        words = jieba.tokenize(text)
        for tk in words:
            print("word %s\t\t start: %d \t\t end:%d" % (tk[0], tk[1], tk[2]))

    def ci_pin(self, text):
        '''统计词的频率'''
        # 分词,切割
        words = jieba.lcut(text)
        counts = {}  ## 建立一个数词的字典。key=词，value=词频
        for word in words:
            if len(word) == 1:  ## 单词字的放弃
                continue
            else:
                counts[word] = counts.get(word, 0) + 1

        items = list(counts.items())  ## 转换为列表

        items.sort(key=lambda x: x[1], reverse=True)  ## 按词频进行降序排序
        return items


if __name__ == '__main__':
    jieba_text = JieBaCut()
    text_info = '迎冬奥新机遇向未来”青年体育国际论坛16日在北京新华网媒体创意工厂举行。团中央书记处书记、全国青联副主席傅振邦出席论坛并致辞，北京冬奥组委、有关国际组织和外国青年、体育组织负责人、现役退役运动员代表、体育产业专家学者、青年志愿者代表、大学生代表等70余人参加活动。论坛设主旨发言、圆桌对话等环节，围绕喜迎北京冬奥开幕、促进冰雪运动发展、支持青年创新创业等主题展开讨论交流。北京冬奥组委运动员委员会主席杨扬、北京冬奥组委志愿者部副部长张丽娜围绕“传承冬奥文化，弘扬冬奥精神”做主旨发言。杨扬在发言中强调：“当前世界正面临各种挑战，体育是少数拥有普遍规则的人类活动，这些普遍规则体现了公平、尊重和友谊的价值观。越是在艰难的环境下，人们越需要精神的鼓舞和共同价值的肯定，而体育正具备了这种力量。”联合国难民署驻华代表卢沛赫、印度青年领袖联合会主席苏万等围绕“冬奥的时代精神与青年责任”做主旨发言。中国男子短道速滑运动员武大靖、清华大学团委书记张婷、冬奥会志愿者代表、大学生代表等围绕“冬奥，新时代中国青年精神面貌”以视频形式发言。主旨发言环节后，八位体育相关领域代表围绕“新时代背景下，体育与青年发展的新使命”和“2022北京冬奥，共享发展新机遇”话题展开圆桌对话，交流分享经验。本次论坛由团中央国际联络部指导，中国青年创业就业基金会主办，冠军基金、共青团吉林省委员会、共青团清华大学委员会共同承办。'

    items = jieba_text.ci_pin(text_info)
    print(items)

    '''
     # jieba.enable_paddle()  # 启动paddle模式。 0.40版之后开始支持，早期版本不支持
     strs = ["我来到北京清华大学", "乒乓球拍卖完了", "中国科学技术大学"]
     for str in strs:
         seg_list = jieba.cut(str, use_paddle=True)  # 使用paddle模式
         print("Paddle Mode: " + '/'.join(list(seg_list)))
 
     seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
     print("Full Mode: " + "/ ".join(seg_list))  # 全模式
 
     seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
     print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
 
     seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
     print(", ".join(seg_list))
 
     seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
     print(", ".join(seg_list))
 
     words = jieba.tokenize('我吃酸辣粉')
     for tk in words:
         print("word %s\t\t start: %d \t\t end:%d" % (tk[0], tk[1], tk[2]))
 
     # -------------------------------------------------
     # 分词,切割
     words = jieba.lcut("我吃酸辣粉")  ##jieba包就用了一次
    '''
