import json
import requests

def send(engine, key, context,
        temperature=1,
        topP=0,
        generatedLength=128,
        topK=3,
        presencePenalty=1,
        frequencyPenalty=1,
        repetitionPenalty=1.2,
        noRepeatNgramSize=3
         ):

    if engine == "qa":
        url = "http://open.wudaoai.com/api/paas/model/v1/open/engines/qa/qa-engine-v1"
        params = {
            "inputText": context["prompt"],
            "inputTextDesc": context["promptDesc"],
            "temperature": temperature,
            "topP": topP,
            "generatedLength": generatedLength,
            "topK": topK,
            "abilityType": "qa",
            "presencePenalty": presencePenalty,
            "frequencyPenalty": frequencyPenalty
        }
    elif engine == "writing":
        url = "http://open.wudaoai.com/api/paas/model/v1/open/engines/writing/writing-engine-v1"
        params = {
            "inputText": context["prompt"],
            "temperature": temperature,
            "topP": topP,
            "generatedLength": generatedLength,
            "topK": topK,
            "presencePenalty": presencePenalty,
            "frequencyPenalty": frequencyPenalty
        }
    elif engine == "chat":
        url = "http://open.wudaoai.com/api/paas/model/v1/open/engines/chat/chat-engine-v1"
        params = {
            "inputText": context["prompt"],
            "temperature": temperature,
            "topP": topP,
            "generatedLength": generatedLength,
            "topK": topK,
            "repetitionPenalty": repetitionPenalty,
            "noRepeatNgramSize": noRepeatNgramSize
            }
    elif engine == "couplet":
        url = "http://open.wudaoai.com/api/paas/model/v1/open/engines/couplet/couplet-engine-v1"
        params = {
            "inputText": context["prompt"]
        }
    else:
        print("please choose engine again,'qa'、'writing'、'chat' or 'couplet'.")

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": key,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    }

    response = requests.post(url, data=json.dumps(params), headers=headers)
    if response.status_code == requests.codes.ok:
        print(response.text)




