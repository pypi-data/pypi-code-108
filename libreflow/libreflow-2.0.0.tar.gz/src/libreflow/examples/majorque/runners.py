from kabaret import flow

from libreflow import baseflow


class AfterEffect(baseflow.runners.EditFileRunner):

    ICON = ("icons.libreflow", "afterfx")

    @classmethod
    def supported_extensions(cls):
        return [".aep", ".png", ".jpg"]

    def executable(self):
        return (
            "C:/Program Files/Adobe/Adobe After Effects 2020/Support Files/AfterFX.exe"
        )


class AfterEffectRender(baseflow.runners.EditFileRunner):

    ICON = ("icons.libreflow", "afterfx")

    @classmethod
    def supported_extensions(cls):
        return [".aep"]


class Photoshop(baseflow.runners.EditFileRunner):

    ICON = ("icons.flow", "photoshop")
    TAGS = ["2D Drawing", "Image Editing"]

    @classmethod
    def supported_extensions(cls):
        return [".psd", ".png", ".jpg"]

    def executable(self):
        return (
            "C:/Program Files/Adobe/Adobe Photoshop CC 2020/Support Files/Photoshop.exe"
        )
