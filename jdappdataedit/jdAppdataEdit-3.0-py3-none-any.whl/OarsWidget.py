from .Functions import select_combo_box_data
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QWidget
from lxml import etree
from PyQt6 import uic
import sys
import os


class OarsWidget(QWidget):
    def __init__(self, env, main_window):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "OarsWidget.ui"), self)

        self._box_list = []
        for key, value in vars(self).items():
            if key.startswith("oars_box_"):
                self._box_list.append(key[9:])
                value.currentIndexChanged.connect(main_window.set_file_edited)
            elif key.startswith("label_title_"):
                value.setStyleSheet("font-weight: bold;")
            elif key.startswith("label_example_"):
                value.setStyleSheet("color: grey")

        self._fill_boxes()

        self.tab_widget.setCurrentIndex(0)

    def _fill_boxes(self):
        # Violence

        self.oars_box_violence_cartoon.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_violence_cartoon.addItem(QCoreApplication.translate("OarsWidget", "Mild: Cartoon characters in unsafe situations"), "mild")
        self.oars_box_violence_cartoon.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Cartoon characters in aggressive conflict"), "moderate")
        self.oars_box_violence_cartoon.addItem(QCoreApplication.translate("OarsWidget", "Intense: Cartoon characters showing graphic violence"), "intense")

        self.oars_box_violence_fantasy.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_violence_fantasy.addItem(QCoreApplication.translate("OarsWidget", "Mild: Fantasy characters in unsafe situations"), "mild")
        self.oars_box_violence_fantasy.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Fantasy characters in aggressive conflict"), "moderate")
        self.oars_box_violence_fantasy.addItem(QCoreApplication.translate("OarsWidget", "Intense: Fantasy characters with graphic violence"), "intense")

        self.oars_box_violence_realistic.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_violence_realistic.addItem(QCoreApplication.translate("OarsWidget", "Mild: Realistic characters in unsafe situations"), "mild")
        self.oars_box_violence_realistic.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Realistic characters in depictions of aggressive conflict"), "moderate")
        self.oars_box_violence_realistic.addItem(QCoreApplication.translate("OarsWidget", "Intense: Realistic characters with graphic violence"), "intense")

        self.oars_box_violence_bloodshed.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_violence_bloodshed.addItem(QCoreApplication.translate("OarsWidget", "Mild: Unrealistic bloodshed"), "mild")
        self.oars_box_violence_bloodshed.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Realistic bloodshed"), "moderate")
        self.oars_box_violence_bloodshed.addItem(QCoreApplication.translate("OarsWidget", "Intense: Depictions of bloodshed and the mutilation of body parts"), "intense")

        self.oars_box_violence_sexual.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_violence_sexual.addItem(QCoreApplication.translate("OarsWidget", "Intense: Rape or other violent sexual behavior"), "intense")

        # Violence II

        self.oars_box_violence_desecration.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_violence_desecration.addItem(QCoreApplication.translate("OarsWidget", "Mild: Visible dead human remains"), "mild")
        self.oars_box_violence_desecration.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Dead human remains that are exposed to the elements"), "moderate")
        self.oars_box_violence_desecration.addItem(QCoreApplication.translate("OarsWidget", "Intense: Graphic depictions of desecration of human bodies, for example being eaten by wild animals"), "intense")

        self.oars_box_violence_slavery.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_violence_slavery.addItem(QCoreApplication.translate("OarsWidget", "Mild: Depictions or references to historical slavery"), "mild")
        self.oars_box_violence_slavery.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Depictions of modern-day slavery"), "moderate")
        self.oars_box_violence_slavery.addItem(QCoreApplication.translate("OarsWidget", "Intense: Graphic depictions of modern-day slavery"), "intense")

        # Drugs

        self.oars_box_drugs_alcohol.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_drugs_alcohol.addItem(QCoreApplication.translate("OarsWidget", "Mild: References to alcoholic beverages"), "mild")
        self.oars_box_drugs_alcohol.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Use of alcoholic beverages"), "moderate")

        self.oars_box_drugs_narcotics.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_drugs_narcotics.addItem(QCoreApplication.translate("OarsWidget", "Mild: References to illicit drugs"), "mild")
        self.oars_box_drugs_narcotics.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Use of illicit drugs"), "moderate")

        self.oars_box_drugs_tobacco.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_drugs_tobacco.addItem(QCoreApplication.translate("OarsWidget", "Mild: References to tobacco products"), "mild")
        self.oars_box_drugs_tobacco.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Use of tobacco products"), "moderate")

        # Sex and Nudity

        self.oars_box_sex_nudity.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_sex_nudity.addItem(QCoreApplication.translate("OarsWidget", "Mild: Brief artistic nudity"), "mild")
        self.oars_box_sex_nudity.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Prolonged nudity"), "moderate")
        self.oars_box_sex_nudity.addItem(QCoreApplication.translate("OarsWidget", "Intense: Explicit nudity showing nipples or sexual organs"), "intense")

        self.oars_box_sex_themes.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_sex_themes.addItem(QCoreApplication.translate("OarsWidget", "Mild: Provocative references or depictions"), "mild")
        self.oars_box_sex_themes.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Sexual references or depictions"), "moderate")
        self.oars_box_sex_themes.addItem(QCoreApplication.translate("OarsWidget", "Intense: Graphic sexual behavior"), "intense")

        # Language

        self.oars_box_language_profanity.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_language_profanity.addItem(QCoreApplication.translate("OarsWidget", "Mild: Mild or infrequent use of profanity e.g. 'Dufus'"), "mild")
        self.oars_box_language_profanity.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Moderate use of profanity e.g. 'Shit'"), "moderate")
        self.oars_box_language_profanity.addItem(QCoreApplication.translate("OarsWidget", "Intense: Strong or frequent use of profanity e.g. 'Fuck'"), "intense")

        self.oars_box_language_humor.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_language_humor.addItem(QCoreApplication.translate("OarsWidget", "Mild: Mild or infrequent use of profanity e.g. 'Dufus'"), "mild")
        self.oars_box_language_humor.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Moderate use of profanity e.g. 'Shit'"), "moderate")
        self.oars_box_language_humor.addItem(QCoreApplication.translate("OarsWidget", "Intense: Strong or frequent use of profanity e.g. 'Fuck'"), "intense")

        self.oars_box_language_discrimination.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_language_discrimination.addItem(QCoreApplication.translate("OarsWidget", "Mild: Negativity towards a specific group of people, e.g. ethnic jokes"), "mild")
        self.oars_box_language_discrimination.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Discrimation designed to cause emotional harm, e.g. racism, or homophobia"), "moderate")
        self.oars_box_language_discrimination.addItem(QCoreApplication.translate("OarsWidget", "Intense: Explicit discrimination based on gender, sexuality, race or religion, e.g. genocide"), "intense")

        # Money

        self.oars_box_money_advertising.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_money_advertising.addItem(QCoreApplication.translate("OarsWidget", "Mild: Product placement, e.g. billboards in a football game"), "mild")
        self.oars_box_money_advertising.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Explicit references to specific brands or trademarked products"), "moderate")
        self.oars_box_money_advertising.addItem(QCoreApplication.translate("OarsWidget", "Intense: Users are encouraged to purchase specific real-world items"), "intense")

        self.oars_box_money_gambling.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_money_gambling.addItem(QCoreApplication.translate("OarsWidget", "Mild: Gambling on random events using tokens or credits"), "mild")
        self.oars_box_money_gambling.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Gambling using fictional money"), "moderate")
        self.oars_box_money_gambling.addItem(QCoreApplication.translate("OarsWidget", "Intense: Gambling using real money"), "intense")

        self.oars_box_money_purchasing.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_money_purchasing.addItem(QCoreApplication.translate("OarsWidget", "Mild: Users are encouraged to donate real money, e.g. using Patreon"), "mild")
        self.oars_box_money_purchasing.addItem(QCoreApplication.translate("OarsWidget", "Intense: Ability to spend real money in-app, e.g. buying new content or new levels"), "intense")

        # Social

        self.oars_box_social_chat.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_social_chat.addItem(QCoreApplication.translate("OarsWidget", "Mild: User-to-user game interactions without chat functionality e.g. playing chess"), "mild")
        self.oars_box_social_chat.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Moderated messaging between users"), "moderate")
        self.oars_box_social_chat.addItem(QCoreApplication.translate("OarsWidget", "Intense: Uncontrolled chat functionality between users"), "intense")

        self.oars_box_social_audio.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_social_audio.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Moderated audio or video chat between users"), "moderate")
        self.oars_box_social_audio.addItem(QCoreApplication.translate("OarsWidget", "Intense: Uncontrolled audio or video chat between users"), "intense")

        self.oars_box_social_contacts.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_social_contacts.addItem(QCoreApplication.translate("OarsWidget", "Intense: Sharing Twitter, Facebook or email addresses"), "intense")

        self.oars_box_social_info.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_social_info.addItem(QCoreApplication.translate("OarsWidget", "Mild: Using any online API, e.g. a user-counter"), "mild")
        self.oars_box_social_info.addItem(QCoreApplication.translate("OarsWidget", "Moderate: Sharing diagnostic data not identifiable to the user, e.g. profiling data"), "moderate")
        self.oars_box_social_info.addItem(QCoreApplication.translate("OarsWidget", "Intense: Sharing information identifiable to the user, e.g. crash dumps"), "intense")

        self.oars_box_social_location.addItem(QCoreApplication.translate("OarsWidget", "None"), "none")
        self.oars_box_social_location.addItem(QCoreApplication.translate("OarsWidget", "Intense: Sharing physical location to other users e.g. a postal address"), "intense")

    def reset_data(self):
        for i in self._box_list:
            getattr(self, "oars_box_" + i).setCurrentIndex(0)

    def open_file(self, content_rating_tag: etree._Element):
        for i in content_rating_tag.findall("content_attribute"):
            try:
                select_combo_box_data(getattr(self, "oars_box_" + i.get("id").replace("-", "_")), i.text)
            except AttributeError:
                print("Unknown ORAS Attribute ID " +  i.get("id").replace("-", "_"), file=sys.stderr)

    def save_file(self, content_rating_tag: etree._Element):
        for i in self._box_list:
            data = getattr(self, "oars_box_" + i).currentData()
            if data == "none":
                continue
            content_attribute_tag = etree.SubElement(content_rating_tag, "content_attribute")
            content_attribute_tag.set("id", i.replace("_", "-"))
            content_attribute_tag.text = data
