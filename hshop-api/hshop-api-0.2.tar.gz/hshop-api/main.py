import requests
from generateqrcode import *
from tqdm import tqdm
def download(id, path):
    '''Downloads content from ID (obtained in the details url of content)'''
    dID = str(id)
    downloadpath = str(path)
    downloadurl = "https://download4.erista.me/content/"
    req = requests.get(downloadurl + "request?id=" + dID)
    data = req.json()
    token = data["token"]
    completedownloadurl = downloadurl + dID + "?token=" + token
    print("URL: " + completedownloadurl)
    print ("Downloading content with ID " + dID + ", please wait...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    response = requests.get(completedownloadurl, stream=False, headers=headers)

    with open(downloadpath + dID + ".cia", "wb") as handle:
            for data in tqdm(response.iter_content(),  unit='B', unit_scale=True, unit_divisor=1024):
                handle.write(data)