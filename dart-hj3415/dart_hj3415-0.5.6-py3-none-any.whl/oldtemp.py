import _pickles.manage_pickles


class ExtractDataFromPage:
    # 페이지의 실제 url을 받아서 내부페이지의 필요한 데이터를 추출하여 딕셔너리로 반환한다.
    @staticmethod
    def 주식분할결정(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        regex_titles = {
            '주식\s?분할\s?내용' : {'분할전': [2, 3], '분할후': [2, 4]},
            '주식\s?분할\s?목적' : {'주식분할목적': [0, 4]},
        }
        return no_sidebar_case(html, regex_titles=regex_titles, match='주식\s?분할\s?내용')

    @staticmethod
    def 주식병합결정(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        regex_titles = {
            '주식\s?병합\s?내용': {'병합전': [2, 3], '병합후': [2, 4]},
            '주식\s?병합\s?목적': {'주식병합목적': [0, 4]},
        }
        return no_sidebar_case(html, regex_titles=regex_titles, match='주식\s?병합\s?내용')

    @staticmethod
    def 자기주식처분결정(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        regex_titles = {
            '처분\s?예정\s?주식\(주\)': {'처분예정보통주식': [0, 3], '처분예정기타주식': [1, 3]},
            '처분\s?목적': {'처분목적': [0, 3]},
        }
        return no_sidebar_case(html, regex_titles=regex_titles, match='처분\s?예정\s?주식\(주\)')

    @staticmethod
    def 공개매수신고서(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        if sidebar_title is None or '요약정보' in sidebar_title:
            regex_titles = {
                '공개\s?매수자': {'매수자': [0, 2], '관계': [1, 2]},
                '공개매수\s?목적': {'매수목적': [0, 2]},

            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles))
            regex_titles = {
                '매수\s?가격': {'매수가격': [0, 3]},
            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, title_col=2))
        return return_dict

    @staticmethod
    def 전환사채권발행결정(final_url, sidebar_title):
        # CB - convertible bond
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        if sidebar_title is None or '전환사채' in sidebar_title:
            regex_titles = {
                '사채의\s?권면': {'사채의권면총액': [0, 4]},
                '사채발행방법': {'사채발행방법': [0, 4]},
            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='사채발행방법'))
        return return_dict

    @staticmethod
    def 신주인수권부사채권발행결정(final_url, sidebar_title):
        # BW - Bond warranty
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        if sidebar_title is None or '신주인수권부사채권' in sidebar_title:
            regex_titles = {
                '사채의\s?권면': {'사채의권면총액': [0, 3]},
                '사채발행방법': {'사채발행방법': [0, 3]},
            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles))
            regex_titles = {
                '사채와\s?인수권의\s?분리여부': {'사채와인수권의분리여부': [0, 3]},
            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, title_col=1, match='사채발행방법'))
        return return_dict

    @staticmethod
    def 교환사채권발행결정(final_url, sidebar_title):
        # EB - Exchange bond
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        if sidebar_title is None or '교환사채권' in sidebar_title:
            regex_titles = {
                '사채의\s?권면': {'사채의권면총액': [0, 4]},
                '사채발행방법': {'사채발행방법': [0, 4]},
            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='사채발행방법'))
        return return_dict

    @staticmethod
    def 만기전사채취득(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        regex_titles = {
            '사채의\s?종류': {'사채의종류': [0, 2]},
            '주당': {'주당가액': [0, 2]},
        }
        return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='사채의\s?취득방법', title_col=1))
        regex_titles = {
            '사채\s?취득금액': {'사채취득금액': [0, 2]},
            '취득한\s?사채의\s?권면': {'취득한사채의권면총액': {0, 2}},
            '취득후\s?사채의\s?권면': {'취득후사채의권면총액': {0, 2}},
            '만기전\s?취득사유': {'만기전취득사유및향후처리방법': {0, 2}},
            '취득자금의\s?원천': {'취득자금의원천': [0, 2]},
        }
        return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='사채의\s?취득방법'))
        return return_dict

    @staticmethod
    def 신주인수권행사(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        regex_titles = {
            '신주인수권\s?행사주식수': {'신주인수권행사주식수누계': [0, 1]},
            '발행주식총수\s?\(주\)': {'발행주식총수': [0, 1]},
            '발행주식총수\s?대비': {'발행주식총수대비': [0, 1]},
        }
        return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='신주인수권\s?행사\s?주식수\s?누계'))
        regex_titles = {
            '신주인수권\s?행사주식수': {'신주인수권행사주식수누계': [0, 1]},
            '발행주식총수\s?\(주\)': {'발행주식총수': [0, 1]},
            '발행주식총수\s?대비': {'발행주식총수대비': [0, 1]},
        }
        return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='신주인수권\s?행사\s?주식수\s?누계'))
        table_df = pd.read_html(html, match='행사일', header=1)[0]
        logger.info(f'****** Table No.1 ******')
        logger.info(table_df.to_string())
        logger.info(table_df.iloc[:, 4])
        return_dict['신주인수권행사가액'] = table_df.iloc[:, 4].mean()
        return return_dict

    @staticmethod
    def 소송등의(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        regex_titles = {
        }
        return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='', title_col=1))
        return return_dict

    @staticmethod
    def 주식배당결정(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        regex_titles = {
        }
        return_dict.update(no_sidebar_case(html, regex_titles=regex_titles))
        return return_dict

    @staticmethod
    def 주주총회소집결의(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        regex_titles = {
            '의안\s?주요내용': {'의안주요내용': [0, 2]},
        }
        return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='의안\s?주요내용'))
        if '정관' in return_dict['의안주요내용']:
            regex_titles = {
                '사업목적\s?추가': {'사업목적추가': [0, 1], '사업목적추가이유': [0, 3]},
            }
            try:
                return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='사업목적\s?추가'))
            except ValueError:
                # 사업목적추가테이블만 추출하고 싶음.
                print('사업목적추가 table does not exist in 주주총회 report')
        return return_dict

    @staticmethod
    def 회사합병결정(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        if sidebar_title is None or '회사합병결정' in sidebar_title:
            regex_titles = {
                '합병형태': {'합병형태': [0, 3]},
                '합병비율': {'합병비율': [0, 3]},
                '합병\s?신주의\s?종류와\s?수': {'합병신주보통주식': [0, 3]}
            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='합병의\s?중요영향\s?및\s?효과'))
        return return_dict

    @staticmethod
    def 회사분할결정(final_url, sidebar_title):
        logger.info('<<< ExtractDataFromPage stage >>>')
        logger.info(final_url)
        html = requests.get(final_url).text
        return_dict = {}
        if sidebar_title is None or '회사분할결정' in sidebar_title:
            regex_titles = {
                '분할방법': {'분할방법': [0, 3]},
            }
            return_dict.update(no_sidebar_case(html, regex_titles=regex_titles, match='분할의\s?중요영향\s?및\s?효과'))
            if '물적분할' in return_dict['분할방법']:
                return_dict['분할방법'] = '물적분할'
            elif '인적분할' in return_dict['분할방법']:
                return_dict['분할방법'] = '인적분할'
        return return_dict


class EvalDart:
    min_os_share = 10000000  # 발행주식총수가 천만이하면 유통물량 작은편

    # 페이지에서 추출한 딕셔너리를 바탕으로 분석하여 Notify가 필요한지에 따라 참거짓으로 반환한다.
    @staticmethod
    def 주식분할결정(dict):
        # 주식분할을 실시하면 거래가 활발해지고 주가가 너무 높아서 접근하지 못했던 소액주주 매수세 유입된다.
        c101_dict = CorpDF(dict['code']).get_dict_last_row()
        pre_os_shares = cal_os_share(dict['code'])
        pre_non_os_shares = round(float(dict['분할전']) - pre_os_shares)
        post_os_shares = round((float(c101_dict['유통비율']) / 100) * float(dict['분할후']))
        post_non_os_shares = round(float(dict['분할후']) - post_os_shares)
        logger.info(f'분할전 비유통주식수 : {pre_non_os_shares}')
        logger.info(f'분할전 유통주식수 : {pre_os_shares}')
        logger.info(f'분할후 비유통주식수 : {post_non_os_shares}')
        logger.info(f'분할후 유통주식수 : {post_os_shares}')
        dict['분할전비유통주식수'] = pre_non_os_shares
        dict['분할전유통주식수'] = pre_os_shares
        dict['분할후비유통주식수'] = post_non_os_shares
        dict['분할후유통주식수'] = post_os_shares
        try:
            if pre_os_shares <= EvalDart.min_os_share <= post_os_shares:
                # 분할전 유통주식이 천만주 이하였고 분할후 천만주 이상인 경우
                return True
        except (TypeError, ValueError):
            pass
        return False

    @staticmethod
    def 주식병합결정(dict):
        # 주식병합을 실시하면 저가주 이미지를 탈피할 수 있다.
        c101_dict = CorpDF(dict['code']).get_dict_last_row()
        pre_os_shares = cal_os_share(dict['code'])
        pre_non_os_shares = round(float(dict['병합전']) - pre_os_shares)
        post_os_shares = round((float(c101_dict['유통비율']) / 100) * float(dict['병합후']))
        post_non_os_shares = round(float(dict['병합후']) - post_os_shares)
        logger.info(f'병합전 비유통주식수 : {pre_non_os_shares}')
        logger.info(f'병합전 유통주식수 : {pre_os_shares}')
        logger.info(f'병합후 비유통주식수 : {post_non_os_shares}')
        logger.info(f'병합후 유통주식수 : {post_os_shares}')
        dict['병합전비유통주식수'] = pre_non_os_shares
        dict['병합전유통주식수'] = pre_os_shares
        dict['병합후비유통주식수'] = post_non_os_shares
        dict['병합후유통주식수'] = post_os_shares
        try:
            if EvalDart.min_os_share <= post_os_shares:
                # 병합후에도 유통 주식이 천만주 이상인 경우
                return True
        except (TypeError, ValueError):
            pass
        return False

    @staticmethod
    def 자기주식처분결정(dict):
        min_percentage = .5
        os_shares = cal_os_share(dict['code'])
        try:
            dict['유통주식대비비중'] = round(float(dict['처분예정보통주식']) / os_shares, 2)
        except ValueError:
            dict['유통주식대비비중'] = 0
        if '주식매수' in dict['처분목적'] or '성과금' in dict['처분목적']:
            return False
        elif dict['유통주식대비비중'] < min_percentage:
            return False
        else:
            return True

    @staticmethod
    def 공개매수신고서(dict):
        # 전처리 ■ 체크가 복수로 되는 경우가 있음
        logger.info(dict)
        iter = re.finditer(r'■\w+', str(dict['관계']).replace(' ', ''))
        dict['관계'] = ''
        for string in iter:
            dict['관계'] += string.group().replace('■', '') + ' '

        iter = re.finditer(r'■\w+', str(dict['매수목적']).replace(' ', ''))
        dict['매수목적'] = ''
        for string in iter:
            dict['매수목적'] += string.group().replace('■', '') + ' '

        dict['매수자'] = re.search(r'성명:\w+', str(dict['매수자']).replace(' ', '')).group().replace('성명:', '')
        if re.search(r'\d+', str(dict['매수가격']).replace(',', '')):
            dict['매수가격'] = int(re.search(r'\d+', str(dict['매수가격']).replace(',', '')).group())
            c101_dict = CorpDF(dict['code']).get_dict_last_row()
            logger.info(f'c101: {c101_dict}')
            dict['최근주가'] = c101_dict['주가']
            if dict['매수가격'] > c101_dict['주가']:
                return True
        return False

    @staticmethod
    def 전환사채권발행결정(dict):
        # 주가에 긍정적신호는 아니라 일단 무조건 False
        return False

    @staticmethod
    def 신주인수권부사채권발행결정(dict):
        # 주가에 긍정적신호는 아니라 일단 무조건 False
        return False

    @staticmethod
    def 교환사채권발행결정(dict):
        # 주가에 긍정적신호는 아니라 일단 무조건 False
        return False

    @staticmethod
    def 만기전사채취득(dict):
        if '전환사채' in dict['사채의종류']:
            a = dict['만기전취득사유및향후처리방법'].replace(' ', '')
            if ('Call' in a or 'call' in a or '콜' in a or '합의' in a) and ('소각' in a or '소작' in a):
                return True
        return False

    @staticmethod
    def 신주인수권행사(dict):
        # 주가에 긍정적신호는 아니라 일단 무조건 False
        return False

    @staticmethod
    def 소송등의(dict):
        # 주가에 긍정적신호는 아니라 일단 무조건 False
        return False

    @staticmethod
    def 주식배당결정(dict):
        # 주주가치에는 영향이 없어 아니라 일단 False
        return False

    @staticmethod
    def 주주총회소집결의(dict):
        if '사업목적추가' in dict.keys():
            return True
        else:
            return False

    @staticmethod
    def 회사합병결정(dict):
        if '소규모' in dict['합병형태']:
            return False
        else:
            # 소규모합병이외에는 한번 볼만함.
            return True

    @staticmethod
    def 회사분할결정(dict):
        return True


class Analysis:
    # report_nm과 첫페이지의 사이드바의 메뉴이름(subtitle)
    # title 및 subtitle은 일치가 아니라 포함으로 부분문자열도 가능함.
    dart_titles = {
        '주식분할결정': [],
        '주식병합결정': [],
        '자기주식처분결정': ['자기주식처분결정', ],
        '공개매수신고서': ['요약정보', ],
        '전환사채권발행결정': ['전환사채권발행결정'],
        '신주인수권부사채권발행결정': ['신주인수권부사채권발행결정'],
        '교환사채권발행결정': ['교환사채권발행결정'],
        '만기전사채취득': [],
        '신주인수권행사': [],
        '소송등의': [],
        '주식배당결정': [],
        '주주총회소집결의': [],
        '회사합병결정': ['회사합병결정', ],
        '회사분할결정': ['회사분할결정', ],
    }

    all_corp_code = get_all_corps_codes()

    def __init__(self, date, use_proxy=False):
        # use_proxy는 dart가 막혔을때 프록시를 이용해야할 경우 사용한다.
        logger.info('<<< __init__ stage >>>')
        self.date = date
        self.pickle = Pickle.load_pickle()

    def _yield_final_urls_from_initial_page(self, initial_url, subtitles):
        logger.info('<<< yield_final_urls_from_initial_page >>>')
        logger.info(f'Initial_url : {initial_url}')
        from bs4 import BeautifulSoup
        self.driver.get(initial_url)
        random_sleep()
        source = self.driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        pages = soup.findAll("span", {'unselectable': "on"})
        if len(pages) == 0:
            # 사이드바가 없는 문서의 경우
            yield self.driver.find_element_by_css_selector('#ifrm').get_attribute('src'), None
        else:
            for page in pages:
                print('\t' + page.string)
                for subtitle in subtitles:
                    sidebar_title = str(page.string).replace(' ', '')
                    logger.debug(f"compare {sidebar_title} with {subtitle}")
                    if subtitle in sidebar_title:
                        print(f"\tClick the sidebar {page.string} button...")
                        self.driver.find_element_by_link_text(page.string).click()
                        time.sleep(1)
                        yield self.driver.find_element_by_css_selector('#ifrm').get_attribute('src'), sidebar_title
                    else:
                        continue

    def _noti(self, data_dict):
        if data_dict['rcept_no'] in self.pickle['notified']:
            print('We caught the important report but already notified')
        else:
            print(f'We caught the important report')
            self.pickle['notified'].append(data_dict['rcept_no'])
            logger.info(data_dict)
            noti_str = f"*** {data_dict['report_nm']} ***\n"
            for key, value in data_dict.items():
                noti_str += key + ' : ' + str(value) + '\n'
            Notify.dart_bot(noti_str)

            if data_dict['from'] == 'matching':
                # 매칭의 경우에는 c101 회사정보를 추가해서 보내준다.
                c101_str = f"*** {data_dict['name']} c101 ***\n"
                c101_str += f"http://hj3415.iptime.org/nfapp/report/{data_dict['code']}/\n"
                c101_dict = CorpDF(data_dict['code']).get_dict_last_row()
                for key, value in c101_dict.items():
                    c101_str += key + ' : ' + str(value) + '\n'
                Notify.dart_bot(c101_str)

    def run_common(self, namedtuple, raw_title=None):
        logger.info('<<< run_common() stage >>>')
        # structure of namedtuple
        # 0:index, 1:corp_code, 2:corp_name, 3:stock_code, 4:corp_cls
        # 5:report_nm, 6:rcept_no, 7:flr_nm, 8:rcept_dt, 9:rm
        data_dict = {'name': namedtuple.corp_name,
                     'code': namedtuple.stock_code,
                     'report_nm': namedtuple.report_nm,
                     'rcept_no': namedtuple.rcept_no,
                     'initial_url': 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + str(namedtuple.rcept_no)}

        if not raw_title:
            # favorites의 경우 타이틀을 찾아내야 되기 때문에 [] ()를 제거하고 타이틀을 결정함
            raw_title = re.sub('\[\w+\]', '', re.sub('\(\w+\)', '', data_dict['report_nm']))
            if '주요사항보고서' in raw_title:
                # 주요사항보고서의 경우는 ()안에 타이틀이 들어간다.
                raw_title = re.search('\(\w+\)', data_dict['report_nm']).group().replace('(', '').replace(')', '')
            for dart_title in self.dart_titles.keys():
                # 부분문자열의 경우 처리
                if dart_title in raw_title:
                    raw_title = dart_title
                    break

        subtitles = self.dart_titles[raw_title]
        refined_title = raw_title.replace('ㆍ', '')

        if data_dict['rcept_no'] in self.pickle['analysed']:
            # 이전에 이미 분석된 경우는 넘어감
            print(f"\t<{data_dict['rcept_no']}> already analysed")
            return False
        elif not data_dict['code'] in Analysis.all_corp_code:
            # 가끔 corp db에 없는 회사 공시가 떠서 에러나는 경우가 있다. 신규회사의 경우
            self.pickle['analysed'].append(data_dict['rcept_no'])
            print(f"{data_dict['code']} is not registered in corp db yet..")
            return False
        else:
            print(f"Analysing...{data_dict['initial_url']}")
            print(f'Pages..{subtitles}') if len(subtitles) != 0 else print()
            # initial_url과 subtitle을 보내서 최종 final_url을 반환받는다.
            for final_url, sidebar_title in self._yield_final_urls_from_initial_page(data_dict['initial_url'], subtitles):
                # 각 타이틀별 딕셔너리 추출함수에 맞게 추출된 딕셔너리를 합쳐준다.
                logger.info(f'sidebar_title : {sidebar_title}')
                logger.info(f'final_url : {final_url}')
                data_dict['url' if sidebar_title is None else sidebar_title] = final_url
                data_dict.update(getattr(ExtractDataFromPage, refined_title)(final_url, sidebar_title))
            self.pickle['analysed'].append(data_dict['rcept_no'])
            return data_dict

    def run_for_test(self, raw_title, sdate=None, debug=False, noti=True):
        print('*' * 40 + raw_title + '*' * 40)
        df = DartDF(sdate=sdate, edate=self.date, title=raw_title).get_df_from_online()
        logger.info(df.to_string())
        print(f'Count : {len(df.index)}')
        for namedtuple in df.itertuples():
            data_dict = self.run_common(namedtuple, raw_title)
            if not data_dict:
                continue
            data_dict['from'] = 'matching'  # noti에서 data_dict의 근원을 파악하기 위해사용

            if debug:
                # 아이템을 하나만 분석하고 중단한다.
                pprint.pprint(data_dict)
                break
            logger.info('<<< EvalDart stage >>>')
            if getattr(EvalDart, raw_title.replace('ㆍ', ''))(data_dict) and noti:
                self._noti(data_dict)
            pprint.pprint(data_dict)
            random_sleep()

        self.pickle['date'] = self.date
        Pickle.save_pickle(self.pickle)

    def run_for_one_df(self, df: pd.DataFrame):
        print('*' * 40 + 'Analyse with dataframe' + '*' * 40)
        df = df[~df['report_nm'].str.contains('기재정정|첨부정정')]
        df = df[~df['report_nm'].str.contains('자회사의|종속회사의')]
        logger.info(df.to_string())
        print(f'Count : {len(df.index)}')
        for namedtuple in df.itertuples():
            data_dict = self.run_common(namedtuple)
            if not data_dict:
                continue

            pprint.pprint(data_dict)
            random_sleep()
            yield data_dict

    def run_by_titles(self):
        logger.info('<<< run_by_titles() stage >>>')
        print(f'Titles : {self.dart_titles.keys()}')
        for raw_title in self.dart_titles.keys():
            print('*' * 40 + raw_title + '*' * 40)
            filtered_df = DartDF(self.date, title=raw_title).get_df_from_online()
            logger.info(filtered_df.to_string())
            print(f'Count : {len(filtered_df.index)}')
            for namedtuple in filtered_df.itertuples():
                data_dict = self.run_common(namedtuple, raw_title)
                if not data_dict:
                    continue
                data_dict['from'] = 'matching'  # noti에서 data_dict의 근원을 파악하기 위해사용
                logger.info('<<< EvalDart stage >>>')
                if getattr(EvalDart, raw_title.replace('ㆍ', ''))(data_dict):
                    self._noti(data_dict)
                pprint.pprint(data_dict)
                random_sleep()
            self.pickle['date'] = self.date
            Pickle.save_pickle(self.pickle)

    def run_by_favorites(self):
        logger.info('<<< run_by_favorites() stage >>>')
        fav_dict = _pickles.manage_pickles.Pickle2.load_pickle()
        print(f'Favorites : {fav_dict}')
        for fav_one_code, fav_one_name in fav_dict.items():
            print('*' * 40 + fav_one_code + '\t' + fav_one_name + '*' * 40)
            df = DartDF(edate=self.date, code=fav_one_code).get_df_from_online()
            logger.info(df.to_string())
            for namedtuple in df.itertuples():
                data_dict = self.run_common(namedtuple)
                if not data_dict:
                    continue
                data_dict['from'] = 'favorites' # noti에서 data_dict의 근원을 파악하기 위해사용

                print(f'Data : {data_dict}')
                self._noti(data_dict)
                random_sleep()

        self.pickle['date'] = self.date
        Pickle.save_pickle(self.pickle)

    def run(self):
        # 분석전에 dart를 미리 저장하여 filtered_df를 가져올때 db를 이용하도록 한다.
        start_time = time.time()
        dart_db.save_df_to_dart_db('t' + self.date, DartDF(self.date).get_df_from_online())
        self.run_by_favorites()
        self.run_by_titles()
        print(f'Total spent time : {round(time.time() - start_time, 2)} sec')
        print('done.')