import json
from myLabTools.tools import JsonTool
from myLabTools.db.mongodb import MongoDB



class CNKIArticleQuery:
    def __init__(self,db_config):

        self.history_article_mongodb = MongoDB(**db_config)

    def get_head(self,article_id):
        head = []
        head_info = []
        for h in self.history_article_mongodb.select_iter(table_name="article_head",field_names_list=["title","authors","abs","keywords"],query={"article_id":article_id}):
            head_info = h

        if len(head_info) > 0:
            title,authors,abs_str,keywords = head_info
            head ={
                "title":title,
                "authors":authors.split("##"),
                "abs":abs_str,
                "keywords":keywords.split("##")
            }
        return head

    def get_refs(self,article_id):
        # 获取文章的参考文献
        refs_info = {}

        # sql_str = "select ref_id, ref_text, ref_type, related_book, entity  from article_back_v2 where article_id = '{}'".format(article_id)
        # refs = history_article_mysqldb.select_from_db(sql_str)
        for ref_info in self.history_article_mongodb.select_iter(table_name="article_back_v2",field_names_list=["ref_id", "ref_text", "ref_type", "related_book", "entity"],query={"article_id":article_id}):
            ref_id, ref_text, ref_type, related_book, entity = ref_info
            refs_info[ref_id] = {
                "text":ref_text,
                "type":ref_type,
                "related_book":related_book,
                "entity":entity
            }
        return refs_info

    def get_section(self,article_id):
        # sql_str = "select section_id, text , content_type from article_section where article_id = '{}'".format(article_id)
        # sections = history_article_mysqldb.select_from_db(sql_str)
        sections_info = {}
        for row in self.history_article_mongodb.select_iter(table_name="article_section",field_names_list=["section_id", "text" , "content_type"],query={"article_id":article_id}):
            section_id, text , content_type = row
            sections_info[section_id] = {
                "text":text,
                "content_type":content_type
            }
        return sections_info
    def get_all_info(self,article_id,head_info = True,ref_info = True):
        return self.get_article_sents(article_id,head_info,ref_info)

    def get_article_sents(self,article_id,head_info = True,ref_info = True):
        # 获取文章的正文

        fields = ["section_id" , "para_id" , "sent_id" , "text" , "ents_list" , "ents_stat" , "has_book_mark" , "has_book_ents" , "citaions_id_list" , "has_citations" , "cls_type" , "discourse_tag" , "discourse_cause" , "discourse_effect" , "opinion_holder"]
        
        body = {}

        sections_info = self.get_section(article_id)


        for row in self.history_article_mongodb.select_iter(table_name="article_sents_v5",field_names_list=fields,query={"article_id":article_id}):
            section_id , para_id , sent_id , text , ents_list , ents_stat , has_book_mark , has_book_ents , citaions_id_list , has_citations , cls_type , discourse_tag , discourse_cause , discourse_effect , opinion_holder = row
            temp = {
                        "sent":text,
                        "type":cls_type
                    }
            entity_list = json.loads(ents_list)
            if len(entity_list) > 0 :
                temp["entity"] = entity_list

            if section_id not in body.keys():
                body[section_id] = {
                    "section_info":sections_info[section_id]  if not section_id == "0" else "",
                    "section_id":section_id,
                    "paras_info":{}
                }
            
            para_info = body[section_id]["paras_info"].get(para_id,[])
            para_info.append(temp)
            body[section_id]["paras_info"][para_id] = para_info
        body_info = dict(list(sorted(body.items(), key=lambda item:int(item[0]), reverse=False)))
        for sect_id ,sect_info in body_info.items():
            para_info = sect_info["paras_info"]
            para_info = dict(list(sorted(para_info.items(), key=lambda item:int(item[0]), reverse=False)))
            sect_info["paras_info"] = list(para_info.values())
        body_info = list(body_info.values())

        if head_info:
            head = self.get_head(article_id=article_id)
        else:
            head = {}
        
        if ref_info:
            refs_info = self.get_refs(article_id=article_id)
        else:
            refs_info = {}


        return {
            "head":head,
            "body":body_info,
            "back":refs_info
        }
    



if __name__ == "__main__":
    article_id = "afsx199904002"
    json_tool = JsonTool()
    cnki_a_q = CNKIArticleQuery()
    r = cnki_a_q.get_all_info(article_id)
    print(json_tool.dump_str(r))
