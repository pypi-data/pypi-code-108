#!/usr/bin/env python3
import os
import re
import sys
import json
import linecache
from pyocs.pyocs_filesystem import PyocsFileSystem


class PyocsAppJson:

    def __init__(self, JsonPath):
        app_json_path = os.path.abspath('.')+'/'+JsonPath
        linetext = linecache.getline(app_json_path, 2).strip()
        marcotext = "".join(re.findall(r'\"(.*?)\"',linetext))

        with open(app_json_path,'r') as load_f:
            json_data = json.load(load_f)

        self.repo = json_data[marcotext]["gradle"]["repo"]
        self.group = json_data[marcotext]["gradle"]["group"]
        self.name = json_data[marcotext]["gradle"]["name"]
        self.version = json_data[marcotext]["gradle"]["version"]
        self.classifier = json_data[marcotext]["gradle"]["classifier"]
        self.group_str = self.group.replace('.','/')

    #获取指定json APP 信息
    def GetAppInfo(self,JsonPath):
        os.system('cvt-what-app -f '+JsonPath)

    #获取指定json APP 文件
    def GetAppFile(self,outdir):
        download_head = "https://artifactory.gz.cvte.cn/artifactory/"
        if self.repo == "tv-smart":
            download_argv = self.repo+"-releases-local/"+self.group_str+"/"+self.name+"/"+self.version+"/"
        else:
            download_argv = self.repo+"-release-local/"+self.group_str+"/"+self.name+"/"+self.version+"/"

        if self.classifier == "":
            apkname = self.name+"-"+self.version+".apk"
        else:
            apkname = self.name+"-"+self.version+"-"+self.classifier+".apk"
        download_link = download_head + download_argv + apkname
        if outdir == '.':
            os.system('wget '+download_link)
        else:
            os.system('mkdir '+outdir)
            os.system('wget -O'+' ./'+outdir+'/ '+download_link)

        print("=====================================")
        print(self.name+self.version+" APK已下载到本目录")
        print("=====================================")

    #获取指定json APP 翻译表格
    def GetAppXls(self,outdir):
        if os.access(os.path.abspath('.')+'/'+self.name+'_'+self.version+'.xls', os.F_OK):
            print(os.path.abspath('.')+'/'+self.name+'_'+self.version+'.xls\n'+"此APK的翻译表格已存在,请先删除后获取最新的!")
            return
        download_head = "https://artifactory.gz.cvte.cn/artifactory/"
        if self.repo == "tv-smart":
            download_argv = self.repo+"-releases-local/"+self.group_str+"/"+self.name+"/"+self.version+"/"
        else:
            print("=============\n此APK无翻译表\n=============\n")
            return
        if outdir == '.':
            pass
        else:
            os.system('mkdir '+outdir)

        if self.name == "Media3":
            xlsname = self.name+"%3Amedia_browser.xls"
            download_link = download_head + download_argv + xlsname
            os.system('wget -O'+' ./'+outdir+'/'+self.name+'_'+self.version+'_browser.xls '+download_link)
            xlsname = self.name+"%3Amedia_common_library.xls"
            download_link = download_head + download_argv + xlsname
            os.system('wget -O'+' ./'+outdir+'/'+self.name+'_'+self.version+'_common_library.xls '+download_link)
            xlsname = self.name+"%3Amedia_players.xls"
            download_link = download_head + download_argv + xlsname
            os.system('wget -O'+' ./'+outdir+'/'+self.name+'_'+self.version+'_players.xls '+download_link)
        else:
            xlsname = self.name+"%3Aapp.xls"
            download_link = download_head + download_argv + xlsname
            os.system('wget -O'+' ./'+outdir+'/'+self.name+'_'+self.version+'.xls '+download_link)

        print("=====================================")
        print(self.name+self.version+" APK的翻译表已下载到本目录")
        print("=====================================")

    def GetAppRes(self,outdir):
        os.system('change_jdk 8')
        print("=====================================================\n")
        print("=========此命令需要JAVA环境的支持，如果反编译失败========\n")
        print("======请先手动输入 change_jdk 8 命令后再次使用命令======\n")
        print("=====================================================\n")
        if os.access(os.path.abspath('.')+'/'+outdir+'/apktool', os.F_OK):
            pass
        else:
            getfile = PyocsFileSystem()
            apktool_jar_link = "https://drive.cvte.com/p/DWKUJacQn_sBGO3ABQ"
            apktool_link = "https://drive.cvte.com/p/DRzJRWgQn_sBGO_ABQ"

            if outdir == '.':
                getfile.get_file_from_nut_driver(apktool_link,".")
                getfile.get_file_from_nut_driver(apktool_jar_link,".")
                os.system('chmod 777 apktool')
                os.system('chmod 777 apktool.jar')
            else:
                os.system('mkdir '+outdir)
                getfile.get_file_from_nut_driver(apktool_link,"./"+outdir)
                getfile.get_file_from_nut_driver(apktool_jar_link,"./"+outdir)
                os.system('chmod 777 '+'./'+outdir+'/apktool')
                os.system('chmod 777 '+'./'+outdir+'/apktool.jar')

        download_head = "https://artifactory.gz.cvte.cn/artifactory/"
        if self.repo == "tv-smart":
            download_argv = self.repo+"-releases-local/"+self.group_str+"/"+self.name+"/"+self.version+"/"
        else:
            download_argv = self.repo+"-release-local/"+self.group_str+"/"+self.name+"/"+self.version+"/"

        if self.classifier == "":
            apkname = self.name+"-"+self.version+".apk"
        else:
            apkname = self.name+"-"+self.version+"-"+self.classifier+".apk"
        download_link = download_head + download_argv + apkname

        os.chdir(outdir)
        os.system('wget '+download_link)
        os.system('./apktool d '+'./'+apkname)
        os.remove('./'+apkname)
        if outdir == '.':
            pass
        else:
            os.chdir("..")
        print("=====================================")
        print(self.name+self.version+" APK的反编译资源文件已处理到本目录")
        print("=====================================")

    def RemoveApktool(self,outdir):
        os.chdir(outdir)
        os.remove('./apktool')
        os.remove('./apktool.jar')

class Deal_AppJsonTranslation():
    #获取common下所有能rro的翻译表格
    #GlobalUI   LauncherDimfire LauncherFall4   LauncherSpace4    TvProvision2
    #LiveTvGlobal Media3  PairedGuide   Pictorial  Settings2     StarkStore     TvAssistant 
    def __init__(self):
        self.ts_list = [
            "GlobalUI/app_config.json",
            "LauncherFall4/app_config.json",
            "LauncherSpace4/app_config.json",
            "TvProvision2/app_config.json",
            "LiveTvGlobal/app_config.json",
            "Media3/app_config.json",
            "PairedGuide/app_config.json",
            "Pictorial/app_config.json",
            "Settings2/app_config.json",
            "StarkStore/app_config.json",
            "TvAssistant/app_config.json",]

    def GetALLAppTranslationXls(self,outdir):

        for jsonname in self.ts_list:
            appjson = PyocsAppJson(jsonname)
            appjson.GetAppXls(outdir)
        libStarkRes_link ="https://artifactory.gz.cvte.cn/artifactory/tv-smart-releases-local/com/cvte/sdk/libStarkRes/1.16.13.3-HOTFIX/libStarkRes%3Aapp.xls"
        os.system('wget -O'+' ./'+outdir+'/libStarkRes-1.16.4.0.xls '+libStarkRes_link)
        print("=====================================")
        print("常用所有APK的翻译表已下载到"+outdir+"目录")
        print("=====================================")

    def GetALLAppFile(self,outdir):
        for jsonname in self.ts_list:
            appjson = PyocsAppJson(jsonname)
            appjson.GetAppFile(outdir)
        print("=====================================")
        print("常用所有APK的文件已下载到"+outdir+"目录")
        print("=====================================")

    def GetALLAppResFile(self,outdir):
        os.system('change_jdk 8')
        print("=====================================================\n")
        print("=========此命令需要JAVA环境的支持，如果反编译失败========\n")
        print("======请先手动输入 change_jdk 8 命令后再次使用命令======\n")
        print("=====================================================\n")
        for jsonname in self.ts_list:
            appjson = PyocsAppJson(jsonname)
            appjson.GetAppRes(outdir)
        print("=====================================")
        print("常用所有APK的反编译资源已处理到"+outdir+"目录")
        print("=====================================")
        appjson.RemoveApktool(outdir)