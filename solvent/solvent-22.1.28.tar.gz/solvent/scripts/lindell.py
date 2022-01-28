import time

import log
import pomace

from . import Script


class MyPillow(Script):

    URL = "https://www.mypillow.com/"

    def run(self, page) -> pomace.Page:
        person = pomace.fake.person

        log.info("Clearing cookies")
        pomace.shared.browser.cookies.delete()
        page = pomace.visit(self.URL)

        log.debug("Waiting for modal...")
        for _ in range(10):
            time.sleep(0.5)
            modal = pomace.shared.browser.find_by_id("ltkpopup-content")
            if modal and modal.visible:
                break
        else:
            log.warn("No modal found")

        log.info(f"Submitting phone number: {person.phone}")
        page.fill_phone(person.phone)
        return page.click_submit()

    def check(self, page) -> bool:
        return "Thank you!" in page


class FrankSpeech(Script):

    URL = "https://frankspeech.com/"

    def run(self, page) -> pomace.Page:
        log.info("Clearing cookies")
        pomace.shared.browser.cookies.delete()
        page = pomace.visit(self.URL)

        page.fill_phone_number(pomace.fake.phone_number.replace("-", ""))
        return page.click_submit()

    def check(self, page) -> bool:
        return "home" in page.url
