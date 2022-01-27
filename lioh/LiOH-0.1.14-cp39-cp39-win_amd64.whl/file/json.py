# json保存一个字典
import json
version_json ={
    "name"         : "LiOH",
    "version"      : "0.1.11",
    "description"  : "A LiOH package",
    "author"       : "LiOH",
    "author_email" : "908716811@qq.com",
    "url"          : "http://www.LiOH.xyz/",
    "packages"     : ['LiOH', 'LiOH.adv']
}# END VERSION_JSON

with open("./tset_version.json","w") as f:
    json.dump(version_json,f)