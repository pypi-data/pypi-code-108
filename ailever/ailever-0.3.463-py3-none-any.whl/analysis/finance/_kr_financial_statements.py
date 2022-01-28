import OpenDartReader
import pandas as pd
import plotly.graph_objects as go

class MetaClass(type):
    def __new__(cls, clsname, bases, namespace):
        namespace['__str__'] = lambda self: str(self.values)
        namespace['values'] = None
        return type.__new__(cls, clsname, bases, namespace)

SubFinState = MetaClass('SubFinState', (dict,), {})


class KRFinState:
    def __init__(self, API_key):
        dart = OpenDartReader(API_key) 

        rcept_no = dart.finstate('005930', 2018).rcept_no[0]
        attaches = dart.attach_file_list(rcept_no)
        attaches_query = attaches.query('type=="excel"')

        file_name = attaches_query.file_name.values[0]
        url = attaches.query('type=="excel"').url.values[0]
        dart.retrieve(url, file_name)

        sheet_names = pd.ExcelFile(file_name).sheet_names
        for sheet_name in sheet_names:
            if sheet_name == '연결 재무상태표':
                self.BSData = pd.read_excel(file_name, sheet_name=sheet_name, skiprows=6)
            elif sheet_name == '연결 손익계산서':
                self.ISData = pd.read_excel(file_name, sheet_name=sheet_name, skiprows=6)
            elif sheet_name == '연결 포괄손익계산서':
                self._ISData = pd.read_excel(file_name, sheet_name=sheet_name, skiprows=6)
            elif sheet_name == '연결 현금흐름표':
                self.CFData = pd.read_excel(file_name, sheet_name=sheet_name, skiprows=6)

        self.__init()
        self.__validation()

    def __init(self):
        # statement of financial position
        self.BS = SubFinState()
        self.BS.assets = SubFinState()
        self.BS.assets.current_assets = SubFinState()
        self.BS.assets.non_current_assets = SubFinState()
        self.BS.liabilities = SubFinState()
        self.BS.liabilities.current_liabilities = SubFinState()
        self.BS.liabilities.non_current_liabilities = SubFinState()
        self.BS.shareholders_equity = SubFinState()
        self.BS.shareholders_equity.owners_equity = SubFinState()
        self.BS.shareholders_equity.non_controlling_entity = SubFinState()
        self.__BS()

        # statement of income
        self.IS = SubFinState()
        self.IS.revenue = SubFinState()
        self.IS.cost_of_goods_sold = SubFinState()
        self.IS.gross_profit = SubFinState()
        self.IS.operating_expenses = SubFinState()
        self.IS.operating_income = SubFinState()
        self.IS.non_operating_revenue = SubFinState()
        self.IS.non_operating_expenses = SubFinState()
        self.IS.income_before_tax = SubFinState()
        self.IS.income_tax = SubFinState()
        self.IS.net_income = SubFinState()
        self.IS.others = SubFinState()
        self.__IS()

        # statement of cash flow
        self.CF = SubFinState()
        self.CF.operating_activities = SubFinState()
        self.CF.investing_activities = SubFinState()
        self.CF.financing_activities = SubFinState()
        self.CF.others = SubFinState()
        self.__CF()

    def __BS(self):
        list_of_current_assets = [
            '현금및현금성자산',
            '단기금융상품',
            '단기매도가능금융자산',
            '단기상각후원가금융자산',
            '단기당기손익-공정가치금융자산',
            '매출채권',
            '미수금',
            '선급금',
            '선급비용',
            '재고자산',
            '기타유동자산',
            '매각예정분류자산',
        ]
        list_of_non_current_assets = [
            '장기매도가능금융자산',
            '만기보유금융자산',
            '상각후원가금융자산',
            '기타포괄손익-공정가치금융자산',
            '당기손익-공정가치금융자산',
            '관계기업 및 공동기업 투자',
            '유형자산',
            '무형자산',
            '장기선급비용',
            '순확정급여자산',
            '이연법인세자산',
            '기타비유동자산',
        ]
        list_of_current_liabilities = [
            '매입채무',
            '단기차입금',
            '미지급금',
            '선수금',
            '예수금',
            '미지급비용',
            '미지급법인세',
            '유동성장기부채',
            '충당부채',
            '기타유동부채',
            '매각예정분류부채',
        ]
        list_of_non_current_liabilities = [
            '사채',
            '장기차입금',
            '장기미지급금',
            '순확정급여부채',
            '이연법인세부채',
            '장기충당부채',
            '기타비유동부채',
        ]
        list_of_owners_equity = [
            '지배기업 소유주지분',
            '자본금',
            '우선주자본금',
            '보통주자본금',
            '주식발행초과금',
            '이익잉여금',
            '기타자본항목',
            '매각예정분류기타자본항목',
        ]
        list_of_non_controlling_equity = [
            '비지배지분',
        ]

        for _bs in self.BSData.values:
            fs_name = _bs[0].strip()
            fs_value = _bs[1]
            # assets
            if fs_name in list_of_current_assets:
                self.BS.assets.current_assets[fs_name] = fs_value
            elif fs_name in list_of_non_current_assets:
                self.BS.assets.non_current_assets[fs_name] = fs_value
            # liabilities
            elif fs_name in list_of_current_liabilities:
                self.BS.liabilities.current_liabilities[fs_name] = fs_value
            elif fs_name in list_of_non_current_liabilities:
                self.BS.liabilities.non_current_liabilities[fs_name] = fs_value
            # shareholders_equity
            elif fs_name in list_of_owners_equity:
                self.BS.shareholders_equity.owners_equity[fs_name] = fs_value
            elif fs_name in list_of_non_controlling_equity:
                self.BS.shareholders_equity.non_controlling_entity[fs_name] = fs_value

    def __IS(self):
        for _is in self.ISData.values:
            fs_name = _is[0].strip()
            fs_value = _is[1]
            if fs_name in ['수익(매출액)']:
                self.IS.revenue[fs_name] = fs_value
            elif fs_name in ['매출원가']:
                self.IS.cost_of_goods_sold[fs_name] = fs_value
            elif fs_name in ['매출총이익']:
                self.IS.gross_profit[fs_name] = fs_value
            elif fs_name in ['판매비와관리비']:
                self.IS.operating_expenses[fs_name] = fs_value
            elif fs_name in ['영업이익(손실)']:
                self.IS.operating_income[fs_name] = fs_value
            elif fs_name in ['기타수익', '지분법이익', '금융수익']:
                self.IS.non_operating_revenue[fs_name] = fs_value
            elif fs_name in ['기타비용', '금융비용']:
                self.IS.non_operating_expenses[fs_name] = fs_value
            elif fs_name in ['법인세비용차감전순이익(손실)']:
                self.IS.income_before_tax[fs_name] = fs_value
            elif fs_name in ['법인세비용']:
                self.IS.income_tax[fs_name] = fs_value
            elif fs_name in ['당기순이익(손실)']:
                self.IS.net_income[fs_name] = fs_value
            else:
                self.IS.others[fs_name] = fs_value

    def __CF(self):
        list_of_operating_activities = [
            '영업에서 창출된 현금흐름',
            '당기순이익',
            '조정',
            '영업활동으로 인한 자산부채의 변동',
            '이자의 수취',
            '이자의 지급',
            '배당금 수입',
            '법인세 납부액',
        ]
        list_of_investing_activities = [
            '단기금융상품의 순감소(증가)',
            '단기상각후원가금융자산의 순증가',
            '단기당기손익-공정가치금융자산의 순증가',
            '단기매도가능금융자산의 처분',
            '단기매도가능금융자산의 취득',
            '장기금융상품의 처분',
            '장기금융상품의 취득',
            '장기매도가능금융자산의 처분',
            '장기매도가능금융자산의 취득',
            '만기보유금융자산의 취득',
            '상각후원가금융자산의 취득',
            '기타포괄손익-공정가치금융자산의 처분',
            '기타포괄손익-공정가치금융자산의 취득',
            '당기손익-공정가치금융자산의 처분',
            '당기손익-공정가치금융자산의 취득',
            '관계기업 및 공동기업 투자의 처분',
            '관계기업 및 공동기업 투자의 취득',
            '유형자산의 처분',
            '유형자산의 취득',
            '무형자산의 처분',
            '무형자산의 취득',
            '사업결합으로 인한 현금유출액',
            '사업양도로 인한 현금유입액',
            '현금의 기타유출입',
        ]
        list_of_financing_activities = [
            '단기차입금의 순증가(감소)',
            '자기주식의 취득',
            '사채 및 장기차입금의 차입',
            '사채 및 장기차입금의 상환',
            '배당금 지급',
            '비지배지분의 증감',
        ]

        for _cf in self.CFData.values:
            fs_name = _cf[0].strip()
            fs_value = _cf[1]
            if fs_name in list_of_operating_activities:
                self.CF.operating_activities[fs_name] = fs_value
            elif fs_name in list_of_investing_activities:
                self.CF.investing_activities[fs_name] = fs_value
            elif fs_name in list_of_financing_activities:
                self.CF.financing_activities[fs_name] = fs_value
            else:
                self.CF.others[fs_name] = fs_value

    def __validation(self):
        pass

    def BalanceSheet(self):
		labels =  ["Assets", 'Current Assets', 'Non-Current Assets',"Liabilities", 'Current Liabilities', 'Non-Current Liabilities', "Shareholders Equity",      "Owner's Equity", "Non Controlling Entity"]
		parents = [      "",         'Assets',             'Assets',           "",         'Liabilities',             'Liabilities',                    "", 'Shareholders Equity',    'Shareholders Equity']

		fig = go.Figure(go.Treemap(
			labels = labels,
			parents = parents,
		))
		fig.show()
		return fig

    def IncomeStatement(self):
        pass
    def CashFlowStatement(self):
        pass
