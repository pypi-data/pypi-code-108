from os import path, remove
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from hi_mail_download.driver_builder import DriverBuilder
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import zipfile, os, shutil
from tkinter import *
import threading

download_path = path.dirname(path.realpath(__file__))

class HiMailDownload:
    def __init__(self):
        self.root3 = Tk()
        self.root3.title("请稍后")
        self.root3.geometry("300x100")
        self.lab = Label(self.root3, text='请耐心等待...', font=("微软雅黑", 10))

        self.dowmloadstep = 0
        self.logfilepath = download_path + "logfile.txt"

    def print_debug(self, threadName, delay):
        dowmloadsteptmp = 255
        while 1:
            sleep(delay)
            if self.dowmloadstep == dowmloadsteptmp:
                continue
            else:
                dowmloadsteptmp = self.dowmloadstep

            print("debug..." + str(self.dowmloadstep))

            if self.dowmloadstep == 0:
                self.lab["text"]="正在初始化..."

            elif self.dowmloadstep == 1:
                self.lab["text"]="正在打开浏览器..."

            elif self.dowmloadstep == 2:
                self.lab["text"]="正在登录..."

            elif self.dowmloadstep == 3:
                self.lab["text"]="选择未读邮件..."

            elif self.dowmloadstep == 4:
                self.lab["text"]="正在下载..."

            elif self.dowmloadstep == 5:
                self.lab["text"]="正在关闭浏览器..."

            elif self.dowmloadstep == 6:
                self.lab["text"]="正在解压下载文件..."

            elif self.dowmloadstep == 7:
                self.lab["text"]="正在导出到目标文件夹..."

            elif self.dowmloadstep == 8:
                #self.lab["text"]="操作完成，结束"
                self.root3.destroy()
                break

            self.root3.update()


    def showpage(self,messagetext,logshow=0):
        root1 = Toplevel()
        root1.title("导出结论")
        photo = PhotoImage(file="./picture/result.png")
        Label(root1, text=messagetext,
              justify=LEFT,
              image=photo,
              compound=CENTER,
              font=(13)).grid(row=0, column=0, padx=30, sticky=W)

        if logshow == 1:
            Button(root1, text='查看详情', width=10, command=self.opendownfile).grid(row=1, column=0,padx=10, pady=50)
        else:
            Button(root1, text='确认', width=10, command=root1.destroy).grid(row=1, column=0, padx=10, pady=50)

    def opendownfile(self):
        root2 = Toplevel()
        sb = Scrollbar(root2)
        sb.pack(side=RIGHT, fill=Y)  # 需要先 将滚动条放置 到一个合适的位置 , 然后开始填充 .
        lb = Listbox(root2, width=70,yscrollcommand=sb.set)  # 内容 控制滚动条 .

        f = open(self.logfilepath)
        line = f.readline()
        while line:
            print(line, end = '')
            lb.insert(END, line)
            line = f.readline()
        f.close()

        lb.pack(side=LEFT, fill=BOTH)
        sb.config(command=lb.yview)

    def download_file(self, account, passwd, addressPath,openbrown):
        try:
            threading.Thread(target=self.download_file_service,args=("Thread-1",account, passwd, addressPath,openbrown,),
                             daemon=True).start()
        except:
            print("Error: 无法启动线程1")

        self.lab.grid(row=1, column=2, padx=100, pady=30, sticky=W)

        try:
            threading.Thread(target=self.print_debug, args=("Thread-2", 1,),
                             daemon=True).start()
        except:
            print("Error: 无法启动线程2")

        self.root3.mainloop()

    def download_file_service(self, threadName,account, passwd, addressPath, openbrown):

        driver_builder = DriverBuilder()

        expected_download = path.join(download_path, "messages_package.zip")

        # clean downloaded file
        try:
            remove(expected_download)
        except OSError:
            pass

        assert (not path.isfile(expected_download))

        self.dowmloadstep = 1
        try:
            if openbrown == 1:
                driver = driver_builder.get_driver(download_path, headless=False)
            else:
                driver = driver_builder.get_driver(download_path, headless=True)
        except:
            self.dowmloadstep = 8
            sleep(.5)
            messagetext="工具的google版本与PC安装的google版本不一致，请更新exe文件！"
            self.showpage(messagetext)
            assert()

        self.hisense_mail_operate(driver, account, passwd)

        self.wait_until_file_exists(expected_download, 30)

        self.dowmloadstep = 5
        driver.close()

        assert (path.isfile(expected_download))

        if os.path.exists(expected_download):
            plm_path=download_path+"\\temp"

            if os.path.exists(plm_path):
                shutil.rmtree(plm_path)

            logfile = open(self.logfilepath, 'w+')

            self.dowmloadstep = 6
            f = zipfile.ZipFile(expected_download, 'r')
            for file in f.namelist():
                filename = file.encode('cp437').decode('gbk')  # 先使用cp437编码，然后再使用gbk解码
                print(filename)
                print(filename, file=logfile)
                f.extract(file, plm_path)  # 解压缩ZIP文件
                os.chdir(plm_path)  # 切换到目标目录
                os.rename(file, filename)  # 重命名文件
                os.chdir(download_path)

            f.close()
            #addressPath = "V:\HX_Release_SW\PLM"
            print(addressPath)

            if path.isfile(expected_download):
                try:
                    remove(expected_download)
                except OSError:
                    pass

            self.dowmloadstep = 7
            if os.path.exists(addressPath):
                messagetext1="导出成功！已拷贝到目标文件夹\n\n"
                print(messagetext1)
            else:
                addressPath = download_path + "\\bak"
                messagetext1 = "导出成功！目标文件夹不存在，已保存在工具目录的bak文件夹中，\n\n请手动复制到服务器！\n\n"
                print(messagetext1)

            print("\n\n存放目录: " + addressPath, file=logfile)
            logfile.close()

            mailcount=0
            f_list = os.listdir(plm_path)
            for fileNAME in f_list:
                oldname = plm_path + "\\" + fileNAME
                newname = addressPath + "\\" + fileNAME
                shutil.copyfile(oldname, newname)
                mailcount += 1
            print("total count = " + str(mailcount))
            if os.path.exists(plm_path):
                shutil.rmtree(plm_path)
            self.dowmloadstep = 8
            sleep(.5)

            messagetext=messagetext1 + "本次导出邮件数量为：" + str(mailcount) + "封"
            self.showpage(messagetext,1)

        print("done")



    @staticmethod
    def wait_until_file_exists(actual_file, wait_time_in_seconds=5):
        waits = 0
        while not path.isfile(actual_file) and waits < wait_time_in_seconds:
            print("sleeping...." + str(waits))
            sleep(.5)  # make sure file completes downloading
            waits += .5


    def hisense_mail_operate(self,driver, account, passwd):
        driver.get("http://himail.hisense.com/")
        wait = WebDriverWait(driver, 100)

        self.dowmloadstep = 2
        # 1、找到账号框，输入账号
        hisense_account = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="uid"]')))
        hisense_account.clear()
        hisense_account.send_keys(account)
        # 2、找到密码框，输入密码
        hisense_password = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        # hisense_password = driver.find_element_by_xpath('//*[@id="password"]')
        hisense_password.clear()
        hisense_password.send_keys(passwd)

        # 选择区域
        hisense_local = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="u-form-item u-form-item-1 localMenu"]')))
        hisense_local.click()
        hisense_country = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@data-mailname="webmail/haixinserver/cn"]')))
        hisense_country.click()
        # 3、找到登陆框，点击登陆
        hisense_login = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="u-btn u-btn-primary submit j-submit"]')))
        # hisense_login = driver.find_element_by_xpath('//*[@class="u-btn u-btn-primary submit j-submit"]').click()
        hisense_login.click()
        driver.implicitly_wait(10)

        try:
            # 4、找到文件夹的other
            hisense_other_doc = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mltree_7_span"]/div')))
            # hisense_other_doc = driver.find_element_by_xpath('//*[@id="mltree_7_span"]/div').click()
            hisense_other_doc.click()
            driver.implicitly_wait(10)
            sleep(3)
        except:
            self.dowmloadstep = 8
            sleep(.5)
            driver.close()
            messagetxt = "登录失败！请确认是否账号密码错误。"
            self.showpage(messagetxt)
            assert ()

        self.dowmloadstep = 3
        # 5、找到plm文件夹
        hisense_plm = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mltree_11_span"]/div')))
        # hisense_plm = driver.find_element_by_xpath('//*[@id="mltree_11_span"]/div').click()
        hisense_plm.click()
        sleep(3)
        driver.implicitly_wait(20)
        # 6、找到选择按钮
        hisense_status = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="previewLayout"]//*[@data-dropdown="select"]')))
        # hisense_status = driver.find_element_by_xpath('//*[@id="previewLayout"]//*[@data-dropdown="select"]').click()
        hisense_status.click()
        # 7、找到未读按钮
        hisense_unread = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="previewLayout"]//*[@value="select:unread"]')))
        # hisense_unread = driver.find_element_by_xpath('//*[@id="previewLayout"]//*[@value="select:unread"]').click()
        hisense_unread.click()
        # 8、找到more按钮
        try:
            hisense_more = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="previewLayout"]//*[@data-dropdown="more"]')))
            # hisense_more = driver.find_element_by_xpath('//*[@id="previewLayout"]//*[@data-dropdown="more"]').click()
            hisense_more.click()
            hisense_download = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="previewLayout"]//*[@value="more:pack"]')))
            # hisense_download = driver.find_element_by_xpath('//*[@id="previewLayout"]//*[@value="more:pack"]').click()
            hisense_download.click()
        except:
            self.dowmloadstep = 8
            sleep(.5)
            driver.close()
            messagetxt = "没有新的未读邮件！"
            self.showpage(messagetxt)
            assert ()

        self.dowmloadstep = 4
        hisense_downmark = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="previewLayout"]//*[@data-dropdown="mark"]')))
        # hisense_downmark = driver.find_element_by_xpath('//*[@id="previewLayout"]//*[@data-dropdown="mark"]').click()
        hisense_downmark.click()
        hisense_downread = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="previewLayout"]//*[@value="mark:read"]')))
        # hisense_downread = driver.find_element_by_xpath('//*[@id="previewLayout"]//*[@value="mark:read"]').click()
        hisense_downread.click()






