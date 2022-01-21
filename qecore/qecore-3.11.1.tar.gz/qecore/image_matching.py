#!/usr/bin/env python3
import sys
from os import path
from time import sleep
from dogtail.rawinput import click
from behave import step
from qecore.utility import run


try:
    import cv2
except ModuleNotFoundError:
    print("You need to install an 'opencv-python' via pip or 'python3-opencv' via yum/dnf.")
except ImportError:
    print("A possibility of an error on secondary architecture. Image matching will not be available.")


HELP_MESSAGE = """
You are encouraged to build your own step function according to your needs.
Two steps that you see bellow are:
    * General step that just compares and asserts the result.
    * General step that just compares and clicks on the found result.

What is needed for image match:
    * You need to capture an image in which we look for the element you want to find.
        * Provided by capture_image method in Matcher class.
        * This option is True by default.
        * If you have your own, set capture=False and provide self.screen_path in the Matcher class.

    * You need to match the two images, you are looking for a 'needle'.
      So you provide it in function or in step call (.feature file).
        * Provided by match which will return True or False. Lets user react on False return value.
        * Provided by assert_match which will assert the result and terminate the test on False.

    * (Optional) You can draw the result for attachment or
            your own confirmation that matching works.
        * Provided by draw method on Matcher instance to get an image with highlighted needle.
          Highlight is a red rectangle exactly in a place of a match, surrounding provided needle.

    * (Optional) You can click on your found result.
        * Provided by click method in Matcher instance.
        * Requirements are of course success of a match/assert_match.

    * (Optional) You can embed result to test report.
        * For this option the method draw is required.
        * Use method provided in TestSandbox class:
            attach_image_to_report(context, image=image_location, caption="DefaultCaption")
        * Or embed it on your own:
            context.embed("image/png", open(image_location, "rb").read(), caption="DefaultCaption")
        * Remember that result is saved in Matcher instance as
            self.diff_path which equals "/tmp/diff.png"

    * (Optional) You can search only in region of screen
        * Firstly, you have to save the region into context.opencv_region attribute
        * Format of this attribute is tuple (node.position, node.size):
            position and size are (x, y) tuples of integers
"""

@step('Image "{needle}" is shown on screen')
@step('Image "{needle}" is shown on screen with threshold "{threshold:f}"')
def image_match(context, needle, threshold=0.8):
    """
    Function with behave step decorators::

        Image "{needle}" is shown on screen
        Image "{needle}" is shown on screen with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    """

    image_match_instance = Matcher(context)
    image_match_instance.assert_match(needle, threshold)
    image_match_instance.draw()


@step('Image "{needle}" is not shown on screen')
@step('Image "{needle}" is not shown on screen with threshold "{threshold:f}"')
def image_not_match(context, needle, threshold=0.8):
    """
    Function with behave step decorators::

        Image "{needle}" is not shown on screen
        Image "{needle}" is not shown on screen with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    """

    image_match_instance = Matcher(context)
    positive_match = image_match_instance.match(needle, threshold)
    if positive_match:
        image_match_instance.draw()
        context.attach_opencv = True
    assert not positive_match, "".join((
        f"Image '{needle}' was found, that was not supposed to happen."
    ))


@step('Image "{needle}" is shown in region')
@step('Image "{needle}" is shown in region with threshold "{threshold:f}"')
def image_region_match(context, needle, threshold=0.8):
    """
    Function with behave step decorators::

        Image "{needle}" is shown in region
        Image "{needle}" is shown in region with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    """

    region = getattr(context, "opencv_region", None)
    assert region is not None, "".join((
        "No region, you must set context.opencv_region first!"
    ))
    image_match_instance = Matcher(context)
    image_match_instance.capture_image()
    image_match_instance.crop_image(region)
    image_match_instance.assert_match(needle, threshold, capture=False)
    image_match_instance.draw()


@step('Image "{needle}" is not shown in region')
@step('Image "{needle}" is not shown in region with threshold "{threshold:f}"')
def image_region_not_match(context, needle, threshold=0.8):
    """
    Function with behave step decorators::

        Image "{needle}" is not shown in region
        Image "{needle}" is not shown in region with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    """

    region = getattr(context, "opencv_region", None)
    assert region is not None, "No region, you must set context.opencv_region first!"
    image_match_instance = Matcher(context)
    image_match_instance.capture_image()
    image_match_instance.crop_image(region)
    positive_match = image_match_instance.match(needle, threshold, capture=False)
    if positive_match:
        image_match_instance.draw()
        context.attach_opencv = True
    assert not positive_match, "".join((
        f"Image '{needle}' was found, that was not supposed to happen."
    ))

@step('Locate and click "{needle}"')
def locate_and_click(context, needle):
    """
    Function with behave step decorator::

        Locate and click "{needle}"

    Explanation:

    * **needle** - location of the file to match.
    """

    image_match_instance = Matcher(context)
    image_match_instance.assert_match(needle)
    image_match_instance.click()


class Matcher:
    def __init__(self, context):
        """
        Initiate Matcher instance.

        :type context: <behave.runner.Context>
        :param context: Context object.
        """

        self.context = context
        self.screen_path = "/tmp/pic.png"
        self.diff_path = "/tmp/diff.png"
        self.capture_image_cmd = f"gnome-screenshot -f {self.screen_path}"
        self.needle_width = 0
        self.needle_height = 0
        self.matched_value = 0.0
        self.matched_loc = (0, 0)

        self.ori_img = None
        self.ori_img_gray = None
        self.needle = None
        self.needle_size = None


    def capture_image(self):
        """
        Captures the image.
        """

        run(self.capture_image_cmd)


    def crop_image(self, region):
        """
        Crops the image.

        :type region: list
        :param region: List with four values: (x, y, w, h)
        """

        self.ori_img = cv2.imread(self.screen_path)
        (x, y), (w, h) = region
        if self.context.sandbox.session_type == "wayland":
            y += self.context.sandbox.shell.child("System", "menu").size[1]
        self.ori_img = self.ori_img[y:y+h, x:x+w]
        cv2.imwrite(self.screen_path, self.ori_img)


    def assert_match(self, needle, threshold=0.8, capture=True):
        """
        Calls and asserts the result of :py:func:`match`.

        :type needle: str
        :param needle: Needle location.

        :type threshold: float
        :param threshold: Value of acceptable match.

        :type capture: bool
        :param capture: Decides if the image will be captured.
        """

        assert self.match(needle, threshold, capture), "".join((
            f"Image match value: {self.matched_value}"
        ))



    def match(self, needle, threshold=0.8, capture=True):
        """
        Trying to find the needle image inside the captured image.

        :type needle: str
        :param needle: Needle location.

        :type threshold: float
        :param threshold: Value of acceptable match.

        :type capture: bool
        :param capture: Decides if the image will be captured.

        :rtype: bool
        :return: Boolean value of the matching.
        """

        if capture:
            self.capture_image()

        self.ori_img = cv2.imread(self.screen_path)
        self.ori_img_gray = cv2.cvtColor(self.ori_img, cv2.COLOR_BGR2GRAY)
        self.needle = cv2.imread(path.abspath(needle), 0)
        self.needle_width, self.needle_height = self.needle.shape[::-1]

        match = cv2.matchTemplate(self.ori_img_gray, self.needle, cv2.TM_CCOEFF_NORMED)
        _, self.matched_value, _, self.matched_loc = cv2.minMaxLoc(match)

        return self.matched_value > threshold


    def draw(self):
        """
        Draws the result to the original image.
        """

        self.needle_size = (self.matched_loc[0] + self.needle_width, \
                            self.matched_loc[1] + self.needle_height)
        cv2.rectangle(self.ori_img, self.matched_loc, self.needle_size, (0, 0, 255), 2)
        cv2.imwrite(self.diff_path, self.ori_img)


    def click(self):
        """
        Clicks to the center of the result.
        """

        match_center_x = self.matched_loc[0] + int(self.needle_width / 2)
        match_center_y = self.matched_loc[1] + int(self.needle_height / 2)
        click(match_center_x, match_center_y)
        sleep(1)
