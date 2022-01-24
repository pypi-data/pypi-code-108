from pprint import pprint
from requests import post

username = "eclair.c@droidtown.co"
apikey   = "ZnGXwO1emaw$z$Yrkp-Uo-VF3AO+Kvj"

#url = "https://api.droidtown.co/Articut/API/"
#payload = {
    #"username": username,
    #"api_key" : apikey,
    #"input_str": "人工智慧導入至臨床流程中，代表著醫師將有更多時間和病患討論病情，以制定客製化精準的放射治療，帶來更溫暖人性化的癌症治療，讓治療中的病患更為安心。未來如搭配雲端服務，人工智慧將使得醫療資源不豐沛的偏遠地區，亦可得到世界級的腫瘤圈選效果。"
#}

#response = post(url, json=payload)
#resultPOS = response.json()["result_pos"]

#pprint(resultPOS)

#url = "https://api.droidtown.co/Articut/Addons/"
#payload = {
    #"username": username,
    #"api_key" : apikey,
    #"result_pos": ["".join(resultPOS)],
    #"func": ["get_verb_stem"],
    #"index_with_pos": True
#}


#response = post(url, json=payload)

#pprint(response.json())

from ArticutAPI import Articut

articut = Articut(username, apikey)

#inputSTR = """楊進勝犯血液中酒精濃度達百分之零點零五以上而駕駛動力交通工具罪，
              #處有期徒刑參月，如易科罰金，以新臺幣壹仟元折算壹日。被告楊進勝所
              #為，係犯刑法第185 條之3 第1項第1 款之血液中酒精濃度達百分之0.05
              #以上而駕駛動力交通工具罪。""".replace("\n", "").replace(" ", "")

#resultDICT = articut.parse(inputSTR)
#print(resultDICT)

## getCrime() 取出「法律」名稱 (e.g., 民法、刑法) 以及罪名。
#crimeLIST = articut.LawsToolkit.getCrime(resultDICT)
#pprint(crimeLIST)
## ['刑法', '血液中酒精濃度達百分之零點零五以上而駕駛動力交通工具罪']


## getPenalty() 取出判決文中的刑責
#penaltyLIST = articut.LawsToolkit.getPenalty(resultDICT)
#pprint(penaltyLIST)
## ['有期徒刑參月']


## getLawArticle() 取得法條編號
#lawIndexLIST = articut.LawsToolkit.getLawArticle(resultDICT)
#pprint(lawIndexLIST)
## ['第185 條之3 第1 項第1 款']


#inputSTR = """滿堂紅麻辣鍋！地址:台中市西區台灣大道二段459號14樓"""
#resultDICT = articut.parse(inputSTR)
#pprint(resultDICT)
#city = articut.localRE.getAddressCity(resultDICT)
#pprint(city)
#road = articut.localRE.getAddressRoad(resultDICT)
#pprint(road)

#inputSTR = """我喜歡吃黃色的奇異果"""
#resultDICT = articut.parse(inputSTR)
#pprint(resultDICT)
#color = articut.getColorLIST(resultDICT)
#pprint(color)

#inputSTR = "《小糧倉》菜單販售品項十分多元，雞白湯拉麵、咖哩飯、鐵板漢堡排定食等。"
#resultDICT = articut.parse(inputSTR)
#pprint(resultDICT)
#nerDICT = articut.NER.getFood(resultDICT)
#pprint(nerDICT)

#inputSTR = "其實早在五月15日開始突破百例之前，這起社區大爆發疫情就已經有一些端倪。上星期我們約好了，這件事情今天下午六點到八點要討論。"
#resultDICT = articut.parse(inputSTR)
#pprint(resultDICT)
#nerDICT = articut.NER.getDate(resultDICT)
#pprint(nerDICT)
#nerDICT = articut.NER.getTime(resultDICT)
#pprint(nerDICT)

#inputSTR = "今年十歲的彼德有一個八歲的弟弟和一個十四歲的姐姐"

#result = articut.parse(inputSTR)
#ageLIST = articut.NER.getAge(result)
#pprint(result)
#pprint(ageLIST)

#result = [{"result_list": [{"result_pos": ["<TIME_year>今年</TIME_year><ENTITY_num>十</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_person>彼德</ENTITY_person><ACTION_verb>有</ACTION_verb><ENTITY_classifier>一個</ENTITY_classifier><ENTITY_num>八</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_pronoun>弟弟</ENTITY_pronoun><FUNC_conjunction>和</FUNC_conjunction><ENTITY_classifier>一個</ENTITY_classifier><ENTITY_num>十四</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_pronoun>姐姐</ENTITY_pronoun>"], "status": True},
#{"result_pos": ["<TIME_year>今年</TIME_year><ENTITY_num>十一</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_person>彼德</ENTITY_person><ACTION_verb>有</ACTION_verb><ENTITY_classifier>一個</ENTITY_classifier><ENTITY_num>七</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_pronoun>弟弟</ENTITY_pronoun><FUNC_conjunction>和</FUNC_conjunction><ENTITY_classifier>一個</ENTITY_classifier><ENTITY_num>十四</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_pronoun>姐姐</ENTITY_pronoun>"], "status": True}], "status": True}]
#ageLIST = articut.NER.getAge(result)
##pprint(result)
#pprint(ageLIST)

#inputSTR = "容量1公升的牛奶紙盒裡只能裝 995.5毫升的水"

#result = articut.parse(inputSTR)
#capacityLIST = articut.NER.getCapacity(result)
#pprint(result)
#pprint(capacityLIST)


#inputSTR = "其實早在五月15日開始突破百例之前，這起社區大爆發疫情就已經有一些端倪。"

#result = articut.parse(inputSTR)
#dateLIST = articut.NER.getDate(result)
#pprint(result)
#pprint(dateLIST)


result = [{"result_list": [{"result_pos": ["<TIME_year>今年</TIME_year><ENTITY_num>十</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_person>彼德</ENTITY_person><ACTION_verb>有</ACTION_verb><ENTITY_classifier>一個</ENTITY_classifier><ENTITY_num>八</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_pronoun>弟弟</ENTITY_pronoun><FUNC_conjunction>和</FUNC_conjunction><ENTITY_classifier>一個</ENTITY_classifier><ENTITY_num>十四</ENTITY_num><ENTITY_noun>歲</ENTITY_noun><FUNC_inner>的</FUNC_inner><ENTITY_pronoun>姐姐</ENTITY_pronoun>"], "status": True},
                           {"result_pos": ["<KNOWLEDGE_addTW>屏東縣大平村5鄰中山路79號</KNOWLEDGE_addTW>", "<KNOWLEDGE_addTW>台東縣大平村5鄰中山路79號</KNOWLEDGE_addTW>"], "status": True},
                           {'result_pos': ['<ENTITY_person>楊進勝</ENTITY_person><ACTION_verb>犯</ACTION_verb><ENTITY_noun>血液</ENTITY_noun><RANGE_locality>中</RANGE_locality><ENTITY_oov>酒精</ENTITY_oov><ENTITY_nouny>濃度</ENTITY_nouny><ACTION_verb>達</ACTION_verb><ENTITY_measurement>百分之零點零五</ENTITY_measurement><RANGE_locality>以上</RANGE_locality><FUNC_inner>而</FUNC_inner><ENTITY_nouny>駕駛</ENTITY_nouny><ENTITY_nouny>動力</ENTITY_nouny><ENTITY_noun>交通</ENTITY_noun><ENTITY_nounHead>工具罪</ENTITY_nounHead>', '，', '<ACTION_verb>處</ACTION_verb><MODIFIER>有期</MODIFIER><ENTITY_nounHead>徒刑</ENTITY_nounHead><TIME_month>參月</TIME_month>', '，', '<FUNC_inter>如</FUNC_inter><ACTION_verb>易科</ACTION_verb><ENTITY_nouny>罰金</ENTITY_nouny>', '，', '<FUNC_inner>以</FUNC_inner><ENTITY_noun>新臺幣</ENTITY_noun><KNOWLEDGE_currency>壹仟元</KNOWLEDGE_currency><ACTION_verb>折算</ACTION_verb><TIME_day>壹日</TIME_day>', '。', '<ENTITY_nouny>被告</ENTITY_nouny><ENTITY_person>楊進勝</ENTITY_person><FUNC_inner>所</FUNC_inner><AUX>為</AUX>', '，', '<AUX>係</AUX><ACTION_verb>犯</ACTION_verb><ENTITY_nouny>刑法</ENTITY_nouny><KNOWLEDGE_lawTW>第185條之3第1項第1款</KNOWLEDGE_lawTW><FUNC_inner>之</FUNC_inner><ENTITY_noun>血液</ENTITY_noun><RANGE_locality>中</RANGE_locality><ENTITY_oov>酒精</ENTITY_oov><ENTITY_nouny>濃度</ENTITY_nouny><ACTION_verb>達</ACTION_verb><ENTITY_measurement>百分之0.05</ENTITY_measurement><RANGE_locality>以上</RANGE_locality><FUNC_inner>而</FUNC_inner><ENTITY_nouny>駕駛</ENTITY_nouny><ENTITY_nouny>動力</ENTITY_nouny><ENTITY_noun>交通</ENTITY_noun><ENTITY_nounHead>工具罪</ENTITY_nounHead>', '。'], 'status': True}],
           "status": True}]
ageLIST = articut.LawsToolkit.getEventRef(result)
#pprint(result)
pprint(ageLIST)

#inputSTR = "屏東縣大平村5鄰中山路79號"

#result = articut.parse(inputSTR)
#pprint(result)

#roadResult = articut.localRE.getAddressRoad(result)
#pprint(roadResult)

#sectionResult = articut.localRE.getAddressSection(result)
#pprint(sectionResult)

#alleyResult = articut.localRE.getAddressAlley(result)
#pprint(alleyResult)

#numberResult = articut.localRE.getAddressNumber(result)
#pprint(numberResult)

#floorResult = articut.localRE.getAddressFloor(result)
#pprint(floorResult)

#roomResult = articut.localRE.getAddressRoom(result)
#pprint(roomResult)