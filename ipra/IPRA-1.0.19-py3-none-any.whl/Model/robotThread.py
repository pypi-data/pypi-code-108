from ipra.Model.Robot.baseRobot import BaseRobot
from ipra.Model.Robot.bocgRobot import BOCGRobot
from ipra.Model.Robot.cignaRobot import CignaRobot
from ipra.Model.Robot.manulifeRobot import ManulifeRobot
from ipra.Model.Robot.pruRobot import PruRobot
from ipra.Model.Robot.axaRobot import AxaRobot
from ipra.Model.Robot.chinaLifeRobot import ChinaLifeRobot
from ipra.Model.Robot.fwdRobot import FwdRobot
from ipra.Model.Robot.aiaRobot import AiaRobot
from ipra.Model.Robot.yflifeRobot import YFLifeRobot
from ipra.Model.Robot.sunlifeRobot import SunLifeRobot
from ipra.Model.Robot.generali import GeneraliRobot
from ipra.Model.Robot.chubbRobot import ChubbRobot
import threading

class robotThread (threading.Thread):
    def __init__(self, type , policyList , frame , reportPath, inputPath):
        threading.Thread.__init__(self)
        self.type = type
        self.policyList = policyList
        self.frame = frame
        self._stopevent = threading.Event()
        self.robotInstance = None
        self.reportPath = reportPath
        self.inputPath = inputPath

    def run(self):
        self.createRobotClass()

    def join(self, timeout):
        self._stopevent.set()
        if self.robotInstance != None:
            self.robotInstance.setIsStopped(True)
        threading.Thread.join(self, timeout)

    def createRobotClass(self):
        if self.type == 'AIA':
            self.robotInstance = AiaRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'AXA':
            self.robotInstance = AxaRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'BOCG':
            self.robotInstance = BOCGRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'CHINALIFE':
            self.robotInstance = ChinaLifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'PRU':
            self.robotInstance = PruRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == "FWD":
            self.robotInstance = FwdRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == "MANULIFE":
            self.robotInstance = ManulifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'YFL':
            self.robotInstance = YFLifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'SUNLIFE':
            self.robotInstance = SunLifeRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'CIGNA':
            self.robotInstance = CignaRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'GENERALI':
            self.robotInstance = GeneraliRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()
        elif self.type == 'CHUBB':
            self.robotInstance = ChubbRobot(self.policyList,self.frame,self.reportPath,self.inputPath)
            self.robotInstance.execRobot()

    