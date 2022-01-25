"""MAKE A MEME."""

import click
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class MemeText:
    """Make a MEME, class."""

    def __init__(self, image_path, top, bottom, save_path, fontsize, border):
        """init..."""
        self.image_path = image_path
        self.top = top
        self.bottom = bottom
        self.save_path = save_path
        self.default_fontsize = fontsize
        self.current_fontsize = self.default_fontsize
        self.border = border
        self.white = (255, 255, 255, 0)
        self.black = (0, 0, 0, 128)

        self.image = Image.open(self.image_path)
        self.draw = ImageDraw.Draw(self.image)

        self.default_font = ImageFont.truetype(
            "impact.ttf", self.default_fontsize)
        self.font = self.default_font

        self.draw_top()
        self.draw_bottom()

        if self.save_path:
            self.save()
        else:
            self.image.show()

    def fit_width(self, text):
        """Check text width < image width
        if greater make font smaller and check again."""
        image_width, image_height = self.image.size
        text_width, text_height = self.font.getsize(text)
        if text_width >= image_width - 10:
            self.current_fontsize -= 1
            self.font = ImageFont.truetype("impact.ttf", self.current_fontsize)
            self.fit_width(text)

    def save(self):
        self.image.save(self.save_path)

    def draw_top(self):
        if self.top:
            self.current_fontsize = self.default_fontsize
            self.font = self.default_font
            self.fit_width(self.top)
            x = self.offset_width_for(self.top)
            self.draw_border_text(x, 0, self.top)

    def draw_bottom(self):
        if self.bottom:
            self.current_fontsize = self.default_fontsize
            self.font = self.default_font
            self.fit_width(self.bottom)
            x = self.offset_width_for(self.bottom)
            y = self.offset_height_for(self.bottom)
            self.draw_border_text(x, y, self.bottom)

    def offset_width_for(self, text):
        image_width, image_height = self.image.size
        text_width, text_height = self.font.getsize(text)
        offset_x = (image_width / 2) - (text_width / 2)
        return offset_x

    def offset_height_for(self, text):
        """Offset heigth."""
        image_width, image_height = self.image.size
        ascent, descent = self.font.getmetrics()
        offset_y = image_height - ascent - descent
        return offset_y

    def draw_border_text(self, x, y, text):
        """Draw black border around text, origin is top left.
        https://stackoverflow.com/questions/47123649/pil-draw-transparent-text-on-top-of-an-image
        """
        width = self.border
        self.draw.text(
            (x - width, y), text, self.black, font=self.font)
        self.draw.text(
            (x + width, y), text, self.black, font=self.font)
        self.draw.text(
            (x, y - width), text, self.black, font=self.font)
        self.draw.text(
            (x, y + width), text, self.black, font=self.font)

        self.draw.text(
            (x + width, y + width), text, self.black, font=self.font)
        self.draw.text(
            (x + width, y - width), text, self.black, font=self.font)
        self.draw.text(
            (x - width, y - width), text, self.black, font=self.font)
        self.draw.text(
            (x - width, y + width), text, self.black, font=self.font)

        self.draw.text((x, y), text, self.white, font=self.font)

    def metrics(self, text):
        """get metrics...

        https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pils-imagefont-class
        """

        print(f'image size: {self.image.size}')
        print(f' text size: {self.font.getsize(text)}')
        ascent, descent = self.font.getmetrics()
        print(f'    ascent: {ascent}')
        print(f'   descent: {descent}')
        print(f'      mask: {self.font.getmask(self.top).getbbox()}')


@click.command()
@click.option("--image", type=click.Path(exists=True))
@click.option("--top")
@click.option("--bottom")
@click.option("--save", type=click.Path())
@click.option("--fontsize", default=80)
@click.option("--border", default=3)
def main(image, top, bottom, save, fontsize, border):
    mm = MemeText(image, top, bottom, save, fontsize, border)


if __name__ == '__main__':
    main()
