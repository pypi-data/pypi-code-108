from __future__ import absolute_import, division, print_function, unicode_literals

from ruamel.yaml.comments import CommentedMap

from publisher.processing.data_sources.utils import copy_assets
from publisher.processing.data_sources.info_card import get_more_info_data

INFORMATION_CARD_LIST = []


class OverviewWidget:
    def __init__(self, overview_data):
        self.cards = []

        for page in overview_data:
            formatted_page = InformationCardWidget(page)
            self.cards.append(formatted_page.dump()[0])

    def dump(self):
        return self.cards


class InformationCardWidget:
    def __init__(self, info_data):
        self.infoId = info_data["code"]
        self.cta_text = ""
        self.title = info_data["title"]
        self.subTitle = info_data["subTitle"]
        self.assets = []
        self.sections = []

        if "cta_text" in info_data:
            self.cta_text = info_data.get("cta_text", "")

        if "sourceDir" in info_data:
            self.sourceDir = info_data["sourceDir"]

        for section in info_data["sections"]:
            formatted_section = InformationCardSection(section)
            self.sections.append(formatted_section.dump())

    def dump(self):
        return [
            {
                "information_card": CommentedMap([
                    ("code", self.infoId),
                    ("cta_text", self.cta_text),
                    ("title", self.title),
                    ("subTitle", self.subTitle),
                    ("assets", self.assets),
                    ("sections", self.sections)
                ])
            }
        ]


class InformationCardSection:
    def __init__(self, data):
        self.title = data["title"]
        self.body = data["body"]

    def dump(self):
        return CommentedMap([
            ("title", self.title),
            ("body", self.body)
        ])


class Asset:
    def __init__(self, asset_type, step_id="", name=""):
        self.type = asset_type
        self.stepId = step_id
        self.code = ""
        self.name = name

    def dump(self):
        return {
            self.type: CommentedMap([
                ("code", "%s_%s" % (self.stepId, self.type)),
                ("name", self.name)
            ])}


class EulaAsset:
    def __init__(self, eula_file):
        self.eulaFile = eula_file

        if eula_file:
            self.required = "yes"
        else:
            self.required = "no"

    def dump(self):
        return CommentedMap([
            ("eula_asset", self.eulaFile),
            ("requires_complete_profile", self.required)
        ])


class AutoCompleteWidget:
    def __init__(self, step_id):
        self.stepId = step_id

    def dump(self):
        return {
            "auto_complete": CommentedMap([
                ("code", self.stepId + "_autocomplete_1"),
                ("duration", 1300),
            ])
        }


class DraggerWidget:
    def __init__(self, step_id, xy_points):
        self.stepId = step_id
        self.xyPoints = xy_points

    def dump(self):
        return {
            "dragger_ab": CommentedMap([
                ("code", self.stepId + "_dragger_ab_1"),
                ("start_x", float(self.xyPoints["start"][0]) / 320),
                ("start_y", float(self.xyPoints["start"][1]) / 436),
                ("target_x", float(self.xyPoints["target"][0]) / 320),
                ("target_y", float(self.xyPoints["target"][1]) / 436),
            ])
        }


class DirDraggerWidget:
    def __init__(self, step_id, dragger_data):
        self.stepId = step_id
        self.draggerData = dragger_data

    def dump(self):
        return {
            "dragger_directional": CommentedMap([
                ("code", self.stepId + "_dragger_directional_1"),
                ("start_x", float(self.draggerData["start"][0]) / 320),
                ("start_y", float(self.draggerData["start"][1]) / 436),
                ("target_angle", self.draggerData["angle"]),
                ("tolerance", self.draggerData["tolerance"]),
                ("distance", self.draggerData["distance"]),
            ])
        }


class TapWidget:
    def __init__(self, step_id, tap_data):
        self.stepId = step_id
        self.tapData = tap_data

    def dump(self):
        return {
            "tap": CommentedMap([
                ("code", self.stepId + "_tap_1"),
                ("position_x", float(self.tapData["target"][0]) / 320),
                ("position_y", float(self.tapData["target"][1]) / 436),
                ("duration", 0),
            ])
        }


class HoldWidget:
    def __init__(self, step_id, hold_data):
        self.stepId = step_id
        self.holdData = hold_data

    def dump(self):
        return {
            "tap": CommentedMap([
                ("code", self.stepId + "_tap_1"),
                ("position_x", float(self.holdData["target"][0]) / 320),
                ("position_y", float(self.holdData["target"][1]) / 436),
                ("duration", self.holdData["duration"]),
                ("min_value", self.holdData["start"]),
                ("max_value", self.holdData["finish"]),
                ("units", self.holdData["units"]),
            ])
        }


class PipWidget:
    def __init__(self, step_id, pip_data, pip_image, pip_video):
        self.stepId = step_id
        self.pipData = pip_data
        self.assets = []

        image_asset = Asset("image", self.stepId, pip_image)
        self.assets.append(image_asset.dump())
        if pip_video:
            video_asset = Asset("video", self.stepId, pip_video)
            self.assets.append(video_asset.dump())

    def dump(self):
        return {
            "pip": CommentedMap([
                ("code", self.stepId + "_pip_1"),
                ("position", self.pipData["position"]),
                ("expandable", self.pipData["expandable"]),
                ("shrinkable", self.pipData["shrinkable"]),
                ("assets", self.assets),
            ])
        }


class LabelWidget:
    def __init__(self, step_id, label_num, label_data, code):
        self.stepId = step_id
        self.labelNum = label_num
        self.labelData = label_data
        self.infoCard = None
        self.parentCode = code

        if not self.labelData["moreInfoId"] == "":
            info_data, source_dir = get_more_info_data(self.labelData["moreInfoId"], self.parentCode)

            if isinstance(info_data, dict):
                info_card = InformationCardWidget(info_data)
                self.infoCard = info_card.dump()
            else:
                self.infoCard = info_data

            INFORMATION_CARD_LIST.append(source_dir)

    def dump(self):
        label = {
            "label": CommentedMap([
                ("code", "%s_label_%d" % (self.stepId, int(self.labelNum) + 1)),
                ("text_anchor_x", float(self.labelData["textPosition"][0]) / 320),
                ("text_anchor_y", float(self.labelData["textPosition"][1]) / 436),
                ("content", self.labelData["text"]),
            ])
        }

        if self.labelData["targetPosition"]:
            label["label"].update({"position_x": float(self.labelData["targetPosition"][0]) / 320})
            label["label"].update({"position_y": float(self.labelData["targetPosition"][1]) / 436})
        else:
            new_x = float(self.labelData["textPosition"][0]) / 320
            new_y = float(self.labelData["textPosition"][1]) / 436

            label["label"].update({"position_x": new_x - 0.001})
            label["label"].update({"position_y": new_y + 0.001})

        if self.infoCard:
            label["label"].update({"information_cards": self.infoCard})

        return label


class InfoPointWidget:
    def __init__(self, step_id, info_point_num, info_point_data, code):
        self.stepId = step_id
        self.infoPointNum = info_point_num
        self.infoPointData = info_point_data
        self.infoCard = None
        self.parentCode = code

        if not self.infoPointData["moreInfoId"] == "":
            info_data, source_dir = get_more_info_data(self.infoPointData["moreInfoId"], self.parentCode)

            if isinstance(info_data, dict):
                info_card = InformationCardWidget(info_data)
                self.infoCard = info_card.dump()
            else:
                self.infoCard = info_data

            INFORMATION_CARD_LIST.append(source_dir)

    def dump(self):
        info_point = {
            "label": CommentedMap([
                ("code", "%s_info_point_%d" % (self.stepId, int(self.infoPointNum) + 1)),
                ("position_x", float(self.infoPointData["targetPosition"][0]) / 320),
                ("position_y", float(self.infoPointData["targetPosition"][1]) / 436),
                ("content", self.infoPointData["text"]),
            ])
        }

        if self.infoCard:
            info_point["label"].update({"information_cards": self.infoCard})

        return info_point


class GalleryWidget:
    def __init__(self, step_id, gallery_data):
        self.stepId = step_id
        self.galleryData = gallery_data
        self.galleryItems = []

    def dump(self):
        for i, item in enumerate(self.galleryData):
            self.galleryItems.append(
                CommentedMap([
                    ("title", self.galleryData[item]["title"]),
                    ("text", self.galleryData[item]["text"]),
                ])
            )

            code = "%s_gallery_%s" % (self.stepId, str(i))
            main_file = Asset(self.galleryData[item]["type"], code, self.galleryData[item]["mainFile"])
            thumb_file = Asset("thumbnail", code, self.galleryData[item]["thumbFile"])

            self.galleryItems[i].update(main_file.dump())
            self.galleryItems[i].update(thumb_file.dump())

        gallery = {
            "gallery": CommentedMap([
                ("code", self.stepId + "_gallery_1"),
                ("items", self.galleryItems),
            ])
        }

        return gallery


class FlipbookWidget:
    def __init__(self, step_id, flipbook_data):
        self.stepId = step_id
        self.flipbookData = flipbook_data
        self.assets = []

        code = "%s_flipbook" % self.stepId
        image_asset = Asset("image", code, self.flipbookData["image"])
        self.assets.append(image_asset.dump())
        video_asset = Asset("video", code, self.flipbookData["video"])
        self.assets.append(video_asset.dump())

    def dump(self):
        return {
            "flip_book": CommentedMap([
                ("code", self.stepId + "_flipbook_1"),
                ("scrubber_position", self.flipbookData["scrubberPos"]),
                ("assets", self.assets),
            ])
        }


class McqWidget:
    def __init__(self, step_id, text, correct, incorrect):
        self.stepId = step_id
        self.text = text
        self.correct = correct
        self.incorrect = incorrect

    def dump(self):
        return {
            "mcq": CommentedMap([
                ("code", "TEST_" + self.stepId + "multi_choice_1"),
                ("content", self.text),
                ("answer", self.correct),
                ("choices", self.incorrect),
            ])
        }


class TextWidget:
    def __init__(self, step_id, text):
        self.stepId = step_id
        self.text = text

    def dump(self):
        return {
            "text": CommentedMap([
                ("code", self.stepId + "_text_1"),
                ("content", self.text),
            ])
        }


class Channel:
    def __init__(self):
        self.code = ""
        self.name = ""
        self.type = ""
        self.eula = False
        self.assets = []

    def dump(self, yaml_obj, stream):
        badge_asset = Asset("badge", "channel", "channel-%sbadge" % self.code)
        banner_asset = Asset("banner", "channel", "channel-%sbanner" % self.code)

        self.assets.append(badge_asset.dump())
        self.assets.append(banner_asset.dump())

        if self.eula:
            eula_asset = Asset("eula", "channel", "channel-%seula" % self.code)
            self.assets.append(eula_asset.dump())

        yaml_obj.dump(CommentedMap([("name", self.name), ("code", self.code), ("type", self.type),
                                    ("eula_required", self.eula), ("assets", self.assets)]), stream)


class Procedure:
    def __init__(self):
        self.code = ""
        self.name = ""
        self.author = ""
        self.organisation = ""
        self.doiCode = ""
        self.distributionGroups = []
        self.overview = []
        self.devices = []
        self.channel = ""
        self.phases = []
        self.specialties = []
        self.eulaFile = ""
        self.eula = ""
        self.assets = []
        self.formattedOverview = []
        self.formattedDevices = []
        self.vbs = False
        self.locales = []

    def dump(self, yaml_obj, stream):
        # Check if overview is already formatted
        if isinstance(self.overview, dict):
            self.formattedOverview = OverviewWidget(self.overview).dump()
        else:
            self.formattedOverview = self.overview

        if isinstance(self.devices, dict):
            self.formattedDevices = OverviewWidget(self.devices).dump()
        else:
            self.formattedDevices = self.devices

        icon_asset = Asset("icon")
        icon_asset.stepId = "procedure"
        icon_asset.name = "icon"

        card_asset = Asset("card")
        card_asset.stepId = "procedure"
        card_asset.name = "card"

        self.assets.append(icon_asset.dump())
        self.assets.append(card_asset.dump())

        self.eula = EulaAsset(self.eulaFile).dump()

        yaml_obj.dump(CommentedMap([("name", self.name),
                                    ("overview", self.formattedOverview),
                                    ("devices", self.formattedDevices),
                                    ("channel", self.channel),
                                    ("author", self.author),
                                    ("doi_code", self.doiCode),
                                    ("organisation", self.organisation),
                                    ("authorization", self.eula),
                                    ("distribution_groups", self.distributionGroups),
                                    ("phases", [p.code for p in self.phases]),
                                    ("is_vbs", self.vbs),
                                    ("specialties", self.specialties),
                                    ("assets", self.assets),
                                    ("locales", self.locales)]), stream)


class Phase:
    def __init__(self):
        self.procedureCode = ""
        self.code = ""
        self.released_as = ""
        self.name = ""
        self.publish = "yes"
        self.supported_app = "touchsurgery"
        self.distributionGroups = []
        self.countryRestriction = ""
        self.assets = []
        self.learnObjectives = []
        self.formattedLearnObjectives = []
        self.formattedTestObjectives = []
        self.testObjectives = []
        self.informationCards = []
        self.translationFiles = []
        self.phaseDir = ""
        self.stepNumbers = True
        self.infoStep = True
        self.vbs = False

    def format_learn_data(self):
        for i, objective in enumerate(self.learnObjectives):
            if objective["name"] == "Build Information" and not self.infoStep:
                # Skip formatting the information step
                continue

            # Format steps
            formatted_steps = []
            for step in objective["steps"]:

                # Record metadata required by studio tools

                first_frame = step.get("firstImage", "")
                last_frame = step.get("lastImage") or first_frame

                studio_metadata = {
                    "first_frame": first_frame,
                    "last_frame": last_frame,
                }

                # Format any widgets
                widgets = []

                text = step["text"]
                if self.stepNumbers:
                    # Add step numbers to text for QA purposes
                    text = "Step %s:- %s" % (step["stepId"], step["text"])
                text_widget = TextWidget(step["stepId"], text)
                widgets.append(text_widget.dump())

                if "auto" in step:
                    auto_widget = AutoCompleteWidget(step["stepId"])
                    widgets.append(auto_widget.dump())

                if "dragger" in step:
                    dragger_widget = DraggerWidget(step["stepId"], step["dragger"])
                    widgets.append(dragger_widget.dump())

                if "dirDragger" in step:
                    dir_dragger_widget = DirDraggerWidget(step["stepId"], step["dirDragger"])
                    widgets.append(dir_dragger_widget.dump())

                if "tap" in step:
                    step["tap"]["duration"] = 0
                    tap_widget = TapWidget(step["stepId"], step["tap"])
                    widgets.append(tap_widget.dump())

                if "hold" in step:
                    hold_widget = HoldWidget(step["stepId"], step["hold"])
                    widgets.append(hold_widget.dump())

                if "infoPoints" in step:
                    for infoPoint in step["infoPoints"]:
                        info_point_widget = InfoPointWidget(step["stepId"], infoPoint, step["infoPoints"][infoPoint],
                                                            self.procedureCode)
                        widgets.append(info_point_widget.dump())

                if "pip" in step:
                    if step["pip"]["sequence"]:
                        pip_image = "%s%05d" % (step["pip"]["view"], int(step["firstImage"]))
                        pip_video = "video-%s%05d-%s%05d" % (step["pip"]["view"], int(step["firstImage"]),
                                                             step["pip"]["view"], int(step["lastImage"]))
                    else:
                        pip_image = step["pip"]["view"] + "_image"
                        pip_video = None

                    pip_widget = PipWidget(step["stepId"], step["pip"], pip_image, pip_video)
                    widgets.append(pip_widget.dump())

                if "labels" in step:
                    for label in step["labels"]:
                        label_widget = LabelWidget(step["stepId"], label, step["labels"][label], self.procedureCode)
                        widgets.append(label_widget.dump())

                if "gallery" in step:
                    gallery_widget = GalleryWidget(step["stepId"], step["gallery"])
                    widgets.append(gallery_widget.dump())

                if "flipbook" in step:
                    flipbook_widget = FlipbookWidget(step["stepId"], step["flipbook"])
                    widgets.append(flipbook_widget.dump())

                # Get moreInfoData and add to textWidget
                if "moreInfoId" in step:
                    info_data, source_dir = get_more_info_data(step["moreInfoId"], self.procedureCode)

                    if isinstance(info_data, dict):
                        info_card = InformationCardWidget(info_data)
                        formatted_data = info_card.dump()
                    else:
                        formatted_data = info_data

                    INFORMATION_CARD_LIST.append(source_dir)
                    widgets[0]["text"].update({"information_cards": formatted_data})

                # Format image and video assets
                image_asset = Asset("image", step["stepId"], "image%05d" % int(step["firstImage"]))
                assets = [image_asset.dump()]
                if step["firstImage"] and step["lastImage"] and not step["firstImage"] == step["lastImage"]:
                    name = "video-image%05d-image%05d" % (int(step["firstImage"]), int(step["lastImage"]))
                    video_asset = Asset("video", step["stepId"], name)
                    assets.append(video_asset.dump())

                # Format overall step
                formatted_steps.append(
                    CommentedMap(
                        [
                            ("code", int(step["stepId"])),
                            ("studio_metadata", studio_metadata),
                            ("widgets", widgets),
                            ("assets", assets),
                        ]
                    )
                )

            # Format objectives
            self.formattedLearnObjectives.append(CommentedMap([
                ("name", objective["name"]),
                ("code", i + 1),
                ("steps", formatted_steps)
            ]))

    def format_test_data(self):
        for i, objective in enumerate(self.testObjectives):
            # Format steps
            formatted_steps = []
            if objective["steps"]:
                for step in objective["steps"]:

                    if "testFirstImage" in step and "testLastImage" in step:
                        first_frame = step["testFirstImage"]
                        last_frame = step["testLastImage"] or first_frame
                    else:
                        first_frame = step.get("firstImage", "")
                        last_frame = step.get("lastImage") or first_frame

                    studio_metadata = {
                        "first_frame": first_frame,
                        "last_frame": last_frame,
                    }

                    widgets = []

                    if "correctChoice" in step:
                        mcq_widget = McqWidget(step["stepId"], step["testText"], step["correctChoice"],
                                               step["incorrectChoices"])
                        widgets.append(mcq_widget.dump())
                    elif "testDragger" in step:
                        if step["testText"]:
                            text_widget = TextWidget("TEST_" + step["stepId"], step["testText"])
                            widgets.append(text_widget.dump())
                        dragger_widget = DraggerWidget("TEST_" + step["stepId"], step["testDragger"])
                        widgets.append(dragger_widget.dump())
                    elif "auto" in step:
                        auto_widget = AutoCompleteWidget("TEST_" + step["stepId"])
                        widgets.append(auto_widget.dump())
                    else:
                        auto_widget = AutoCompleteWidget("TEST_" + step["stepId"])
                        widgets.append(auto_widget.dump())

                    # Format image and video assets
                    if "testFirstImage" in step:
                        image_asset = Asset("image", "TEST_" + step["stepId"],
                                            "test_image%05d" % int(step["testFirstImage"]))
                    else:
                        image_asset = Asset("image", "TEST_" + step["stepId"], "image%05d" % int(step["firstImage"]))

                    assets = [image_asset.dump()]

                    video_name = ""
                    if "testFirstImage" in step and "testLastImage" in step:
                        video_name = "video-test_image%05d-test_image%05d" % (int(step["testFirstImage"]),
                                                                              int(step["testLastImage"]))
                    elif step["firstImage"] and step["lastImage"]:
                        video_name = "video-image%05d-image%05d" % (int(step["firstImage"]), int(step["lastImage"]))

                    if video_name:
                        video_asset = Asset("video", "TEST_" + step["stepId"], video_name)
                        assets.append(video_asset.dump())

                    # Format overall step
                    formatted_steps.append(
                        CommentedMap(
                            [
                                ("code", "TEST_%s" % str(step["stepId"])),
                                ("studio_metadata", studio_metadata),
                                ("widgets", widgets),
                                ("assets", assets),
                            ]
                        )
                    )

                # Format objectives
                self.formattedTestObjectives.append(CommentedMap([
                    ("name", objective["name"]),
                    ("code", "TEST_%d" % (i + 1)),
                    ("steps", formatted_steps)
                ]))

    def copy_info_assets(self):
        for sourceDir in INFORMATION_CARD_LIST:
            copy_assets(sourceDir, self.phaseDir)

    def dump(self, yaml_obj, stream):
        global INFORMATION_CARD_LIST
        INFORMATION_CARD_LIST = []

        self.format_learn_data()
        self.format_test_data()

        self.copy_info_assets()

        icon_asset = Asset("icon")
        icon_asset.stepId = "phase"
        icon_asset.name = "icon"

        self.assets.append(icon_asset.dump())

        yaml_obj.dump(
            CommentedMap([("name", self.name), ("publish", self.publish), ("supported_app", self.supported_app),
                          ("distribution_groups", self.distributionGroups),
                          ("country_restriction", self.countryRestriction), ("assets", self.assets),
                          ("objectives", self.formattedLearnObjectives),
                          ("test_objectives", self.formattedTestObjectives)]), stream)
