import smtplib ,email
import email.mime.multipart as Multipart# import MIMEMultipart  
import email.mime.text as Text # import MIMEText  
import email.mime.base as Base# import MIMEBase  
import os.path  as path
import mimetypes  
import imaplib, string
import time
import poplib
__version__='1.1.0'
class send_email():
    def __init__(self,account,password,Sender=' ',To=' ',smtpServer=None,login=True):
        if smtpServer is not None:
             self.server = smtplib.SMTP(smtpServer)
        if login is True:
            self.login(account=account,password=password)
        self.Sender=Sender
        self.To=To
        self.account=account
    def login(self,account,password):
        smtp=account.split('@')[-1]
        try:
            self.server = smtplib.SMTP("smtp."+smtp)
            self.server.login(account,password) #仅smtp服务器需要验证时  
            return True
        except:
            return False
    def send(self,content,accessory=[],receiver=[],Subject='Content',To = None ,From = " ",Sender=None,isHtml = False): 
        if Sender is None:Sender=self.Sender
        if To is None:To=self.To
        # 构造MIMEMultipart对象做为根容器  
        main_msg = Multipart.MIMEMultipart()     
        # 构造MIMEText对象做为邮件显示内容并附加到根容器  
        if isHtml:
            text_msg = Text.MIMEText(content,_charset="utf-8" ,_subtype='html')
        else:
            text_msg = Text.MIMEText(content,_charset="utf-8" )  
        main_msg.attach(text_msg)  
              
        # 构造MIMEBase对象做为文件附件内容并附加到根容器  
              
        ## 读入文件内容并格式化 [方式1]－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－  
        def AddAccessory(filename):
            if not path.isfile(filename):return
            data = open(filename, 'rb')  
            ctype,encoding = mimetypes.guess_type(filename)  
            if ctype is None or encoding is not None:  
                ctype = 'application/octet-stream'  
            maintype,subtype = ctype.split('/',1)  
            file_msg = Base.MIMEBase(maintype, subtype)  
            file_msg.set_payload(data.read())  
            data.close( )  
            email.encoders.encode_base64(file_msg)#把附件编码  
            ## 设置附件头  
            basename = path.basename(filename)  
            file_msg.add_header('Content-Disposition','attachment', filename = basename.encode('gbk').decode('gbk'))#修改邮件头  
            main_msg.attach(file_msg)  
        if isinstance(accessory,str):AddAccessory(accessory)
        else:
            for i in accessory:AddAccessory(i)
        # 设置根容器属性  
        main_msg['From'] = From
        main_msg['To'] = To  
        main_msg['Subject'] = Subject  
        print(Subject,From,To)
        main_msg['Date'] = email.utils.formatdate( )  
        main_msg['Sender']=Sender
        # 得到格式化后的完整文本  
        fullText = main_msg.as_string( )  
              
        # 用smtp发送邮件  
        try:  
            self.server.sendmail(From, receiver, fullText)  
        except:
            return False
        finally:
            return True 
    def __del__(self):
        self.server.quit()
class pop_accept_email:
    def __init__(self,account,password):
        self.account=account
        self.password=password
    def login(self):
        host='pop.'+self.account.split('@')[-1]
        self.pop_conn = poplib.POP3_SSL(host)  
        self.pop_conn.user(self.account)  
        self.pop_conn.pass_(self.password)  
    def accept(self):
        self.login()
        ret = self.pop_conn.stat() 
        n=ret[0]
        if n==0:return None
        #Get messages from server:  
        messages = [self.pop_conn.retr(n) ]
        # Concat message pieces:  
        messages = ["\n".join(mssg[1]) for mssg in messages]  
          
        #Parse message intom an email object:  
        messages = [parser.Parser().parsestr(mssg) for mssg in messages]  
        for message in messages:  
            print(message['Subject'])
            break
        x=n-229
        if x<1:x=1
        for i in range(x,n+1):self.pop_conn.dele(i)
        self.pop_conn.quit()
class imap_accept_email:
    def __init__(self,account,password):
        host='imap.'+account.split('@')[-1]
        self.M = imaplib.IMAP4_SSL(host)  
        self.M.login(account,password)  
    def accept(self,**kargv):
        result, message = self.M.select('INBOX') 
        typ, data = self.M.search(None, 'ALL')  
        for num in string.split(data[0]): 
            typ, data = self.M.fetch(num, '(RFC822)')  
            msg = email.message_from_string(data[0][1])  
            print(msg)
            return msg  
    def __del__(self):
        self.M.logout()
class server:
    def __init__(self,account,password):
        self.send_server=send_email(account,password)
        self.account = account
    def send(self,receiver,mail_data):
        content = mail_data.get('content','')
        accessory = mail_data.get('attachments',[])
        Subject = mail_data.get('subject','None')
        To = mail_data.get('to',None)
        Sender= mail_data.get('sender',None)
        isHtml = mail_data.get('isHtml',False)
        From = mail_data.get('from','')
        From='{0}<{1}>'.format(self.account.split('@')[0].strip(),self.account)
        self.send_server.send(content,accessory,receiver,Subject,To,From,Sender,isHtml)
if __name__=='__main__':
    x=server('test@test.net','password')
    mail = {
        'subject':'测试subjuect',
        'from':'测试from',
        'to':'to',
        'sender':'im_sender',
        'content':'content',
        'isHtml':False}
    x.send(['tset@test.com'] , mail)