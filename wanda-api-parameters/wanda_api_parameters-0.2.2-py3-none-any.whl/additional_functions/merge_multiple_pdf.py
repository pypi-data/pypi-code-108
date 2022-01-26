from PyPDF2 import PdfFileMerger
import os

def merge_pdf(source_path, output_name: str, add_bookmark: bool=True):
    """Merge all pdfs in source_path."""
    if type(source_path) is list:
        pdfs = source_path
        source_path = os.path.split(source_path[0])[0]
    else:
        pdfs = []
        for file in os.listdir(source_path):
            if file.endswith(".pdf"):
                pdfs.append(os.path.join(source_path, file))

    merger = PdfFileMerger(strict=False)
    for pdf in pdfs:
        if add_bookmark:
            merger.append(pdf, os.path.splitext(os.path.split(pdf)[1])[0])
        else:
            merger.append(pdf)

    merger.write(os.path.join(source_path, "{}.pdf".format(output_name)))
    merger.close()

if __name__ == "__main__":
    # Input
    fp = r"n:\Projects\11207000\11207338\D. Drawings\19Juli2021 - Network information\IWTP-8\Drawings"
    fp = r"n:\Projects\11207000\11207338\D. Drawings\19Juli2021 - Network information\SWTP-9\Drawings"
    merge_pdf(source_path=fp,
              output_name="SWTP-9_combined_drawings",
              add_bookmark=True)

