import binascii
import getpass
import hashlib
import json
import os
import shutil
import time
from typing import Any


def openWindowsFolder(folder: str):
    os.system(f"start explorer {folder}")


def getPath(basePath: str = "", *parList: str):
    return os.path.abspath(os.path.join(basePath, *parList))


def getUserPath(*parList: str):
    return getPath(os.path.expanduser("~"), *parList)


def getDesktopPath(*parList: str):
    return getUserPath("Desktop", *parList)


def writeFile(file: str, data: str, encoding: str = 'utf8', newline: str = '\n'):
    makeFolder(os.path.dirname(file))
    with open(file, 'w', encoding=encoding, newline=newline) as f:
        f.write(data)
        f.flush()
        f.close()
    return file


def writeBinFile(file: str, data: bytes):
    makeFolder(os.path.dirname(file))
    with open(file, 'wb') as f:
        f.write(data)
        f.flush()
        f.close()
    return file


def readFile(file: str, encoding: str = 'utf8', newline: str = '\n'):
    with open(file, 'r', encoding=encoding, newline=newline) as f:
        data = f.read()
        f.close()
    return data


def readBinFile(file: str):
    with open(file, 'rb') as f:
        data = f.read()
        f.close()
    return data


def jsonDumps(value: Any):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def remove(fileOrFolder: str):
    if os.path.isfile(fileOrFolder):
        os.remove(fileOrFolder)
    elif os.path.isdir(fileOrFolder):
        shutil.rmtree(fileOrFolder)


def makeFolder(folder: str):
    if not os.path.exists(folder):
        os.makedirs(folder)


def clearFolder(*folderAry: str):
    for folder in folderAry:
        if os.path.isdir(folder):
            for target in getFileAndFolderList(folder):
                remove(target)


def copy(fromFileOrFolder: str, toFileOrFolder: str):
    if os.path.isfile(fromFileOrFolder):
        fromFile = fromFileOrFolder
        toFile = toFileOrFolder
        makeFolder(os.path.dirname(toFile))
        shutil.copyfile(fromFile, toFile)
    elif os.path.isdir(fromFileOrFolder):
        fromFolder = fromFileOrFolder
        toFolder = toFileOrFolder
        makeFolder(os.path.dirname(toFolder))
        shutil.copytree(fromFolder, toFolder)


def getFileExtName(file: str):
    '''返回文件扩展名（不包含.）'''
    if "." in file:
        return file[file.rfind('.') + 1:].lower()
    else:
        return None


def getFileBaseName(file: str):
    fileName = os.path.basename(file)
    if "." in fileName:
        return fileName[:fileName.rfind(".")]
    else:
        return fileName


def getFileList(folder: str):
    ary: list[str] = []
    for targetName in os.listdir(folder):
        target = os.path.join(folder, targetName)
        if os.path.isfile(target):
            ary.append(target)
    return ary


def getFolderList(folder: str):
    ary: list[str] = []
    for targetName in os.listdir(folder):
        target = os.path.join(folder, targetName)
        if os.path.isdir(target):
            ary.append(target)
    return ary


def getFileAndFolderList(folder: str):
    ary: list[str] = []
    for targetName in os.listdir(folder):
        target = os.path.join(folder, targetName)
        ary.append(target)
    return ary


def getAllFileList(folder: str):
    ary: list[str] = []
    for targetName in getFileAndFolderList(folder):
        target = os.path.join(folder, targetName)
        if os.path.isfile(target):
            ary.append(target)
        elif os.path.isdir(target):
            ary.extend(getAllFileList(target))
    return ary


def getAllFolderList(folder: str):
    ary: list[str] = []
    for targetName in getFileAndFolderList(folder):
        target = os.path.join(folder, targetName)
        if os.path.isdir(target):
            ary.append(target)
            ary.extend(getAllFolderList(target))
    return ary


def getAllFileAndFolderList(folder: str):
    ary: list[str] = []
    for targetName in getFileAndFolderList(folder):
        target = os.path.join(folder, targetName)
        if os.path.isfile(target):
            ary.append(target)
        elif os.path.isdir(target):
            ary.append(target)
            ary.extend(getAllFileAndFolderList(target))
    return ary


def getFileMD5(file: str):
    return getDataMD5(readBinFile(file))


def getStrMD5(content: str):
    return getDataMD5(content.encode())


def getDataMD5(data: bytes):
    return hashlib.md5(data).hexdigest()


def getFileCRC(file: str):
    return getDataCRC(readBinFile(file))


def getStrCRC(content: str):
    return getDataCRC(content.encode())


def getDataCRC(data: bytes):
    return hex(binascii.crc32(data))[2:].zfill(8)


def getClassFullName(clazz: type):
    return f"{clazz.__module__}.{clazz.__name__}"


def makeTempWorkspace(clearOneDayBefore: bool = True):
    baseWorkspaceFoler = getPath(os.path.expanduser("~"), "beniutils.workspace")
    makeFolder(baseWorkspaceFoler)
    nowTime = int(time.time() * 10000000)
    if clearOneDayBefore:
        oneDayBeforeTime = nowTime - 24 * 60 * 60 * 10000000
        for folderName in os.listdir(baseWorkspaceFoler):
            if int(folderName) < oneDayBeforeTime:
                remove(getPath(baseWorkspaceFoler, folderName))
    for i in range(100):
        nowTime += i
        workspaceFolder = getPath(baseWorkspaceFoler, str(nowTime))
        if not os.path.exists(workspaceFolder):
            makeFolder(workspaceFolder)
            return workspaceFolder
    raise Exception("创建tempWorkspace目录失败")


def syncFolder(fromFolder: str, toFolder: str):
    # 删除多余目录
    toSubFolderList = sorted(getAllFolderList(toFolder), reverse=True)
    for toSubFolder in toSubFolderList:
        fromSubFolder = os.path.join(fromFolder, toSubFolder[len(toFolder + os.path.sep):])
        if not os.path.isdir(fromSubFolder):
            remove(toSubFolder)
    # 删除多余文件
    toFileList = getAllFileList(toFolder)
    for toFile in toFileList:
        fromFile = os.path.join(fromFolder, toFile[len(toFolder + os.path.sep):])
        if not os.path.isfile(fromFile):
            remove(toFile)
    # 同步文件
    fromFileList = getAllFileList(fromFolder)
    for fromFile in fromFileList:
        toFile = os.path.join(toFolder, fromFile[len(fromFolder + os.path.sep):])
        if os.path.isfile(toFile):
            fromData = readBinFile(fromFile)
            toData = readBinFile(toFile)
            if fromData != toData:
                writeBinFile(toFile, fromData)
        else:
            remove(toFile)
            copy(fromFile, toFile)
    # 添加新增目录
    fromSubFolderList = sorted(getAllFolderList(fromFolder), reverse=True)
    for fromSubFolder in fromSubFolderList:
        toSubFolder = os.path.join(toFolder, fromSubFolder[len(fromFolder + os.path.sep):])
        if not os.path.isdir(toSubFolder):
            makeFolder(toSubFolder)


_DEFAULT_FMT = '%Y-%m-%d %H:%M:%S'


def timestampByStr(value: str, fmt: str = _DEFAULT_FMT):
    return int(time.mktime(time.strptime(value, fmt)))


def strByTimestamp(timestamp: float = time.time(), fmt: str = _DEFAULT_FMT):
    ary = time.localtime(timestamp)
    return time.strftime(fmt, ary)


def hold(msg: str | None = None, showInput: bool = True, *exitValueList: str):
    msg = msg or "测试暂停，输入exit可以退出"
    exitValueList = exitValueList or ("exit",)
    inputFunc = showInput and input or getpass.getpass
    while True:
        inputValue = inputFunc(f"{msg}：")
        if inputValue in exitValueList:
            return inputValue


IntFloatStr = int | float | str
IntFloat = int | float


def toFloat(value: IntFloatStr, default: float):
    result = default
    try:
        result = float(value)
    except:
        pass
    return result


def toInt(value: IntFloatStr, default: int):
    result = default
    try:
        result = int(value)
    except:
        pass
    return result


def getLimitedValue(value: IntFloat, minValue: IntFloat, maxValue: IntFloat):
    value = min(value, maxValue)
    value = max(value, minValue)
    return value


_xPar = "0123456789abcdefghijklmnopqrstuvwxyz"


def intToX(value: int) -> str:
    n = len(_xPar)
    return ((value == 0) and "0") or (intToX(value // n).lstrip("0") + _xPar[value % n])


def xToInt(value: str):
    return int(value, len(_xPar))


# def scrapy(urlList, parseFun, extendSettings=None):

#     from scrapy.crawler import CrawlerProcess
#     from scrapy.utils.log import get_scrapy_root_handler
#     import scrapy.http

#     resultList = []
#     resultUrlList = urlList[:]

#     class TempSpider(scrapy.Spider):

#         name = str(random.random())
#         start_urls = urlList

#         def parse(self, response):
#             itemList, urlList = parseFun(response)
#             if itemList:
#                 resultList.extend(itemList)
#             if urlList:
#                 for url in urlList:
#                     resultUrlList.append(url)
#                     yield scrapy.http.Request(url)

#     settings = {
#         'LOG_LEVEL': logging.INFO,
#         'LOG_FORMAT': '%(asctime)s %(levelname)-1s %(message)s',
#         'LOG_DATEFORMAT': '%Y-%m-%d %H:%M:%S',
#         'DOWNLOAD_TIMEOUT': 5,
#         'CONCURRENT_REQUESTS': 50,
#         'RETRY_HTTP_CODES': [514],
#         'RETRY_TIMES': 5,
#         # 'ITEM_PIPELINES': {
#         #    ptGetClassFullName( TempPipeline ): 300,
#         # },
#     }
#     if extendSettings:
#         for k, v in extendSettings.items():
#             settings[k] = v

#     process = CrawlerProcess(settings)
#     process.crawl(TempSpider)
#     process.start()

#     rootHandler = get_scrapy_root_handler()
#     if rootHandler:
#         rootHandler.close()

#     # 函数执行后再调用logging都会有2次显示在控制台
#     logging.getLogger().handlers = []

#     return resultList, resultUrlList
