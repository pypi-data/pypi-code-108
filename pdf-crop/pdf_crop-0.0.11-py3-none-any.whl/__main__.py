import argparse
from rich.console import Console
from rich.table import Table
from pdf_crop.crop_pymupdf import PymuPDFCrop
from helper import rect_str


def parse_arguments():
    common_parser = argparse.ArgumentParser(add_help=True)
    common_parser.add_argument(
        "-i", "--input_file", type=str, required=True, help="Input PDF"
    )
    common_parser.add_argument(
        "-p",
        "--page",
        action="append",
        nargs=6,
        metavar=("number", "left", "top", "right", "bottom", "output"),
        required=False,
        help="Which pages to crop",
    )
    common_parser.add_argument("--space", type=int, default=5, help="Detection space")
    common_parser.add_argument(
        "--threshold", type=float, default=0.008, help="White threshold to recognize a border"
    )

    return common_parser.parse_known_args()


def validate_flags(flags):
    pass


def main():
    flags, unparsed = parse_arguments()
    validate_flags(flags)
    input_file = flags.input_file
    page_option = flags.page

    table = Table(title="PDF Crop Summary", leading=0)
    table.add_column("Page No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("MediaBox", justify="right", style="magenta")
    table.add_column("CropBox", justify="right", style="magenta")
    table.add_column("Output", justify="right", style="green")

    pdf_crop = PymuPDFCrop(input_file=input_file, space=flags.space, threshold=flags.threshold)
    if page_option is None:
        for i in range(pdf_crop.page_count()):
            output_file, media_box, crop_box = pdf_crop.crop(i)
            table.add_row(str(i), rect_str(media_box), rect_str(crop_box), output_file)
    else:
        for option in page_option:
            page_no = int(option[0])
            left = int(option[1])
            top = int(option[2])
            right = int(option[3])
            bottom = int(option[4])
            output_file = option[5]
            if left == -1 or top == -1 or right == -1 or bottom == -1:
                crop_box = None
            else:
                crop_box = (left, top, right, bottom)
            output_file, media_box, crop_box = pdf_crop.crop(
                page_no, output_file=output_file, crop_box=crop_box
            )
            table.add_row(
                option[0], rect_str(media_box), rect_str(crop_box), output_file
            )
    # Show summary
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
