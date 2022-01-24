import requests
import urllib
from requests_ntlm import HttpNtlmAuth
import json
import re

class Share_Point(object):
    def __init__(self, base_url,username,password,site):
        self.base_url=base_url
        self.username=username
        self.password=password
        #site网站集加站点
        self.site=site 
        self.auth_session()
    # 登录验证
    def auth_session(self):
        session = requests.Session()
        session.auth = HttpNtlmAuth(self.username,self.password)
        self.session=session
    # 获取Digest
    def get_Digest_Value(self):
        headers={}
        headers["Content-Type"]= "application/json"
        headers["Accept"]= "application/json;odata=verbose"
        self.session.headers=headers
        response=self.session.post(url=f"{self.base_url}/{self.site}/_api/contextinfo")
        data=json.loads(response.text)
        try:
            result=data["d"]["GetContextWebInformation"]["FormDigestValue"]
        except:
            result=None
        return result    
    #根据用户名获取ID,用户名格式【域\用户名】,授权时使用
    def get_user_id(self,login_name):
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        self.session.headers=headers
        param_str=f"""i:0#.w|{login_name}"""
        param_url=urllib.parse.quote(param_str)
        url=f"{self.base_url}/{self.site}/_api/Web/siteusers(@v)?@v='{param_url}'"""
        response=self.session.get(url)
        result=json.loads(response.text)
        try:
            user_id= result["d"]["Id"]
        except:
            user_id=None
        return user_id
    #获取站点所在网站集权限级别列表
    def get_role_list(self):
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        self.session.headers=headers
        url=f"{self.base_url}/{self.site}/_api/Web/RoleDefinitions"
        response=self.session.get(url)
        result=json.loads(response.text)
        if "error" not in result:
            role_dict={row["Name"]:row["Id"] for row in result["d"]["results"]}
        else:
            role_dict={}
        return role_dict

    # 创建文件夹，folder_path为父路径的全路径
    def create_folder(self,folder_path,folder_name):
        post_data={
        "__metadata": {
            "type": "SP.Folder"
        },
        "ServerRelativeUrl": f"{folder_path}/{folder_name}"
        }
        post_data=json.dumps(post_data)
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        headers["Content-Length"]= str(len(post_data))
        headers["X-RequestDigest"]=self.get_Digest_Value()
        self.session.headers=headers
        url=f"""{self.base_url}/{self.site}/_api/web/folders"""
        response=self.session.post(url=url,data=post_data)
        result=json.loads(response.text)
        if "error" in result:
            error_code=result["error"]["message"]
            raise Exception(error_code)
        else:
            ServerRelativeUrl=result["d"]["ServerRelativeUrl"]
            return ServerRelativeUrl   

    # 上传文件，folder_path：目录全路径不含文件名,file_name:文件名,content:bytes文件 ByteID.getvalue
    def file_upload(self,folder_path,file_name,content):
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        headers["Content-Length"]= str(len(content))
        headers["X-RequestDigest"]= self.get_Digest_Value()
        self.session.headers=headers
        url=f"""{self.base_url}/{self.site}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')/Files/Add(url='{file_name}', overwrite=true)"""
        response=self.session.post(url=url,data=content)
        result=json.loads(response.text)
        if "error" in result:
            error_code=result["error"]["message"]
            raise Exception(error_code)
        else:
            ServerRelativeUrl=result["d"]["ServerRelativeUrl"]
            return ServerRelativeUrl    

    # 获取文件uri
    def get_file_uri(self,file_path):
        url=f"{self.base_url}/{self.site}/_api/Web/GetFileByServerRelativePath(decodedurl='{file_path}')/ListItemAllFields"
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        self.session.headers=headers
        response=self.session.get(url)
        result=json.loads(response.text)
        if "error" not in result:
            uri=result["d"]["__metadata"]["uri"]
            return uri
        else:
            error_code=result["error"]["message"]
            raise Exception(error_code)
        
    # 获取文件夹uri
    def get_floder_uri(self,floder_path):
        url=f"{self.base_url}/{self.site}/_api/Web/GetFolderByServerRelativePath(decodedurl='{floder_path}')/ListItemAllFields"
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        self.session.headers=headers
        response=self.session.get(url)
        result=json.loads(response.text)
        if "error" not in result:
            uri=result["d"]["__metadata"]["uri"]
            return uri
        else:
            error_code=result["error"]["message"]
            raise Exception(error_code)
        
    # 打断uri的集成
    def breakroleinheritance(self,uri):
        url=uri+ "/breakroleinheritance(true)"
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        headers["X-RequestDigest"]= self.get_Digest_Value()
        self.session.headers=headers
        response=self.session.post(url)
        result=json.loads(response.text)
        if "error" not in result:
            return True
        else:
            error_code=result["error"]["message"]
            raise Exception(error_code)

    # uri上添加权限
    def add_permission(self,user_id,role_id,uri):
        url=uri+f"/roleassignments/addroleassignment(principalid={user_id},roledefid={role_id})"
        headers={}
        headers["Accept"]= "application/json;odata=verbose"
        headers["Content-Type"]= "application/json;odata=verbose"
        headers["X-RequestDigest"]= self.get_Digest_Value()
        self.session.headers=headers
        response=self.session.post(url)
        result=json.loads(response.text)

        if "error" not in result:
            return True
        else:
            error_code=result["error"]["message"]
            raise Exception(error_code)

    def download_file(self,file_path):
        url=f"""{self.base_url}/{self.site}/{file_path}"""
        # 如果文件过大可以用stream流下载,可实现文段下载
        res=self.session.get(url,stream=True)
        if  'Content-Disposition' in res.headers.keys():
            filename=res.headers['Content-Disposition']
            searchObj = re.search(r'filename=(.*)', filename, re.M | re.I)
            if searchObj:
                filename = urllib.parse.unquote(searchObj.group(1))
        else:
            filename=url[url.rfind("/")+1:]
        # res.content 是文件的bytes流,可以直接用io.wirte() 'wb'写入文件
        return res.content