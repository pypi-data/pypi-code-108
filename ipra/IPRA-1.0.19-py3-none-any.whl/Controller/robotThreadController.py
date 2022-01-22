
from ipra.Model.robotThread import robotThread
import configparser
from datetime import datetime
import os

class RobotThreadController:
    def __init__(self):
        self.threadPool_runningRobot = []
        self.config_obj = configparser.ConfigParser()
        self.config_obj.read("C:\IPRA\config.ini")
        self.reportPath = self.config_obj['report_path']['outputPath']+'\\'+datetime.today().strftime("%d_%m_%Y_%H_%M_%S")+'\\'
        self.inputPath = self.config_obj['report_path']['inputPath']
        #self.__createDirectory()
    
    def __createDirectory(self):
        if os.path.exists(self.reportPath):
            pass
        else:
            os.mkdir(path=self.reportPath)

        pass
    
    def destoryAllRobotThread(self):
        for x in self.threadPool_runningRobot:
            x.join(0)
    
    def  createRobotThread(self,policyList,frameList):
        self.config_obj.read("C:\IPRA\config.ini")
        self.reportPath = self.config_obj['report_path']['outputPath']+'\\'+datetime.today().strftime("%d_%m_%Y_%H_%M_%S")+'\\'
        self.inputPath = self.config_obj['report_path']['inputPath']
        self.__createDirectory()
        for company_iteration,company in enumerate(policyList):
            if(len(company)>1):
                robot = robotThread(company[0],company[1:],frameList[company_iteration],self.reportPath,self.inputPath)
                self.threadPool_runningRobot.append(robot)
                robot.start()
        return
        