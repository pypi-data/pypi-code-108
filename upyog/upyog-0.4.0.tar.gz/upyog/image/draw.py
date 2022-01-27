from upyog.imports import *
from upyog.os.read_files import PathLike

__all__ = [
    "draw_rectangle",
    "draw_rectangles",
    "draw_rounded_rectangle",
    "draw_ellipse",
    "draw_circle",
    "draw_keypoint",
    "draw_keypoints",
    "draw_vertical_bars",
    "draw_horizontal_bars",
    "draw_text",
    "draw_text_within_xyxy",
    "Box",
]


def get_fill(fill: Tuple[int, int, int], opacity: float):
    if fill:
        opacity = int(opacity * 255)
        return fill + (opacity,)


def draw_rectangle(
    img: Image.Image,
    xyxy: tuple,
    fill: Optional[tuple] = (255, 255, 255),
    opacity=0.25,
    width=None,
):
    # NOTE: This draws a _filled_ rectangle
    new = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(new)
    fill = get_fill(fill, opacity)
    draw.rectangle(xyxy, fill=fill, outline=fill, width=width)

    img = Image.alpha_composite(img.convert("RGBA"), new)
    img = img.convert("RGB")

    return img


def draw_rectangles(
    img, xyxys: List[tuple], fill: Optional[tuple] = (255, 255, 255), opacity=0.25
):
    for xyxy in xyxys:
        img = draw_rectangle(img, xyxy, fill, opacity)

    return img


# TODO: Use ImageDraw.Draw
def draw_rounded_rectangle(
    img: Image.Image, xyxy: tuple, radius=10, color="white", opacity=1.0, width=3
):
    """Draw a rounded rectangle"""
    from aggdraw import Pen, Draw

    xl, yu, xr, yl = xyxy
    draw = Draw(img)
    pen = Pen(color, opacity=int(opacity * 255), width=width)
    r = radius

    # fmt: off
    draw.line((xl+r/2, yu, xr-r/2, yu), pen)      # Top Horizontal
    draw.arc((xr-r, yu, xr, yu+r), 0, 90, pen)    # Upper right

    draw.line((xr, yu+r/2, xr, yl-r/2), pen)      # Right Vertical
    draw.arc((xr-r, yl-r, xr, yl), 270, 360, pen) # Lower right

    draw.line((xr-r/2, yl, xl+r/2, yl), pen)      # Bottom Horizontal
    draw.arc((xl+r, yl, xl, yl-r), 0, 90, pen)    # Lower left

    draw.line((xl, yl-r/2, xl, yu+r/2), pen)      # Left Vertical
    draw.arc((xl, yu, xl+r, yu+r), 90, 180, pen)  # Upper left
    # fmt: on

    return draw.flush()


def draw_ellipse(img, xyxy, fill=(255, 255, 255), opacity=0.8):
    new = Image.new("RGBA", img.size)
    draw = ImageDraw.Draw(new)
    fill = get_fill(fill, opacity)

    draw.ellipse(xyxy, fill=fill, width=0, outline=None)
    img = Image.alpha_composite(img.convert("RGBA"), new)
    img = img.convert("RGB")

    return img


def draw_circle(img, xy, radius, fill=(255, 255, 255), opacity=0.8):
    x, y, r = *xy, radius
    xyxy = x - r, y - r, x + r, y + r
    return draw_ellipse(img, xyxy, fill, opacity)


def draw_keypoint(
    img, xy, fill=(255, 255, 255), opacity=0.8, radius=None, dynamic_radius=True
):
    radius = radius or get_dynamic_radius(img)
    return draw_circle(img, xy, radius, fill, opacity)


def draw_keypoints(
    img, xys, fill=(255, 255, 255), opacity=0.8, radius=None, dynamic_radius=True
):
    fills = None
    if fill:
        if not isinstance(fill[0], (list, tuple)):
            fills = [fill] * len(xys)
        else:
            fills = fill

    for xy, fill in zip(xys, fills):
        img = draw_keypoint(img, xy, fill, opacity, radius, dynamic_radius)
    return img


def get_dynamic_radius(img):
    # Borrowed from `icevision.draw_keypoints`
    w, h = img.size
    area = h * w
    r = int(0.01867599 * (area ** 0.4422045))
    return max(r, 1)


def calc_offset(thickness):
    return int((thickness - 1) / 2)


def draw_vertical_bars(img, width_percentages, fill, thickness, opacity):
    W, H = img.size
    off = offset = calc_offset(thickness)

    xyxys = []
    for w in width_percentages:
        if isinstance(w, float):
            w = W * w
            xyxys += [(w - off, 0, w + off, H)]
        elif isinstance(w, (tuple, list)):
            assert len(w) == 2
            start, end = w
            xyxys += [(W * start, 0, W * end, H)]

    return draw_rectangles(img, xyxys, opacity=opacity, fill=fill)


def draw_horizontal_bars(img, height_percentages, fill, thickness, opacity):
    W, H = img.size
    off = offset = calc_offset(thickness)

    xyxys = []
    for h in height_percentages:
        if isinstance(h, float):
            h = H * h
            xyxys += [(0, h - off, W, h + off)]
        elif isinstance(h, (tuple, list)):
            assert len(h) == 2
            start, end = h
            xyxys += [(0, H * start, W, H * end)]

    return draw_rectangles(img, xyxys, opacity=opacity, fill=fill)


color = lambda r, g, b: f"rgb({r},{g},{b})"


def get_font(font_path=None, size=30) -> ImageFont.FreeTypeFont:
    if font_path:
        return ImageFont.truetype(font_path, size=size)
    else:
        return get_fallback_font()


def get_fallback_font() -> ImageFont.FreeTypeFont:
    font_path = str(
        Path(__file__).parent.parent.parent / "assets" / "EuroStyleNormal.ttf"
    )
    return get_font(font_path, size=30)


def _write_text(
    text,
    xy,
    draw: ImageDraw.Draw,
    font: ImageFont.ImageFont,
    bordered=True,
    border_color="black",
    font_color="white",
    anchor=None,
):
    label = text
    x, y = xy
    if bordered:
        draw.text((x - 1, y), label, border_color, font, anchor)
        draw.text((x + 1, y), label, border_color, font, anchor)
        draw.text((x, y - 1), label, border_color, font, anchor)
        draw.text((x, y + 1), label, border_color, font, anchor)

        # thicker border
        draw.text((x - 1, y - 1), label, border_color, font, anchor)
        draw.text((x + 1, y - 1), label, border_color, font, anchor)
        draw.text((x - 1, y + 1), label, border_color, font, anchor)
        draw.text((x + 1, y + 1), label, border_color, font, anchor)

    try:
        draw.text(xy, text, font_color, font, anchor)
    except OSError as e:
        msg = f"Failed to write text {text} due to error: {e}"
        warnings.warn(msg)

    text_xyxy = draw.textbbox(xy, text, font, anchor)

    return draw, text_xyxy


def draw_text_within_xyxy(
    img: Image.Image,
    xyxy: tuple,
    label: str,
    font_path: str,
    base_font_size=20,
    pad_percentage: float = 0.03,
    text_color=(255, 255, 255),
    bordered: bool = False,
    add_background: bool = True,
    background_fill=(0, 0, 0),
    background_opacity=0.15,
    location: Literal["bottom", "top"] = "bottom",
):
    box = Box(xyxy)
    draw = ImageDraw.Draw(img)
    font = ImageFont.FreeTypeFont(font_path, size=base_font_size)
    _font = font
    pad = box.height * pad_percentage

    # Dynamically adjust font size to fit the bounding box
    text_box = draw.textbbox(box.bottom_center, label, font, anchor="mt")
    text_box = Box(text_box)
    if location == "bottom":
        text_box.adjust("y2", -pad)
    else:
        text_box.adjust("y1", pad)

    try:
        while not (text_box.height > box.height) and (text_box.width > box.width):
            font = ImageFont.FreeTypeFont(font_path, size=base_font_size)
            text_box = Box(draw.textbbox(box.bottom_center, label, font, anchor="mt"))
            text_box.adjust("x1", -pad)
            text_box.adjust("x2", pad)
            base_font_size -= 1

        _box = deepcopy(box)
        if location == "bottom":
            _box.adjust("y2", -pad)
        else:
            _box.adjust("y1", pad)

        text_xyxy = _box.bottom_center if location == "bottom" else _box.top_center
        anchor = "ms" if location == "bottom" else "mt"
        draw, text_xyxy = _write_text(
            label,
            text_xyxy,
            draw,
            font,
            bordered=bordered,
            border_color="black",
            font_color=text_color,
            anchor=anchor,
        )

        if add_background:
            # print(f"Before: {text_xyxy}")
            _xyxy = Box(text_xyxy)
            pad_x = _xyxy.height * 0.025
            pad_y = _xyxy.height * 0.03

            _xyxy.adjust("y1", -pad_y)
            _xyxy.adjust("x1", -pad_x)
            _xyxy.adjust("x2", pad_x)
            _x1, _y1, _x2, _y2 = _xyxy.xyxy

            # fmt: off
            # FIXME: yuck...
            x1,y1,x2,y2 = xyxy
            if _x1 < x1: _x1 = x1
            if _x2 > x2: _x2 = x2
            if _y2 > y2: _y2 = y2
            # if _y1 < y1: _y1 = xyxy[1]
            # fmt: on

            img = draw_rectangle(
                img, (_x1, _y1, _x2, _y2), background_fill, background_opacity
            )
    except Exception as e:
        larger_factor = text_box.area / box.area
        msg = f"Failed to resize text. Estimated font size is {larger_factor}x larger than bbox area. Exception={e}"
        warnings.warn(msg)

    return img


# Source: https://www.haptik.ai/tech/putting-text-on-images-using-python-part2/
def get_line_height(font: ImageFont.FreeTypeFont):
    return font.getsize("hg")[1]


# fmt: off
TEXT_POSITIONS = Literal[
    "top_left",       "top_center",        "top_right",
    "center_left",      "center",       "center_right",
    "bottom_left",   "bottom_center",   "bottom_right",
]

# https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
TEXT_ANCHORS = {
    "top_left":    None,      "top_center": "mt",        "top_right": "rt",
    "center_left": "lm",          "center": "mm",     "center_right": "rm",
    "bottom_left": "lb",   "bottom_center": "mb",     "bottom_right": "rb",
}
# fmt: on


def concat_multiline_text(text: Union[str, List[str]]):
    if isinstance(text, str):
        return text
    else:
        return "\n".join(text)


def _get_constraned_xyxy(img, height_constraints, width_constraints):
    return (
        img.width * width_constraints[0],
        img.height * height_constraints[0],
        img.width * width_constraints[1],
        img.height * height_constraints[1],
    )


def draw_text(
    img: Image.Image,
    text: Union[str, List[str]],
    position: TEXT_POSITIONS,
    font_path: Optional[PathLike] = None,
    font_size: int = 30,
    font_border=False,
    font_color=(255, 255, 255),
    font_border_color=(0, 0, 0),
    padding: Union[int, float] = 0.03,
    line_spacing: float = 1.3,  # Only used if text is List[str]
    height_constraints: Tuple[int, int] = (0.0, 1.0),
    width_constraints: Tuple[int, int] = (0.0, 1.0),
):
    assert position in TEXT_POSITIONS.__args__
    font = get_font(font_path, font_size)
    padding = int(img.height * padding) if isinstance(padding, float) else padding

    if isinstance(text, str):
        # Single-line text
        # TODO: Move this to a dedicated function?
        draw = ImageDraw.Draw(img)

        xyxy = _get_constraned_xyxy(img, height_constraints, width_constraints)
        img_box = Box(xyxy)
        img_box.shrink(padding)

        draw, _ = _write_text(
            text=text,
            xy=img_box[position],
            draw=draw,
            font=font,
            bordered=font_border,
            border_color=font_border_color,
            font_color=font_color,
            anchor=TEXT_ANCHORS[position],
        )

    else:
        img = _draw_multiline_text(
            img=img,
            position=position,
            lines=text,
            font=font,
            padding=padding,
            bordered_font=font_border,
            font_color=font_color,
            font_border_color=font_border_color,
            line_spacing=line_spacing,
            height_constraints=height_constraints,
            width_constraints=width_constraints,
        )
    return img


# https://www.haptik.ai/tech/putting-text-on-images-using-python-part2/
def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(" ")
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ""
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word,
            # add the line to the lines array
            lines.append(line)
    return lines


def _draw_multiline_text(
    img: Image.Image,
    # xy: Tuple[int, int],  # Starting point
    position: TEXT_POSITIONS,
    lines: List[str],
    font: ImageFont.FreeTypeFont,
    padding: int,
    bordered_font=False,
    font_color="white",
    font_border_color="black",
    line_spacing=1.0,
    height_constraints: Tuple[int, int] = (0.0, 1.0),
    width_constraints: Tuple[int, int] = (0.0, 1.0),
):
    assert position in TEXT_POSITIONS.__args__
    line_height = get_line_height(font)
    total_line_height = get_total_line_height(lines, font, line_spacing)
    draw = ImageDraw.Draw(img)

    # total_line_height = line_height * len(lines) * line_spacing

    xyxy = _get_constraned_xyxy(img, height_constraints, width_constraints)
    img_box = Box(xyxy)
    img_box.shrink(10)

    # fmt: off
    x, y = img_box[position]
    anchor = TEXT_ANCHORS[position]
    anchor = f"{anchor[0]}t"

    if "center" in position: y -= total_line_height / 2
    if "bottom" in position: y -= total_line_height
    # fmt: on

    lines_final = []
    for line in lines:
        lines_final += text_wrap(line, font, img_box.width)

    for line in lines_final:
        xy = (x, y)
        draw, _ = _write_text(
            line, xy, draw, font, bordered_font, font_border_color, font_color, anchor
        )
        y += line_height * line_spacing

    return img


def get_total_line_height(lines, font, line_spacing):
    line_height = get_line_height(font)
    num_lines = len(lines)

    height = line_height * (num_lines - 1) * line_spacing
    height += line_height

    return height


class Box:
    def __init__(self, xyxy):
        self._xyxy = xyxy
        self.x1, self.y1, self.x2, self.y2 = xyxy
        self.setup()

    def __getitem__(self, position: str):
        return getattr(self, position)

    # fmt: off
    def shrink_left  (self, amt: int): self.adjust("x1",  amt)
    def shrink_top   (self, amt: int): self.adjust("y1",  amt)
    def shrink_right (self, amt: int): self.adjust("x2", -amt)
    def shrink_bottom(self, amt: int): self.adjust("y2", -amt)
    # fmt: on

    def shrink(self, amt: int):
        "Decrease box dimensions by `amt` on all sides"
        self.shrink_left(amt)
        self.shrink_top(amt)
        self.shrink_right(amt)
        self.shrink_bottom(amt)

    def expand(self, amt: int):
        "Increase box dimensions by `amt` on all sides"
        self.adjust("y1", -amt)
        self.adjust("x1", -amt)
        self.adjust("x2", amt)
        self.adjust("y2", amt)

    def adjust(self, dim: str, amt):
        assert dim in ["x1", "x2", "y1", "y2"]
        setattr(self, dim, getattr(self, dim) + amt)
        self.setup()

    def setup(self):
        self._dimensions()
        self._centers()
        self._corners()
        self._points()

    def _dimensions(self):
        self.height = self.y2 - self.y1
        self.width = self.x2 - self.x1
        self.area = self.height * self.width

    def _centers(self):
        self.center_horz = self.x1 + self.width / 2
        self.center_vert = self.y1 + self.height / 2
        self.center = (self.center_horz, self.center_vert)

    def _corners(self):
        self.top_left = (self.x1, self.y1)
        self.bottom_right = (self.x2, self.y2)
        self.top_right = (self.x2, self.y1)
        self.bottom_left = (self.x1, self.y2)

    def _points(self):
        self.top_center = (self.center_horz, self.y1)
        self.bottom_center = (self.center_horz, self.y2)
        self.center_right = (self.x2, self.center_vert)
        self.center_left = (self.x1, self.center_vert)

    @property
    def cxcywh(self):
        return (self.center_horz, self.center_vert, self.width, self.height)

    @property
    def xyxy(self):
        return (self.x1, self.y1, self.x2, self.y2)

    def __repr__(self):
        return f"Box({self.x1}, {self.y1}, {self.x2}, {self.y2})"
