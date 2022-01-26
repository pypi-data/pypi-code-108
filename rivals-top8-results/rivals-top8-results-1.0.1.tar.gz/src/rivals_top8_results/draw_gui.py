import json
import os
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QComboBox, QGraphicsScene, QMainWindow

from PIL import Image

from draw_results import draw_results
from draw_qt import Ui_MainWindow

from TournamentFetcher import TournamentFetcher

from draw_results import draw_top8

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(1109, 419)

        self.top8_bindings = {
            "meta": {
                "title": self.ui.tournament_title,
                "date": self.ui.tournament_date,
                "participants": self.ui.tournament_participants,
                "background": self.ui.tournament_bg,
                "background_variant": self.ui.tournament_bg_variant,
            },
            "settings": {
                "rgb": self.ui.tournament_rgb,
                "bg_opacity": self.ui.tournament_bg_opacity,
            },
            "1": {
                "nickname": self.ui.nickname_P1,
                "character": self.ui.character_P1,
                "skin": self.ui.skin_P1,
                "secondary": self.ui.secondary_P1,
                "tertiary": self.ui.tertiary_P1,
            },
            "2": {
                "nickname": self.ui.nickname_P2,
                "character": self.ui.character_P2,
                "skin": self.ui.skin_P2,
                "secondary": self.ui.secondary_P2,
                "tertiary": self.ui.tertiary_P2,
            },
            "3": {
                "nickname": self.ui.nickname_P3,
                "character": self.ui.character_P3,
                "skin": self.ui.skin_P3,
                "secondary": self.ui.secondary_P3,
                "tertiary": self.ui.tertiary_P3,
            },
            "4": {
                "nickname": self.ui.nickname_P4,
                "character": self.ui.character_P4,
                "skin": self.ui.skin_P4,
                "secondary": self.ui.secondary_P4,
                "tertiary": self.ui.tertiary_P4,
            },
            "5": {
                "nickname": self.ui.nickname_P5,
                "character": self.ui.character_P5,
                "skin": self.ui.skin_P5,
                "secondary": self.ui.secondary_P5,
                "tertiary": self.ui.tertiary_P5,
            },
            "6": {
                "nickname": self.ui.nickname_P6,
                "character": self.ui.character_P6,
                "skin": self.ui.skin_P6,
                "secondary": self.ui.secondary_P6,
                "tertiary": self.ui.tertiary_P6,
            },
            "7": {
                "nickname": self.ui.nickname_P7,
                "character": self.ui.character_P7,
                "skin": self.ui.skin_P7,
                "secondary": self.ui.secondary_P7,
                "tertiary": self.ui.tertiary_P7,
            },
            "8": {
                "nickname": self.ui.nickname_P8,
                "character": self.ui.character_P8,
                "skin": self.ui.skin_P8,
                "secondary": self.ui.secondary_P8,
                "tertiary": self.ui.tertiary_P8,
            },
        }

        # fills ComboBoxes with characters and skin data
        # each ComboBox is then modified at runtime
        chars_dir = fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\resources\\characters\\Main\\"
        chars = [f for f in os.listdir(chars_dir)]
        for c in chars:
            # builds a skin list for each character
            char_skins = [
                n.replace(".png", "") for n in os.listdir(chars_dir + "\\" + c)
            ]

            # fills each skin_P1 with characters and skins
            for i in range(1, 9):
                self.top8_bindings["" + str(i)]["character"].addItem(c, char_skins)

        # fills ComboBox with stagelist
        stages_dir = fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\resources\\Backgrounds\\"
        stages = [f for f in os.listdir(stages_dir)]
        for s in stages:
            backgrounds = [
                n.replace(".png", "") for n in os.listdir(stages_dir + "\\" + s)
            ]
            self.top8_bindings["meta"]["background"].addItem(s, backgrounds)

        # TODO: make this dynamic just like the skin ComboBoxes
        # adds stage variants selections
        self.top8_bindings["meta"]["background_variant"].addItem("1")
        self.top8_bindings["meta"]["background_variant"].addItem("2")

        # needed to populate skins ComboBoxes
        self.ui.character_P1.currentIndexChanged.connect(self.updateP1SkinCombo)
        self.ui.character_P2.currentIndexChanged.connect(self.updateP2SkinCombo)
        self.ui.character_P3.currentIndexChanged.connect(self.updateP3SkinCombo)
        self.ui.character_P4.currentIndexChanged.connect(self.updateP4SkinCombo)
        self.ui.character_P5.currentIndexChanged.connect(self.updateP5SkinCombo)
        self.ui.character_P6.currentIndexChanged.connect(self.updateP6SkinCombo)
        self.ui.character_P7.currentIndexChanged.connect(self.updateP7SkinCombo)
        self.ui.character_P8.currentIndexChanged.connect(self.updateP8SkinCombo)

        # loads results from json and from png
        self.load_results()
        self.load_img_results()

        # calls method upon clicking
        self.ui.fetch_button.clicked.connect(self.fetch_results)
        self.ui.reset_button.clicked.connect(self.clear_results)
        self.ui.generate_button.clicked.connect(self.save_and_gen_results)

        # spawns window
        self.show()

    def updateP1SkinCombo(self, index):
        self.ui.skin_P1.clear()
        skins = self.ui.character_P1.itemData(index)

        self.ui.skin_P1.addItems(["Skin"])
        self.ui.skin_P1.setCurrentIndex(0)

        if skins:
            self.ui.skin_P1.addItems(skins)

    def updateP2SkinCombo(self, index):
        self.ui.skin_P2.clear()
        skins = self.ui.character_P2.itemData(index)

        self.ui.skin_P2.addItems(["Skin"])
        self.ui.skin_P2.setCurrentIndex(0)

        if skins:
            self.ui.skin_P2.addItems(skins)

    def updateP3SkinCombo(self, index):
        self.ui.skin_P3.clear()
        skins = self.ui.character_P3.itemData(index)

        self.ui.skin_P3.addItems(["Skin"])
        self.ui.skin_P3.setCurrentIndex(0)

        if skins:
            self.ui.skin_P3.addItems(skins)

    def updateP4SkinCombo(self, index):
        self.ui.skin_P4.clear()
        skins = self.ui.character_P4.itemData(index)

        self.ui.skin_P4.addItems(["Skin"])
        self.ui.skin_P4.setCurrentIndex(0)

        if skins:
            self.ui.skin_P4.addItems(skins)

    def updateP5SkinCombo(self, index):
        self.ui.skin_P5.clear()
        skins = self.ui.character_P5.itemData(index)

        self.ui.skin_P5.addItems(["Skin"])
        self.ui.skin_P5.setCurrentIndex(0)

        if skins:
            self.ui.skin_P5.addItems(skins)

    def updateP6SkinCombo(self, index):
        self.ui.skin_P6.clear()
        skins = self.ui.character_P6.itemData(index)

        self.ui.skin_P6.addItems(["Skin"])
        self.ui.skin_P6.setCurrentIndex(0)

        if skins:
            self.ui.skin_P6.addItems(skins)

    def updateP7SkinCombo(self, index):
        self.ui.skin_P7.clear()
        skins = self.ui.character_P7.itemData(index)

        self.ui.skin_P7.addItems(["Skin"])
        self.ui.skin_P7.setCurrentIndex(0)

        if skins:
            self.ui.skin_P7.addItems(skins)

    def updateP8SkinCombo(self, index):
        self.ui.skin_P8.clear()
        skins = self.ui.character_P8.itemData(index)

        self.ui.skin_P8.addItems(["Skin"])
        self.ui.skin_P8.setCurrentIndex(0)

        if skins:
            self.ui.skin_P8.addItems(skins)

    def load_results(self, json_file=fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\resources\\bracket.json"):
        with open(fr"{(json_file)}") as top8_file:
            top8 = json.load(top8_file)

        # loads up the json's content into the GUI
        top8_rounds = list(self.top8_bindings.keys())
        for r in top8_rounds:
            top8_fields = list(self.top8_bindings[r].keys())

            for f in top8_fields:
                if f == "rgb":
                    self.top8_bindings[r][f].setText(str(top8[r][f]))

                if type(self.top8_bindings[r][f]) == QComboBox:
                    self.top8_bindings[r][f].setCurrentText(str(top8[r][f]))
                else:
                    self.top8_bindings[r][f].setText(str(top8[r][f]))

    def clear_results(self):
        with open(fr"{os.getcwd()}/resources/empty_bracket.json") as top8_file:
            top8 = json.load(top8_file)

        # loads up the json's content into the GUI
        top8_rounds = list(self.top8_bindings.keys())
        for r in top8_rounds:
            top8_fields = list(self.top8_bindings[r].keys())

            for f in top8_fields:
                if f == "rgb":
                    self.top8_bindings[r][f].setText(str(top8[r][f]))

                if type(self.top8_bindings[r][f]) == QComboBox:
                    self.top8_bindings[r][f].setCurrentText(str(top8[r][f]))
                else:
                    self.top8_bindings[r][f].setText(str(top8[r][f]))

    def load_img_results(self):
        scene = QGraphicsScene()
        self.ui.preview.setScene(scene)
        pixmap = QPixmap("results.png").scaledToWidth(458)
        scene.addPixmap(pixmap)

    def fetch_results(self):
        if self.ui.tournament_url.text():
            # TODO: fix this in the TournamentFetcher library
            bracket_url_to_json(
                self.ui.tournament_url.text()[:-1]
                if self.ui.tournament_url.text()[-1] == "/"
                else self.ui.tournament_url.text()
            )
            self.load_results()

    def save_and_gen_results(self):
        # saves into json file
        with open(fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\resources\\bracket.json") as top8_file:
            top8 = json.load(top8_file)

        # saves up data in dictionary
        top8_rounds = list(self.top8_bindings.keys())
        for r in top8_rounds:
            top8_fields = list(self.top8_bindings[r].keys())

            for f in top8_fields:
                # rgb property needs to be handled differently since it's in a JSON array
                if f == "rgb":
                    top8[r][f] = self.top8_bindings[r][f].text()
                    top8[r][f] = top8[r][f].replace("[", "").replace("]", "")
                    top8[r][f] = [int(i) for i in top8[r][f].split(", ")]

                # bg opacity needs to be an integer
                elif f == "bg_opacity":
                    top8[r][f] = int(self.top8_bindings[r][f].text())

                elif type(self.top8_bindings[r][f]) == QComboBox:
                    combobox_names = [
                        "Character",
                        "Secondary",
                        "Tertiary",
                        "Background",
                        "Variant",
                    ]
                    if self.top8_bindings[r][f].currentText() in combobox_names:
                        top8[r][f] = ""
                    else:
                        top8[r][f] = self.top8_bindings[r][f].currentText()
                else:
                    top8[r][f] = self.top8_bindings[r][f].text()

        # dumps onto json file
        with open(fr"{os.path.abspath(os.getcwd())}/rivals_top8_results/resources/bracket.json", "w") as top8_file:
            json.dump(top8, top8_file, indent=4)

        # generates png output
        with open(fr"{os.path.abspath(os.getcwd())}/rivals_top8_results/resources/bracket.json") as bracket_file:
            bracket = json.load(bracket_file)

        generate_from_json(bracket)

        # refreshes preview
        self.load_img_results()


def generate_from_json(bracket):
    logo = Image.open(fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\Resources\Layout\logo.png")
    logo = logo.resize(
        (int(logo.size[0] * 0.35), int(logo.size[1] * 0.35)), resample=Image.BOX
    )

    nicknames = []
    characters = []
    skins = []
    secondaries = []
    tertiaries = []

    for i in range(1, 9):
        nicknames.append(bracket[str(i)]["nickname"])
        characters.append(bracket[str(i)]["character"])
        skins.append(bracket[str(i)]["skin"])
        secondaries.append(bracket[str(i)]["secondary"])
        tertiaries.append(bracket[str(i)]["tertiary"])

    top8 = draw_top8(
        nicknames,
        characters,
        skins,
        secondaries,
        tertiaries,
        layout_rgb=tuple(bracket["settings"]["rgb"]),
        bg_opacity=bracket["settings"]["bg_opacity"],
        resize_factor=1.3,
        save=False,
    )

    draw_results(
        top8,
        stage=bracket["meta"]["background"],
        title=bracket["meta"]["title"],
        attendees_num=bracket["meta"]["participants"],
        date=bracket["meta"]["date"],
        layout_rgb=tuple(bracket["settings"]["rgb"]),
        stage_variant=bracket["meta"]["background_variant"],
        logo=logo,
        logo_offset=(-100, -12),
    )


def bracket_url_to_json(url):
    with open("resources/challonge.json") as challonge_file:
        challonge = json.load(challonge_file)

    t = TournamentFetcher(
        challonge_auth={
            "nickname": challonge["nickname"],
            "api_key": challonge["api_key"],
        }
    )

    # subdomain is temporarily hardcoded to true
    tournament = t.fetch_tournament(url, subdomain=True)
    participants = (
        tournament.participants[["username", "placement"]]
        .sort_values(by="placement")
        .head(8)["username"]
        .to_list()
    )

    # opens bracket json file
    with open(fr"resources\bracket.json") as bracket_file:
        bracket = json.load(bracket_file)

    # sets meta data
    bracket["meta"]["title"] = tournament.tournament_name
    bracket["meta"]["date"] = tournament.meta.start_at[0][0:10]
    bracket["meta"]["participants"] = tournament.participants_count

    # TODO: properly implement mains / renames
    with open(r"resources/mains.json") as mains_file:
        mains = json.load(mains_file)

    with open(r"resources/renames.json") as renames_file:
        renames = json.load(renames_file)

    for i in range(1, 9):
        # bracket[str(i)]["nickname"] = renames[participants[i - 1]]
        bracket[str(i)]["nickname"] = tournament.participants.nickname[i]
        # bracket[str(i)]["character"] = mains[bracket[str(i)]["nickname"]]
        # bracket[str(i)]["character"] = "Zetterburn"
        bracket[str(i)]["skin"] = "Default"

    with open(fr"{os.getcwd()}/resources/bracket.json", "w") as top8_file:
        json.dump(bracket, top8_file, indent=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
