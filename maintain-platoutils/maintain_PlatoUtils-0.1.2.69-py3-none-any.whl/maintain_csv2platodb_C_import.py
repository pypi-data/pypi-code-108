import requests
import json


def importData(gUrl,taskId="12"):

    url="{}/api/import/import".format(gUrl)

    payload = json.dumps({
        "taskId": taskId
    })
    headers = {
        'Proxy-Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62',
        'Content-Type': 'application/json',
        'Origin': 'http://9.135.95.249:7001',
        'Referer': 'http://9.135.95.249:7001/import',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '_ga=GA1.1.599074290.1616395720; locale=ZH_CN; Hm_lvt_b9cb5b394fd669583c13f8975ca64ff0=1627524967,1627612772,1627879099,1627959086; nsid=de94b8d118e557ff3e54875946395226; nh=9.135.95.249:13708; nu=root; np=nebula; _gid=GA1.1.1256907028.1628059656; Hm_lpvt_b9cb5b394fd669583c13f8975ca64ff0=1628063018; _gat_gtag_UA_60523578_4=1'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

    return response.json()


if __name__=="__main__":
    
    # test
    ghost="9.135.95.249"
    gport=13708
    guser="root"
    gpassword="nebula"
    gspace="post_skill_school_ianxu"
    gUrl="http://9.135.95.249:7001"

    taskId="12"

    importData(gUrl,taskId=taskId)