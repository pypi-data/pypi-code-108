from django.test import TestCase

import os
from base64 import b64decode
from uuid import uuid4
from social_layer.mediautils.utils import get_img_orientation, check_if_img

class MediaUtilsTestCase(TestCase):
    def setUp(self):
        self.dummy_file = '/tmp/{}'.format(uuid4().hex)

    def tearDown(self):
        try:
            os.remove(self.dummy_file)
        except FileNotFoundError:
            pass

    def test_get_img_orientation_landscape(self):
        """ test detection of a landscape image """
        with open(self.dummy_file, 'bw') as f:
            f.write(b64decode(landscape))
        orient = get_img_orientation(self.dummy_file)
        self.assertEqual(orient, 'landscape')

    def test_get_img_orientation_portrait(self):
        """ test detection of a portrait image """
        with open(self.dummy_file, 'bw') as f:
            f.write(b64decode(portrait))
        orient = get_img_orientation(self.dummy_file)
        self.assertEqual(orient, 'portrait')

    def test_check_if_img(self):
        """ unitary test for function that checks if file is image """
        with open(self.dummy_file, 'bw') as f:
            f.write(b64decode(portrait))
        self.assertTrue(check_if_img(self.dummy_file))
        # now with a negative
        with open(self.dummy_file, 'bw') as f:
            f.write(b'garbage')
        self.assertFalse(check_if_img(self.dummy_file))
        # A Gif file
        with open(self.dummy_file, 'bw') as f:
            f.write(b64decode(small_gif))
        self.assertTrue(check_if_img(self.dummy_file))


# The following base64 are small media and videos to be used on tests
# Small PNG
small_image = "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAEUlEQVQImWNgYGD4z4AE/gMADwMB/414xEUAAAAASUVORK5CYII="
# Portrait PNG
portrait = """iVBORw0KGgoAAAANSUhEUgAAAAIAAAAECAMAAACTMR4LAAADAFBMVEUAAAAAADMAAGYAAJkAAMwA
AP8AMwAAMzMAM2YAM5kAM8wAM/8AZgAAZjMAZmYAZpkAZswAZv8AmQAAmTMAmWYAmZkAmcwAmf8A
zAAAzDMAzGYAzJkAzMwAzP8A/wAA/zMA/2YA/5kA/8wA//8zAAAzADMzAGYzAJkzAMwzAP8zMwAz
MzMzM2YzM5kzM8wzM/8zZgAzZjMzZmYzZpkzZswzZv8zmQAzmTMzmWYzmZkzmcwzmf8zzAAzzDMz
zGYzzJkzzMwzzP8z/wAz/zMz/2Yz/5kz/8wz//9mAABmADNmAGZmAJlmAMxmAP9mMwBmMzNmM2Zm
M5lmM8xmM/9mZgBmZjNmZmZmZplmZsxmZv9mmQBmmTNmmWZmmZlmmcxmmf9mzABmzDNmzGZmzJlm
zMxmzP9m/wBm/zNm/2Zm/5lm/8xm//+ZAACZADOZAGaZAJmZAMyZAP+ZMwCZMzOZM2aZM5mZM8yZ
M/+ZZgCZZjOZZmaZZpmZZsyZZv+ZmQCZmTOZmWaZmZmZmcyZmf+ZzACZzDOZzGaZzJmZzMyZzP+Z
/wCZ/zOZ/2aZ/5mZ/8yZ///MAADMADPMAGbMAJnMAMzMAP/MMwDMMzPMM2bMM5nMM8zMM//MZgDM
ZjPMZmbMZpnMZszMZv/MmQDMmTPMmWbMmZnMmczMmf/MzADMzDPMzGbMzJnMzMzMzP/M/wDM/zPM
/2bM/5nM/8zM////AAD/ADP/AGb/AJn/AMz/AP//MwD/MzP/M2b/M5n/M8z/M///ZgD/ZjP/Zmb/
Zpn/Zsz/Zv//mQD/mTP/mWb/mZn/mcz/mf//zAD/zDP/zGb/zJn/zMz/zP///wD//zP//2b//5n/
/8z///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAABlenwdAAABAHRSTlP/////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
//////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG8mZagAA
AAlwSFlzAAAOxAAADsQBlSsOGwAAABFJREFUCJljuM7AwHCdAUwCABQ0A12jAvcIAAAAAElFTkSu
QmCC"""
# Landscape PNG
landscape = """iVBORw0KGgoAAAANSUhEUgAAAAQAAAACCAMAAABIdo1RAAADAFBMVEUAAAAAADMAAGYAAJkAAMwA
AP8AMwAAMzMAM2YAM5kAM8wAM/8AZgAAZjMAZmYAZpkAZswAZv8AmQAAmTMAmWYAmZkAmcwAmf8A
zAAAzDMAzGYAzJkAzMwAzP8A/wAA/zMA/2YA/5kA/8wA//8zAAAzADMzAGYzAJkzAMwzAP8zMwAz
MzMzM2YzM5kzM8wzM/8zZgAzZjMzZmYzZpkzZswzZv8zmQAzmTMzmWYzmZkzmcwzmf8zzAAzzDMz
zGYzzJkzzMwzzP8z/wAz/zMz/2Yz/5kz/8wz//9mAABmADNmAGZmAJlmAMxmAP9mMwBmMzNmM2Zm
M5lmM8xmM/9mZgBmZjNmZmZmZplmZsxmZv9mmQBmmTNmmWZmmZlmmcxmmf9mzABmzDNmzGZmzJlm
zMxmzP9m/wBm/zNm/2Zm/5lm/8xm//+ZAACZADOZAGaZAJmZAMyZAP+ZMwCZMzOZM2aZM5mZM8yZ
M/+ZZgCZZjOZZmaZZpmZZsyZZv+ZmQCZmTOZmWaZmZmZmcyZmf+ZzACZzDOZzGaZzJmZzMyZzP+Z
/wCZ/zOZ/2aZ/5mZ/8yZ///MAADMADPMAGbMAJnMAMzMAP/MMwDMMzPMM2bMM5nMM8zMM//MZgDM
ZjPMZmbMZpnMZszMZv/MmQDMmTPMmWbMmZnMmczMmf/MzADMzDPMzGbMzJnMzMzMzP/M/wDM/zPM
/2bM/5nM/8zM////AAD/ADP/AGb/AJn/AMz/AP//MwD/MzP/M2b/M5n/M8z/M///ZgD/ZjP/Zmb/
Zpn/Zsz/Zv//mQD/mTP/mWb/mZn/mcz/mf//zAD/zDP/zGb/zJn/zMz/zP///wD//zP//2b//5n/
/8z///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAABlenwdAAABAHRSTlP/////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
//////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG8mZagAA
AAlwSFlzAAAOxAAADsQBlSsOGwAAABFJREFUCJljuM5wnYEBiK8DABDWA10njQoFAAAAAElFTkSu
QmCC"""
# A Gif file
small_gif = """R0lGODlhAgACAPAAAAAAAAAAACH5BAEAAAEALAAAAAACAAIAAAIDRAIFADs="""
# Small Mp4 Video
small_video = """AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAAAsxtZGF0AAACrQYF//+p
3EXpvebZSLeWLNgg2SPu73gyNjQgLSBjb3JlIDE2MCByMzAxMSBjZGU5YTkzIC0gSC4yNjQvTVBF
Ry00IEFWQyBjb2RlYyAtIENvcHlsZWZ0IDIwMDMtMjAyMCAtIGh0dHA6Ly93d3cudmlkZW9sYW4u
b3JnL3gyNjQuaHRtbCAtIG9wdGlvbnM6IGNhYmFjPTEgcmVmPTMgZGVibG9jaz0xOjA6MCBhbmFs
eXNlPTB4MzoweDExMyBtZT1oZXggc3VibWU9NyBwc3k9MSBwc3lfcmQ9MS4wMDowLjAwIG1peGVk
X3JlZj0xIG1lX3JhbmdlPTE2IGNocm9tYV9tZT0xIHRyZWxsaXM9MSA4eDhkY3Q9MSBjcW09MCBk
ZWFkem9uZT0yMSwxMSBmYXN0X3Bza2lwPTEgY2hyb21hX3FwX29mZnNldD00IHRocmVhZHM9MSBs
b29rYWhlYWRfdGhyZWFkcz0xIHNsaWNlZF90aHJlYWRzPTAgbnI9MCBkZWNpbWF0ZT0xIGludGVy
bGFjZWQ9MCBibHVyYXlfY29tcGF0PTAgY29uc3RyYWluZWRfaW50cmE9MCBiZnJhbWVzPTMgYl9w
eXJhbWlkPTIgYl9hZGFwdD0xIGJfYmlhcz0wIGRpcmVjdD0xIHdlaWdodGI9MSBvcGVuX2dvcD0w
IHdlaWdodHA9MiBrZXlpbnQ9MjUwIGtleWludF9taW49MjUgc2NlbmVjdXQ9NDAgaW50cmFfcmVm
cmVzaD0wIHJjX2xvb2thaGVhZD00MCByYz1jcmYgbWJ0cmVlPTEgY3JmPTIzLjAgcWNvbXA9MC42
MCBxcG1pbj0wIHFwbWF4PTY5IHFwc3RlcD00IGlwX3JhdGlvPTEuNDAgYXE9MToxLjAwAIAAAAAP
ZYiEACv//vXb8yysZmf/AAAC8W1vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAAAoAAEAAAEA
AAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAIAAAIbdHJhawAAAFx0a2hkAAAAAwAAAAAAAAAAAAAAAQAAAAAAAAAo
AAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAACAAAA
AgAAAAAAJGVkdHMAAAAcZWxzdAAAAAAAAAABAAAAKAAAAAAAAQAAAAABk21kaWEAAAAgbWRoZAAA
AAAAAAAAAAAAAAAAMgAAAAIAVcQAAAAAAC1oZGxyAAAAAAAAAAB2aWRlAAAAAAAAAAAAAAAAVmlk
ZW9IYW5kbGVyAAAAAT5taW5mAAAAFHZtaGQAAAABAAAAAAAAAAAAAAAkZGluZgAAABxkcmVmAAAA
AAAAAAEAAAAMdXJsIAAAAAEAAAD+c3RibAAAAJpzdHNkAAAAAAAAAAEAAACKYXZjMQAAAAAAAAAB
AAAAAAAAAAAAAAAAAAAAAAACAAIASAAAAEgAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAABj//wAAADRhdmNDAfQACv/hABdn9AAKkZsr8fHwgAAAAwCAAAAZB4kSywEABmjr
48RIRP/4+AAAAAAYc3R0cwAAAAAAAAABAAAAAQAAAgAAAAAcc3RzYwAAAAAAAAABAAAAAQAAAAEA
AAABAAAAFHN0c3oAAAAAAAACxAAAAAEAAAAUc3RjbwAAAAAAAAABAAAAMAAAAGJ1ZHRhAAAAWm1l
dGEAAAAAAAAAIWhkbHIAAAAAAAAAAG1kaXJhcHBsAAAAAAAAAAAAAAAALWlsc3QAAAAlqXRvbwAA
AB1kYXRhAAAAAQAAAABMYXZmNTguNDUuMTAw"""
