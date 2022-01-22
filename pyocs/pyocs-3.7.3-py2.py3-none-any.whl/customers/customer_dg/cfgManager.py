import xml.etree.ElementTree as ET
import os
work_dir = str(os.environ.get('HOME')) + '/.dg_res'
class CfgManager(object):
    def __init__(self,fileName):
        self.ruleFile = fileName
        self.tree = ET.parse(self.ruleFile)
        self.root = self.tree.getroot()

    def get_customer_list(self):
        customerList = set()
        for customer in self.root:
            customerList.add(customer.attrib['name'])

        return customerList

    def get_rule(self,cusName):
        cusList = self.get_customer_list()
        if cusName not in cusList:
            print("the customer %s you input is not exist" % cusName)
            return 1
        ruleList = list()
        for customer in self.root.findall(".//*[@name='%s']" % cusName):
            for matchingRule in customer.findall('param'):
                param = matchingRule.text
                ruleList.append(param)

        return ruleList

    def create_node(self,tag, property_map, content):  
        '''''新造一个节点 
        tag:节点标签 
        property_map:属性及属性值map 
        content: 节点闭合标签里的文本内容 
        return 新节点'''  
        element = ET.Element(tag, property_map)  
        element.text = content
        return element

    def add_child_node(self,element,nodelist):  
        '''''给一个节点添加子节点 
        nodelist: 节点列表 
        element: 子节点'''  
        for node in nodelist:  
            element.insert(0,node)  

    def write_xml(self,tree, out_path):  
        '''''将xml文件写出 
        tree: xml树 
        out_path: 写出路径'''  
        tree.write(out_path, encoding="utf-8",xml_declaration=True,method="xml") 
        
    def add_rule(self,cusName,newRuleList):
        # 传入一个客户名，一个包含规则的集合
        # 需要检查是否是新客户，需要检查是否包含已有的规则
        # cusName: 需要新增规则的客户
        # newRuleList：需要新增的规则集合
        cusList = self.get_customer_list()
        ruleList = self.get_rule(cusName)
        nodeList = set()
        if cusName in cusList:
            cus = self.root.findall(".//*[@name='%s']" % cusName)
            for newRule in newRuleList:
                if newRule not in ruleList:
                    print("root: %s is not in the root list"%newRule)
                    node = self.create_node("param",{},newRule)
                    nodeList.add(node)
                else:
                    print("root: %s is already in the root list"%newRule)
                
                self.add_child_node(cus[0],nodeList)
                self.write_xml(self.tree,"./root.xml")
        else:
            print("new customer OR input error , check if you need to add it")

    def delete_node(self,fatherNode,delNodeList):
        #从父节点中删除集合中的节点
        #fatherNode:所要删除的节点的父节点
        #delNodeList:所要删除的节点的集合
        for node in delNodeList:
            resultNodeList = fatherNode.findall(".//*[.='%s']" % node)
            if len(resultNodeList) == 0:
                print("can not find the root: %s" % node)
            else:
                delete_node = resultNodeList[0]
                fatherNode.remove(delete_node)

    def remove_rule(self,cusName,delRuleList):
        #在指定的客户中删除规则
        #cusName: 所要删除规则的客户
        #ruleList: 删除的规则集合
        #cusList = self.get_customer_list()
        #拿到客户节点
        cus = self.root.findall(".//*[@name='%s']" % cusName)
        Cus = cus[0]
        if cusName in cusList:
            self.delete_node(Cus,delRuleList)
            self.write_xml(self.tree,"./root.xml")
        else:
            print("check if the customer exist")


