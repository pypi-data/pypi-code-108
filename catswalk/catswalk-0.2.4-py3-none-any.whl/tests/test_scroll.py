from catswalk.scraping.webdriver import CWWebDriver
import time
from catswalk.scraping.types.type_webdriver import *


binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
executable_path = "/Users/rv/ws/tools/chromedriver"
proxy = None
headless = True
    
request = CWWebDriver(binary_location=binary_location, executable_path=executable_path, execution_env=EXECUTION_ENV.LOCAL,  device = DEVICE.MOBILE_GALAXY_S5)
#url="https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python"
#url="https://video.unext.jp/book/title/BSD0000027810"
url="https://comic.k-manga.jp/title/95912/pv"
request.get(url=url)
#class_name = "AkamaiImage__AdjustedImg-d0gvt4-0 gRoDaG"
#class_name = "AkamaiImage__AdjustedImg-d0gvt4-0 gRoDaG"
class_name = "gaevent-detail-notlogin-bookchapter btn"
request.move_to_element_by_class_name(class_name)
request.scroll_by_offset(100)

time.sleep(1000)
request.close()