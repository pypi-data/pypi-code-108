from pyocs import pyocs_software
from pyocs import pyocs_demand
import pprint
import sys
import os
_space_ = 55


def get_SK706_BOM_DATA(ocsnum):
    pp = pprint.PrettyPrinter(indent=4)
    ocs_request = pyocs_demand.PyocsDemand(ocsnum)
    reset_str = ""

    ret = ocs_request.get_ocs_title()
    
    #board
    boardstr = ocs_request.get_port_name()
    boardstr = boardstr.replace("_","_SUB_")
    
    reset_str +="#define CVT_DEF_BOARD_TYPE".ljust(_space_)+"ID_BD_TP_SK706S_"+boardstr+ "_CH" + "\n"

    #chip
    if "MT9632EAATDB" in ocs_request.get_chip_name():
        reset_str +="#define CVT_DEF_CHIP_TYPE".ljust(_space_)+"ID_CHIP_MT9632EAATDB\n"
    elif "MT9632EAATAF" in ocs_request.get_chip_name():
        reset_str +="#define CVT_DEF_CHIP_TYPE".ljust(_space_)+"ID_CHIP_MT9632EAATAF\n"

    #duty
    reset_str +="#define CVT_DEF_CURRENT_REF_DUTY".ljust(_space_)+ocs_request.get_pwm()+"\n"

    return reset_str

def get_SK508_BOM_DATA(ocsnum):
    pp = pprint.PrettyPrinter(indent=4)
    ocs_request = pyocs_demand.PyocsDemand(ocsnum)
    reset_str = ""

    ret = ocs_request.get_ocs_title()

    #board
    boardstr = ocs_request.get_port_name()
    boardstr = boardstr.replace("_","_SUB_")
    if "PB801" in boardstr:
        reset_str +="#define CVT_DEF_BOARD_TYPE".ljust(_space_)+"ID_BD_TP_SK508_"+boardstr+"\n"
    else:
        reset_str +="#define CVT_DEF_BOARD_TYPE".ljust(_space_)+"ID_BD_TP_SK508S_"+boardstr+"\n"
    #chip
    if "3510N0N" in ocs_request.get_chip_name():
        reset_str +="#define CVT_DEF_CHIP_TYPE".ljust(_space_)+"ID_CHIP_V3510N0N\n"
    elif "3510D0N" in ocs_request.get_chip_name():
        reset_str +="#define CVT_DEF_CHIP_TYPE".ljust(_space_)+"ID_CHIP_V3510D0N\n"
    if "ATBM7821B" not in ocs_request.get_chip_name():
        reset_str +="#define CVT_DEF_MARKET_REGION".ljust(_space_)+"ID_MARKET_REGION_ATV_ONLY\n"
    #tuner
    if ocs_request.get_tuner_type() == "R842（IEC头）":
        reset_str +="#define CVT_DEF_TUNER_TYPE".ljust(_space_)+"ID_TUNER_R842_ON_BOARD\n"
    elif ocs_request.get_tuner_type() == "R842（IEC头）,RT710(F螺纹头)":
        reset_str +="#define CVT_DEF_TUNER_TYPE".ljust(_space_)+"ID_TUNER_R842_ON_BOARD\n"
        reset_str +="#define CVT_DEF_SECOND_TUNER_TYPE".ljust(_space_)+"ID_TUNER_RT710_ON_BOARD\n"

    #flash
    if "4G" in ocs_request.get_flash_size():
        reset_str +="#define CVT_DEF_FLASH_SIZE".ljust(_space_)+"ID_FLASH_4G\n"
    elif "8G" in ocs_request.get_flash_size():
        reset_str +="#define CVT_DEF_FLASH_SIZE".ljust(_space_)+"ID_FLASH_8G\n"

    #ci
    if ocs_request.get_choose_ci() == "CI":
        reset_str +="#define CVT_EN_CI_FUNC".ljust(_space_)+"1\n"
    if ocs_request.get_ci_plus() == "CI_Plus （CVTE）":
        reset_str +="#define CVT_DEF_CI_PLUS_TYPE".ljust(_space_)+"ID_CI_PLUS_TYPE_CI_PLUS\n"

    #duty
    reset_str +="#define CVT_DEF_CURRENT_REF_DUTY".ljust(_space_)+ocs_request.get_pwm()+"\n"

    #bluetooth
    if "WB8723DU" in ocs_request.get_wifi_bluetooth() and "蓝牙" in ocs_request.get_wifi_bluetooth():
        reset_str +="#define CVT_DEF_BLUETOOTH_TYPE".ljust(_space_)+"ID_BLUETOOTH_TYPE_RTK8761\n"
    #charge
    if ocs_request.get_other_app_software() == "Eshare多屏互动（CVTE）":
        reset_str +="#define CVT_EN_APPLIST_ESHARE".ljust(_space_)+"1\n"
    

    return reset_str
'''
    ret = ocs_request.get_ocs_title()
    print("get_ocs_title:" + ret)
    ret = ocs_request.get_flash_model()
    print("get_flash_model:" + ret)
    ret = ocs_request.get_chipset_name()
    print("get_chipset_name:" + ret)
    ret = ocs_request.get_product_name()
    print("get_product_name:" + ret)
    ret = ocs_request.get_ci_plus()
    print("get_ci_plus:" + ret)
    ret = ocs_request.get_region_name()
    print("get_region_name:" + ret)
    ret = ocs_request.get_pwm()
    print("get_pwm:" + ret)
    ret = ocs_request.get_customer_machine()
    print("get_customer_machine:" + ret)
    ret = ocs_request.get_other_app_software()
    print("get_other_app_software:" + ret)
    ret = ocs_request.get_chip_name()
    print("get_chip_name:" + ret)
    ret = ocs_request.get_flash_size()
    print("get_flash_size:" + ret)
    ret = ocs_request.get_port_name()
    print("get_port_name:" + ret)
    ret = ocs_request.get_ddr_size()
    print("get_ddr_size:" + ret)
    ret = ocs_request.get_tuner_type()
    print("get_tuner_type:" + ret)
    ret = ocs_request.get_wifi_bluetooth()
    print("get_wifi_bluetooth:" + ret)
    ret = ocs_request.get_choose_ci()
    print("get_choose_ci:" + ret)
    ret = ocs_request.get_choose_wifi()
    print("get_choose_wifi:" + ret)
    ret = ocs_request.get_ddr_info()
    print("get_ddr_info:" + ret)
'''



def get_bom_param(bomnum):
    
    confirm_task = pyocs_software.PyocsSoftware()
    ret = confirm_task.get_ocs_number_from_customer_name_bom(customer_name="启悦", customer_bom=bomnum)
    if len(ret) == 0:
        print("料号为空，OCS上搜索不到!")
        return "ERROR"
    else:
        pp = pprint.PrettyPrinter(indent=4)
        product_name = pyocs_demand.PyocsDemand(ret[0]).get_product_name()
        #print(product_name)
        if ("SK508" in product_name):
            return get_SK508_BOM_DATA(ret[0])
        elif ("SK706" in product_name):
            return get_SK706_BOM_DATA(ret[0])


if __name__ == '__main__':
    bomnum = -1
    if (len(sys.argv) > 1):
        bomnum = sys.argv[1]
    else:
        print("请输入料号作为参数传入!")

    print(get_bom_param(bomnum))