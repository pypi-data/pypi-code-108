import log
import pomace

from . import Script


class ProLifeWhistle(Script):

    URL = "https://prolifewhistleblower.com/anonymous-form/"
    SKIP = True

    def run(self, page) -> pomace.Page:
        while person := pomace.fake.person:
            if person.state == "Texas":
                log.info(f"Beginning iteration as person from {person.city}")
                break

        log.info("Navigating to the form")
        page = page.click_send_tip(wait=0.5)

        page.fill_violation("Right to life")
        page.fill_evidence("Witness")
        page.fill_clinic(f"{person.county} Clinic")
        page.fill_city(person.city)
        page.fill_state(person.state)
        page.fill_zip(person.zip_code)
        page.fill_county(person.county)
        page.click_no(wait=0.5)

        log.info("Submitting the form")
        return page.click_submit(wait=2.0)

    def check(self, page) -> bool:
        return "verification failed" not in page
