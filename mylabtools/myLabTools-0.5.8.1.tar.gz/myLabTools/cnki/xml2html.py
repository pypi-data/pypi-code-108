# coding: utf-8
import re
import html
import lxml.etree as ET
from os.path import join as pjoin
import pickle
import os
from tqdm import tqdm


xml_input_dir = r"../xmldata"
xml_output_dir = "../htmldata"
xsl_filename = r"../data/article_v3.xsl"
xslt = ET.parse(xsl_filename)
transform = ET.XSLT(xslt)

def get_guandianju():
    gdj_list = pickle.load(open("../data/guandianju_v1_rf_simple.pkl","rb"))
    gdj_dict = {}
    article_sent_dict = {}
    for gdj_sent in gdj_list:
        gdj_dict[gdj_sent["id"]] = gdj_sent["sent"]
        temp = article_sent_dict.get(gdj_sent["article_id"],[])
        temp.append(gdj_sent["id"])
        article_sent_dict[gdj_sent["article_id"]] = temp
    return article_sent_dict,gdj_dict



def add_span(article_id,html_code):
    try:
        sents = [gdj_dict[id] for id in article_sent_dict[article_id]]
    except KeyError as e:
        print(article_id)
        return html_code
    start_span = '<span style="color:red">'
    end_span = "</span>"
    for sent in sents:
        if "REF#" in sent:
            if sent.startswith("REF#") or sent.endswith("#"):
                sent = re.sub("REF#.*?#","",sent)
            else:
                sent = re.sub("REF#(.*?)#",r"<sup> \1 </sup>",sent)
        html_code = html_code.replace(sent,start_span + sent + end_span)
    return html_code


def xml2html(xml_filename = "afsx901.002.xml"):
    dom = ET.parse(pjoin(xml_input_dir,xml_filename))
    newdom = transform(dom)
    html_code = ET.tostring(newdom,pretty_print=True,encoding="utf-8")
    html_code = html.unescape(html_code.decode('utf-8'))
    return html_code
print("load xml2html success")
def xml2spaned_html(xml_filename):
    html_code = xml2html(xml_filename)
    html_code = add_span(xml_filename.replace(".xml",""),html_code)
    with open(pjoin(xml_output_dir,xml_filename.replace("xml","html")),"w+",encoding="utf-8" )as f :
        f.write(html_code)


if __name__ == '__main__':
    article_sent_dict,gdj_dict = get_guandianju()
    print("load data success!")
    for file_name in tqdm(os.listdir(xml_input_dir)):
        xml2spaned_html(file_name)