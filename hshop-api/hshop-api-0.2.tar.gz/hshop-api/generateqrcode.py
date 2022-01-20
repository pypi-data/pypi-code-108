import requests
import qrcode
from os import startfile
from PIL import Image
def generateDownloadQRCode(id, path):
    '''Generates a QR Code with a link to a content download from URL, for usage in FBI.'''

    dID = str(id)
    downloadurl = "https://download4.erista.me/content/"
    req = requests.get(downloadurl + "request?id=" + dID)
    data = req.json()
    token = data["token"]
    completedownloadurl = downloadurl + dID + "?token=" + token
    print("URL: " + completedownloadurl)

    qr = qrcode.make(completedownloadurl)
    qrimagepath = path + dID + ".png"
    qr.save(qrimagepath)
    print("QR Code saved to: " + qrimagepath)
    startfile(qrimagepath)