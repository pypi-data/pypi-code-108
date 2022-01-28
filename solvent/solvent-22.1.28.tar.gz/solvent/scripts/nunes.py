import pomace
from selenium.common.exceptions import UnexpectedAlertPresentException

from . import Script


class Nunes(Script):

    URL = "https://iqconnect.lmhostediq.com/iqextranet/EsurveyForm.aspx?__cid=CA22DN&__sid=100088&__crop=15548.37359788.2764358.1492115"

    def run(self, page) -> pomace.Page:
        for index in range(3):
            pomace.shared.browser.find_by_css('[value="Yes"]')[index].click()

        try:
            page = page.click_submit()
        except UnexpectedAlertPresentException:
            if alert := pomace.shared.browser.get_alert():
                alert.accept()
            page = pomace.auto()

        page.fill_email(pomace.fake.email)
        return page.click_sign_up_now()

    def check(self, page) -> bool:
        return "subscribe" in page.url
