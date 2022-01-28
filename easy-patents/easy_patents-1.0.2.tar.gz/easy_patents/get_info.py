import os
import requests
import mojimoji
import time
import datetime
import configparser
import zipfile
import json
import glob
import pathlib
from easy_patents.get_apitoken import HOST
from easy_patents.auth_info import AuthInfo, DATETIME_FORMAT
from easy_patents.errors import is_error


AUTHINFO = AuthInfo()
CONFIG = AUTHINFO.config

API_RETRY = 3
API_SLEEP_TIME = 1
API_TEMPORARY_ERRORS = {'210', '302', '303'}


def get_api_info(url):
    '''
    API情報を取得する関数
    レスポンスがjsonデータの場合にはjson形式に変換する

    Parameters
    ----------
    url : str
        取得先URL
    accesstoken : str
        アクセストークン

    Returns
    -------
    json or response
        取得したデータ
    '''
    # 通信失敗などで取得エラーがありうるので、RETRY回までリトライする
    for i in range(0, API_RETRY):
        accesstoken = AUTHINFO.get_accesstoken()
        header = {
            "Host": HOST,
            "Authorization": "Bearer " + accesstoken
        }
        response = requests.get(url, headers=header)
        # jsonファイル以外の場合には取得は成功しているので、breakする
        if response.headers['content-type'] != "application/json":
            break
        response = response.json()
        status_code = response["result"]["statusCode"]
        # statusCodeがAPI_TEMPORARY_ERRORSの場合、
        # API_SLEEP_TIME秒スリープしてからリトライ
        if status_code in API_TEMPORARY_ERRORS:
            time.sleep(API_SLEEP_TIME)
            continue
        break

    # ステータスコードを確認してエラーの場合にはエラーを投げる
    # 対象とするのはjsonのみ
    if not isinstance(response, requests.Response):
        is_error(response)
    return response


def get_app_progress(case_number):
    '''
    特許経過情報の取得
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_progress

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。
    accesstoken : str
        アクセストークン

    Returns
    -------
    json
        特許経過情報のJsonデータ

    Examples
    --------
    >>> info = get_app_progress("２０２０－００８４２３")
    >>> info["result"]["data"]["inventionTitle"]
    '管理システム及び管理方法'
    '''
    url = make_url("app_progress", case_number)
    return get_api_info(url)


def get_app_progress_simple(case_number):
    '''
    指定された特許出願番号に紐づく経過情報（優先権基礎情報、原出願情報、分割出願群情報を含まない）を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_progress_simple

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。
    accesstoken : str
        アクセストークン

    Returns
    -------
    json
        特許経過情報のJsonデータ

    Examples
    --------
    >>> info = get_app_progress_simple("２０２０－００８４２３")
    >>> info["result"]["data"]["inventionTitle"]
    '管理システム及び管理方法'
    '''
    url = make_url("app_progress_simple", case_number)
    return get_api_info(url)


def get_divisional_app_info(case_number):
    '''
    指定された特許出願番号に紐づく分割出願情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-divisional_app_info

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。
    accesstoken : str
        アクセストークン

    Returns
    -------
    json
        分割出願情報のJsonデータ

    Examples
    --------
    >>> info = get_divisional_app_info("２００７－０３５９３７")
    >>> info["result"]["data"]['parentApplicationInformation'] ['parentApplicationNumber']
    '2000009310'
    '''
    url = make_url("divisional_app_info", case_number)
    return get_api_info(url)


def get_priority_right_app_info(case_number):
    '''
    指定された特許出願番号に紐づく優先基礎出願情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-priority_right_app_info

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。
    accesstoken : str
        アクセストークン

    Returns
    -------
    json
        優先基礎情報のJsonデータ

    Examples
    --------
    >>> info = get_priority_right_app_info("2020008423")
    >>> info["result"]["data"]["priorityRightInformation"][0]['nationalPriorityDate']
    '20190730'
    '''
    url = make_url("priority_right_app_info", case_number)
    return get_api_info(url)


def get_applicant_attorney_cd(code):
    '''
    指定された申請人コードで申請人(出願人・代理人)氏名・名称を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-applicant_attorney-cd

    Parameters
    ----------
    code : str
        申請人コード
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    json
        申請人情報のJsonデータ

    Examples
    --------
    >>> info = get_applicant_attorney_cd("718000266")
    >>> info["result"]["data"]["applicantAttorneyName"]
    '特許庁長官'
    '''
    url = make_url("applicant_attorney_cd", code)
    return get_api_info(url)


def get_applicant_attorney(name):
    '''
    指定された申請人氏名・名称を完全一致検索で、申請人(出願人・代理人)コードを取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-applicant_attorney

    Parameters
    ----------
    name : str
        氏名

    Returns
    -------
    json
        申請人情報のJsonデータ

    Examples
    --------
    >>> info = get_applicant_attorney("特許庁長官")
    >>> info["result"]["data"]["applicantAttorney"][0]['applicantAttorneyCd']
    '718000266'
    '''
    url = make_url("applicant_attorney", name, convert=False)
    return get_api_info(url)


def get_case_number_reference(seed, case_number):
    '''
    指定された種別と案件番号に紐づく案件番号を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-case_number_reference

    Parameters
    ----------
    seed : str
        application, publication, regstrationのどれか
    case_number : str
        applicationの場合には出願番号、publicationの場合には公開番号、registrationの場合には登録番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    json
        案件情報のJsonデータ
    '''
    url = make_url("case_number_reference", case_number, seed=seed)
    return get_api_info(url)


def get_application_reference(case_number):
    '''
    出願について出願番号に紐づく案件番号を取得する。

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。
    accesstoken : str
        アクセストークン

    Returns
    -------
    json
        案件情報のJsonデータ

    Examples
    --------
    >>> info = get_application_reference("2020008423")
    >>> info['result']["data"]["publicationNumber"]
    '2021022359'
    '''
    return get_case_number_reference('application', case_number)


def get_publication_reference(case_number):
    '''
    公開について公開・公表番号に紐づく案件番号を取得する。

    Parameters
    ----------
    case_number : str
        公開・公表番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    json
        案件情報のJsonデータ

    Examples
    --------
    >>> info = get_publication_reference("2021022359")
    >>> info['result']["data"]["registrationNumber"]
    '6691280'
    '''
    return get_case_number_reference('publication', case_number)


def get_registration_reference(case_number):
    '''
    登録について登録番号に紐づく案件番号を取得する。

    Parameters
    ----------
    case_number : str
        登録番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    json
        案件情報のJsonデータ

    Examples
    --------
    >>> info = get_registration_reference("6691280")
    >>> info['result']["data"]["applicationNumber"]
    '2020008423'
    '''
    return get_case_number_reference('registration', case_number)


def get_app_doc_cont_opinion_amendment(case_number):
    '''
    指定された特許出願番号に対応する実体審査における特許申請書類の実体ファイル（意見書・手続補正書）のZIPファイルをダウンロードする。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_doc_cont_opinion_amendment

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    zipを含むレスポンス
        意見書・手続き補正書のzip

    Examples
    --------
    >>> info = get_app_doc_cont_opinion_amendment("2020008423")
    >>> info.headers['content-type']
    'application/zip'
    '''
    url = make_url("app_doc_cont_opinion_amendment", case_number)
    return get_api_info(url)


def get_app_doc_cont_refusal_reason_decision(case_number):
    '''
    指定された特許出願番号に対応する実体審査における発送書類の実体ファイル（拒絶理由通知書、特許査定、拒絶査定、補正の却下の決定）のZIPファイルをダウンロードする。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_doc_cont_opinion_amendment

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    zipを含むレスポンス
        拒絶理由通知等

    Examples
    --------
    >>> info = get_app_doc_cont_refusal_reason_decision("2020008423")
    >>> info.headers['content-type']
    'application/zip'
    '''
    url = make_url("app_doc_cont_refusal_reason_decision", case_number)
    return get_api_info(url)


def get_app_doc_cont_refusal_reason(case_number):
    '''
    指定された特許出願番号に対応する拒絶理由通知書のZIPファイルをダウンロードする。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_doc_cont_refusal_reason

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    zipを含むレスポンス
        拒絶理由通知等

    Examples
    --------
    >>> info = get_app_doc_cont_refusal_reason("2007035937")
    >>> info.headers['content-type']
    'application/zip'
    '''
    url = make_url("app_doc_cont_refusal_reason", case_number)
    return get_api_info(url)


def get_cite_doc_info(case_number):
    '''
    指定された特許出願番号に紐づく引用文献情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-cite-doc-info

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    json
        引用文献情報のjsonデータ

    Examples
    --------
    >>> info = get_cite_doc_info("2020008423")
    >>> info["result"]["data"]["patentDoc"][0]["documentNumber"]
    'JPA 421211144'
    '''
    url = make_url("cite_doc_info", case_number)
    return get_api_info(url)


def get_registration_info(case_number):
    '''
    指定された特許出願番号に紐づく登録情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-registration-info

    Parameters
    ----------
    case_number : str
        出願番号
        全角は半角に変換される。また-と/は無視される。

    Returns
    -------
    json
        登録情報のjsonデータ

    Examples
    --------
    >>> info = get_registration_info("2020008423")
    >>> info["result"]["data"]["expireDate"]
    '20400122'
    '''
    url = make_url("registration_info", case_number)
    return get_api_info(url)


def save_to_file(response, dirname, filename=None):
    '''
    responseのcontentをファイルに保存する関数

    Parameters
    ----------
    response : Response
        レスポンスオブジェクト(主にzipファイル取得用)
    dirname : str
        保存先ディレクトリ名
    filename : str
        保存先ファイル名
        省略された場合には、Content-Dispositionから取得

    Returns
    -------
    str
        保存先ファイルのフルパス

    Examples
    --------
    >>> info = get_app_doc_cont_refusal_reason("2007035937")
    >>> base_dir = os.path.dirname(__file__)
    >>> save_dir = os.path.join(base_dir, "tmp")
    >>> os.makedirs(save_dir, exist_ok=True)

    # ファイル名を指定しない場合、Content-Dispositionが使用される
    >>> save_path = save_to_file(info, save_dir)
    >>> save_path
    'tmp/docContRefusalReason_2007035937.zip'
    >>> os.path.exists(save_path)
    True

    # ファイル名を指定すると、その名前で保存
    >>> save_path = save_to_file(info, save_dir, "test.zip")
    >>> save_path
    'tmp/test.zip'
    >>> os.path.exists(save_path)
    True
    '''
    if filename is None:
        filename = response.headers['Content-Disposition'].split("=")[1]
    save_path = os.path.join(dirname, filename)
    with open(save_path, "wb") as f:
        f.write(response.content)
    return save_path


def zfill_key(key, delimiter, digit=6):
    '''
    keyの0埋めをする関数
    出願番号は、-などで区切った右側が6桁なので、6桁になるまで0埋めする
    
    Parameters
    ----------
    key : str
        出願番号など
    delimiter : str
        区切り文字
    digit : int
        桁数

    Returns
    -------
    str
        0埋め後の文字列

    Examples
    --------
    # 区切り文字の右側を0埋め
    >>> zfill_key("2020-8423", "-")
    '2020008423'
    >>> zfill_key("2020-12", "-")
    '2020000012'
    >>> zfill_key("2020/8423", "/")
    '2020008423'

    # 区切り文字がない場合にはそのままの文字列を返す
    >>> zfill_key("20208423", "/")
    '20208423'
    '''
    if delimiter in key:
        first, second = key.split(delimiter)
        key = first + second.zfill(digit)
    return key

def convert_key(key):
    '''
    半角変換と、出願番号などの形式に沿うように変換する関数

    Paramters
    ---------
    key : str
        変換対象文字列

    Returns
    -------
    str
        変換後の文字列

    Examples
    --------
    >>> convert_key("特願２０２０－８４２３号")
    '2020008423'
    >>> convert_key("特開２０２０／８４２３号")
    '2020008423'
    >>> convert_key("2020008423")
    '2020008423'
    >>> convert_key("特許第1234567号")
    '1234567'
    '''
    key = mojimoji.zen_to_han(key)
    key = key.replace("特願", "")
    key = key.replace("特開", "")
    key = key.replace("特表", "")
    key = key.replace("特許", "")
    key = key.replace("第", "")
    key = key.replace("号", "")
    key = key.replace("公報", "")
    key = zfill_key(key, "-")
    key = zfill_key(key, "/")
    return key


def make_url(api_name, key, seed=None, convert=True):
    '''
    APIでのアクセス先URLを作成する関数

    Parameters
    ----------
    api_name : str
        取得先APIの名前(app_progressなど)
    key ; str
        取得すべき情報を特定するためのキー(例:出願番号)
    seed : str
        application, publication, registrationのどれか
    convert : boolean
        keyを半角に変換するかどうか

    Returns
    -------
    str
        URL

    Examples
    --------
    >>> make_url("app_progress", "特願２０２０－８５２４")
    'https://ip-data.jpo.go.jp/api/patent/v1/app_progress/2020008524'
    >>> make_url("app_progress", "特願２０２０－８５２４", convert=False)
    'https://ip-data.jpo.go.jp/api/patent/v1/app_progress/特願２０２０－８５２４'
    >>> make_url("app_progress", "特願２０２０－８５２４", seed="test")
    'https://ip-data.jpo.go.jp/api/patent/v1/app_progress/test/2020008524'
    '''
    base_url = "https://ip-data.jpo.go.jp/api/patent/v1"
    if convert:
        key = convert_key(key)
    if seed:
        url = "%s/%s/%s/%s" % (base_url, api_name, seed, key)
    else:
        url = "%s/%s/%s" % (base_url, api_name, key)
    return url


def make_dir_path(api_type, key, file_type="json"):
    '''
    ディレクトリパス文字列を作成するとともに、そのディレクトリを作成する関数

    Parameters
    ----------
    api_type: str
        app_progressのようなAPIの種別を特定する文字列
    key: str
        対象の情報を特定するためのキー(出願番号等)
    file_type: str
        保存するファイルのタイプ(拡張子)

    Returns
    -------
    str
        ディレクトリパス文字列
    '''
    if file_type == "zip":
        dir_name = CONFIG['DirPath']['zip_dir']
    else:
        dir_name = CONFIG['DirPath']['data_dir']
    p = pathlib.Path(dir_name)
    if p.is_absolute():
        dir_path = os.path.join(dir_name, key, api_type)
    else:
        base_dir = os.path.dirname(__file__)
        dir_path = os.path.join(base_dir, dir_name, key, api_type)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def unzip_and_save(response, api_type, key, zip_file_name=None):
    '''
    zipを含むレスポンスを、zipの解凍まで行う

    Parameters
    ----------
    response: Response
        レスポンスオブジェクト
    api_type: str
        APIの種別
    key: str
        出願番号などのキー
    zip_file_name: str
        中間ファイルのzipファイル名を指定したい場合に使用

    Returns
    -------
    str
        解凍後のファイルが格納されたディレクトリパス

    Examples
    --------
    >>> info = get_app_doc_cont_refusal_reason("2007035937")
    >>> unzip_and_save(info, "app_doc_cont_refusal_reason", "2007035937")
    'data/2007035937/app_doc_cont_refusal_reason'
    '''
    # zipファイルの保存
    zip_dir = make_dir_path(api_type, key, file_type="zip")
    zip_path = save_to_file(response, zip_dir, zip_file_name)

    # zipファイルの解凍
    file_dir = make_dir_path(api_type, key, file_type="xml")

    with zipfile.ZipFile(zip_path) as z:
        z.extractall(file_dir)
    os.remove(zip_path)
    return file_dir

def get_latest_file(file_dir):
    search_path = os.path.join(file_dir, "*")
    files = glob.glob(search_path) 
    if files:
        return max(files, key=os.path.getctime)
    else:
        return ""


def get_unzip_data(func, key, reget_date=30):
    '''
    unzipしたデータのディレクトリ名を取得する

    Parameters
    ----------
    func: func
        API情報取得関数
    key: str
        対象の情報を特定するためのキー(出願番号など)
    reget_date:boolean
        既存のファイルの存否に関係なくAPI情報を取得するかどうか

    Returns
    -------
    str
        ディレクトリ名

    Examples
    --------
    >>> key = "2020008423"
    >>> get_unzip_data(get_app_doc_cont_refusal_reason_decision, key)
    'data/2020008423/app_doc_cont_refusal_reason_decision'
    '''
    api_type = get_api_type(func)
    key = convert_key(key)
    file_dir = make_dir_path(api_type, key, file_type="xml")
    now = datetime.datetime.now()
    expire_date = now - datetime.timedelta(days=reget_date)
    latest_file = get_latest_file(file_dir)
    if latest_file:
        file_timestamp = os.path.getctime(latest_file)
        create_date = datetime.datetime.fromtimestamp(file_timestamp)
        if expire_date < create_date:
            return file_dir
    response = func(key)
    return unzip_and_save(response, api_type, key)


def get_json_path(dir_name, non_exist_ok=True):
    '''
    指定されたディレクトリにあるjsonパスを返す
    
    Parameters
    ----------
    dir_name: str
        ディレクトリ名
    
    Returns
    -------
    str
        jsonファイルパス or 空文字列
    '''
    file_name = "api_data.json"
    json_path = os.path.join(dir_name, file_name)
    if non_exist_ok:
        return json_path
    if os.path.exists(json_path):
        return json_path
    else:
        return ""


def save_json(json_data, file_dir):
    '''
    jsonデータを保存する

    Parameters
    ----------
    json_data: json
        jsonデータ
    file_dir: str
        保存先ディレクトリ名

    Returns
    -------
    str
        保存後のファイル名

    Examples
    --------
    >>> info = get_app_progress("2020-8423")
    >>> file_dir = make_dir_path("app_progress", "2020008423", file_type="json")
    >>> file_path = save_json(info, file_dir)
    >>> os.path.exists(file_path)
    True
    '''
    json_path = get_json_path(file_dir)
    now = datetime.datetime.now()
    json_data['ep_data'] = {
            'create_date': now.strftime(DATETIME_FORMAT),
            'file_path': json_path,
    }
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=4)
    return json_path


def get_api_type(func):
    '''
    API情報取得関数の関数名からAPI種別を特定する関数

    Parameters
    ----------
    func:func
        API情報取得関数

    Returns
    -------
    str
        API情報取得関数を特定する文字列
    '''
    # 関数名のget_以降を取得
    return func.__name__[4:]


'''
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
'''


def get_json(func, key, reget_date=30, convert=True):
    '''
    jsonデータを取得する

    Parameters
    ----------
    func: func
        API情報を取得するための関数
    key: str
        どの情報化を特定するキー(出願番号など)
    reget_date: int
        ファイルの存否に関係なくjsonデータを取得するか

    Returns
    -------
    json
        対象のJsonデータ

    Examples
    --------
    >>> info = get_json(get_app_progress, "2020-8422")
    >>> info['result']['data']['inventionTitle']
    '窓装置及び窓の施工方法'

    >>> json_dir = make_dir_path('app_progress', '2020008422', file_type="json")
    >>> search_path = os.path.join(json_dir, "*")
    >>> before_get_json = len(glob.glob(search_path))

    # reget_date=0の場合、ファイルの即取得がなされる
    >>> info = get_json(get_app_progress, "2020-8422", reget_date=0)

    # reget_dateが0でない場合、ファイルの取得日からreget_date経ったときのみ再取得がなされる
    >>> info = get_json(get_app_progress, "2020-8422", reget_date=30)
    '''
    api_type = get_api_type(func)
    if convert:
        key = convert_key(key)
    json_dir = make_dir_path(api_type, key, file_type="json")
    json_file = get_json_path(json_dir, non_exist_ok=False)
    if json_file != "":
        now = datetime.datetime.now()
        expire_date = now - datetime.timedelta(days=reget_date)
        with open(json_file) as f:
            json_data = json.load(f)
        create_date = datetime.datetime.strptime(json_data['ep_data']['create_date'], DATETIME_FORMAT)
        if expire_date < create_date:
             return json_data
    # 既存ファイルがないか、再取得日数を過ぎている場合には、
    # API情報を取得する
    json_data = func(key)
    # 次回以降の処理のために保存
    save_json(json_data, json_dir)
    return json_data


def app_progress(case_number, reget_date=30):
    '''
    指定された特許出願番号に紐づく経過情報（優先権基礎情報、原出願情報、分割出願群情報を含まない）を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_progress<
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        特許経過情報のjsonデータ

    Examples
    --------
    >>> info = app_progress("２０２０－００８４２３")
    >>> info["result"]["data"]["inventionTitle"]
    '管理システム及び管理方法'
    '''
    return get_json(get_app_progress, case_number, reget_date)


def app_progress_simple(case_number, reget_date=30):
    '''
    指定された特許出願番号に紐づく経過情報（優先権基礎情報、原出願情報、分割出願群情報を含まない）を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_progress_simple
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        特許経過情報のjsonデータ

    Examples
    --------
    >>> info = app_progress_simple("２０２０－００８４２３")
    >>> info["result"]["data"]["inventionTitle"]
    '管理システム及び管理方法'
    '''
    return get_json(get_app_progress_simple, case_number, reget_date)


def divisional_app_info(case_number, reget_date=30):
    '''
    指定された特許出願番号に紐づく分割出願情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-divisional_app_info
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        分割出願情報のjsonデータ

    Examples
    --------
    >>> info = divisional_app_info("２００７－０３５９３７")
    >>> info["result"]["data"]['parentApplicationInformation'] ['parentApplicationNumber']
    '2000009310'
    '''
    return get_json(get_divisional_app_info, case_number, reget_date)


def priority_right_app_info(case_number, reget_date=30):
    '''
    指定された特許出願番号に紐づく優先基礎出願情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-priority_right_app_info
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        優先出願情報のjsonデータ

    Examples
    --------
    >>> info = priority_right_app_info("2020008423")
    >>> info["result"]["data"]["priorityRightInformation"][0]['nationalPriorityDate']
    '20190730'
    '''
    return get_json(get_priority_right_app_info, case_number, reget_date)


def applicant_attorney_cd(code, reget_date=30):
    '''
    指定された申請人コードで申請人(出願人・代理人)氏名・名称を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-applicant_attorney-cd
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    code: str
        申請人コード
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        申請人情報のjsonデータ

    Examples
    --------
    >>> info = applicant_attorney_cd("718000266")
    >>> info["result"]["data"]["applicantAttorneyName"]
    '特許庁長官'
    '''
    return get_json(get_applicant_attorney_cd, code, reget_date)


def applicant_attorney(name, reget_date=30):
    '''
    指定された申請人氏名・名称を完全一致検索で、申請人(出願人・代理人)コードを取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-applicant_attorney
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    name: str
        申請人名称
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        申請人情報のjsonデータ

    Examples
    --------
    >>> info = applicant_attorney("特許庁長官")
    >>> info["result"]["data"]["applicantAttorney"][0]['applicantAttorneyCd']
    '718000266'
    '''
    return get_json(get_applicant_attorney, name, reget_date, convert=False)


def application_reference(case_number, reget_date=30):
    '''
    出願番号に紐づく案件番号を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-case_number_reference
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        案件情報のjsonデータ

    Examples
    --------
    >>> info = application_reference("2020008423")
    >>> info['result']["data"]["publicationNumber"]
    '2021022359'
    '''
    return get_json(get_application_reference, case_number, reget_date)


def publication_reference(case_number, reget_date=30):
    '''
    公開について公開・公表番号に紐づく案件番号を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-case_number_reference
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        公開・公表番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        案件情報のjsonデータ

    Examples
    --------
    >>> info = publication_reference("2021022359")
    >>> info['result']["data"]["registrationNumber"]
    '6691280'
    '''
    return get_json(get_publication_reference, case_number, reget_date)


def registration_reference(case_number, reget_date=30):
    '''
    登録について登録番号に紐づく案件番号を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-case_number_reference
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        登録番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json
        案件情報のjsonデータ

    Examples
    --------
    >>> info = registration_reference("6691280")
    >>> info['result']["data"]["applicationNumber"]
    '2020008423'
    '''
    return get_json(get_registration_reference, case_number, reget_date)


def app_doc_cont_opinion_amendment(case_number, reget_date=30):
    '''
    指定された特許出願番号に対応する実体審査における特許申請書類の実体ファイル（意見書・手続補正書）のxmlが格納されたディレクトリパスを返す。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_doc_cont_opinion_amendment
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    str
        ディレクトリパス

    Examples
    --------
    >>> app_doc_cont_opinion_amendment("2020008423")
    'data/2020008423/app_doc_cont_opinion_amendment'
    '''
    return get_unzip_data(get_app_doc_cont_opinion_amendment, case_number, reget_date)


def app_doc_cont_refusal_reason_decision(case_number, reget_date=30):
    '''
    指定された特許出願番号に対応する実体審査における発送書類の実体ファイル（拒絶理由通知書、特許査定、拒絶査定、補正の却下の決定）のxmlファイルの格納ディレクトリを返す
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_doc_cont_opinion_amendment
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    str
        ディレクトリパス

    Examples
    --------
    >>> app_doc_cont_refusal_reason_decision("2020008423")
    'data/2020008423/app_doc_cont_refusal_reason_decision'
    '''
    return get_unzip_data(get_app_doc_cont_refusal_reason_decision, case_number, reget_date)


def app_doc_cont_refusal_reason(case_number, reget_date=30):
    '''
    指定された特許出願番号に対応する拒絶理由通知書のZIPファイルをダウンロードする。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-app_doc_cont_refusal_reason
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    str
        ディレクトリパス

    Examples
    --------
    >>> app_doc_cont_refusal_reason("2007035937")
    'data/2007035937/app_doc_cont_refusal_reason'
    '''
    return get_unzip_data(get_app_doc_cont_refusal_reason, case_number, reget_date)


def cite_doc_info(case_number, reget_date=30):
    '''
    指定された特許出願番号に紐づく引用文献情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-cite-doc-info
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json 
        引用文献情報のjsonデータ

    Examples
    --------
    >>> info = cite_doc_info("2020008423")
    >>> info["result"]["data"]["patentDoc"][0]["documentNumber"]
    'JPA 421211144'
    '''
    return get_json(get_cite_doc_info, case_number, reget_date)


def registration_info(case_number, reget_date=30):
    '''
    指定された特許出願番号に紐づく登録情報を取得する。
    https://ip-data.jpo.go.jp/api_guide/api_reference.html#/%E7%89%B9%E8%A8%B1%E6%83%85%E5%A0%B1%E5%8F%96%E5%BE%97API/get-registration-info
    既存のファイルがある場合には、既存のファイルを読み込む

    Parameters
    ----------
    case_number: str
        出願番号
    reget_date: int
        データ再取得までの日数
    
    Returns
    -------
    json 
        登録情報のjsonデータ

    Examples
    --------
    >>> info = registration_info("2020008423")
    >>> info["result"]["data"]["expireDate"]
    '20400122'
    '''
    return get_json(get_registration_info, case_number, reget_date)


if __name__ == "__main__":
     import doctest
     doctest.testmod()
