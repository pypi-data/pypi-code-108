# Datetime Formats
DATE_YMD_TIME_HMS_F = "%Y-%m-%d %H:%M:%S.%f"
DATE_YMD_TIME_HMS = "%Y-%m-%d %H:%M:%S"
DATE_YMD_TIME_HMS_ALT = "%Y-%m-%d %H-%M-%S"
DATE_YMD_TIME_HMS_TZ = "%Y-%m-%d %H:%M:%S%z"
DATE_YMD_TIME_HM = "%Y-%m-%d %H:%M"
DATE_YMD_TIME_HM_ALT = "%Y-%m-%d %H-%M"
DATE_MD_TIME_HM = "%m-%d_%H-%M"
DATE_YMD = "%Y-%m-%d"
DATE_YM = "%Y-%m"
DATE_MD = "%m-%d"
DATE_D = "%d"
TIME_HM = "%H:%M"
TIME_HM_ALT = "%H-%M"

# Exchanges & Delivery Area Codes
SYSTEMS = {"M7": ("epex", "hupx", "tge", "southpool"), "NordPool": ("nordpool", "ibex", "cropex")}
EXCHANGES = ("epex", "nordpool", "hupx", "southpool", "tge", "ibex", "cropex")
EIC_CODES = {
	"epex": ('10YAT-APG------L', '10YBE----------2', '10YDK-1-------AA', '10YDK-2--------M', '10YFI-1--------U',
	         '10YFR-RTE------C', '10YDE-VE-------2', '10YDE-RWENET---I', '10YDE-EON------1', '10YDE-ENBW-----N',
	         '10YLU-CEGEDEL-NQ', '10YNL----------L', '10YNO-1--------2', '10YNO-2--------T', '10YNO-3--------J',
	         '10YNO-4--------9', '10Y1001A1001A48H', '10Y1001A1001A44P', '10Y1001A1001A46L', '10Y1001A1001A45N',
	         '10YCH-SWISSGRIDZ', '10YGB----------A'),
	"nordpool": ('10YDK-1--------W', '10YDK-2--------M', '10YFI-1--------U', '10YDOM-1001A084H', '10Y1001A1001A39I',
	             '10YLV-1001A00074', '10YLT-1001A0008Q', '10YNO-1--------2', '10YNO-2--------T', '10YNO-3--------J',
	             '10YNO-4--------9', '10Y1001A1001A48H', '10Y1001A1001A44P', '10Y1001A1001A45N', '10Y1001A1001A46L',
	             '10Y1001A1001A47J', 'IT-BRNN--------D', 'IT-CNOR--------Y', 'IT-COAC--------U', 'IT-CORS--------G',
	             'IT-CSUD--------B', 'IT-FOGN--------0', 'IT-MALT0-------R', 'IT-NORD--------N', 'IT-PRGP0-------R',
	             'IT-ROSN--------8', 'IT-SARD--------F', 'IT-SICI--------Y', 'IT-SUD---------W', '10YPT-REN------W',
	             '10YES-REE------0', '10YMA-ONE------O', '10Y1001A1001A57G', '10YNL----------L', '10YBE----------2',
	             '10YDE-ENBW-----N', '10YDE-RWENET---I', '10YDE-EON------1', '10YDE-VE-------2', '10YFR-RTE------C',
	             '10YCH-SWISSGRIDZ', '10YAT-APG------L', '10YDK-1-------AA', '10Y1001A1001A64J', '10YHR-HEP------M',
	             '10YCA-BULGARIA-R', '10Y1001A1001A59C', '10YPL-AREA-----S', '10Y1001A1001A58E', '38YNPSLVEXP----Y',
	             '38YNPSLVIMP----5', '38YNPSRUIMP----S', '10YCB-GERMANY--8', '10Y1001A1001A56I', '10Y1001A1001A55K',
	             '43YLRE-------008', '43YLRI--------04', '10YDOM-PL-SE-LT2', '10YSI-ELES-----O', '10YCZ-CEPS-----N',
	             '10YHU-MAVIR----U', '10YRO-TEL------P', '10Y1001A1001B012', '11Y0-0000-0265-K'),
	"hupx": ('10YHU-MAVIR----U',),
	"southpool": ('10YSI-ELES-----O',),
	"tge": ('10YPL-AREA-----S',),
	"ibex": ('10YCA-BULGARIA-R',),
	"cropex": ('10YHR-HEP------M',)}
NORDPOOL_EIC_CODES = {1: '10YDK-1--------W', 2: '10YDK-2--------M', 3: '10YFI-1--------U', 4: '10YDOM-1001A084H',
                      5: '10Y1001A1001A39I', 6: '10YLV-1001A00074', 7: '10YLT-1001A0008Q', 8: '10YNO-1--------2',
                      9: '10YNO-2--------T', 10: '10YNO-3--------J', 11: '10YNO-4--------9', 12: '10Y1001A1001A48H',
                      13: '10Y1001A1001A44P', 14: '10Y1001A1001A45N', 15: '10Y1001A1001A46L',
                      16: '10Y1001A1001A47J', 17: 'IT-BRNN--------D', 18: 'IT-CNOR--------Y', 19: 'IT-COAC--------U',
                      20: 'IT-CORS--------G', 21: 'IT-CSUD--------B', 22: 'IT-FOGN--------0', 23: 'IT-MALT0-------R',
                      24: 'IT-NORD--------N', 25: 'IT-PRGP0-------R', 26: 'IT-ROSN--------8', 27: 'IT-SARD--------F',
                      28: 'IT-SICI--------Y', 29: 'IT-SUD---------W', 30: '10YPT-REN------W', 31: '10YES-REE------0',
                      32: '10YMA-ONE------O', 33: '10Y1001A1001A57G', 34: '10YNL----------L', 35: '10YBE----------2',
                      36: '10YDE-ENBW-----N', 37: '10YDE-RWENET---I', 38: '10YDE-EON------1', 39: '10YDE-VE-------2',
                      40: '10YFR-RTE------C', 41: '10YCH-SWISSGRIDZ', 42: '10YAT-APG------L', 43: '10YDK-1-------AA',
                      44: '10Y1001A1001A64J', 45: '10YHR-HEP------M', 46: '10YCA-BULGARIA-R', 86: '10Y1001A1001A59C',
                      88: '10YPL-AREA-----S', 90: '10Y1001A1001A58E', 92: '38YNPSLVEXP----Y', 93: '38YNPSLVIMP----5',
                      94: '38YNPSRUIMP----S', 95: '10YCB-GERMANY--8', 96: '10Y1001A1001A56I', 97: '10Y1001A1001A55K',
                      98: '43YLRE-------008', 99: '43YLRI--------04', 100: '10YDOM-PL-SE-LT2', 108: '10YSI-ELES-----O',
                      109: '10YCZ-CEPS-----N', 110: '10YHU-MAVIR----U', 111: '10YRO-TEL------P',
                      113: '10Y1001A1001B012', 114: '11Y0-0000-0265-K'}

# Products
PRODUCTS = {"hourly": (
	"XBID_Hour_Power", "Intraday_Hour_Power", "GB_Hour_Power", "P60MIN", "Hourly_BSP", "Hour_Power_Local_OTC",
	"Hour_Power_Local"),
	"half-hourly": ("XBID_Half_Hour_Power", "Intraday_Half_Hour_Power", "GB_Half_Hour_Power", "P30MIN"),
	"quarter-hourly": (
		"XBID_Quarter_Hour_Power", "Intraday_Quarter_Hour_Power", "GB_Quarter_Hour_Power", "P15MIN",
		"Quarterly_BSP", "Quarter_Hour_Power_Local"),
	"continuous": ("Continuous_Power_Peak", "Continuous_Power_Base")}
PRODUCTS["all"] = PRODUCTS["hourly"] + PRODUCTS["quarter-hourly"] + PRODUCTS["half-hourly"] + PRODUCTS["continuous"]
