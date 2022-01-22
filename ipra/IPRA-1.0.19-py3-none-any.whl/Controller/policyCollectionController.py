
from ipra.Model.policyCollection import PolicyCollection
import pandas as pd

class PolicyCollectionController:
    def __init__(self):
        self.policyCollection = PolicyCollection()
        return
    
    def policySwitch(self,record):
        if record[0] == 'AIA':
            self.policyCollection.AIA.append(record[1])
        elif record[0] == 'AXA':
            self.policyCollection.AXA.append(record[1])
        elif record[0] == 'BOCG':
            self.policyCollection.BOCG.append(record[1])
        elif record[0] == 'CHINALIFE':
            self.policyCollection.CHINALIFE.append(record[1])
        elif record[0] == 'PRU':
            self.policyCollection.PRU.append(record[1])
        elif record[0] == 'FWD':
            self.policyCollection.FWD.append(record[1])
        elif record[0] == "MANULIFE":
            self.policyCollection.MANULIFE.append(record[1])
        elif record[0] == 'YFL':
            self.policyCollection.YFLIFE.append(record[1])
        elif record[0] == 'SUNLIFE':
            self.policyCollection.SUNLIFE.append(record[1])
        elif record[0] == 'CIGNA':
            self.policyCollection.CIGNA.append(record[1])
        elif record[0] == 'GENERALI':
            self.policyCollection.GENERALI.append(record[1])
        elif record[0] == 'CHUBB':
            self.policyCollection.CHUBB.append(record[1])
            
    
    def policySwitchByList(self,recordLists):
        for record in recordLists:
            self.policySwitch(record)
    
    def getPolicyListFromFile(self,filePath):
        try:
            policy_no_col = pd.read_excel(filePath,sheet_name='IPRA',usecols='A:B',header=0,dtype=str)
            policy_no_list = policy_no_col.values.tolist()
            for policy in policy_no_list:
                self.policySwitch(policy)
            return True
        except:
            return False
    
    def getPolicyCollection(self):
        return self.policyCollection.getTotalList()
    
    def cleanAllPolicy(self):
        self.policyCollection.cleanAllPolicy()
    
    def getSupportedList(self):
        return self.policyCollection.getSupportedList()