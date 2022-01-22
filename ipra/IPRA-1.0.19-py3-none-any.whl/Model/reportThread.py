from typing import overload
from ipra.Model.Robot.baseRobot import BaseRobot
from ipra.Model.Robot.bocgRobot import BOCGRobot
from ipra.Model.Robot.cignaRobot import CignaRobot
from ipra.Model.Robot.manulifeRobot import ManulifeRobot
from ipra.Model.Robot.pruRobot import PruRobot
from ipra.Model.Robot.axaRobot import AxaRobot
from ipra.Model.robotThread import robotThread
from ipra.Model.Robot.fwdRobot import FwdRobot
from ipra.Model.Robot.chinaLifeRobot import ChinaLifeRobot
from ipra.Model.Robot.aiaRobot import AiaRobot
from ipra.Model.Robot.yflifeRobot import YFLifeRobot
from ipra.Model.Robot.sunlifeRobot import SunLifeRobot
from ipra.Model.Robot.generali import GeneraliRobot
from ipra.Model.Robot.chubbRobot import ChubbRobot

class reportThread (robotThread):
    def __init__(self, type , policyList , frame, reportPath,inputPath):
        robotThread.__init__(self,type,policyList,frame, reportPath,inputPath)
        pass

    def createRobotClass(self):
        if self.type == 'AIA':
            self.robotInstance = AiaRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'AXA':
            self.robotInstance = AxaRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'BOCG':
            self.robotInstance = BOCGRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'CHINALIFE':
            self.robotInstance = ChinaLifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'PRU':
            self.robotInstance = PruRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == "FWD":
            self.robotInstance = FwdRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == "MANULIFE":
            self.robotInstance = ManulifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'YFL':
            self.robotInstance = YFLifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'SUNLIFE':
            self.robotInstance = SunLifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'CIGNA':
            self.robotInstance = CignaRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'GENERALI':
            self.robotInstance = GeneraliRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
        elif self.type == 'CHUBB':
            self.robotInstance = ChubbRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execReport()
