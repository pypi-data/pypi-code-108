import qrcode
from pyzbar import pyzbar
import typer
from PIL import Image
from pathlib import Path
import sys
from typing import Optional

app = typer.Typer(help="Awesome QRCode CLI")

@app.command()
def decode(image: str, all: Optional[bool] = False):
    if Path(image).is_file():
        """
        Decode an image containing a QRCode and retrive data from the QRCode.

        Optionally specify --all if you want to get all information extracted from the QRCode.
        """
        img = pyzbar.decode(Image.open(image))
        if all:
            data = img
        else:
            data = img[0].data.decode("utf-8")
        print(data)
    else:
        typer.echo(typer.style("Image invalid or unspecified!", fg="red", bold=True))

@app.command()
def create(data: str, name: str = typer.Option("default.png"), foreground: str = typer.Option("black", "--fg", "--foreground"), background: str = typer.Option("white", "--bg", "--background")):
    """
    Create an image containging your own data embedded into a QRCode.

    Optionally specify the name of the image with the --name flag.

    Other flags:

    --fg (specify foreground color of QRCode).
    
    --bg (specify background color of QRCode).
    """
    if ".png" not in name:
        typer.echo(typer.style("Name needs to end in .png!", fg="red", bold=True))
        sys.exit(1)

    qr = qrcode.QRCode(version=1, box_size=15, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(fill_color=foreground, back_color=background)
    image.save(name)