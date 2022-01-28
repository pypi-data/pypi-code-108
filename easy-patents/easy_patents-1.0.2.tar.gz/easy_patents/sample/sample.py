from easy_patents.get_info import *

# 実行前に同じディレクトリにあるconfig.iniを編集する必要があります
# username に特許庁からもらったusernameを記入してください。
# passwordに特許庁からもらったpasswordを記入してください。
# 他はいじらなくて大丈夫です（AuthInfoにより自動で更新されます)


# 第1引数にそれに必要なキー(出願番号など)を指定する
# 最新の情報を取得したい場合には、第2引数をTureにする。
case_info = app_progress("特願２０２０－００８４２３")

print(case_info["result"]["data"]["inventionTitle"])

# 第1引数にそれに必要なキー(出願番号など)を指定する
# 最新の情報を取得したい場合には、第2引数をTureにする。
xml_dir = app_doc_cont_opinion_amendment("特願２０２０－００８４２３")

# 戻り値は、解凍後のxmlが格納されたディレクトリのパス
print(xml_dir)


# もし、タイムアウトかアクセス集中でエラーになった場合に
# 10秒スリープ後にリトライしたい場合
# その他のエラーの詳細はjpoapi_errorsを参照のこと

from easy_patents.errors import TemporaryError
import time

try: 
    case_info = app_progress("特願２０２０－００８４２３")
except TemporaryError:
    time.sleep(10)
    case_info = app_progress("特願２０２０－００８４２３")



# try文を書きたくない人向け関数も存在する。
from easy_patents.errors import try_get, TooManyAccessError

# エラー時に実行する関数を定義する。
def error_print(func, key, error):
    print("%s %s %s" % (func.__name__, key, error))

# アクセス上限に達している場合、以下の関数を実行するとerror_printが実行される。
# errors=(JPOAPITooManyAccessError, JPOAPITemporaryError)と指定することで、# 指定したエラーに対して、func_when_errorで指定された関数が実行される
info = try_get(
        func=registration_reference,
        key="6691280",
        errors=(TooManyAccessError),
        func_when_error=error_print
)

