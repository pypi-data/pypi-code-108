import projectRule
from pyocs.pyocs_demand import PyocsDemand
import customers
from pyocs.pyocs_exception import *

class PyocsRulerChoose:

    # 用于样品订单和代测订单的规则映射
    sample_map_dict = {
        "HV35X": {
            "CVTE": projectRule.hisi35x.customer.CvteSample,
            "金品": projectRule.hisi35x.customer.Jinpin,
        },
        "HV553": {
            "CVTE": projectRule.hisi553.customer.CvteSample,
            "金品": projectRule.hisi553.customer.Jinpin,
        },
        "MSD358": {
            "CVTE": projectRule.msd358.customer.cvteSample,
            "金品": projectRule.msd358.customer.Jinpin,
        },
        "MT5510": {
            "CVTE": projectRule.mtk5510.customer.CvteSample,
            "金品": projectRule.mtk5510.customer.Jinpin,
        },
        "MT5522": {
            "CVTE": projectRule.mtk5522.customer.CvteSample,
            "金品": projectRule.mtk5522.customer.Jinpin,
        },
        "V530": {
            "CVTE": projectRule.hisi530.customer.CvteSample,
            "金品": projectRule.hisi530.customer.Jinpin,
        },
        "V310": {
            "CVTE": projectRule.hisi530.customer.CvteSample,
            "金品": projectRule.hisi530.customer.Jinpin,
        },
        "RDA8503": {
            "CVTE": projectRule.rda8503.customer.CvteSample,
            "金品": projectRule.rda8503.customer.Jinpin,
        },
        "V56": {
            "CVTE": projectRule.v56.customer.CvteSample,
            "金品": projectRule.v56.customer.Jinpin,
            "明彩": projectRule.v56.customer.Mingcai,
            "朝野": projectRule.v56.customer.Chaoye,
        },
        "V53WT": {
            "CVTE": projectRule.v56.customer.CvteSample,
            "金品": projectRule.v56.customer.Jinpin,
            "明彩": projectRule.v56.customer.Mingcai,
            "朝野": projectRule.v56.customer.Chaoye,
        },
        "MS3663": {
            "CVTE": projectRule.msd3663.customer.CvteSample,
            "金品": projectRule.msd3663.customer.Jinpin,
            "明彩": projectRule.msd3663.customer.Mingcai,
            "朝野": projectRule.msd3663.customer.Chaoye,
        },
        "MS3683": {
            "CVTE": projectRule.msd3683.customer.CvteSample,
            "金品": projectRule.msd3683.customer.Jinpin,
        },
        "SK706/MT9632/SK506/MS6681": {
            "CVTE": projectRule.mtk9632.customer.CvteSample,
            "金品": projectRule.mtk9632.customer.Jinpin,
            "明彩": projectRule.mtk9632.customer.Mingcai,
            "朝野": projectRule.mtk9632.customer.Chaoye,
        },
        "SK708D/T972": {
            "CVTE": projectRule.aml972.customer.CvteSample,
            "金品": projectRule.aml972.customer.Jinpin,
            "明彩": projectRule.aml972.customer.Mingcai,
            "朝野": projectRule.aml972.customer.Chaoye,
        },
        "SK702/HV56X": {
            "金品": projectRule.hisi56x.customer.Jinpin,
        },
        "ATM30/T920L": {
            "CVTE": projectRule.aml920.customer.CvteSample,
            "金品": projectRule.aml920.customer.Jinpin,
            "朝野": projectRule.aml920.customer.Chaoye,
        },
        "MT9256/SK516": {
            "CVTE": projectRule.mtk9256.customer.CvteSample,
            "金品": projectRule.mtk9256.customer.Jinpin,
        },
        "MT9255": {
            "CVTE": projectRule.mt9255.customer.CvteSample,
            "金品": projectRule.mt9255.customer.Jinpin,
            "朝野": projectRule.mt9255.customer.Chaoye,
        },
    }

    # 客户需求表映射
    customer_dt_map_dict = {
        "朝野": {
            "RDA8503": customers.customer_chaoye.RDA8503,
            "MT5510": customers.customer_chaoye.MT5510,
            "MSD358": customers.customer_chaoye.MS358,
            "HV553": customers.customer_chaoye.HV553,
            "V56": customers.customer_chaoye.V56
        }
    }

    def __init__(self):
        pass

    def get_sample_ruler(self, ocs_demand: PyocsDemand):
        """
            获取样品订单或者代测订单的处理规则
        :return: 返回处理规则
        """
        tv_project = ocs_demand.get_ocs_project_name()
        tv_customer = ocs_demand.get_ocs_customer()
        for project_name in self.sample_map_dict.keys():
            if tv_project in project_name:
                for customer_name in self.sample_map_dict[project_name]:
                    if customer_name in tv_customer:
                        ruler = self.sample_map_dict[project_name][customer_name].Ruler(ocs_demand)
                        return ruler
                raise CustomerNoSupportError('此方案还未支持此客户，需要您的参与')
        raise ProjectNoSupportError('此项目还未支持，需要您的参与')

    def get_customer_excel_ruler(self, ocs_demand: PyocsDemand, excel_para: str, excel_file_location: str):
        tv_project = ocs_demand.get_ocs_project_name()
        tv_customer = ocs_demand.get_ocs_customer()
        for customer_name in self.customer_dt_map_dict.keys():
            if customer_name in tv_customer:
                for project_name in self.customer_dt_map_dict[customer_name]:
                    if project_name in tv_project:
                        ruler = self.customer_dt_map_dict[customer_name][tv_project].ruler.Ruler(
                            ocs_demand, excel_para, excel_file_location=excel_file_location)
                        return ruler
                raise ProjectNoSupportError('此客户还未支持此方案，需要您的参与')
        raise CustomerNoSupportError('此客户还未支持，需要您的参与')
