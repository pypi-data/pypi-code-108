import markdown
import Famcy
import json

class displayParagraph(Famcy.FamcyBlock):
    """
    Represents the block to display
    paragraph. 
    """
    def __init__(self):
        self.value = displayParagraph.generate_template_content()
        super(displayParagraph, self).__init__()
        self.init_block()

    @classmethod
    def generate_template_content(cls):
        return {
                "title": "displayParagraph",
                "content": '''
**Nexuni 会社ウェブサイトの案内** 

    1. 希望能讓來到Nexuni的新朋友都能夠快速地學習並瞭解我們工作時會使用到的軟體、程式語言、工具等等。
    2. 作為能力考核的依據
    3. 整合所有公司內部的管理工具，如發票上傳、PO申請、報帳工具、打卡記錄等

快速入門:

    * 點擊總覽 -> 訓練網介紹（可以看到本網頁的所有的內容簡介
    * 點擊相關訓練內容 -> 開始練習
    * 點擊總覽 -> 學習進度裡面的進度報告（可以看到練習的成果）

（網頁內容的版權皆為Nexuni Co. 擁有）
'''
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "displayParagraph"

        h3_temp = Famcy.h3()
        h4_temp = Famcy.h4()

        self.body.addElement(h3_temp)
        self.body.addElement(h4_temp)

    def render_inner(self):
        self.body.children[0].innerHTML = self.value["title"]
        self.body.children[1].innerHTML = markdown.markdown(self.value["content"])

        return self.body
